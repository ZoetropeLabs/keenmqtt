""" Functions and classes for a command line app version of keenmqtt """

import logging
import yaml
import time
import click

from keenmqtt import KeenMQTT


@click.command()
@click.option('-c', '--config', default="config.yaml", help="Relative path to config file, defaults to config.yaml.")
def main(config):

	with open(config) as configfp:
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

if __name__ == '__main__':
    main()