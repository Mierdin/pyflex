#!/usr/bin/env python
""" UCS worker class for pyflex

    In the future, this will really be the core renderer. All of the 
    work of deleting config that shouldn't be there, or creating it
    when it should, will be handled here.

"""
from worker import FlexWorker
#from functions.functions_ucs import UcsFunctions
from functions.newfunctions_ucs import NewUcsFunctions
from UcsSdk import UcsHandle


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

            #Exclusing VLANs used for FCoE
            if group != 'storage':

                #TODO: This is really ugly because of the VLAN layout in the
                #config file. Maybe need to figure out a way to restructure it
                for vlanid, vlanname in self.config['vlans'][group].iteritems():
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

        #Pull MAC Pool Configuration Info
        macpools = self.config['ucs']['pools']['mac']

        #MAC Pools
        for fabric in macpools: #TODO: This loop is here for the future, but obviously since the name is statically set, this only works with a single pool per fabric, currently.
            newfxns.createMacPool(fabric, macpools[fabric]['blockbegin'], macpools[fabric]['blockend'])

        """ WWPN POOLS """

        #Pull WWPN Pool Configuration Info
        wwpnpools = self.config['ucs']['pools']['wwpn']

        #WWPN Pools
        for fabric in wwpnpools: #TODO: This loop is here for the future, but obviously since the name is statically set, this only works with a single pool per fabric, currently.
            newfxns.createWwpnPool(fabric, wwpnpools[fabric]['blockbegin'], wwpnpools[fabric]['blockend'])

        """ GLOBAL POLICIES """

        newfxns.setPowerPolicy("grid")
        newfxns.setChassisDiscoveryPolicy(str(self.config['ucs']['links']))

        """ QOS """

        newfxns.setGlobalQosPolicy(self.config['qos'])
        for classname, hostcontrol in self.config['qos']['classes'].iteritems():
            newfxns.createQosPolicy(classname, hostcontrol)

        """ ORG-SPECIFIC POLICIES """

        newfxns.createLocalDiskPolicy("NO_LOCAL", "no-local-storage")
        newfxns.createLocalDiskPolicy("RAID1", "raid-mirrored")
        newfxns.createHostFWPackage("HOST_FW_PKG")
        newfxns.createMaintPolicy("MAINT_USERACK", "user-ack")
        newfxns.createNetControlPolicy("NTKCTRL-CDP")