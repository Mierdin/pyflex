#!/usr/bin/env python
""" Base worker class for pyflex

"""

class FlexWorker:
    """ Base worker class for PyFlex """

    def __init__(self, config):
        """ Imports configuration information for this worker instance """
        self.config = config

    def endworker(self):
        """ ends this worker """
        pass
