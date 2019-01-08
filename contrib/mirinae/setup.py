from setuptools import setup, Extension

mirinae_module = Extension('mirinae', sources=['mirinaemodule.c', 'crypto/sph/sph_groestl.c', 'crypto/kupyna/kupyna_tables.c', 'crypto/kupyna/kupyna512.c'])

setup( name='mirinae',
       version='0.1.0',
       description='Python module for Mirinae hash algorithm.',
       maintainer='iamstenman',
       maintainer_email='iamstenman@protonmail.com',
       url='https://github.com/MicroBitcoin/MirinaePython',
       keywords=['mirinae'],
       ext_modules=[mirinae_module])
