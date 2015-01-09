#!/usr/bin/env python

from UcsSdk import *

handle = UcsHandle()
handle.Login(
    "10.12.0.97", 
    "config", 
    "config"
)

print "logged in"

wwpnreturn = {}
wwpnreturn['fabAWWPNs'] = {}
wwpnreturn['fabBWWPNs'] = {}

fabAWWPNs = {}
fabBWWPNs = {}


def getServiceProfiles(handle):
    crc = handle.ConfigResolveChildren("lsServer", "org-root/org-TEST_ORG", None)
    moList = []
    for child in crc.OutConfigs.GetChild():
        if (isinstance(child, ManagedObject) == True):
            if child.Type == "instance":
                moList.append(child)
    #WriteObject(moList)
    return moList

def getFcWWPNs(handle, sprofiles):
    moList = []
    for sp in sprofiles:
        crc = handle.ConfigResolveChildren(
            "vnicFc",
            sp.Dn,
            None
        )
        print "Looking at " + sp.Dn
        for child in crc.OutConfigs.GetChild():
            moList.append(child)
            print "appending fcvif " + child.Dn
            if child.SwitchId == "A":
                wwpnreturn['fabAWWPNs'][str(child.Dn)[child.Dn.index("ls-") + 3:].replace("/fc", "")] = child.Addr
            else:
                wwpnreturn['fabBWWPNs'][str(child.Dn)[child.Dn.index("ls-") + 3:].replace("/fc", "")] = child.Addr

    #WriteObject(moList)
    return moList

    #for mo in moList:
        #print dir(mo) #prints properties of an MO object
    #   print mo.Dn

for initiator in getFcWWPNs(handle, getServiceProfiles(handle)):
    pass

print wwpnreturn

# #Retrieve only user-created VLANs
# inFilter = FilterFilter()
# neFilter = NeFilter()
# neFilter.Class = "fabricVlan"
# neFilter.Property = "name"
# neFilter.Value = "default"
# inFilter.AddChild(neFilter)

# return self.handle.ConfigResolveClass("fabricVlan", inFilter=inFilter)

print "DONE"
