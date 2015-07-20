""" Keen mqtt relay class """

import paho.mqtt.client as mqtt
from keen import KeenClient
import json
from datetime import datetime
import logging

logger = logging.getLogger('keenmqtt')

class KeenMQTT:

	def __init__(self):
		self.ready = False
		self.running = False
		self.collection_mapping = {}

	def setup(self, mqtt_client=None, keen_client=None, settings=None):
		"""Setup the clients for this instance.

		Normally called with a settings object containing `keen` and `mqtt` keys
		with dictionary values of settings.

		Args:
			mqtt_client Optional[class]: An instance of an Paho MQTT client class.
			keen_client Optional[class]: An instance of a KeenClient.
			settings Optional[dict]: A settings dict, normally loaded from a config.yaml file.
		Return:
			None
		"""
		if mqtt_client:
			self.mqtt_client = mqtt_client
			self.register_subscriptions()
		else:
			self.connect_mqtt_client(settings)

		if keen_client:
			self.keen_client = keen_client
		else:
			self.connect_keen(settings)

		if 'collection_mappings' in settings:
			for subscription in settings['collection_mappings']:
				collection = settings['collection_mappings'][subscription]
				self.add_collection_mapping(subscription, collection)

		self.ready = True

	def connect_mqtt_client(self, settings):
		"""Setup MQTT client.

		Please note that the MQTT client will not actually connect until either ``step`` or ``start``
		has been called.

		Args:
			settings Optional[dict]: The settings object, such as one read from config.yaml
		Return:
			None
		"""
		mqtt_settings = settings['mqtt']
		if 'client_id' not in mqtt_settings:
			import uuid
			mqtt_settings['client_id'] = str(uuid.uuid4())

		self.mqtt_client = mqtt.Client(mqtt_settings['client_id'])
		self.mqtt_client.on_message = self.on_mqtt_message
		self.mqtt_client.on_connect = self.on_mqtt_connect
		if 'user' in mqtt_settings and len(mqtt_settings['user']):
			self.mqtt_client.username_pw_set(mqtt_settings['user'], mqtt_settings['pass'])
		self.mqtt_client.connect(mqtt_settings['host'], mqtt_settings['port'])

	def connect_keen(self, settings):
		"""Setup the Keen IO client.

		Args:
			settings Optional[dict]: The settings object, such as one read from config.yaml
		Return:
			None
		"""
		if 'keen' in settings:
			self.keen_client = KeenClient(**settings['keen'])
		else:
			self.keen_client = KeenClient()

	def on_mqtt_connect(self, c, client, userdata, rc):
		"""Called when an MQTT connection is made.

		See the Paha MQTT client documentation ``on_connect`` documentation for arguments.
		"""
		logger.info("MQTT Client connected")
		self.register_subscriptions()
		self.ready = True

	def register_subscriptions(self):
		"""This should always be called since re-subscribes after any
		unexpected disconnects.
		"""
		for subscription in self.collection_mapping:
			self.mqtt_client.subscribe(subscription)

	def on_mqtt_message(self, mosq, obj, mqtt_message):
		"""Called when an MQTT message is recieved.

		See the Paha MQTT client documentation ``on_message`` documentation for arguments.
		"""
		topic = mqtt_message.topic
		payload = mqtt_message.payload
		messages = self.decode_payload(topic, payload)
		
		if len(messages):
			for message in messages:
				event = {}
				collection = self.process_collection(topic, message)
				if collection:
					if self.process_topic(event, topic):
						if self.process_payload(event, topic, message):
							if self.process_time(event, topic, message):
								self.push_event(collection, event)

	def start(self):
		"""Automatically loop in a background thread."""
		self.running = True
		self.mqtt_client.loop_start()

	def stop(self):
		"""Disconnect and stop. """
		self.mqtt_client.loop_stop()
		self.running = False

	def step(self):
		"""Do a single MQTT step.

		Use this if you're not running keenmqtt in a background thread with ``start``/``stop``

		"""
		if self.running:
			raise BackgroundRunningException("Cannot perform a step whilst background loop is running.")
		self.mqtt_client.loop()

	def process_topic(self, event, topic):
		"""Process an incoming MQTT message's topic string.

		If the topic contains pertinant information, such as the device ID or location,
		this method can be overriden to perform any translation. By default, a key called
		``mqtt_topic`` containing the topic string will be added to the event dictionary.

		Args:
			event (dict): The event dictionary for this mqtt message.
			topic (str): The topic string.

		Return:
			bool: A Boolean indicating if this message should continue through the pipeline. Return
			``False`` to cancel the processing of this event and stop it from being saved in keen.
		"""
		event['mqtt_topic'] = topic
		return True

	def process_collection(self, topic, message):
		"""Assign a collection to the MQTT message.

		By default will find a matching topic in the collection_mapping dictionary and return
		the associated string. Could also be based on event contents.

		Args:
			event (dict): The event dictionary for this mqtt message.
			topic (str): The topic string.

		Return:
			str: A string indicating the Keen IO collection which this event should be pushed to, or 
			false if a matching event collection could not be found.
		"""
		for subscription in self.collection_mapping:
			if mqtt.topic_matches_sub(subscription, topic):
				return self.collection_mapping[subscription]
		return False

	def add_collection_mapping(self,sub,collection):
		"""Add a subcription to event collection mapping.

		This will overide existing subscriptions if present.

		Args:
			sub (str): The string subscription pattern.
			collection (str): The sting event collection.

		Return:
			None
		"""
		self.collection_mapping[sub] = collection

	def decode_payload(self, topic, payload):
		"""Decode the payload of an incoming MQTT payload.

		By default a JSON object is expected, however this method can be overriden to provide
		alternative means to extract a MQTT payload. For example, a binary format could be 
		extracted here.

		Args:
			topic (str): The topic string.
			payload (str): Raw MQTT payload.

		Returns:
			An array of dictionaries containing the decoded MQTT payload.

		Raises:
			ValueError: Whent the JSON payload cannot be parsed.
		"""
		return [json.loads(payload)]

	def process_payload(self, event, topic, message):
		"""Process an incoming MQTT message's payload.

		Perform any required translations to the payload of the MQTT message, such as removing

		Args:
			event (dict): The event dictionary for this mqtt message.
			topic (str): The topic string.
			message (dict): the decoded MQTT payload

		Returns:
			bool: A Boolean indicating if this message should continue through the pipeline. Return
			``False`` to cancel the processing of this event and stop it from being saved in Keen IO.
		"""
		event.update(message)
		return True

	def process_time(self, event, topic, message):
		"""Process the timestamp which will be sent to Keen IO.

		If the MQTT message contains time information which should be used instead of the event being
		timestamped by Keen IO, set it here.

		Args:
			event (dict): The event dictionary for this mqtt message.
			topic (str): The topic string.
			message (dict): The message dictionary.	

		Returns:
			bool: A Boolean indicating if this message should continue through the pipeline. Return
			``False`` to cancel the processing of this event and stop it from being saved in Keen IO.
		"""
		iso_datetime = self.get_time(topic, message)
		if iso_datetime is not None:
			event['keen'] = {
				"timestamp": iso_datetime
			}
		return True

	def get_time(self, topic, message):
		"""Get the timestamp to send to Keen IO.

		This method is used to extract the timestamp from the MQTT message if required, 
		or to generate a timestamp. By default, the current time will be fetched.

		Args:
			topic (str): The topic string.
			message (dict): The message dictionary.	

		Returns:
			str: A string containing ISO-8601 string.
		"""
		return datetime.now().isoformat()
	
	def push_event(self, collection, event):
		"""Thin wrapper around Keen IO API object.

		Args:
			collection (str): The collection string to push to
			event (dict): The complete event to push
		Returns:
			None
		"""
		assert self.ready == True
		logger.debug("Saving event to collection {collection}: '{event}'".format(collection=collection, event=event))
		self.keen_client.add_event(collection, event)

class BackgroundRunningException(Exception):
	""" Used when the user tries to run in the foreground whilst
	a background loop is already running."""
	pass