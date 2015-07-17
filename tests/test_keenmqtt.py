from keenmqtt import KeenMQTT
import iso8601

class TestKeenMQTTMethods:
	"""Test the KeenMQTT methods"""

	def setup_method(self, _):
		self.keenmqtt = KeenMQTT()

	def test_on_mqtt_message(self, mocker):
		"""Test full message processing, up to keen IO level."""
		timestamp = u"2015-07-17T15:19:26.782672"
		self.keenmqtt.add_collection_mapping("home/exact", "exact")
		mocker.patch.object(self.keenmqtt, 'push_event', autospec=True)
		mocker.patch.object(self.keenmqtt, 'get_time', autospec=True, return_value=timestamp)
		mqtt = Struct()
		mqtt.topic = "home/exact"
		mqtt.payload = '{"test1": 120, "test2": "Hello World!", "test3":true, "test4":null}'
		collection = 'exact'
		event = {
			'mqtt_topic': 'home/exact',
			u"test1": 120, 
			u"test2": u"Hello World!",
			u"test3": True,
			u"test4": None,
			'keen': {
				'timestamp': timestamp
			}
		}
		self.keenmqtt.on_mqtt_message({}, {}, mqtt)
		self.keenmqtt.push_event.assert_called_once_with(collection, event)

	def test_process_topic(self):
		"""Check that the original topic is added to the event."""
		event = {}
		topic = "topic"
		ret_bool = self.keenmqtt.process_topic(event, topic)
		assert ret_bool == True
		assert event['mqtt_topic'] == topic

	def test_process_collection(self):
		"""Test matching some different topic subscriptions.

		Gradually add more subsciptions and check it sill works.
		"""
		assert len(self.keenmqtt.collection_mapping) == 0
		self.keenmqtt.add_collection_mapping("home/exact", "exact")
		assert self.keenmqtt.process_collection("home/exact", {}) == "exact"
		self.keenmqtt.add_collection_mapping("away/+", "away")
		assert self.keenmqtt.process_collection("home/exact", {}) == "exact"
		assert self.keenmqtt.process_collection("away/nonexact", {}) == "away"
		self.keenmqtt.add_collection_mapping("wayaway/#", "wayaway")
		assert self.keenmqtt.process_collection("home/exact", {}) == "exact"
		assert self.keenmqtt.process_collection("away/nonexact", {}) == "away"
		assert self.keenmqtt.process_collection("wayaway/non/exact/test", {}) == "wayaway"

	def test_add_collection_mapping(self):
		"""Test adding and matching basic subscription."""
		topic = "home/test"
		collection = "test"
		self.keenmqtt.add_collection_mapping(topic, "test")
		assert topic in self.keenmqtt.collection_mapping
		assert self.keenmqtt.collection_mapping[topic] == collection

	def test_decode_payload(self):
		"""Test basic json object decoding."""
		json_string = '{"test1": 120, "test2": "Hello World!", "test3":true, "test4":null}'
		test1 = 120
		test2 = u"Hello World!"
		test3 = True
		test4 = None
		decoded_payload = self.keenmqtt.decode_payload("test", json_string)
		assert isinstance(decoded_payload, dict)
		assert decoded_payload[u"test1"] == test1
		assert decoded_payload[u"test2"] == test2
		assert decoded_payload[u"test3"] == test3
		assert decoded_payload[u"test4"] == test4

	def test_process_payload(self):
		"""Test processing the payload."""
		event = {}
		topic = "topic"
		message = {'test':None}
		ret_bool = self.keenmqtt.process_payload(event, topic, message)
		assert ret_bool == True
		assert 'test' in event
		assert event['test'] == None

	def test_process_time(self):
		"""Check that the timestamp is correctly added"""
		event = {}
		topic = "topic/string"
		message = {'test':None}
		ret_bool = self.keenmqtt.process_time(event, topic, message)
		assert ret_bool == True
		assert isinstance(event['keen'], dict)
		assert isinstance(event['keen']['timestamp'], str)
		iso8601.parse_date(event['keen']['timestamp'])

	def test_get_time(self):
		"""Test that a valid timestring is returned from the default get_time method"""
		topic = "topic/string"
		message = {'test':None}
		timestring = self.keenmqtt.get_time(topic, message)
		# Expect no problems
		iso8601.parse_date(timestring)

class TestKeenMQTTMocks:
	pass

class Struct:
	pass