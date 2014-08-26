#!/usr/bin/env python
""" Base worker class for pyflex

"""

class BaseWorker:

    def __init__(self, config):
        
        self.config = config