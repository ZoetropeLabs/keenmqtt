# keenmqtt
A MQTT client which will send configured MQTT messages to keen IO as events for later analysis.

### The problem
IoT data platforms are often a big investment in time and sometimes money, so often a simple MQTT set up is used. This should not prevent one from being able to perform historical analysis of data points.

### The solution
keenmqtt is a simple bridge which will listen for specified MQTT messages and log them on your KeenIO project. This complete history of events will allow you to:
1. Create graphs of old data, such as temperature.
2. Use this data to refine your system.
3. Display this data to your users.

keenmqtt can be run as a standalone daemon, or used in a python program.

## Installation

Clone the repo, run `python setup.py install` in the root. 

Will get on pip soon!

## Usage

### Command Line
Running the stand alone package requires a config file, see `example/config.yaml` for a template.

After installing, run the following to log events:

```bash
	keenmqtt config.yaml
```

### In your program

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request

## History

TODO: Write history

## Credits

Written by Ben Howes & Richard Webb of [Zoetrope](https://zoetrope.io)

With thanks to:
1. [KeenIO](https://keen.io) for a super service.
2. [Eclipse Paho](https://www.eclipse.org/paho/clients/python/) for a great MQTT client.

## License
MIT Licence