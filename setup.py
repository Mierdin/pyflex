from setuptools import setup, find_packages
from distutils.command.install import install as _install

import sys
import platform

if not sys.version_info[0] == 2:
    print "Sorry, Python 3 is not supported (yet)"
    exit()

if sys.version_info[0] == 2 and sys.version_info[1] < 6:
    print "Sorry, Python < 2.6 is not supported"
    exit()

setup(name='pyflex',
      version='1.0.0',
      description="Python framework for building and maintaining a Flexpod environment",
      author="Matt Oswalt",
      author_email="matt@keepingitclassless.net",
      url="https://github.com/Mierdin/pyflex",
      packages=find_packages('.'),
      install_requires=[
                    "setuptools>0.6",
                    "paramiko>=1.7.7.1",
                    "lxml>3.0",
                    "jinja2>=2.7.1",
                    "PyYAML>=3.10",
                    "configobj>=5.0.5"
                    ],
      license="apache",
      platforms=["Linux; OS X; Windows"],
      keywords=('Flexpod'),
      classifiers=[
          'Programming Language :: Python',
          'Topic :: System :: Networking',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ]
      )
