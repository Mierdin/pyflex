#!/usr/bin/env python
""" pyflex

    This is the new home for cmdlet-style python bindings for UCS.

    These will be designed to fail gracefully. Any error handling will
    be done with the purpose of keeping the program going. (i.e. if an 
    object being created already exists, etc. Not going to check to see 
    if an object exists everytime before creating one)
"""

from UcsSdk import *

class NewUcsFunctions:
    """ A working class to help ease how we work with UCS objects """

    FABRICS = ['A', 'B']

    def __init__(self, handle, orgName): #TODO: Currently requiring org info at start of 

        #TODO: is there a way to check to make sure this is a valid handle? I.e. logged in?
        self.handle = handle

        self.orgroot = self.handle.GetManagedObject(None, None, {"Dn":"org-root/"})

        #TODO: Need to re-implement this so you can use root orgs. Currently only suborgs supported
        #Set DN string for org
        #if newfxns.orgName == "root":
        #    newfxns.orgNameDN = "org-root/"
        #else:
        #    newfxns.orgNameDN = "org-root/org-" + newfxns.orgName + "/"

        self.orgName = orgName
        self.orgNameDN = "org-root/org-" + orgName #TODO: Would prefer to get this more dynamically (i.e. self.org.Dn)

        #TODO: Would prefer to reference the getSubOrg method, but is this possible in __init__? Getting a "getSubOrg is not defined" error
        self.org = self.handle.GetManagedObject(None, OrgOrg.ClassId(), 
            {
                OrgOrg.DN : self.orgNameDN
            })

        print "Instantiated New Functions"

    def getSubOrg(self, orgName):
        self.org = self.handle.GetManagedObject(None, OrgOrg.ClassId(), 
            {
                OrgOrg.DN : "org-root/org-" + orgName
            })

    def createSubOrg(self, orgName):
        if self.orgName != "root" :
            try:
                self.handle.AddManagedObject(self.rootorg, OrgOrg.ClassId(), 
                    {
                        OrgOrg.DESCR:self.orgName,
                        OrgOrg.NAME:self.orgName,
                        OrgOrg.DN:"org-root/org-" + self.orgName
                    })
            except UcsException:
                print "Sub-organization already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types

            self.org = self.handle.GetManagedObject(None, OrgOrg.ClassId(), 
                {
                    OrgOrg.DN : self.orgNameDN
                })
        else:
            self.org = self.handle.GetManagedObject(None, OrgOrg.ClassId(), 
                {
                    OrgOrg.DN : "org-root/"
                })


    ###########
    #  VLANS  #
    ###########

    def getVLANs(self):
        return self.handle.ConfigResolveClass("fabricVlan", inFilter=None) 
        #TODO: See if you can figure out how to filter by DN, and eliminate a bit of unnecessary code
        
    def createVLAN(self, vlanid, vlanname):
        try:
            self.handle.AddManagedObject(self.orgroot, "fabricVlan", 
                {
                    "Name":vlanname, 
                    "PubNwName":"", 
                    "DefaultNet":"no", 
                    "PolicyOwner":"local", 
                    "CompressionType":"included", 
                    "Dn":"fabric/lan/net-" + vlanname, 
                    "McastPolicyName":"", 
                    "Id":str(vlanid), 
                    "Sharing":"none"
                })
            print "Created VLAN " + str(vlanid) + ": " + vlanname
        except UcsException as e: #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types
            print "VLAN " + str(vlanid) + ": " + vlanname + " already exists -- " + e.errorDescr

    def removeVLAN(self, mo):
        #TODO: in the usual workflow, you're retrieving the VLAN objects twice. Once for 
        #the get method, and once for this one. See if you can be more efficient (or if it's 
        #a good idea at all)   
        try:     
            obj = self.handle.GetManagedObject(None, FabricVlan.ClassId(), {FabricVlan.DN:mo.Dn})
            self.handle.RemoveManagedObject(obj)
            print "Deleted VLAN " + str(mo.Id) + ": " + mo.Name
        except UcsValidationException as e:  #TODO: This seems to have a different exxception type for missing objects
            print "VLAN " + str(mo.Id) + ": " + mo.Name + " already deleted -- "  + e.errorDescr

    ###########
    #  VSANS  #
    ###########

    def getVSANs(self):
        return self.handle.ConfigResolveClass("fabricVsan", inFilter=None) 
        #TODO: See if you can figure out how to filter by DN, and eliminate a bit of unnecessary code

    def createVSAN(self, fabricid, vsanid, vsanname):
        try:
            obj = self.handle.GetManagedObject(None, None, 
                {
                    "Dn":"fabric/san/" + fabricid.upper()
                })

            self.handle.AddManagedObject(obj, "fabricVsan", 
                {
                    "Name":vsanname, 
                    "ZoningState":"disabled", 
                    "PolicyOwner":"local", 
                    "FcZoneSharingMode":"coalesce",
                    "FcoeVlan":str(vsanid), 
                    "Dn":"fabric/san/" + fabricid.upper() + "/", 
                    "Id":str(vsanid)
                })
            print "Created VSAN " + str(vsanid) + ": " + vsanname
        except UcsException as e: #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types UcsSdk.UcsBase.UcsException: [ErrorCode]: 103[ErrorDescription]: Cannot create; object already exists.
            print "VSAN " + str(vsanid) + ": " + vsanname + " already exists -- " + e.errorDescr

    def removeVSAN(self, mo): 
        try:     
            obj = self.handle.GetManagedObject(None, FabricVsan.ClassId(), {FabricVsan.DN:mo.Dn})
            self.handle.RemoveManagedObject(obj)
            print "Deleted VSAN " + str(mo.Id) + ": " + mo.Name
        except UcsValidationException as e:  #TODO: This seems to have a different exxception type for missing objects
            print "VSAN " + str(mo.Id) + ": " + mo.Name + " already deleted -- " + e.errorDescr


    ###############
    #  MAC POOLS  #
    ###############

    def getMacPool(self, poolname):
        pass

    def createMacPool(self, fabric, blockstart, blockend):
        try:
            mo = self.handle.AddManagedObject(self.org, "macpoolPool", 
                {
                    "Descr":"ESXi Servers Fabric " + fabric, 
                    "Name":"ESXi-MAC-" + fabric, 
                    "AssignmentOrder":"sequential", 
                    "PolicyOwner":"local", 
                    "Dn":self.orgNameDN + "mac-pool-" + \
                        "ESXi-MAC-" + fabric
                })
        except UcsException:
            print "MAC Pool already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types
            mo = self.handle.GetManagedObject(None, None, 
            {
                "Dn":self.orgNameDN + "mac-pool-ESXi-MAC-" + fabric
            }) #We need to do this because the creation of the pool, and it's blocks, are separate actions
        
        try:
            mo_1 = self.handle.AddManagedObject(mo, "macpoolBlock", 
                {
                    "From":blockstart, 
                    "To":blockend, 
                    "Dn":self.orgNameDN + "mac-pool-ESXi-MAC-" + \
                        fabric + "/block-" + blockstart + "-"  + blockend
                })
        except UcsException:
            print "MAC Pool block already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types

    def removeMacPool(self, mo):
        pass






