#!/usr/bin/env python
""" PyFlex

    flexconfig.py is the configuration parser for PyFlex
"""

#TODO: Consider use of the leading underscore for private methods

from jinja2 import Environment, FileSystemLoader
import yaml

ENV = Environment(loader=FileSystemLoader('./templates/'))

class FlexConfig:
    """ Class that handles parsing a YAML configuration
        file and providing info to workers
    """

    def __init__(self, configfile):
        self.configfile = configfile

    def parse_config(self):
        """Pulls YAML configuration from file and returns dict object"""
        with open(self.configfile) as _:
            return yaml.load(_)