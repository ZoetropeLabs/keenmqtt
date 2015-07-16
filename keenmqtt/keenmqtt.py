""" Keen mqtt relay class """

from mosquitto import Mosquitto
from keen import KeenClient

class KeenMQTT():

	def __init__(self):
		self.connect_mqttc()
		self.connect_keen()

	def connect_mqttc(self):
		self.mqttc = Mosquitto()

	def connect_keen(self):

	def onmessage(self, mosq, obj, msg):
		"""Called when an MQTT message is recieved."""
		

	def update():
		"""Call to process any outstanding MQTT messages."""
		self.mqttc.loop()

