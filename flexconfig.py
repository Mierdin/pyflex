#!/usr/bin/env python
""" PyFlex

    flexconfig.py is the configuration parser for PyFlex
"""

#TODO: Consider use of the leading underscore for private methods

# Need to have a configuration validator. Unrealistic to be completely 
# exhaustive, but the simple stuff like ensuring no VLAN overlap, 
# similarly named templates, etc. should be good. Sort of indicates 
# the need for a configuration importer unique to each infrastructure 
# type. Ensure that there is only one VSAN per fabric, etc. Ensure that
# there is no VLAN that overlaps with teh VSAN IDs that you selected,
# in order to preserve FCoE VLAN IDs.

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