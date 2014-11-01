#!/usr/bin/env python
""" pyflex

    This is the new home for cmdlet-style python bindings for UCS.

    These will be designed to fail gracefully. Any error handling will
    be done with the purpose of keeping the program going. (i.e. if an
    object being created already exists, etc. Not going to check to see
    if an object exists everytime before creating one)

    This file may go away in the future - an ideal way of doing things is
    to have this be it's own separate library, PyFlex being a consumer of
    said library. Just FYI

"""

#Import UCS Packages
from UcsSdk import OrgOrg, UcsException, UcsValidationException

#Import Filters
from UcsSdk import FilterFilter, EqFilter, WcardFilter, NeFilter


class NewUcsFunctions(object):
    """ A working class to help ease how we work with UCS objects """

    # TODO: Currently requiring org info at start of
    def __init__(self, handle, orgName):

        # TODO: need to have a check for valid handle i.e. logged in
        self.handle = handle

        #Some functions refer directly to root (i.e. VLANs)
        self.orgroot = self.handle.GetManagedObject(
            None, None,
            {
                "Dn": "org-root/"
            })

        #Set self.org object. Referred to throughout the various functions
        if orgName != "root":
            #Create requested suborg
            self.org = self.createSubOrg(orgName)
        else:
            self.org = self.orgroot

        #Sets other org-related properties. Functions should refer directly
        #to self.orgNameDN - self.orgName is used only by suborg functions
        self.orgName = self.org[0].Name
        self.orgNameDN = self.org[0].Dn + "/"

        print "Instantiated New Functions"

    def getSubOrg(self, orgName):
        suborg = self.handle.GetManagedObject(
            None, OrgOrg.ClassId(),
            {
                OrgOrg.DN: "org-root/org-" + orgName
            })
        return suborg

    def createSubOrg(self, orgName):
        ''' Retrieves only sub-organizations, not root '''
        try:
            return self.handle.AddManagedObject(
                self.orgroot, OrgOrg.ClassId(),
                {
                    "Dn": "org-root/org-" + orgName,
                    "Descr": orgName,
                    "Name": orgName
                })
        except UcsException:
            print "Sub-organization already exists"
            return self.getSubOrg(orgName)

    ###########
    #  VLANS  #
    ###########

    def getVLANs(self):

        #Retrieve only user-created VLANs
        inFilter = FilterFilter()
        neFilter = NeFilter()
        neFilter.Class = "fabricVlan"
        neFilter.Property = "name"
        neFilter.Value = "default"
        inFilter.AddChild(neFilter)

        return self.handle.ConfigResolveClass("fabricVlan", inFilter=inFilter)

    def createVLAN(self, vlanid, vlanname):
        try:
            self.handle.AddManagedObject(
                self.orgroot, "fabricVlan",
                {
                    "Name": vlanname,
                    "PubNwName": "",
                    "DefaultNet": "no",
                    "PolicyOwner": "local",
                    "CompressionType": "included",
                    "Dn": "fabric/lan/net-" + vlanname,
                    "McastPolicyName": "",
                    "Id": str(vlanid),
                    "Sharing": "none"
                })
            print "Created VLAN " + str(vlanid) + ": " + vlanname
        except UcsException as e:
            print "VLAN " + str(vlanid) + ": " + vlanname + \
                " already exists -- " + e.errorDescr

    def removeVLAN(self, mo):
        #TODO: in the usual workflow, you're retrieving the VLAN objects
        #twice. Once for the get method, and once for this one. See if you
        #can be more efficient (or if it's a good idea at all)
        try:
            obj = self.handle.GetManagedObject(None, "fabricVlan", {
                "Dn": mo.Dn
            })
            self.handle.RemoveManagedObject(obj)
            print "Deleted VLAN " + str(mo.Id) + ": " + mo.Name

        #TODO: This has a different exxception type for missing objects
        except UcsValidationException as e:
            print "VLAN " + str(mo.Id) + ": " + mo.Name + \
                " already deleted -- " + e.errorMsg

    ###########
    #  VSANS  #
    ###########

    def getVSANs(self):

        #Retrieve only user-created VSANs
        inFilter = FilterFilter()
        neFilter = NeFilter()
        neFilter.Class = "fabricVsan"
        neFilter.Property = "name"
        neFilter.Value = "default"
        inFilter.AddChild(neFilter)

        return self.handle.ConfigResolveClass("fabricVsan", inFilter=inFilter)

    def createVSAN(self, fabricid, vsanid, vsanname):
        try:
            obj = self.handle.GetManagedObject(None, None, {
                "Dn": "fabric/san/" + fabricid.upper()
            })

            self.handle.AddManagedObject(obj, "fabricVsan", {
                "Name": vsanname,
                "ZoningState": "disabled",
                "PolicyOwner": "local",
                "FcZoneSharingMode": "coalesce",
                "FcoeVlan": str(vsanid),
                "Dn": "fabric/san/" + fabricid.upper() + "/",
                "Id": str(vsanid)
            })
            print "Created VSAN " + str(vsanid) + ": " + vsanname
        except UcsException as e:
            print "VSAN " + str(vsanid) + ": " + vsanname + \
                " already exists -- " + e.errorDescr

    def removeVSAN(self, mo):
        try:
            obj = self.handle.GetManagedObject(None, "fabricVsan", {
                "Dn": mo.Dn
            })
            self.handle.RemoveManagedObject(obj)
            print "Deleted VSAN " + str(mo.Id) + ": " + mo.Name

        #TODO: This has a different exxception type for missing objects
        except UcsValidationException as e:
            print "VSAN " + str(mo.Id) + ": " + mo.Name + \
                " already deleted -- " + e.errorMsg

    ###############
    #  MAC POOLS  #
    ###############

    def getMacPool(self, poolname):
        pass

    def createMacPool(self, fabric, blockstart, blockend):

        #Create Mac Pool Object
        try:
            mo = self.handle.AddManagedObject(self.org, "macpoolPool", {
                "Descr": "ESXi Servers Fabric " + fabric,
                "Name": "ESXi-MAC-" + fabric,
                "AssignmentOrder": "sequential",
                "PolicyOwner": "local",
                "Dn": self.orgNameDN + "mac-pool-" +
                "ESXi-MAC-" + fabric
            })
        except UcsException:
            print "MAC Pool " + "ESXi-MAC-" + fabric + " already exists"
            mo = self.handle.GetManagedObject(None, None, {
                "Dn": self.orgNameDN + "mac-pool-ESXi-MAC-" + fabric
            })

        #Create Mac Pool Block
        try:
            self.handle.AddManagedObject(mo, "macpoolBlock", {
                "From": blockstart,
                "To": blockend,
                "Dn": self.orgNameDN + "mac-pool-ESXi-MAC-" +
                fabric + "/block-" + blockstart + "-" + blockend
            })
        except UcsException:
            print "MAC Pool block " + blockstart + \
                "-" + blockend + " already exists"

    def removeMacPool(self, mo):
        pass

    ################
    #  WWPN POOLS  #
    ################

    def getWwpnPool(self, poolname):
        pass

    def createWwpnPool(self, fabric, blockstart, blockend):
        #Create WWPN Pool Object
        try:
            mo = self.handle.AddManagedObject(self.org, "fcpoolInitiators", {
                "Descr": "ESXi Servers Fabric " + fabric,
                "Name": "ESXi-WWPN-" + fabric,
                "AssignmentOrder": "sequential",
                "PolicyOwner": "local",
                "Dn": self.orgNameDN + "wwpn-pool-" +
                "ESXi-WWPN-" + fabric
            })
        except UcsException:
            print "WWPN Pool " + "ESXi-WWPN-" + fabric + " already exists"
            mo = self.handle.GetManagedObject(None, None, {
                "Dn": self.orgNameDN + "wwpn-pool-ESXi-WWPN-" + fabric
            })

        #Create WWPN Pool Block
        try:
            self.handle.AddManagedObject(mo, "fcpoolBlock", {
                "From": blockstart,
                "To": blockend,
                "Dn": self.orgNameDN + "wwn-pool-ESXi-WWPN-" +
                fabric + "/block-" + blockstart + "-" + blockend
            })
        except UcsException:
            print "WWPN Pool block " + blockstart + \
                "-" + blockend + " already exists"

    def removeWwpnPool(self, mo):
        pass

    #####################
    #  GLOBAL POLICIES  #
    #####################

    def setPowerPolicy(self, redundancy):
        try:
            self.handle.AddManagedObject(self.orgroot, "computePsuPolicy", {
                "PolicyOwner": "local",
                "Redundancy": redundancy,
                "Dn": "org-root/psu-policy",
                "Descr": ""
            }, True)
        except UcsException:
            print "Error setting power policy"

    def setChassisDiscoveryPolicy(self, links):
        try:
            self.handle.AddManagedObject(
                self.orgroot, "computeChassisDiscPolicy",
                {
                    "Descr": "",
                    "PolicyOwner": "local",
                    "LinkAggregationPref": "port-channel",
                    "Action": links,
                    "Name": "",
                    "Rebalance": "user-acknowledged",
                    "Dn": "org-root/chassis-discovery"
                }, True)
        except UcsException:
            print "Error setting Chassis Discovery policy"

    ##################
    #  QOS POLICIES  #
    ##################

    def setGlobalQosPolicy(self, qosconfig):
        try:

            #Pull MTU for default/best-effort class
            defmtu = str(qosconfig['defaultmtu'])

            #We want to send "normal" to UCS, not "1500".
            #Both will work, but "1500" will generate an annoying warning.
            if defmtu == "1500":
                defmtu = "normal"

            #Position ourselves properly within the MO tree
            obj = self.handle.GetManagedObject(None, None, {
                "Dn": "fabric/lan"
            })
            mo = self.handle.AddManagedObject(obj, "qosclassDefinition", {
                "PolicyOwner": "local",
                "Dn": "fabric/lan/classes",
                "Descr": ""
            }, True)

            #Set params for Platinum class
            self.handle.AddManagedObject(mo, "qosclassEthClassified", {
                "Priority": "platinum",
                "Mtu": "9126",
                "Name": "",
                "Dn": "fabric/lan/classes/class-platinum",
                "Weight": "10",
                "AdminState": "disabled",
                "Cos": "5",
                "Drop": "drop",
                "MulticastOptimize": "no"
            }, True)

            #Set params for Gold class
            self.handle.AddManagedObject(mo, "qosclassEthClassified", {
                "Priority": "gold",
                "Mtu": "9126",
                "Name": "",
                "Dn": "fabric/lan/classes/class-gold",
                "Weight": "9",
                "AdminState": "enabled",
                "Cos": "4",
                "Drop": "drop",
                "MulticastOptimize": "no"
            }, True)

            #Set params for Silver class
            self.handle.AddManagedObject(mo, "qosclassEthClassified", {
                "Priority": "silver",
                "Mtu": "9126",
                "Name": "",
                "Dn": "fabric/lan/classes/class-silver",
                "Weight": "8",
                "AdminState": "enabled",
                "Cos": "2",
                "Drop": "drop",
                "MulticastOptimize": "no"
            }, True)

            #Set params for Bronze class
            self.handle.AddManagedObject(mo, "qosclassEthClassified", {
                "Priority": "bronze",
                "Mtu": "9126",
                "Name": "",
                "Dn": "fabric/lan/classes/class-bronze",
                "Weight": "7",
                "AdminState": "enabled",
                "Cos": "1",
                "Drop": "drop",
                "MulticastOptimize": "no"
            }, True)

            #Set params for Best-Effort class
            self.handle.AddManagedObject(mo, "qosclassEthBE", {
                "Name": "",
                "MulticastOptimize": "no",
                "Mtu": defmtu,
                "Dn": "fabric/lan/classes/class-best-effort",
                "Weight": "5"
            }, True)
        except UcsException:
            print "Error setting Global QoS Policy"

    def createQosPolicy(self, classname, hostcontrol):
        try:
            mo = self.handle.AddManagedObject(self.org, "epqosDefinition", {
                "Name": classname,
                "Dn": self.orgNameDN + "ep-qos-" + classname,
                "PolicyOwner": "local",
                "Descr": classname + " QoS Policy"
            })
            self.handle.AddManagedObject(mo, "epqosEgress", {
                "Name": "",
                "Burst": "10240",
                "HostControl": hostcontrol,
                "Prio": classname.lower(),
                "Dn": self.orgNameDN + "ep-qos-" + classname + "/egress",
                "Rate": "line-rate"
            }, True)
        except UcsException:
            print "QoS Policy already exists"

    ###########################
    #  ORG-SPECIFIC POLICIES  #
    ###########################

    def getLocalDiskPolicy(self, name):
        pass

    def createLocalDiskPolicy(self, name, mode):
        try:
            self.handle.AddManagedObject(
                self.org, "storageLocalDiskConfigPolicy",
                {
                    "Name": name,
                    "Descr": name,
                    "PolicyOwner": "local",
                    "ProtectConfig": "yes",
                    "Dn": self.orgNameDN + "local-disk-config-" + name,
                    "Mode": mode,
                    "FlexFlashState": "disable",
                    "FlexFlashRAIDReportingState": "disable"
                })
        except UcsException:
            print "Local Disk Configuration Policy already exists"

    def removeLocalDiskPolicy(self, name):
        pass

    def getHostFWPackage(self, name):
        pass

    def createHostFWPackage(self, name):
        try:
            self.handle.AddManagedObject(
                self.org, "firmwareComputeHostPack",
                {
                    "Name": name,
                    "BladeBundleVersion": "",
                    "RackBundleVersion": "",
                    "PolicyOwner": "local",
                    "Dn": self.orgNameDN + "fw-host-pack-" + name,
                    "Mode": "staged",
                    "IgnoreCompCheck": "yes",
                    "StageSize": "0",
                    "Descr": "Host Firmware Package",
                    "UpdateTrigger": "immediate"
                })
        except UcsException:
            print "Host Firmware Package already exists"

    def removeHostFWPackage(self, name):
        pass

    def getMaintPolicy(self, name):
        pass

    def createMaintPolicy(self, name, policy):
        try:
            self.handle.AddManagedObject(
                self.org, "lsmaintMaintPolicy", {
                    "Descr": name,
                    "SchedName": "",
                    "Name": name,
                    "Dn": self.orgNameDN + "maint-" + name,
                    "PolicyOwner": "local",
                    "UptimeDisr": policy
                })
        except UcsException:
            print "Maintenance Policy already exists"

    def removeMaintPolicy(self, name):
        pass

    def createNetControlPolicy(self, name):
        try:
            self.handle.AddManagedObject(
                self.org, "nwctrlDefinition", {
                    "Name": name,
                    "Cdp": "enabled",
                    "Dn": self.orgNameDN + "nwctrl-" + name,
                    "PolicyOwner": "local",
                    "MacRegisterMode": "only-native-vlan",
                    "UplinkFailAction": "link-down",
                    "Descr": name
                })
        except UcsException:
            print "Network Control Policy already exists"

    #TODO: Tabling this for now. This is a complicated thing to do.
    def createBootPolicy(name):
        pass

    ####################
    #  VNIC TEMPLATES  #
    ####################

    def getVnicTemplate(self, vnicname):
        return self.handle.GetManagedObject(None, None, {
            "Dn": self.orgNameDN + "lan-conn-templ-" + vnicname
            })

    def createVnicTemplate(self, vnicprefix, fabricID):
        try:
            return self.handle.AddManagedObject(
                self.org, "vnicLanConnTempl", {
                    "Name": vnicprefix + "-" + fabricID,
                    "Descr": vnicprefix + " - Fabric " + fabricID,
                    "SwitchId": fabricID,
                    "QosPolicyName": "Best-Effort",
                    "NwCtrlPolicyName": "NTKCTRL-CDP",
                    "StatsPolicyName": "default",
                    "TemplType": "updating-template",
                    "PolicyOwner": "local",
                    "Mtu": "9000",  # TODO: Configurable item?
                    "PinToGroupName": "",

                    "Dn": self.orgNameDN + "lan-conn-templ-" +
                    vnicprefix + "-" + fabricID,

                    "IdentPoolName": "ESXi-MAC-" + fabricID
                })
        except UcsException:
            print "vNIC Template '" + vnicprefix + "-" + \
                fabricID + "' already exists"
            return self.getVnicTemplate(vnicprefix + "-" + fabricID)

    def removeVnicTemplate(self, templatename):
        pass

    def getVnicVlans(self, vnic):
        inFilter = FilterFilter()
        wcardFilter = WcardFilter()
        wcardFilter.Class = "vnicEtherIf"
        wcardFilter.Property = "dn"
        wcardFilter.Value = vnic.Dn
        inFilter.AddChild(wcardFilter)

        return self.handle.ConfigResolveClass("vnicEtherIf", inFilter=inFilter)

    def createVnicVlan(self, vnic, vlanname):
        #TODO: Only works with vNIC templates, presently
        try:
            self.handle.AddManagedObject(vnic, "vnicEtherIf", {
                "Name": vlanname,

                "Dn": self.orgNameDN + "lan-conn-templ-" +
                vnic.Name + "/if-" + vlanname,

                "DefaultNet": "no"
            }, True)
        except UcsException:
            print "vNIC Template '" + vnic.Name + \
                "' already contains VLAN " + vlanname

    def removeVnicVlan(self, vnic, vlanname):
        #TODO: Only works with vNIC templates, presently
        try:
            obj = self.handle.GetManagedObject(
                vnic, "vnicEtherIf",
                {
                    "Name": vlanname
                })
            self.handle.RemoveManagedObject(obj)
            print "Deleted VLAN " + str(vlanname) + " from " + vnic.Dn

        #TODO: This has a different exception type for missing objects
        except UcsValidationException as e:
            print "VLAN " + str(vlanname) + ": " + vnic.Dn + \
                " already deleted -- " + e.errorMsg

    ####################
    #  VHBA TEMPLATES  #
    ####################

    def getVhbaTemplate(self, vhbaname):
        return self.handle.GetManagedObject(None, None, {
            "Dn": self.orgNameDN + "san-conn-templ-" + vhbaname
        })

    def createVhbaTemplate(self, fabricID):
        try:
            return self.handle.AddManagedObject(self.org, "vnicSanConnTempl", {
                "Name": "ESX-VHBA-" + fabricID,
                "Descr": "ESXi Servers - vHBA Fabric " + fabricID,
                "SwitchId": fabricID,
                "QosPolicyName": "",
                "MaxDataFieldSize": "2048",
                "StatsPolicyName": "default",
                "TemplType": "updating-template",
                "PolicyOwner": "local",

                "Dn": self.orgNameDN + "san-conn-templ-ESX-VHBA-" +
                fabricID,

                "PinToGroupName": "",
                "IdentPoolName": "ESXi-WWPN-" + fabricID
            })
        except UcsException:
            print "vHBA Template 'ESX-VHBA-" + fabricID + "' already exists"
            return self.handle.GetManagedObject(None, None, {
                "Dn": self.orgNameDN + "san-conn-templ-ESX-VHBA-" +
                fabricID
            })

    def removeVhbaTemplate(self, templatename):
        pass

    def getVhbaVsan(self, vhba):
        inFilter = FilterFilter()
        eqFilter = EqFilter()
        eqFilter.Class = "vnicFcIf"
        eqFilter.Property = "dn"

        # vHBAs aren't like vNICs - only one VSAN, and it's referenced thusly
        # So no need for wildcards - match DN of vHBA, plus the below literal
        eqFilter.Value = vhba.Dn + "/if-default"
        inFilter.AddChild(eqFilter)

        return self.handle.ConfigResolveClass("vnicFcIf", inFilter=inFilter)

    def createVhbaVsan(self, vhba, vsanname):
        #TODO: Only works with vHBA templates, presently
        try:
            self.handle.AddManagedObject(vhba, "vnicFcIf", {
                "Name": vsanname,

                "Dn": self.orgNameDN + "san-conn-templ-" +
                vhba.Name + "/if-" + vsanname

            }, True)
        except UcsException:
            print "vHBA Template '" + vhba.Name + \
                "' already contains VSAN " + vsanname

    def removeVhbaVsan(self, vsan):
        # No "remove" method necessary.
        pass

    ####################
    #  SP TEMPLATES  #
    ####################

    def createSPTemplate(self, sptname):
        try:

            return self.handle.AddManagedObject(self.org, "lsServer", {
                "Name": sptname,
                "MgmtFwPolicyName": "",
                "MaintPolicyName": "MAINT_USERACK",
                "LocalDiskPolicyName": "NO_LOCAL",
                "Descr": "ESXi Servers",
                "DynamicConPolicyName": "",
                "Type": "updating-template",
                "VconProfileName": "",
                "IdentPoolName": "ESXi-UUID",  # TODO: Not implemented yet
                "HostFwPolicyName": "HOST_FW_PKG",
                "ExtIPPoolName": "ext-mgmt",
                "Uuid": "0",
                "ExtIPState": "pooled",
                "PowerPolicyName": "default",
                "Dn": self.orgNameDN + "ls-" + sptname,
                "BootPolicyName": "BFS_POLICY",  # TODO: Not implemented yet
                "PolicyOwner": "local",
                "StatsPolicyName": "default"
            })

        except UcsException:
            print "SPT CREATION - Service Profile Template '" + \
                sptname + "' already exists"
            return self.handle.GetManagedObject(None, None, {
                "Dn": self.orgNameDN + "ls-" + sptname
            })

    def setVconOrder(self, spt, vnic, transport, order):
        try:
            self.handle.AddManagedObject(self.org, "lsVConAssign", {
                "AdminVcon": "any",
                "VnicName": vnic,
                "Transport": transport,
                "Dn": spt.Dn + "/assign-ethernet-vnic-" + vnic,
                "Order": order
            }, True)
        except UcsException:
            print "SPT CREATION - vcon already mapped"

    def addVnicFromTemplate(self, spt, vnicname):
        try:
            self.handle.AddManagedObject(spt, "vnicEther", {
                "QosPolicyName": "",
                "NwCtrlPolicyName": "",
                "Name": vnicname,
                "IdentPoolName": "",
                "AdminVcon": "any",
                "PinToGroupName": "",
                "StatsPolicyName": "default",
                "AdaptorProfileName": "VMWare",
                "SwitchId": vnicname[-1:],  # TODO: kind of a hack right now
                "Dn": spt.Dn + "/ether-" + vnicname,
                "Addr": "derived",
                "NwTemplName": vnicname
            })
        except UcsException as e:
            print "VNIC MAP - vnic already mapped to SPT -- " + e.errorDescr

    def addVhbaFromTemplate(self, spt, vhbaname):
        try:
            self.handle.AddManagedObject(spt, "vnicFc", {
                "MaxDataFieldSize": "2048",
                "Name": vhbaname,
                "PersBindClear": "no",
                "AdminVcon": "any",
                "PersBind": "disabled",
                "StatsPolicyName": "default",
                "AdaptorProfileName": "VMWare",
                "SwitchId": vhbaname[-1:],  # TODO: kind of a hack right now
                "Dn": spt.Dn + "/fc-" + vhbaname,
                "Addr": "derived",
                "NwTemplName": vhbaname
            })
        except UcsException as e:
            print "VHBA MAP - vhba already mapped to SPT -- " + e.errorDescr

    def setWWNNPool(self, spt, poolname):
        try:
            self.handle.AddManagedObject(spt, "vnicFcNode", {
                "Addr": "pool-derived",
                "Dn": spt.Dn + "/fc-node",
                "IdentPoolName": poolname
            }, True)
        except UcsException:
            print "SPT WWNN pool already set"

    def setPowerState(self, spt, state):
        try:
            self.handle.AddManagedObject(spt, "lsPower", {
                "Dn": spt.Dn + "/power",
                "State": state
            }, True)
        except UcsException:
            print "SPT desired power state already set"

    def spawnZerglings(self, spt, spprefix, number):
        self.handle.LsInstantiateNTemplate(
            spt.Dn, number, spprefix, self.orgNameDN[:-1]
        )
