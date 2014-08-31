from UcsSdk import *

class UcsFunctions:
    # Need to pull over comments from ps1 scripts where relevant

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
            obj = self.handle.GetManagedObject(None, None, {"Dn":"fabric/san/" + fabric.upper()})
            for vsanid, vsanname in vsans[fabric].iteritems():
                try:
                    self.handle.AddManagedObject(obj, "fabricVsan", {"Name":vsanname, "ZoningState":"disabled", "PolicyOwner":"local", "FcZoneSharingMode":"coalesce", "FcoeVlan":str(vsanid), "Dn":"fabric/san/" + fabric.upper() + "/", "Id":str(vsanid)})
                except UcsException:
                    print "Already exists" #convert to logging and TODO: need to handle this better. Need to poke around at the possible exception types


    def createUCSPools(self):
        #TODO: Lots of shortcuts taken here. Need to come back and clean up this atrocious mess.
        pools = self.ucsconfig['ucs']['pools']

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

    def createBootPolicy(handle):
            #This function was moved out of the main policy creation function because BFS can be driven by data retrieved from the storage array.
        #Ideally, the main function should reach into the array (should have a "retrieve four targets" function for this) then this function gets run with an array as an argument for those four tagets to fall into.
        handle.StartTransaction()
        obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root/org-DI_DCA"})
        mo = handle.AddManagedObject(obj, LsbootPolicy.ClassId(), {LsbootPolicy.POLICY_OWNER:"local", LsbootPolicy.REBOOT_ON_UPDATE:"no", LsbootPolicy.NAME:"BOOT_POLICY", LsbootPolicy.ENFORCE_VNIC_NAME:"yes", LsbootPolicy.DN:"org-root/org-DI_DCA/boot-policy-BOOT_POLICY", LsbootPolicy.DESCR:"Boot Policy"})
        mo_1 = handle.AddManagedObject(mo, LsbootVirtualMedia.ClassId(), {LsbootVirtualMedia.DN:"org-root/org-DI_DCA/boot-policy-BOOT_POLICY/read-only-vm", LsbootVirtualMedia.ACCESS:"read-only", LsbootVirtualMedia.ORDER:"1"})
        mo_2 = handle.AddManagedObject(mo, LsbootStorage.ClassId(), {LsbootStorage.DN:"org-root/org-DI_DCA/boot-policy-BOOT_POLICY/storage", LsbootStorage.ORDER:"2"}, True)
        mo_2_1 = handle.AddManagedObject(mo_2, LsbootSanImage.ClassId(), {LsbootSanImage.VNIC_NAME:"ESX-VHBA-A", LsbootSanImage.DN:"org-root/org-DI_DCA/boot-policy-BOOT_POLICY/storage/san-primary", LsbootSanImage.TYPE:"primary"})
        mo_2_1_1 = handle.AddManagedObject(mo_2_1, LsbootSanImagePath.ClassId(), {LsbootSanImagePath.TYPE:"primary", LsbootSanImagePath.DN:"org-root/org-DI_DCA/boot-policy-BOOT_POLICY/storage/san-primary/path-primary", LsbootSanImagePath.LUN:"0", LsbootSanImagePath.WWN:"50:00:00:00:00:00:00:00"})
        mo_2_1_2 = handle.AddManagedObject(mo_2_1, LsbootSanImagePath.ClassId(), {LsbootSanImagePath.TYPE:"secondary", LsbootSanImagePath.DN:"org-root/org-DI_DCA/boot-policy-BOOT_POLICY/storage/san-primary/path-secondary", LsbootSanImagePath.LUN:"0", LsbootSanImagePath.WWN:"50:00:00:00:00:00:00:01"})
        mo_2_2 = handle.AddManagedObject(mo_2, LsbootSanImage.ClassId(), {LsbootSanImage.VNIC_NAME:"ESX-VHBA-B", LsbootSanImage.DN:"org-root/org-DI_DCA/boot-policy-BOOT_POLICY/storage/san-secondary", LsbootSanImage.TYPE:"secondary"})
        mo_2_2_1 = handle.AddManagedObject(mo_2_2, LsbootSanImagePath.ClassId(), {LsbootSanImagePath.TYPE:"primary", LsbootSanImagePath.DN:"org-root/org-DI_DCA/boot-policy-BOOT_POLICY/storage/san-secondary/path-primary", LsbootSanImagePath.LUN:"0", LsbootSanImagePath.WWN:"50:00:00:00:00:00:00:02"})
        mo_2_2_2 = handle.AddManagedObject(mo_2_2, LsbootSanImagePath.ClassId(), {LsbootSanImagePath.TYPE:"secondary", LsbootSanImagePath.DN:"org-root/org-DI_DCA/boot-policy-BOOT_POLICY/storage/san-secondary/path-secondary", LsbootSanImagePath.LUN:"0", LsbootSanImagePath.WWN:"50:00:00:00:00:00:00:03"})
        handle.CompleteTransaction()

    def createVNICandVHBATemplates(handle):
        handle.StartTransaction()
        obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root/org-DI_DCA"})
        mo = handle.AddManagedObject(obj, VnicLanConnTempl.ClassId(), {VnicLanConnTempl.QOS_POLICY_NAME:"qos-1", VnicLanConnTempl.MTU:"1500", VnicLanConnTempl.DESCR:"Management NIC - ESXi Hosts - Fabric A", VnicLanConnTempl.IDENT_POOL_NAME:"ESX-MAC-A", VnicLanConnTempl.NAME:"ESX-MGMT-A", VnicLanConnTempl.TEMPL_TYPE:"updating-template", VnicLanConnTempl.DN:"org-root/org-DI_DCA/lan-conn-templ-ESX-MGMT-A", VnicLanConnTempl.SWITCH_ID:"A", VnicLanConnTempl.POLICY_OWNER:"local", VnicLanConnTempl.NW_CTRL_POLICY_NAME:"NTKCTRLPOLICY", VnicLanConnTempl.PIN_TO_GROUP_NAME:"", VnicLanConnTempl.STATS_POLICY_NAME:"default"})
        mo_1 = handle.AddManagedObject(mo, VnicEtherIf.ClassId(), {VnicEtherIf.DN:"org-root/org-DI_DCA/lan-conn-templ-ESX-MGMT-A/if-VLAN_10", VnicEtherIf.NAME:"VLAN_10", VnicEtherIf.DEFAULT_NET:"no"}, True)
        mo_2 = handle.AddManagedObject(mo, VnicEtherIf.ClassId(), {VnicEtherIf.DN:"org-root/org-DI_DCA/lan-conn-templ-ESX-MGMT-A/if-default", VnicEtherIf.NAME:"default", VnicEtherIf.DEFAULT_NET:"no"}, True)
        handle.CompleteTransaction()

        handle.StartTransaction()
        obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root/org-DI_DCA"})
        mo = handle.AddManagedObject(obj, VnicSanConnTempl.ClassId(), {VnicSanConnTempl.QOS_POLICY_NAME:"", VnicSanConnTempl.POLICY_OWNER:"local", VnicSanConnTempl.NAME:"ESX-VHBA-A", VnicSanConnTempl.SWITCH_ID:"A", VnicSanConnTempl.IDENT_POOL_NAME:"ESX-WWPN-A", VnicSanConnTempl.MAX_DATA_FIELD_SIZE:"2048", VnicSanConnTempl.STATS_POLICY_NAME:"default", VnicSanConnTempl.PIN_TO_GROUP_NAME:"", VnicSanConnTempl.DESCR:"ESXi vHBA Fabric A", VnicSanConnTempl.TEMPL_TYPE:"updating-template", VnicSanConnTempl.DN:"org-root/org-DI_DCA/san-conn-templ-ESX-VHBA-A"})
        mo_1 = handle.AddManagedObject(mo, VnicFcIf.ClassId(), {VnicFcIf.NAME:"VSAN_100", VnicFcIf.DN:"org-root/org-DI_DCA/san-conn-templ-ESX-VHBA-A/if-default"}, True)
        handle.CompleteTransaction()

    def createSpTemplates(handle):
        handle.StartTransaction()
        obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root/org-DI_DCA"})
        mo = handle.AddManagedObject(obj, LsServer.ClassId(), {LsServer.EXT_IPPOOL_NAME:"ext-mgmt", LsServer.BOOT_POLICY_NAME:"BOOT_POLICY", LsServer.TYPE:"updating-template", LsServer.DYNAMIC_CON_POLICY_NAME:"", LsServer.DESCR:"ESXi Service Profile Template", LsServer.BIOS_PROFILE_NAME:"", LsServer.SRC_TEMPL_NAME:"", LsServer.EXT_IPSTATE:"pooled", LsServer.AGENT_POLICY_NAME:"", LsServer.LOCAL_DISK_POLICY_NAME:"default", LsServer.HOST_FW_POLICY_NAME:"HOST_FW_PKG", LsServer.MGMT_FW_POLICY_NAME:"", LsServer.MGMT_ACCESS_POLICY_NAME:"", LsServer.UUID:"0", LsServer.DN:"org-root/org-DI_DCA/ls-ESXi-SPT", LsServer.MAINT_POLICY_NAME:"MAINT-USERACK", LsServer.SCRUB_POLICY_NAME:"", LsServer.USR_LBL:"", LsServer.SOL_POLICY_NAME:"", LsServer.POWER_POLICY_NAME:"default", LsServer.VCON_PROFILE_NAME:"", LsServer.IDENT_POOL_NAME:"main-uuid-pool", LsServer.POLICY_OWNER:"local", LsServer.NAME:"ESXi-SPT", LsServer.STATS_POLICY_NAME:"default"})
        mo_1 = handle.AddManagedObject(mo, LsVConAssign.ClassId(), {LsVConAssign.VNIC_NAME:"ESX-MGMT-A", LsVConAssign.TRANSPORT:"ethernet", LsVConAssign.ORDER:"1", LsVConAssign.ADMIN_VCON:"1", LsVConAssign.DN:"org-root/org-DI_DCA/ls-ESXi-SPT/assign-ethernet-vnic-ESX-MGMT-A"}, True)
        mo_2 = handle.AddManagedObject(mo, LsVConAssign.ClassId(), {LsVConAssign.VNIC_NAME:"ESX-VHBA-A", LsVConAssign.TRANSPORT:"fc", LsVConAssign.ORDER:"1", LsVConAssign.ADMIN_VCON:"2", LsVConAssign.DN:"org-root/org-DI_DCA/ls-ESXi-SPT/assign-fc-vnic-ESX-VHBA-A"}, True)
        mo_3 = handle.AddManagedObject(mo, VnicEther.ClassId(), {VnicEther.SWITCH_ID:"A", VnicEther.ADDR:"derived", VnicEther.STATS_POLICY_NAME:"default", VnicEther.ADAPTOR_PROFILE_NAME:"VMWare", VnicEther.DN:"org-root/org-DI_DCA/ls-ESXi-SPT/ether-ESX-MGMT-A", VnicEther.ORDER:"1", VnicEther.NW_CTRL_POLICY_NAME:"", VnicEther.QOS_POLICY_NAME:"", VnicEther.NAME:"ESX-MGMT-A", VnicEther.PIN_TO_GROUP_NAME:"", VnicEther.IDENT_POOL_NAME:"", VnicEther.ADMIN_VCON:"1", VnicEther.NW_TEMPL_NAME:"ESX-MGMT-A", VnicEther.MTU:"1500"})
        mo_4 = handle.AddManagedObject(mo, VnicFc.ClassId(), {VnicFc.ADAPTOR_PROFILE_NAME:"VMWare", VnicFc.ADDR:"derived", VnicFc.ADMIN_VCON:"2", VnicFc.SWITCH_ID:"A", VnicFc.NW_TEMPL_NAME:"ESX-VHBA-A", VnicFc.PIN_TO_GROUP_NAME:"", VnicFc.PERS_BIND:"disabled", VnicFc.IDENT_POOL_NAME:"", VnicFc.ORDER:"1", VnicFc.PERS_BIND_CLEAR:"no", VnicFc.MAX_DATA_FIELD_SIZE:"2048", VnicFc.QOS_POLICY_NAME:"", VnicFc.NAME:"ESX-VHBA-A", VnicFc.DN:"org-root/org-DI_DCA/ls-ESXi-SPT/fc-ESX-VHBA-A", VnicFc.STATS_POLICY_NAME:"default"})
        mo_4_1 = handle.AddManagedObject(mo_4, VnicFcIf.ClassId(), {VnicFcIf.NAME:"", VnicFcIf.DN:"org-root/org-DI_DCA/ls-ESXi-SPT/fc-ESX-VHBA-A/if-default"}, True)
        mo_5 = handle.AddManagedObject(mo, VnicFcNode.ClassId(), {VnicFcNode.ADDR:"pool-derived", VnicFcNode.DN:"org-root/org-DI_DCA/ls-ESXi-SPT/fc-node", VnicFcNode.IDENT_POOL_NAME:"ESXi-WWNN-POOL"}, True)
        mo_6 = handle.AddManagedObject(mo, LsRequirement.ClassId(), {LsRequirement.NAME:"main-server-pool", LsRequirement.RESTRICT_MIGRATION:"no", LsRequirement.DN:"org-root/org-DI_DCA/ls-ESXi-SPT/pn-req", LsRequirement.QUALIFIER:"B200-M3-QUAL"}, True)
        mo_7 = handle.AddManagedObject(mo, LsPower.ClassId(), {LsPower.DN:"org-root/org-DI_DCA/ls-ESXi-SPT/power", LsPower.STATE:"admin-up"}, True)
        mo_8 = handle.AddManagedObject(mo, FabricVCon.ClassId(), {FabricVCon.INST_TYPE:"manual", FabricVCon.SHARE:"shared", FabricVCon.SELECT:"all", FabricVCon.TRANSPORT:"ethernet,fc", FabricVCon.ID:"1", FabricVCon.PLACEMENT:"physical", FabricVCon.DN:"org-root/org-DI_DCA/ls-ESXi-SPT/vcon-1", FabricVCon.FABRIC:"NONE"}, True)
        mo_9 = handle.AddManagedObject(mo, FabricVCon.ClassId(), {FabricVCon.INST_TYPE:"manual", FabricVCon.SHARE:"shared", FabricVCon.SELECT:"all", FabricVCon.TRANSPORT:"ethernet,fc", FabricVCon.ID:"2", FabricVCon.PLACEMENT:"physical", FabricVCon.DN:"org-root/org-DI_DCA/ls-ESXi-SPT/vcon-2", FabricVCon.FABRIC:"NONE"}, True)
        mo_10 = handle.AddManagedObject(mo, FabricVCon.ClassId(), {FabricVCon.INST_TYPE:"manual", FabricVCon.SHARE:"shared", FabricVCon.SELECT:"all", FabricVCon.TRANSPORT:"ethernet,fc", FabricVCon.ID:"3", FabricVCon.PLACEMENT:"physical", FabricVCon.DN:"org-root/org-DI_DCA/ls-ESXi-SPT/vcon-3", FabricVCon.FABRIC:"NONE"}, True)
        mo_11 = handle.AddManagedObject(mo, FabricVCon.ClassId(), {FabricVCon.INST_TYPE:"manual", FabricVCon.SHARE:"shared", FabricVCon.SELECT:"all", FabricVCon.TRANSPORT:"ethernet,fc", FabricVCon.ID:"4", FabricVCon.PLACEMENT:"physical", FabricVCon.DN:"org-root/org-DI_DCA/ls-ESXi-SPT/vcon-4", FabricVCon.FABRIC:"NONE"}, True)
        handle.CompleteTransaction()

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
