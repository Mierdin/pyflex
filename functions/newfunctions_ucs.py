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

    def __init__(self, handle):

        #TODO: is there a way to check to make sure this is a valid handle? I.e. logged in?
        self.handle = handle

        self.orgroot = self.handle.GetManagedObject(None, None, {"Dn":"fabric/lan"})

        print "Instantiated New Functions"


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