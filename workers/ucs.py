#!/usr/bin/env python
""" UCS worker class for pyflex

"""
from worker import FlexWorker
from functions.functions_ucs import UcsFunctions
from UcsSdk import *

class UcsWorker(FlexWorker):

    def startworker(self):

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
        #DEFINE REST OF UCS WORKFLOW HERE