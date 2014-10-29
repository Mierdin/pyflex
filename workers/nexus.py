#!/usr/bin/env python
""" UCS worker class for pyflex

"""
from worker import FlexWorker
from functions.functions_ucs import UcsFunctions
from UcsSdk import *

class NexusWorker(FlexWorker):
    """ A child worker class that generates and installs Nexus configurations """

    def startworker(self):
        """ Starts this worker """

        #Connect to UCSM
        handle = UcsHandle()

        nxauth = self.config['auth']['nexus']

        handle.Login(
            nxauth['switcha'],
            nxauth['user'], 
            nxauth['pass']
        )

        fxns = UcsFunctions(handle, self.config)
        configa = fxns.gen_snippet('../templates/N5K-A.j2')
        configb = fxns.gen_snippet('../templates/N5K-B.j2')

        transmit_config(nxauth['a'], configa)
        transmit_config(nxauth['b'], configb)

        #TODO: Need to do some clean-up tasks below, or figure out how to slipstream things into the initial config.
            # For instance, the WWPN aliases and zoning - that shouldn't be in the template at all. That should be 
            # generated from a smaller template and transmitted using dynamically retrieved data from UCS