from UcsSdk import *

class UcsFunctions:
    # Need to pull over comments from ps1 scripts where relevant

    FABRICS = ['A', 'B']

    def __init__(self, handle, ucsconfig):
        
        self.handle = handle
        self.ucsconfig = ucsconfig #TODO: ucsconfig is currently just the entire config. Need to organize the config so that it's a little more pruned.

        self.orgName = self.ucsconfig['general']['org']

        if self.orgName == "root":
            self.orgNameDN = "org-root/"
            self.org = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN : self.orgNameDN})
        else:
            self.orgNameDN = "org-root/org-" + self.orgName + "/"
            self.org = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN : self.orgNameDN})

        #Even if self.org is the root org, it's nice to have a separate one for root, that we can use for things that should always refer to root. I.e. the default resource pools
        self.rootorg = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN : "org-root/"})

    def ucsHousekeeping(self):

        try:
            #Add block to iscsi initiator pool
            obj = self.handle.GetManagedObject(None, IppoolPool.ClassId(), {IppoolPool.DN:"org-root/ip-pool-iscsi-initiator-pool"})
            self.handle.AddManagedObject(obj, IppoolBlock.ClassId(), {IppoolBlock.FROM:"1.1.1.1", IppoolBlock.TO:"1.1.1.1", IppoolBlock.DN:"org-root/ip-pool-iscsi-initiator-pool/block-1.1.1.1-1.1.1.1"})
        except UcsException:
            print "Already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types

        #Add suborg if needed
        if len(self.org) == 0 and self.orgName != "root" :
            try:
                self.handle.AddManagedObject(self.rootorg, OrgOrg.ClassId(), {OrgOrg.DESCR:self.orgName, OrgOrg.NAME:self.orgName, OrgOrg.DN:"org-root/org-" + self.orgName})
            except UcsException:
                print "Already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types

            self.org = self.handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN : self.orgNameDN})
        elif self.orgName == "root":
            self.org = self.handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN : "org-root/"})
        else:
            pass #In any other case, the org already exists, and is set correctly via this module's __init__ method
        
        #Set default maintenance policy to user-ack
        self.handle.AddManagedObject(self.rootorg, LsmaintMaintPolicy.ClassId(), {LsmaintMaintPolicy.DN:"org-root/maint-default", LsmaintMaintPolicy.POLICY_OWNER:"local", LsmaintMaintPolicy.UPTIME_DISR:"user-ack", LsmaintMaintPolicy.DESCR:"", LsmaintMaintPolicy.SCHED_NAME:"default"}, True)

        #List default pools, and remove them
        objs = ["org-root/mac-pool-default",
                "org-root/wwn-pool-node-default",
                "org-root/wwn-pool-default",
                "org-root/uuid-pool-default",
                "org-root/compute-pool-default",
                "org-root/iqn-pool-default"
        ]

        for thisobj in objs:
            try:
                self.handle.RemoveManagedObject(self.handle.GetManagedObject(None, None, {"Dn":thisobj}))
            except UcsValidationException:
                print thisobj + " already deleted"
                pass #This pool was likely already deleted

        #TODO: at this point, ext-mgmt is still empty. Consider implementing this here, or even better, in another method.

    def implementPhysicalPortChanges(self):
        #method title obviously a working title :)
        pass

    def createVLANSandVSANS(self):
        
        obj = self.handle.GetManagedObject(None, None, {"Dn":"fabric/lan"})
        
        vlans = self.ucsconfig['vlans']

        for group in vlans:
            if group != 'storage': #Don't want to explicitly add FCoE VLANs here, that's done in the VSAN creation
                for vlanid, vlanname in vlans[group].iteritems():
                    try:
                        self.handle.AddManagedObject(obj, "fabricVlan", {"Name":vlanname, "PubNwName":"", "DefaultNet":"no", "PolicyOwner":"local", "CompressionType":"included", "Dn":"fabric/lan/net-" + vlanname, "McastPolicyName":"", "Id":str(vlanid), "Sharing":"none"})
                    except UcsException:
                        print "Already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types

        vsans = self.ucsconfig['vsans']

        for fabric in vsans:
            obj = self.handle.GetManagedObject(None, None, {"Dn":"fabric/san/" + fabric.upper()}) #Note: This is inside the for loop because VSANs are generally per-fabric, and VLANs are not.
            for vsanid, vsanname in vsans[fabric].iteritems():
                try:
                    self.handle.AddManagedObject(obj, "fabricVsan", {"Name":vsanname, "ZoningState":"disabled", "PolicyOwner":"local", "FcZoneSharingMode":"coalesce", "FcoeVlan":str(vsanid), "Dn":"fabric/san/" + fabric.upper() + "/", "Id":str(vsanid)})
                except UcsException:
                    print "Already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types


    def createUCSPools(self):
        #TODO: Lots of shortcuts taken here. Need to come back and clean up this atrocious mess.
        pools = self.ucsconfig['ucs']['pools']

        #TODO: Implement IP pool

        #MAC Pools
        for fabric in pools['mac']: #TODO: This loop is here for the future, but obviously since the name is statically set, this only works with a single pool per fabric, currently.
            try:
                mo = self.handle.AddManagedObject(self.org, "macpoolPool", {"Descr":"ESXi Servers Fabric " + fabric, "Name":"ESXi-MAC-" + fabric, "AssignmentOrder":"sequential", "PolicyOwner":"local", "Dn":self.orgNameDN + "mac-pool-" + "ESXi-MAC-" + fabric})
            except UcsException:
                print "MAC Pool already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types
                mo = self.handle.GetManagedObject(None, None, {"Dn":self.orgNameDN + "mac-pool-ESXi-MAC-" + fabric}) #We need to do this because the creation of the pool, and it's blocks, are separate actions
            
            try:
                mo_1 = self.handle.AddManagedObject(mo, "macpoolBlock", {"From":pools['mac'][fabric]['blockbegin'], "To":pools['mac'][fabric]['blockend'], "Dn":self.orgNameDN + "mac-pool-ESXi-MAC-" + fabric + "/block-" + pools['mac'][fabric]['blockbegin'] + "-"  + pools['mac'][fabric]['blockend']})
            except UcsException:
                print "MAC Pool block already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types

        #WWPN Pools
        for fabric in pools['wwpn']:
            try:
                mo = self.handle.AddManagedObject(self.org, "fcpoolInitiators", {"Descr":"ESXi Servers Fabric " + fabric, "Name":"ESXi-WWPN-" + fabric, "Purpose":"port-wwn-assignment", "PolicyOwner":"local", "AssignmentOrder":"sequential", "Dn":self.orgNameDN + "wwn-pool-ESXi-WWPN"})
            except UcsException:
                print "WWPN Pool already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types
                mo = self.handle.GetManagedObject(None, None, {"Dn":self.orgNameDN + "wwn-pool-ESXi-WWPN-" + fabric}) #We need to do this because the creation of the pool, and it's blocks, are separate actions

            try:
                mo_1 = self.handle.AddManagedObject(mo, "fcpoolBlock", {"From":pools['wwpn'][fabric]['blockbegin'], "To":pools['wwpn'][fabric]['blockend'], "Dn":self.orgNameDN + "wwn-pool-ESXi-WWPN-" + fabric + "/block-" + pools['wwpn'][fabric]['blockbegin'] + "-" + pools['wwpn'][fabric]['blockend']})
            except UcsException:
                print "WWPN Pool block already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types
        
        #WWNN Pools
        try:   
            mo = self.handle.AddManagedObject(self.org, "fcpoolInitiators", {"Descr":"ESXi Servers", "Name":"ESXi-WWNN", "Purpose":"node-wwn-assignment", "PolicyOwner":"local", "AssignmentOrder":"sequential", "Dn":self.orgNameDN + "wwn-pool-ESXi-WWNN"})
        except UcsException:
            print "WWNN Pool already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types
            mo = self.handle.GetManagedObject(None, None, {"Dn":self.orgNameDN + "wwn-pool-ESXi-WWNN"}) #We need to do this because the creation of the pool, and it's blocks, are separate actions
        try:
            mo_1 = self.handle.AddManagedObject(mo, "fcpoolBlock", {"From":pools['wwnn']['blockbegin'], "To":pools['wwnn']['blockend'], "Dn":self.orgNameDN + "wwn-pool-ESXi-WWNN/block-" + pools['wwnn']['blockbegin'] + "-" + pools['wwnn']['blockend']})
        except UcsException:
            print "WWNN Pool block already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types
        
        #UUID Pools
        try:
            mo = self.handle.AddManagedObject(self.org, "uuidpoolPool", {"Descr":"ESXi Servers", "Name":"ESXi-UUID", "Dn":self.orgNameDN + "uuid-pool-ESXi-UUID", "PolicyOwner":"local", "Prefix":"derived", "AssignmentOrder":"sequential"})
        except UcsException:
            print "UUID Pool already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types
            mo = self.handle.GetManagedObject(None, None, {"Dn":self.orgNameDN + "wwn-pool-ESXi-UUID"}) #We need to do this because the creation of the pool, and it's blocks, are separate actions        

        try:
            mo_1 = self.handle.AddManagedObject(mo, "uuidpoolBlock", {"From":pools['uuid']['blockbegin'], "To":pools['uuid']['blockend'], "Dn":self.orgNameDN + "uuid-pool-ESXi-UUID/block-from-" + pools['uuid']['blockbegin'] + "-to-" + pools['uuid']['blockend']})
        except UcsException:
            print "UUID Pool block already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types


    def ucsCreatePolicies(self):
        #Create/set global policies
        self.handle.AddManagedObject(self.rootorg, "computePsuPolicy", {"PolicyOwner":"local", "Redundancy":"grid", "Dn":"org-root/psu-policy", "Descr":""}, True)
        self.handle.AddManagedObject(self.rootorg, "computeChassisDiscPolicy", {"Descr":"", "PolicyOwner":"local", "LinkAggregationPref":"port-channel", "Action":str(self.ucsconfig['ucs']['links']), "Name":"", "Rebalance":"user-acknowledged", "Dn":"org-root/chassis-discovery"}, True)

        qos = self.ucsconfig['qos']
        defmtu = str(qos['defaultmtu'])

        #UCS will actually accept 1500, but will generate an annoying warning
        if defmtu == "1500":
            defmtu = "normal"

        #Global QoS policy
        obj = self.handle.GetManagedObject(None, None, {"Dn":"fabric/lan"})
        mo = self.handle.AddManagedObject(obj, "qosclassDefinition", {"PolicyOwner":"local", "Dn":"fabric/lan/classes", "Descr":""}, True)
        self.handle.AddManagedObject(mo, "qosclassEthClassified", {"Mtu":"normal", "Name":"", "Dn":"fabric/lan/classes/class-gold", "Weight":"9", "AdminState":"enabled", "Cos":"4", "Drop":"drop", "MulticastOptimize":"no"}, True)
        self.handle.AddManagedObject(mo, "qosclassEthClassified", {"Mtu":"normal", "Name":"", "Dn":"fabric/lan/classes/class-silver", "Weight":"8", "AdminState":"enabled", "Cos":"2", "Drop":"drop", "MulticastOptimize":"no"}, True)
        self.handle.AddManagedObject(mo, "qosclassEthClassified", {"Mtu":"normal", "Name":"", "Dn":"fabric/lan/classes/class-bronze", "Weight":"7", "AdminState":"enabled", "Cos":"1", "Drop":"drop", "MulticastOptimize":"no"}, True)
        self.handle.AddManagedObject(mo, "qosclassEthBE",
            {
                "Name":"",
                "MulticastOptimize":"no",
                "Mtu":defmtu,
                "Dn":"fabric/lan/classes/class-best-effort",
                "Weight":"5"
            },
            True)

        #Configure NTP

        #Configure TimeZone

        #Configure SNMP Community

        #Configure SNMP Traps

        #Create individual QoS Policies
        classes = { 
            "Gold":"none",
            "Silver":"none",
            "Bronze":"none",
            "Best-Effort":"full"
        }

        for classname, hostcontrol in classes.iteritems():
            try:
                mo = self.handle.AddManagedObject(self.org, "epqosDefinition", {"Name":classname, "Dn":self.orgNameDN + "ep-qos-" + classname, "PolicyOwner":"local", "Descr":classname + " QoS Policy"})
                mo_1 = self.handle.AddManagedObject(mo, "epqosEgress", {"Name":"", "Burst":"10240", "HostControl":hostcontrol, "Prio":classname.lower(), "Dn":self.orgNameDN + "ep-qos-" + classname + "/egress", "Rate":"line-rate"}, True)
            except UcsException:
                print "QoS Policy already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types        

        #TODO: Tabling the idea of a blade qualification policy for now. Flexpods don't dictate what blade type you use, so this is a little too much complexity right now. 
            #Will circle back and deal with this later, but for now, manual assignment of blades will suffice.
        #mo = handle.AddManagedObject(self.org, ComputeQual.ClassId(), {ComputeQual.DN:"org-root/org-DI_DCA/blade-qualifier-B200-M3-QUAL", ComputeQual.POLICY_OWNER:"local", ComputeQual.NAME:"B200-M3-QUAL", ComputeQual.DESCR:"B200 M3 Qualification Policy"})
        #mo_1 = handle.AddManagedObject(mo, ComputePhysicalQual.ClassId(), {ComputePhysicalQual.DN:"org-root/org-DI_DCA/blade-qualifier-B200-M3-QUAL/physical", ComputePhysicalQual.MODEL:"UCSB-B200-M3"})
        #handle.AddManagedObject(self.org, ComputePoolingPolicy.ClassId(), {ComputePoolingPolicy.POLICY_OWNER:"local", ComputePoolingPolicy.DN:"org-root/org-DI_DCA/pooling-policy-B200-M3-PLCY", ComputePoolingPolicy.QUALIFIER:"B200-M3-QUAL", ComputePoolingPolicy.POOL_DN:"org-root/org-DI_DCA/compute-pool-main-server-pool", ComputePoolingPolicy.NAME:"B200-M3-PLCY", ComputePoolingPolicy.DESCR:"B200 M3 Server Pool Policy"})

        #Create Local Disk Configurations
        try:
            self.handle.AddManagedObject(obj, "storageLocalDiskConfigPolicy", 
                {       
                    "Name":"NO_LOCAL", 
                    "Descr":"No Local Disk", 
                    "PolicyOwner":"local", 
                    "ProtectConfig":"yes", 
                    "Dn":self.orgNameDN + "local-disk-config-NO_LOCAL", 
                    "Mode":"no-local-storage", 
                    "FlexFlashState":"disable", 
                    "FlexFlashRAIDReportingState":"disable"
                })
        except UcsException:
            print "Local Disk Configuration Policy already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types 

        try:
            self.handle.AddManagedObject(obj, "storageLocalDiskConfigPolicy", #Creating this just so that it's there. Not currently used in the boot-from-SAN configuration
                {        
                    "Name":"RAID1", 
                    "Descr":"Local Disk arranged in RAID 1", 
                    "PolicyOwner":"local", 
                    "ProtectConfig":"yes", 
                    "Dn":self.orgNameDN + "local-disk-config-RAID1", 
                    "Mode":"raid-mirrored", 
                    "FlexFlashState":"disable", 
                    "FlexFlashRAIDReportingState":"disable"
                })
        except UcsException:
            print "Local Disk Configuration Policy already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types

        #Create Host Firmware Package
        try:
            self.handle.AddManagedObject(self.org, "firmwareComputeHostPack", {"Name":"HOST_FW_PKG", "BladeBundleVersion":"", "RackBundleVersion":"", "PolicyOwner":"local", "Dn":self.orgNameDN + "fw-host-pack-HOST_FW_PKG", "Mode":"staged", "IgnoreCompCheck":"yes", "StageSize":"0", "Descr":"Host Firmware Package", "UpdateTrigger":"immediate"})
        except UcsException:
            print "Host Firmware Package already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types
        
        #Create Maintenance Policy
        try:
            self.handle.AddManagedObject(self.org, "lsmaintMaintPolicy", {"Descr":"User-Ack Maintenance Policy", "SchedName":"", "Name":"MAINT-USERACK", "Dn":self.orgNameDN + "maint-MAINT-USERACK", "PolicyOwner":"local", "UptimeDisr":"user-ack"})
        except UcsException:
            print "Maintenance Policy already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types
        
        #Create Network Control Policy (enable CDP)
        try:
            mo = self.handle.AddManagedObject(self.org, "nwctrlDefinition", {"Name":"NTKCTRL-CDP", "Cdp":"enabled", "Dn":self.orgNameDN + "nwctrl-NTKCTRL-CDP", "PolicyOwner":"local", "MacRegisterMode":"only-native-vlan", "UplinkFailAction":"link-down", "Descr":"Network Control Polcy - CDP Enabled"})
            mo_1 = self.handle.AddManagedObject(mo, "dpsecMac", {"Name":"", "Dn":self.orgNameDN + "nwctrl-NTKCTRL-CDP/mac-sec", "Forge":"allow", "PolicyOwner":"local", "Descr":""}, True)
        except UcsException:
            print "Network Control Policy already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types

    def createBootPolicy(self):
        #TODO: Ideally, this function should reach into the array (should have a "retrieve four targets" function for this) then this function gets run with an array as an argument for those four tagets to fall into.
        
        targets = self.ucsconfig['storage']['targets']

        #TODO: I decided to wrap the entire thing in a try block....may break it out further once simplified, having a try block per line is a bit much right now. We'll just 
        try:
            #Create Boot Policy
            mo = self.handle.AddManagedObject(self.org, "lsbootPolicy", {"Name":"BFS_POLICY", "EnforceVnicName":"yes", "Dn":self.orgNameDN + "boot-policy-BFS_POLICY", "PolicyOwner":"local", "RebootOnUpdate":"no", "Descr":"Boot Policy (Boot From SAN)"})

            #Add CD-ROM Boot
            self.handle.AddManagedObject(mo, "lsbootVirtualMedia", {"Access":"read-only", "Dn":self.orgNameDN + "boot-policy-BFS_POLICY/read-only-vm", "Order":"1"})

            #Add SAN Boot
            mo_2 = self.handle.AddManagedObject(mo, "lsbootStorage", {"Order":"2", "Dn":self.orgNameDN + "boot-policy-BFS_POLICY/storage"}, True)

            #Add SAN Boot Target Fabric A
            mo_2_1 = self.handle.AddManagedObject(mo_2, "lsbootSanImage", {"VnicName":"ESX-VHBA-A", "Type":"primary", "Dn":self.orgNameDN + "boot-policy-BFS_POLICY/storage/san-primary"})
            mo_2_1_1 = self.handle.AddManagedObject(mo_2_1, "lsbootSanImagePath", {"Dn":self.orgNameDN + "boot-policy-BFS_POLICY/storage/san-primary/path-primary", "Type":"primary", "Lun":"0", "Wwn":targets['A'][0]})
            mo_2_1_2 = self.handle.AddManagedObject(mo_2_1, "lsbootSanImagePath", {"Dn":self.orgNameDN + "boot-policy-BFS_POLICY/storage/san-primary/path-secondary", "Type":"secondary", "Lun":"0", "Wwn":targets['A'][1]})

            #Add SAN Boot Target Fabric B
            mo_2_2 = self.handle.AddManagedObject(mo_2, "lsbootSanImage", {"VnicName":"ESX-VHBA-B", "Type":"secondary", "Dn":self.orgNameDN + "boot-policy-BFS_POLICY/storage/san-secondary"})
            mo_2_2_1 = self.handle.AddManagedObject(mo_2_2, "lsbootSanImagePath", {"Dn":self.orgNameDN + "boot-policy-BFS_POLICY/storage/san-secondary/path-primary", "Type":"primary", "Lun":"0", "Wwn":targets['B'][0]})
            mo_2_2_2 = self.handle.AddManagedObject(mo_2_2, "lsbootSanImagePath", {"Dn":self.orgNameDN + "boot-policy-BFS_POLICY/storage/san-secondary/path-secondary", "Type":"secondary", "Lun":"0", "Wwn":targets['B'][1]})
       
        except UcsException:
            print "Boot Policy already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types

    def createVNICTemplates(self):

        #TODO: This method is currently written to statically support a very common vNIC layout. In the future, some kind of mechanism should be written to support changes to this layout if desired. 
                # That said, the below "vlangroups" dictionary that maps vNIC prefixes to intended VLAN group in the config is the current prototype mechanism

        #maps vNIC "prefix" to intended VLAN group in config file
        vlangroups = {
            "ESX-MGMT": "mgmt",
            "ESX-NFS": "nfs",
            "ESX-PROD": "prod"
        }

        #vNIC
        for vnicprefix, vlangroup in vlangroups.iteritems():
            
            for fabricID in UcsFunctions.FABRICS:
                try:
                    mo = self.handle.AddManagedObject(self.org, "vnicLanConnTempl", 
                        {
                            "Name":vnicprefix + "-" + fabricID,
                            "Descr":vnicprefix + " - Fabric " + fabricID, # TODO: Need a better description method with current "vlangroups" mechanism
                            "SwitchId":fabricID, 
                            "QosPolicyName":"BE", 
                            "NwCtrlPolicyName":"NTKCTRL-CDP", 
                            "StatsPolicyName":"default", 
                            "TemplType":"updating-template", 
                            "PolicyOwner":"local", 
                            "Mtu":"9000", #Setting to 9000 here since class-default is still set to 1500, so this doesn't hurt much.  Consider adding this as a configurable item. 
                            "PinToGroupName":"", 
                            "Dn":self.orgNameDN + "lan-conn-templ-" + vnicprefix + "-" + fabricID, 
                            "IdentPoolName":"ESXi-MAC-" + fabricID
                        })
                except UcsException:
                    print "vNIC '" + vnicprefix + "-" + fabricID + "' already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types
                    mo = self.handle.GetManagedObject(None, None, {"Dn":self.orgNameDN + "lan-conn-templ-" + vnicprefix + "-" + fabricID}) #We need to do this because the creation of the vNIC, and it's VLANs, are separate actions

                #Add VLANs to vNIC
                vlans = self.ucsconfig['vlans']

                for vlanid, vlanname in vlans[vlangroup].iteritems():
                    
                    try:

                        self.handle.AddManagedObject(mo, "vnicEtherIf", 
                            {
                                "Name":vlanname, 
                                "Dn":self.orgNameDN + "lan-conn-templ-" + vnicprefix + "-" + fabricID + "/if-" + vlanname, 
                                "DefaultNet":"no" #Currently setting no native VLAN for any vNICs, leaving it up to the downstream device to tag (for now)
                            }, True)

                    except UcsException:
                        print "vNIC Template '" + vnicprefix + "-" + fabricID + "' already contains VLAN " + vlanname #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types

    def createVHBATemplates(self):

        #vHBA
        for fabricID in UcsFunctions.FABRICS:
            
            try:
                mo = self.handle.AddManagedObject(self.org, "vnicSanConnTempl", 
                    {
                        "Name":"ESX-VHBA-" + fabricID, 
                        "Descr":"ESXi Servers - vHBA Fabric " + fabricID, 
                        "SwitchId":fabricID, 
                        "QosPolicyName":"", 
                        "MaxDataFieldSize":"2048", 
                        "StatsPolicyName":"default", 
                        "TemplType":"updating-template", 
                        "PolicyOwner":"local", 
                        "Dn":self.orgNameDN + "san-conn-templ-ESX-VHBA-" + fabricID, 
                        "PinToGroupName":"", 
                        "IdentPoolName":"ESXi-WWPN-" + fabricID
                    })
            except UcsException:
                print "vHBA 'ESX-VHBA-" + fabricID + "' already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types
                mo = self.handle.GetManagedObject(None, None, {"Dn":self.orgNameDN + "san-conn-templ-ESX-VHBA-" + fabricID}) #We need to do this because the creation of the vHBA, and it's VSANs, are separate actions

            try:
                self.handle.AddManagedObject(mo, "vnicFcIf", 
                    {
                        "Name":"FCoE_Fabric_" + fabricID,
                        "Dn":self.orgNameDN + "san-conn-templ-ESX-VHBA-" + fabricID + "/if-default"
                    }, True)
            except UcsException:
                print "vHBA Template 'ESX-VHBA-" + fabricID + "' already contains VSAN " + "FCoE_Fabric_" + fabricID #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types


    def createSpTemplate(self):
        
        sptname = self.ucsconfig['ucs']['sptname']

        vnics = [ #Specify the order of vNICs/vHBAs (Python list insertion order is persistent)
            "ESX-MGMT-A",
            "ESX-MGMT-B",
            "ESX-NFS-A",
            "ESX-NFS-B",
            "ESX-PROD-A",
            "ESX-PROD-B",
            "ESX-VHBA-A",
            "ESX-VHBA-B"
        ]
        
        #Create Service Profile Template
        try:
            mo = self.handle.AddManagedObject(self.org, "lsServer",  #TODO: Make sure to associate with server pool once that feature is implemented
                {
                    "Name":sptname, 
                    "MgmtFwPolicyName":"", 
                    "MaintPolicyName":"MAINT-USERACK", 
                    "LocalDiskPolicyName":"NO_LOCAL",
                    "Descr":"This is the main Service Profile Template for ESXi Servers", 
                    "DynamicConPolicyName":"", 
                    "Type":"updating-template", 
                    "MgmtAccessPolicyName":"", 
                    "VconProfileName":"", 
                    "BiosProfileName":"", 
                    "SrcTemplName":"", 
                    "SolPolicyName":"", 
                    "IdentPoolName":"ESXi-UUID", 
                    "HostFwPolicyName":"HOST_FW_PKG", 
                    "AgentPolicyName":"", 
                    "ScrubPolicyName":"", 
                    "ExtIPPoolName":"ext-mgmt", 
                    "Uuid":"0", 
                    "ExtIPState":"pooled", 
                    "UsrLbl":"", 
                    "PowerPolicyName":"default", 
                    "Dn":self.orgNameDN + "ls-" + sptname, 
                    "BootPolicyName":"BFS_POLICY", 
                    "PolicyOwner":"local", 
                    "StatsPolicyName":"default"
                })
        except UcsException:
            print "SPT CREATION - Service Profile Template '" + sptname + "' already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types
            mo = self.handle.GetManagedObject(None, None, {"Dn":self.orgNameDN + "ls-" + sptname}) #We need to do this because the creation of the vHBA, and it's VSANs, are separate actions

        #Create vNIC VCON assignments
        for vnic in vnics:

            #This is a temporary measure to ensure the FC vcons are assigned last
            transport = "ethernet"
            if vnics.index(vnic) == 6 or vnics.index(vnic) == 7:
                transport = "fc"

            try:
                self.handle.AddManagedObject(mo, "lsVConAssign", 
                    {
                        "AdminVcon":"any", 
                        "VnicName":vnic, 
                        "Transport":transport, 
                        "Dn":self.orgNameDN + "ls-" + sptname + "/assign-ethernet-vnic-" + vnic, 
                        "Order":str(vnics.index(vnic) + 1)
                    }, True)
            except UcsException:
                print "SPT CREATION - vcon already mapped" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types

        for vnic in vnics:
            
            if vnics.index(vnic) <= 5:

                try:
                    #Add vNICs
                    self.handle.AddManagedObject(mo, "vnicEther", 
                        {
                            "QosPolicyName":"", 
                            "NwCtrlPolicyName":"", 
                            "Name":vnic, 
                            "IdentPoolName":"", 
                            "Mtu":"9000", #TODO: Why does this property exist? The MTU is set in the template. Experiment with the use or non-use of this value
                            "AdminVcon":"any", 
                            "PinToGroupName":"", 
                            "StatsPolicyName":"default", 
                            "AdaptorProfileName":"VMWare", 
                            "SwitchId":vnic[-1:], #TODO: Currently using string slicing to get Fabric ID. Might want to think about a different method.
                            "Dn":self.orgNameDN + "ls-" + sptname + "/ether-" + vnic, 
                            "Addr":"derived", 
                            "Order":"1", 
                            "NwTemplName":vnic
                        })
                except UcsException:
                    print "SPT CREATION - vnic already mapped to SPT" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types

            else:

                try:

                    #Add vHBAs
                    vnicfc = self.handle.AddManagedObject(mo, "vnicFc", 
                        {
                            "MaxDataFieldSize":"2048", 
                            "Name":vnic, 
                            "PersBindClear":"no", 
                            "IdentPoolName":"", 
                            "QosPolicyName":"", 
                            "AdminVcon":"any", 
                            "PersBind":"disabled", 
                            "PinToGroupName":"", 
                            "StatsPolicyName":"default", 
                            "AdaptorProfileName":"VMWare", 
                            "SwitchId":vnic[-1:], #TODO: Currently using string slicing to get Fabric ID. Might want to think about a different method.
                            "Dn":self.orgNameDN + "ls-" + sptname + "/fc-" + vnic, 
                            "Addr":"derived", 
                            "Order":"7", 
                            "NwTemplName":vnic
                        })

                    #TODO: Pretty sure this isn't needed. This should basically be ignored right now since the vHBA Template is being referenced. Dig into the docs and verify this. (maybe copy XML for SPT with and without this?)
                    self.handle.AddManagedObject(vnicfc, "vnicFcIf", 
                        {
                            "Name":"",
                            "Dn":self.orgNameDN + "ls-" + sptname + "/fc-" + vnic + "/if-default"
                        }, True)
                except UcsException:
                    print "SPT CREATION - vhba already mapped to SPT" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types
        
        #Set WWNN Pool
        try:
            self.handle.AddManagedObject(mo, "vnicFcNode", 
                {
                    "Addr":"pool-derived", 
                    "Dn":self.orgNameDN + "ls-" + sptname + "/fc-node", 
                    "IdentPoolName":"ESXi-WWNN"
                }, True)
        except UcsException:
            print "SPT CREATION - WWNN pool set already" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types
        
        #Set desired power state
        try:
            self.handle.AddManagedObject(mo, "lsPower", 
                {
                    "Dn":self.orgNameDN + "ls-" + sptname + "/power",
                    "State":"admin-up"
                }, True)
        except UcsException:
            print "SPT CREATION - desired power state set already" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types

        #Create VCONs
        for i in range(1, 4):
            try:
                self.handle.AddManagedObject(mo, "fabricVCon", 
                    {
                        "Dn":self.orgNameDN + "ls-" + sptname + "/vcon-" + str(i), 
                        "Select":"all", 
                        "Transport":"ethernet,fc", 
                        "Fabric":"NONE", 
                        "Share":"shared", 
                        "InstType":"auto", 
                        "Id":str(i), 
                        "Placement":"physical"
                    }, True)
            except UcsException:
                print "SPT CREATION - VCON created already" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types

    def spawnZerglings(handle):
        pass

    def getFaults(handle, organization):
        """Gets current faults from UCS"""
        try:
            getRsp = handle.GetManagedObject(None, FaultInst.ClassId())
            if (getRsp != None):
                result = WriteObject(getRsp)
            
        except SystemExit, e:
            sys.exit(e)

        except Exception, err:
            handle.Logout()
            print "Exception:", str(err)
            import traceback, sys
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
        return result
