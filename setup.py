from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys
import re

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(os.path.join(here, filename)) as f:
            buf.append(f.read())
    return sep.join(buf)

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

reqs_file = open(os.path.join(here, 'requirements.txt'), 'r')
reqs = [req.strip() for req in reqs_file.readlines()]
reqs_file.close()

def find_version(*file_paths):
    version_file = codecs.open(os.path.join(here, *file_paths), 'r').read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


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
    version=find_version('keenmqtt', '__init__.py'),
    url='https://github.com/ZoetropeImaging/keenmqtt',
    license='MIT',
    author='Ben Howes',
    tests_require=['pytest', 'pytest-mock', 'iso8601'],
    install_requires=reqs,
    cmdclass={'test': PyTest},
    author_email='ben@zoetrope.io',
    description='An MQTT client which will send configured MQTT messages to keen IO as events for later analysis.',
    long_description=read_md('README.md'),
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
        'testing': ['pytest', 'pytest-mock', 'iso8601'],
    },
    entry_points={
        'console_scripts': [
            'keenmqtt = keenmqtt.app:main',
        ]
    }
)
