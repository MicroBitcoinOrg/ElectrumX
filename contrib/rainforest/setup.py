from setuptools import setup, Extension

rainforest_module = Extension('rainforest', sources=['rainforestmodule.c'])

setup(name='rainforest',
		version='0.1.0',
		description='Python module for Rainforest hash algorithm.',
		maintainer='iamstenman',
		maintainer_email='iamstenman@protonmail.com',
		url='https://github.com/MicroBitcoin/RainforestPython',
		keywords=['rainforest'],
		ext_modules=[rainforest_module])
