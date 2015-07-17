
from keenmqtt import KeenMQTT
import iso8601

class TestKeenMQTTMethods:
	"""Test the KeenMQTT methods"""

	def setup_method(self, _):
		self.keenmqtt = KeenMQTT()

	def test_process_topic(self):
		event = {}
		topic = "topic"
		ret_bool = self.keenmqtt.process_topic(event, topic)
		assert ret_bool == True
		assert event['mqtt_topic'] == topic

	def test_process_collection_exact(self):
		assert len(self.keenmqtt.collection_mapping) == 0

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