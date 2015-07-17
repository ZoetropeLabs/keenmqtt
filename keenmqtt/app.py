""" Functions and classes for a command line app version of keenmqtt """

import logging
import yaml
from optparse import OptionParser
import time

from keenmqtt import KeenMQTT


if __name__ == '__main__':

	parser = OptionParser()
	parser.add_option("-c", "--config", dest="config",
		help="relative path to config file, defaults to config.yaml",
		default="config.yaml")

	(options, args) = parser.parse_args()

	with open(options.config) as configfp:
		config = yaml.load(configfp)

	logging.basicConfig(level=logging.DEBUG)
	logging.getLogger("requests").setLevel(logging.WARNING)

	keenmqtt = KeenMQTT()
	keenmqtt.setup(settings=config)
	logging.info("starting")
	keenmqtt.start()

	try:
		while True:
			time.sleep(10)
	except KeyboardInterrupt() as e:
		logging.info("shutting down")
		keenmqtt.stop()