#!/usr/bin/env python
""" UCS worker class for pyflex

"""
from worker import FlexWorker
from functions.functions_ucs import UcsFunctions
from functions.newfunctions_ucs import NewUcsFunctions
from UcsSdk import *

class UcsWorker(FlexWorker):
    """ A child worker class that pertains specifically to UCS """

    def startworker(self):
        """ Starts this worker """

        #Connect to UCSM
        handle = UcsHandle()

        ucsauth = self.config['auth']['ucs']

        print ucsauth

        handle.Login(
            ucsauth['host'], 
            ucsauth['user'], 
            ucsauth['pass']
        )

        newfxns = NewUcsFunctions(handle, self.config['general']['org'])


        """ VLANS """

        vlans = {}

        #Get a list of all VLANs, regardless of group
        for group in self.config['vlans']:
            if group != 'storage': #Don't want to explicitly add FCoE VLANs here, that's done in the VSAN creation
                for vlanid, vlanname in self.config['vlans'][group].iteritems():  #TODO: This is really ugly because of the VLAN layout in the config file. Maybe need to figure out a way to restructure it.
                    vlans[vlanid] = vlanname

        #Add all VLANs in the list
        for vlanid, vlanname in vlans.iteritems():
            newfxns.createVLAN(vlanid, vlanname)

        #Remove any VLANs within UCS that are not in the config
        for mo in newfxns.getVLANs().OutConfigs.GetChild():
            if mo.Dn[:10] == "fabric/lan" and mo.Dn[:22] != "fabric/lan/net-default":
                if int(mo.Id) in vlans:
                    pass
                else:
                    newfxns.removeVLAN(mo)


        """ VSANS """

        vsans = {}

        #Create VSANs from the list
        for vsanid, vsanname in self.config['vsans']['a'].iteritems():
            newfxns.createVSAN("A", vsanid, vsanname)
        for vsanid, vsanname in self.config['vsans']['b'].iteritems():
            newfxns.createVSAN("B", vsanid, vsanname)

        #Remove any VSANs within UCS that are not in the config
        for mo in newfxns.getVSANs().OutConfigs.GetChild():
            if int(mo.Id) in self.config['vsans']['a'] or int(mo.Id) in self.config['vsans']['b']:
                pass
            else:
                if int(mo.Id) != 1:
                    newfxns.removeVSAN(mo)

        """ MAC POOLS """

        #TODO: Lots of shortcuts taken here. Need to come back and clean up this atrocious mess.
        pools = self.config['ucs']['pools']

        #TODO: Implement IP pool. Preferably in suborg, as housekeeping is populating ext-mgmt with dummy block

        #MAC Pools
        for fabric in pools['mac']: #TODO: This loop is here for the future, but obviously since the name is statically set, this only works with a single pool per fabric, currently.
            newfxns.createMacPool(fabric, pools['mac'][fabric]['blockbegin'], pools['mac'][fabric]['blockend'])










        #I am commenting this out while I am re-developing the workflow. The functions
        #referred to below are untouched - feel free to uncomment and use them
        
        #fxns = UcsFunctions(handle, self.config)
        #fxns.ucsHousekeeping()
        #fxns.createVLANSandVSANS()
        #fxns.createUCSPools()
        #fxns.ucsCreatePolicies()
        #fxns.createBootPolicy()
        #xns.createVNICTemplates()
        #fxns.createVHBATemplates()
        #fxns.createSpTemplate()
        #fxns.spawnZerglings()
        #DEFINE REST OF UCS WORKFLOW HERE