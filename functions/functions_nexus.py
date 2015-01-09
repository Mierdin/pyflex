#!/usr/bin/env python
""" pyflex

    functions_nexus contains all functions pertinent to building,
    configuring, or retrieving data from a Cisco Nexus switch

    Will use the paramiko library for iterating through a rendered
    Jinja2 template line-by-line, and writing to a switch.

"""

import paramiko
from jinja2 import Environment, FileSystemLoader

class NexusFunctions:
    """ Class that contains all functions for Cisco Nexus"""

    FABRICS = ['A', 'B']

    def __init__(self, handle, nxconfig):
        self.handle = handle

        #TODO: nxconfig is currently just the entire config. Prune this
        self.config = nxconfig

    def gen_template(self, template):
        """ Renders a Jinja2 template. """

        ENV = Environment(loader=FileSystemLoader('../templates/'))

        template = ENV.get_template(template + ".j2")
        return template.render(config=self.config)

    def transmit_config(self, auth, config):
        pass
