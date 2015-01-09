#!/usr/bin/env python
""" UCS worker class for pyflex

    In the future, this will really be the core renderer. All of the
    work of deleting config that shouldn't be there, or creating it
    when it should, will be handled here.

    Think of the functions file(s) as just that - containers of functions.
    This file is where those functions are called, and where you determine
    your workflow (i.e. checking for existence of a resource before deleting
    it)

"""

#Import UCS Packages
from UcsSdk import UcsHandle

#Import PyFlex Dependencies
from worker import FlexWorker
from functions.newfunctions_ucs import NewUcsFunctions


class UcsWorker(FlexWorker):
    """ A child worker class that pertains specifically to UCS """

    FABRICS = ['A', 'B']

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

        newfxns = NewUcsFunctions(handle, self.config['ucs']['org'])

        """ VLANS """

        #Temporary dict, to take the groups out of the picture temporarily
        #This is a good example of why you need to rethink this mapping
        vlans = {}

        #Get a list of all VLANs, regardless of group
        for group in self.config['vlans']:

            #Add to temporary dict
            for vlanid, vlanname in self.config['vlans'][group] \
                    .iteritems():
                vlans[str(vlanid)] = vlanname

        #Remove any VLANs within UCS that are not in temporary dict
        for mo in newfxns.getVLANs().OutConfigs.GetChild():
            if mo.Id in vlans.keys() and vlans[mo.Id] == mo.Name:
                pass
            else:
                newfxns.removeVLAN(mo)

        #Add all VLANs in the temporary dict to UCS
        for vlanid, vlanname in vlans.iteritems():
            newfxns.createVLAN(vlanid, vlanname)

        """ VSANS """

        #Temporary dict, to take the groups out of the picture temporarily
        #This is a good example of why you need to rethink this mapping
        vsans = {}

        #Get a list of all VLANs, regardless of group
        for fabric in self.config['vsans']:

            #Add to temporary dict
            for vsanid, vsanname in self.config['vsans'][fabric] \
                    .iteritems():
                vsans[str(vsanid)] = vsanname

        #Remove any VSANs within UCS that are not in temporary dict
        for mo in newfxns.getVSANs().OutConfigs.GetChild():
            if mo.Id in vsans.keys() and vsans[mo.Id] == mo.Name:
                pass
            else:
                newfxns.removeVSAN(mo)

        #Add all VSANs in the temporary dict to UCS
        for fabric in ['a', 'b']:
            for vsanid, vsanname in self.config['vsans'][fabric].iteritems():
                newfxns.createVSAN(fabric.upper(), vsanid, vsanname)

        """ IP KVM POOL """

        newfxns.createIpPool(
            self.config['ucs']['pools']['ip']['start'],
            self.config['ucs']['pools']['ip']['end'],
            self.config['ucs']['pools']['ip']['mask'],
            self.config['ucs']['pools']['ip']['gw']
        )

        """ MAC POOLS """

        #Pull MAC Pool Configuration Info
        macpools = self.config['ucs']['pools']['mac']

        #MAC Pools
        for fabric in macpools:
            newfxns.createMacPool(
                fabric,
                macpools[fabric]['blockbegin'],
                macpools[fabric]['blockend']
            )

        """ WWPN POOLS """

        #Pull WWPN Pool Configuration Info
        wwpnpools = self.config['ucs']['pools']['wwpn']

        #WWPN Pools
        for fabric in wwpnpools:
            newfxns.createWwpnPool(
                fabric,
                wwpnpools[fabric]['blockbegin'],
                wwpnpools[fabric]['blockend']
            )

        #TODO: UUID POOL

        #TODO: WWNN POOL

        """ GLOBAL POLICIES """

        newfxns.setPowerPolicy("grid")
        newfxns.setChassisDiscoveryPolicy(str(self.config['ucs']['links']))

        """ QOS """

        newfxns.setGlobalQosPolicy(self.config['qos'])
        for classname, hostcontrol in self.config['qos']['classes'] \
                .iteritems():
            newfxns.createQosPolicy(classname, hostcontrol)

        """ ORG-SPECIFIC POLICIES """

        newfxns.createLocalDiskPolicy("NO_LOCAL", "no-local-storage")
        newfxns.createLocalDiskPolicy("RAID1", "raid-mirrored")
        newfxns.createHostFWPackage("HOST_FW_PKG")
        newfxns.createMaintPolicy("MAINT_USERACK", "user-ack")
        newfxns.createNetControlPolicy("NTKCTRL-CDP")

        """ VNIC TEMPLATES """

        # Create vNIC Templates
        for vnicprefix, vlangroup in self.config['ucs']['vlangroups'] \
                .iteritems():

            for fabricid in self.FABRICS:

                #Create vNIC Template
                vnic = newfxns.createVnicTemplate(vnicprefix, fabricid)[0]

                #Remove any VLANs on this emplate that are not in the config
                for vlanMo in newfxns.getVnicVlans(vnic).OutConfigs \
                        .GetChild():

                    #Have to use Name and values - no "Id" parameter
                    if vlanMo.Name in self.config['vlans'][vlangroup].values():
                        pass
                    else:
                        newfxns.removeVnicVlan(vnic, vlanMo.Name)

                #Add VLANs from configuration to this vNIC
                for vlanid, vlanname in self.config['vlans'][vlangroup] \
                        .iteritems():

                    newfxns.createVnicVlan(vnic, vlanname)

        """ VHBA TEMPLATES """

        # Create vHBA Templates
        for fabricid in self.FABRICS:
            vhba = newfxns.createVhbaTemplate(fabricid)[0]

            # No removal method necessary; will override existing VSAN setting
            for vsanid, vsanname in self.config['vsans'][fabricid.lower()] \
                    .iteritems():

                newfxns.createVhbaVsan(vhba, vsanname)

        """ SP TEMPLATES """

        spt = newfxns.createSPTemplate(self.config['ucs']['sptname'])

        vnics = [ #TODO: This is an ugly way to do this
            "ESX-MGMT-A",
            "ESX-MGMT-B",
            "ESX-NFS-A",
            "ESX-NFS-B",
            "ESX-PROD-A",
            "ESX-PROD-B"
        ]

        vhbas = [
            "ESX-VHBA-A",
            "ESX-VHBA-B"
        ]

        #Create vNIC VCON assignments
        for vnic in vnics:
            transport = "ethernet"
            order = str(vnics.index(vnic) + 1)
            newfxns.setVconOrder(spt[0], vnic, transport, order)
            newfxns.addVnicFromTemplate(spt[0], vnic)

        for vhba in vhbas:
            transport = "fc"
            order = str(vhbas.index(vhba) + 1)
            newfxns.setVconOrder(spt[0], vhba, transport, order)
            newfxns.addVhbaFromTemplate(spt[0], vhba)

        newfxns.setWWNNPool(spt[0], "ESXi-WWNN")
        newfxns.setPowerState(spt[0], "admin-up")

        # newfxns.spawnZerglings(
        #         spt[0],
        #         self.config['ucs']['spprefix'],
        #         self.config['ucs']['numbertospawn']
        #     )
