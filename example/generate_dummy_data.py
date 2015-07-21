
import paho.mqtt.client as mqtt
import json
import random
import time

"""
	Very simple and hacky script to publish a load of mock sensor values for testing purposes.
"""

def make_dummy_payload(sensor_id, sensor_value):
	payload = {
		'sensor_id': sensor_id,
		'sensor_value': sensor_value,
		'type': 'temperature'
	}
	return json.dumps(payload)

if __name__ == "__main__":
	client = mqtt.Client('dummy')
	client.connect('localhost')
	sensor_id = 'sensor101'
	for i in xrange(100):
		sensor_value = random.uniform(10, 30)
		payload = make_dummy_payload(sensor_id, sensor_value)
		print payload 
		client.publish("home/temperature/{}".format(sensor_id), payload)
		client.loop()
		time.sleep(2)