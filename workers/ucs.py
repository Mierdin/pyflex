#!/usr/bin/env python
""" UCS worker class for pyflex

"""
from worker import BaseWorker
from functions.functions_ucs import UcsFunctions
from UcsSdk import *

class UcsWorker(BaseWorker):

    def startworker(self):

        #Connect to UCSM
        handle = UcsHandle()
        handle.Login(
            self.config['auth']['ucs']['host'], 
            self.config['auth']['ucs']['user'], 
            self.config['auth']['ucs']['pass']
        )

        fxns = UcsFunctions(handle, self.config)

        #DEFINE REST OF UCS WORKFLOW HERE