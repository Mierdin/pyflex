#!/usr/bin/env python
""" pyflex

    comms module for pyflex. Should place all communication functions like
    email, slack, irc, here.
"""

import logging
from flexconfig import FlexConfig
from workers.ucs import UcsWorker

class Comms:

    def __init__(self):

        cfg_obj = FlexConfig("config.yml")
        self.config = cfg_obj.parse_config()
