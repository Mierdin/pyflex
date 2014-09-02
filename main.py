#!/usr/bin/env python
""" pyflex

    Main starting point for PyFlex. Can be instantiated
    in another library, or run as a script as shown below.
"""

import logging
from flexconfig import FlexConfig
from workers.ucs import UcsWorker

class PyFlex:
    """ Main PyFlex class. Primarily used to
        spawn workers and import configurations
    """

    def __init__(self):
        """ Creates an object from configuration service """

        cfg_obj = FlexConfig("config.yml")
        self.config = cfg_obj.parse_config("config.yml")

    def start(self):
        """ Creates new workers and starts them """
        this_ucs = UcsWorker(self.config)

        this_ucs.startworker()

    def end(self):
        """ Ends worker processes """
        pass

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(format='%(asctime)s %(message)s')
    #pp = pprint.PrettyPrinter(indent=1)
    pyflex = PyFlex()
    pyflex.start()
    #   pyflex.join()
    print "FINISHED"
