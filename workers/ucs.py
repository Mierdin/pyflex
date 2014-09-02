#!/usr/bin/env python
""" UCS worker class for pyflex

"""
from worker import FlexWorker
from functions.functions_ucs import UcsFunctions
from UcsSdk import *

class UcsWorker(FlexWorker):
    """ A child worker class that pertains specifically to UCS """

    def startworker(self):
        """ Starts this worker """

        #Connect to UCSM
        handle = UcsHandle()

        ucsauth = self.config['auth']['ucs']

        handle.Login(
            ucsauth['host'], 
            ucsauth['user'], 
            ucsauth['pass']
        )

        fxns = UcsFunctions(handle, self.config)
        fxns.ucsHousekeeping()
        fxns.createVLANSandVSANS()
        fxns.createUCSPools()
        fxns.ucsCreatePolicies()
        fxns.createBootPolicy()
        fxns.createVNICTemplates()
        fxns.createVHBATemplates()
        fxns.createSpTemplate()
        fxns.spawnZerglings()
        #DEFINE REST OF UCS WORKFLOW HERE