""" Keen mqtt relay class """

import paho.mqtt.client as mqtt
from keen import KeenClient
import json
from datetime import datetime

class KeenMQTT:

	def __init__(self):
		self.ready = False
		self.collection_mapping = {}

	def setup(self, mqtt_client=None, keen_client=None, settings=None):
		"""Setup the clients for this instance.

		Normally called with a settings object containing `keen` and `mqtt` keys
		with dictionary values of settings.

		"""
		if mqtt_client:
			self.mqtt_client = mqtt_client
		else:
			self.connect_mqtt_client(settings)

		if keen_client:
			self.keen_client = keen_client
		else:
			self.connect_keen(settings)
		self.ready = True

	def connect_mqtt_client(self, settings):
		self.mqtt_client = mqtt()
		self.mqtt_client.on_message = self.on_mqtt_message
		self.mqtt_client.on_connect = self.on_mqtt_connect

	def connect_keen(self, settings):
		self.keen_client = KeenClient()

	def on_mqtt_connect(self):
		"""Called when an MQTT connection is made."""
		pass #TODO

	def on_mqtt_message(self, mosq, obj, mqtt_message):
		"""Called when an MQTT message is recieved."""
		topic = mqtt_message.topic
		payload = mqtt_message.payload
		message = self.decode_payload(topic, payload)
		event = {}
		collection = self.process_collection(topic, message)
		if collection:
			if self.process_topic(event, topic):
				if self.process_payload(event, topic, message):
					if self.process_time(event, topic, message):
						self.push_event(collection, event)

	def update():
		"""Call to process any outstanding MQTT messages."""
		self.mqtt_client.loop()

	def process_topic(self, event, topic):
		"""Process an incoming MQTT message's topic string.

		If the topic contains pertinant information, such as the device ID or location,
		this method can be overriden to perform any translation. By default, a key called
		``mqtt_topic`` will be added to the event dictionary.

		Args:
			self: KeenMQTT instance, or subclass.
			event: The event dictionary for this mqtt message.
			topic: The topic string.

		Returns:
			A Boolean indicating if this message should continue through the pipeline. Return
			``False`` to cancel the processing of this event and stop it from being saved in keen.
		"""
		event['mqtt_topic'] = topic
		return True

	def process_collection(self, topic, message):
		"""Assign a collection to the MQTT message.

		By default will find a matching topic in the collection_mapping dictionary and return
		the associated string. Could also be based on event contents.

		Args:
			self: KeenMQTT instance, or subclass.
			event: The event dictionary for this mqtt message.
			topic: The topic string.

		Return:
			A string indicating the Keen IO collection which this event should be pushed to, or 
			false if a matching event collection could not be found.
		"""
		for subscription in self.collection_mapping:
			if mqtt.topic_matches_sub(subscription, topic):
				return self.collection_mapping[subscription]
		return False

	def add_collection_mapping(self,sub,collection):
		"""Add a subecription to event collection mapping.

		This will overide existing subscriptions if present.

		Args:
			self: KeenMQTT instance, or subclass.
			sub: The string subscription pattern.
			collection: The sting event collection.

		Return:
			None.
		"""
		self.collection_mapping[sub] = collection

	def decode_payload(self, topic, payload):
		"""Decode the payload of an incoming MQTT payload.

		By default a JSON object is expected, however this method can be overriden to provide
		alternative means to extract a MQTT payload. For example, a binary format could be 
		extracted here.

		Args:
			self: KeenMQTT instance, or subclass.
			topic: The topic string.
			payload: Raw MQTT payload.

		Returns:
			A dictionary containing the decoded MQTT payload.

		Raises:
			ValueError: Whent the JSON payload cannot be parsed.
		"""
		return json.loads(payload)

	def process_payload(self, event, topic, message):
		"""Process an incoming MQTT message's payload.

		Perform any required translations to the payload of the MQTT message, such as removing

		Args:
			self: KeenMQTT instance, or subclass.
			event: The event dictionary for this mqtt message.
			topic: The topic string.
			message: the decoded MQTT payload

		Returns:
			A Boolean indicating if this message should continue through the pipeline. Return
			``False`` to cancel the processing of this event and stop it from being saved in Keen IO.
		"""
		event.update(message)
		return True

	def process_time(self, event, topic, message):
		"""Process the timestamp which will be sent to Keen IO.

		If the MQTT message contains time information which should be used instead of the event being
		timestamped by Keen IO, set it here.

		Args:
			self: KeenMQTT instance, or subclass.
			event: The event dictionary for this mqtt message.
			topic: The topic string.
			message: The message dictionary.	

		Returns:
			A Boolean indicating if this message should continue through the pipeline. Return
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
			self: KeenMQTT instance, or subclass.
			topic: The topic string.
			message: The message dictionary.	

		Returns:
			A string containing ISO-8601 string.
		"""
		return datetime.now().isoformat()
	
	def push_event(self, collection, event):
		assert self.ready == True
		self.keen_client.add_event(collection, event)
