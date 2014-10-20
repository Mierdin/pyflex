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

from UcsSdk import OrgOrg, UcsException, FabricVlan, UcsValidationException


class NewUcsFunctions(object):
    """ A working class to help ease how we work with UCS objects """

    FABRICS = ['A', 'B']

    #TODO: Currently requiring org info at start of
    def __init__(self, handle, orgName):

        #TODO: need to have a check for valid handle i.e. logged in
        self.handle = handle

        #Some functions refer directly to root (i.e. VLANs)
        self.orgroot = self.handle.GetManagedObject(
            None, None,
            {
                "Dn": "org-root/"
            })

        #Set self.org object. Referred to throughout the various functions
        if orgName != "root":
            self.org = self.getSubOrg(orgName)
        else:
            self.org = self.orgroot

        #For some reason, org objects are stored as lists
        for item in self.org:

            #Sets other org-related properties. Functions should refer directly
            #to self.orgNameDN - self.orgName is used only by suborg functions
            self.orgName = item.Name
            self.orgNameDN = item.Dn + "/"

        #Create requested suborg
        self.createSubOrg(self.orgName)

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
            self.handle.AddManagedObject(
                self.orgroot, OrgOrg.ClassId(),
                {
                    "Dn": "org-root/org-" + self.orgName,
                    "Desc": self.orgName,
                    "Name": self.orgName
                })
        except UcsException:
            print "Sub-organization already exists"

        self.org = self.handle.GetManagedObject(
            None, OrgOrg.ClassId(),
            {
                OrgOrg.DN: self.orgNameDN
            })

    ###########
    #  VLANS  #
    ###########

    def getVLANs(self):
        return self.handle.ConfigResolveClass("fabricVlan", inFilter=None)
        #TODO: See if you can figure out how to filter by DN,
        # and eliminate the filtering done at the ucs worker

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
            obj = self.handle.GetManagedObject(
                None, FabricVlan.ClassId(),
                {
                    FabricVlan.DN: mo.Dn
                })
            self.handle.RemoveManagedObject(obj)
            print "Deleted VLAN " + str(mo.Id) + ": " + mo.Name

        #TODO: This has a different exxception type for missing objects
        except UcsValidationException as e:
            print "VLAN " + str(mo.Id) + ": " + mo.Name + \
                " already deleted -- " + e.errorDescr

    ###########
    #  VSANS  #
    ###########

    def getVSANs(self):
        return self.handle.ConfigResolveClass("fabricVsan", inFilter=None)
        #TODO: Same filtering TODO as with the getVLANs method

    def createVSAN(self, fabricid, vsanid, vsanname):
        try:
            obj = self.handle.GetManagedObject(None, None,
                {
                    "Dn": "fabric/san/" + fabricid.upper()
                })

            self.handle.AddManagedObject(obj, "fabricVsan",
                {
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
            obj = self.handle.GetManagedObject(None, FabricVsan.ClassId(),
                {
                    FabricVsan.DN: mo.Dn
                })
            self.handle.RemoveManagedObject(obj)
            print "Deleted VSAN " + str(mo.Id) + ": " + mo.Name

        #TODO: This has a different exxception type for missing objects
        except UcsValidationException as e:
            print "VSAN " + str(mo.Id) + ": " + mo.Name + \
                " already deleted -- " + e.errorDescr

    ###############
    #  MAC POOLS  #
    ###############

    def getMacPool(self, poolname):
        pass

    def createMacPool(self, fabric, blockstart, blockend):

        #Create Mac Pool Object
        try:
            mo = self.handle.AddManagedObject(self.org, "macpoolPool",
                {
                    "Descr": "ESXi Servers Fabric " + fabric,
                    "Name": "ESXi-MAC-" + fabric,
                    "AssignmentOrder": "sequential",
                    "PolicyOwner": "local",
                    "Dn": self.orgNameDN + "mac-pool-" +
                    "ESXi-MAC-" + fabric
                })
        except UcsException:
            print "MAC Pool " + "ESXi-MAC-" + fabric + " already exists"
            mo = self.handle.GetManagedObject(None, None,
            {
                "Dn": self.orgNameDN + "mac-pool-ESXi-MAC-" + fabric
            })

        #Create Mac Pool Block
        try:
            self.handle.AddManagedObject(mo, "macpoolBlock",
                {
                    "From": blockstart,
                    "To": blockend,
                    "Dn": self.orgNameDN + "mac-pool-ESXi-MAC-" +
                    fabric + "/block-" + blockstart + "-" + blockend
                })
        except UcsException:
            print "MAC Pool block " + blockstart + "-" + blockend + " already exists"

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
            mo = self.handle.AddManagedObject(self.org, "fcpoolInitiators",
                {
                    "Descr": "ESXi Servers Fabric " + fabric,
                    "Name": "ESXi-WWPN-" + fabric,
                    "AssignmentOrder": "sequential",
                    "PolicyOwner": "local",
                    "Dn": self.orgNameDN + "wwpn-pool-" +
                    "ESXi-WWPN-" + fabric
                })
        except UcsException:
            print "WWPN Pool " + "ESXi-WWPN-" + fabric + " already exists"
            mo = self.handle.GetManagedObject(None, None,
            {
                "Dn": self.orgNameDN + "wwpn-pool-ESXi-WWPN-" + fabric
            })

        #Create WWPN Pool Block
        try:
            self.handle.AddManagedObject(mo, "fcpoolBlock",
                {
                    "From": blockstart,
                    "To": blockend,
                    "Dn": self.orgNameDN + "wwn-pool-ESXi-WWPN-" +
                    fabric + "/block-" + blockstart + "-" + blockend
                })
        except UcsException:
            print "WWPN Pool block " + blockstart + "-" + blockend + " already exists"

    def removeWwpnPool(self, mo):
        pass

    ##############
    #  POLICIES  #
    ##############

    def setPowerPolicy(self, redundancy):
        try:
            self.handle.AddManagedObject(self.orgroot, "computePsuPolicy", 
                {
                    "PolicyOwner": "local", 
                    "Redundancy": redundancy, 
                    "Dn": "org-root/psu-policy", 
                    "Descr": ""
                }, True)
        except UcsException:
            print "Error setting power policy"

    def setChassisDiscoveryPolicy(self, links):
        try:
            self.handle.AddManagedObject(self.orgroot, "computeChassisDiscPolicy", 
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

    def setGlobalQosPolicy(self, qosconfig):
        try:

            #Pull MTU for default/best-effort class
            defmtu = str(qosconfig['defaultmtu'])

            #We want to send "normal" to UCS, not "1500".
            #Both will work, but "1500" will generate an annoying warning.
            if defmtu == "1500":
                defmtu = "normal"

            #Position ourselves properly within the MO tree
            obj = self.handle.GetManagedObject(None, None, {"Dn":"fabric/lan"})
            mo = self.handle.AddManagedObject(obj, "qosclassDefinition", 
                {
                    "PolicyOwner":"local", 
                    "Dn":"fabric/lan/classes", 
                    "Descr":""
                }, True)

            #Set params for Platinum class
            self.handle.AddManagedObject(mo, "qosclassEthClassified", 
                {
                    "Priority":"platinum",
                    "Mtu":"9126", 
                    "Name":"", 
                    "Dn":"fabric/lan/classes/class-platinum", 
                    "Weight":"10", 
                    "AdminState":"disabled", 
                    "Cos":"5", 
                    "Drop":"drop", 
                    "MulticastOptimize":"no"
                }, True)

            #Set params for Gold class
            self.handle.AddManagedObject(mo, "qosclassEthClassified", 
                {
                    "Priority":"gold",
                    "Mtu":"9126", 
                    "Name":"", 
                    "Dn":"fabric/lan/classes/class-gold", 
                    "Weight":"9", 
                    "AdminState":"enabled", 
                    "Cos":"4", 
                    "Drop":"drop", 
                    "MulticastOptimize":"no"
                }, True)

            #Set params for Silver class
            self.handle.AddManagedObject(mo, "qosclassEthClassified", 
                {
                    "Priority":"silver",
                    "Mtu":"9126", 
                    "Name":"", 
                    "Dn":"fabric/lan/classes/class-silver", 
                    "Weight":"8", 
                    "AdminState":"enabled", 
                    "Cos":"2", 
                    "Drop":"drop", 
                    "MulticastOptimize":"no"
                }, True)

            #Set params for Bronze class
            self.handle.AddManagedObject(mo, "qosclassEthClassified", 
                {
                    "Priority":"bronze",
                    "Mtu":"9126", 
                    "Name":"", 
                    "Dn":"fabric/lan/classes/class-bronze", 
                    "Weight":"7", 
                    "AdminState":"enabled", 
                    "Cos":"1", 
                    "Drop":"drop", 
                    "MulticastOptimize":"no"
                }, True)

            #Set params for Best-Effort class
            self.handle.AddManagedObject(mo, "qosclassEthBE",
                {
                    "Name":"",
                    "MulticastOptimize":"no",
                    "Mtu":defmtu,
                    "Dn":"fabric/lan/classes/class-best-effort",
                    "Weight":"5"
                },
                True)
        except UcsException:
            print "Error setting Global QoS Policy"

    def createQosPolicy(self, classname, hostcontrol):
        try:
            mo = self.handle.AddManagedObject(self.org, "epqosDefinition", 
                {
                    "Name":classname, 
                    "Dn":self.orgNameDN + "ep-qos-" + classname, 
                    "PolicyOwner":"local", 
                    "Descr":classname + " QoS Policy"
                })
            self.handle.AddManagedObject(mo, "epqosEgress", 
                {
                    "Name":"", 
                    "Burst":"10240", 
                    "HostControl":hostcontrol, 
                    "Prio":classname.lower(), 
                    "Dn":self.orgNameDN + "ep-qos-" + classname + "/egress", 
                    "Rate":"line-rate"
                }, True)
        except UcsException:
            print "QoS Policy already exists"     
