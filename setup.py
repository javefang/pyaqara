"""Setup file for aqara package."""
import os
from distutils.core import setup

ver = os.environ["VERSION"]

setup(name='pyaqara',
 version=ver,
 description='Python API for interfacing with the Aqara gateway',
 url='https://github.com/javefang/pyaqara',
 download_url="https://github.com/javefang/pyaqara/tarball/" + ver,
 author='Xinghong Fang',
 author_email= 'xinghong.fang@gmail.com',
 license='MIT',
 packages=['aqara'],
 keywords = ['aqara', 'home', 'automation', 'sensor'],
 install_requires=[
   'pycrypto'
 ]
)
