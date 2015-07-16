from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

import keenmqtt

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md')

setup_path = os.path.dirname(__file__)
reqs_file = open(os.path.join(setup_path, 'requirements.txt'), 'r')
reqs = reqs_file.readlines()
reqs_file.close()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='keenmqtt',
    version=keenmqtt.__version__,
    url='https://github.com/ZoetropeImaging/keenmqtt',
    license='MIT',
    author='Ben Howes',
    tests_require=['pytest'],
    install_requires=reqs,
    cmdclass={'test': PyTest},
    author_email='ben@zoetrope.io',
    description='An MQTT client which will send configured MQTT messages to keen IO as events for later analysis.',
    long_description=long_description,
    packages=['keenmqtt'],
    include_package_data=True,
    platforms='any',
    test_suite='keenmqtt.test.test_keenmqtt',
    classifiers = [
        'Programming Language :: Python',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    extras_require={
        'testing': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'keenmqtt = keenmqtt.app:main',
        ]
    }
)
