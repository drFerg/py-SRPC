from setuptools import setup, find_packages

setup(
   name='SRPC',    # This is the name of your PyPI-package.
   version='0.1',     # Update the version number for new releases
   author='Fergus Leahy',
   license='ISC',
   url='https://github.com/fergul/py-SRPC',
   packages=find_packages(),
   scripts=['bin/hwdb.py', 'bin/echoClient.py'],
)
