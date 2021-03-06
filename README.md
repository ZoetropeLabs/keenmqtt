[![Build Status](https://travis-ci.org/ZoetropeLabs/keenmqtt.svg?branch=master)](https://travis-ci.org/ZoetropeLabs/keenmqtt) [![Documentation Status](https://readthedocs.org/projects/keenmqtt/badge/?version=latest)](https://readthedocs.org/projects/keenmqtt/?badge=latest) [![Coverage Status](https://coveralls.io/repos/ZoetropeLabs/keenmqtt/badge.svg?branch=master&service=github)](https://coveralls.io/github/ZoetropeLabs/keenmqtt?branch=master)

# keenmqtt
A MQTT client which will send configured MQTT messages to keen IO as events for later analysis.

![System Diagram of keenmqtt](docs/system_diagram.png)

### The problem
IoT data platforms are often a big investment in time and sometimes money, so often a simple MQTT set up is used. This should not prevent one from being able to perform historical analysis of data points.

See the **[blog article](https://zoetrope.io/tech-blog/simple-mqtt-iot-logging)** with a live example.

### The solution
keenmqtt is a simple bridge which will listen for specified MQTT messages and log them on your KeenIO project. This complete history of events will allow you to:

1. Create graphs of old data, such as temperature.
2. Use this data to refine your system.
3. Display this data to your users.

keenmqtt can be run as a standalone daemon, or used in a python program.

## Installation

```bash
	pip install keenmqtt
```

Or clone/download the repo, run `python setup.py install` in the root. 

## Usage

### Command Line
Running the stand alone package requires a config file, see `example/config.yaml` for a template. The CLI currently assumes that the MQTT system uses JSON messages and that all fields will be logged in the keenIO event.

After installing, run the following to log events:

```bash
	keenmqtt -c config.yaml
```

A config file contains connection details for the MQTT broker, as well as a mapping of MQTT topic patterns to keenIO collections. For example, if you are publishing temperature events:

```yaml
collection_mappings:
    'temperature/+': temperature
```

Any number of mappings can be added.

### In your program
keenMQTT has been specifically designed so that almost any part of the pipeline can be overriden or customised.

The source is well documented, [see readthedocs](http://keenmqtt.readthedocs.org/en/latest/keenmqtt.html#module-keenmqtt.keenmqtt)

**Example: Custom payload formats**
As an example; if you had a sensor which publishes an ascii format sensor reading, you can define a custom payload decoder for topics which match that sensor value as follows:

```python
from keenmqtt import KeenMQTT

class CustomDecoder(KeenMQTT):
	def decode_payload(self, topic, payload):
		"""Decode a plain ASCII format sensor reading"""
		if 'humidity' in topic:
			event = {
				"value": int(payload)
			}
		else:
			#Assume default JSON encoding
			event = KeenMQTT.decode_payload(self, topic, payload)
		return event
```

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request

## History

0.0.1: Working version of the CLI app.

## Credits

Written by Ben Howes & Richard Webb of [Zoetrope](https://zoetrope.io)

With thanks to:

1. [KeenIO](https://keen.io) for a super service.
2. [Eclipse Paho](https://www.eclipse.org/paho/clients/python/) for a great MQTT client.

## License
MIT Licence