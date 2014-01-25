#Need to pull over comments from ps1 scripts where relevant

def ucsHousekeeping(handle):
	##### Start-Of-PythonScript #####
	obj = handle.GetManagedObject(None, MacpoolPool.ClassId(), {MacpoolPool.DN:"org-root/mac-pool-default"})
	handle.RemoveManagedObject(obj)

	obj = handle.GetManagedObject(None, IppoolPool.ClassId(), {IppoolPool.DN:"org-root/ip-pool-iscsi-initiator-pool"})
	handle.AddManagedObject(obj, IppoolBlock.ClassId(), {IppoolBlock.FROM:"1.1.1.1", IppoolBlock.TO:"1.1.1.1", IppoolBlock.DN:"org-root/ip-pool-iscsi-initiator-pool/block-1.1.1.1-1.1.1.1"})

	obj = handle.GetManagedObject(None, FcpoolInitiators.ClassId(), {FcpoolInitiators.DN:"org-root/wwn-pool-node-default"})
	handle.RemoveManagedObject(obj)

	obj = handle.GetManagedObject(None, FcpoolInitiators.ClassId(), {FcpoolInitiators.DN:"org-root/wwn-pool-default"})
	handle.RemoveManagedObject(obj)

	obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root"})
	handle.AddManagedObject(obj, OrgOrg.ClassId(), {OrgOrg.DESCR:"DCA", OrgOrg.NAME:"DCA", OrgOrg.DN:"org-root/org-DI_DCA"})

	obj = handle.GetManagedObject(None, UuidpoolPool.ClassId(), {UuidpoolPool.DN:"org-root/uuid-pool-default"})
	handle.RemoveManagedObject(obj)

	obj = handle.GetManagedObject(None, ComputePool.ClassId(), {ComputePool.DN:"org-root/compute-pool-default"})
	handle.RemoveManagedObject(obj)

	obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root"})
	handle.AddManagedObject(obj, LsmaintMaintPolicy.ClassId(), {LsmaintMaintPolicy.DN:"org-root/maint-default", LsmaintMaintPolicy.POLICY_OWNER:"local", LsmaintMaintPolicy.UPTIME_DISR:"user-ack", LsmaintMaintPolicy.DESCR:"", LsmaintMaintPolicy.SCHED_NAME:""}, True)

	obj = handle.GetManagedObject(None, IqnpoolPool.ClassId(), {IqnpoolPool.DN:"org-root/iqn-pool-default"})
	handle.RemoveManagedObject(obj)

def createVLANSandVSANS(handle):
	obj = handle.GetManagedObject(None, FabricLanCloud.ClassId(), {FabricLanCloud.DN:"fabric/lan"})
	handle.AddManagedObject(obj, FabricVlan.ClassId(), {FabricVlan.COMPRESSION_TYPE:"included", FabricVlan.DN:"fabric/lan/net-VLAN_10", FabricVlan.SHARING:"none", FabricVlan.PUB_NW_NAME:"", "policyOwner":"local", FabricVlan.ID:"10", FabricVlan.MCAST_POLICY_NAME:"", FabricVlan.NAME:"VLAN_10", FabricVlan.DEFAULT_NET:"no"})

	obj = handle.GetManagedObject(None, None, {"dn":"fabric/san/A"})
	handle.AddManagedObject(obj, FabricVsan.ClassId(), {FabricVsan.DN:"fabric/san/A/", FabricVsan.ID:"100", "policyOwner":"local", FabricVsan.ZONING_STATE:"disabled", FabricVsan.FCOE_VLAN:"100", FabricVsan.FC_ZONE_SHARING_MODE:"coalesce", FabricVsan.NAME:"VSAN_100"})

	obj = handle.GetManagedObject(None, FabricSanCloud.ClassId(), {FabricSanCloud.DN:"fabric/san"})
	handle.AddManagedObject(obj, FabricVsan.ClassId(), {FabricVsan.DN:"fabric/san/B/", FabricVsan.ID:"200", "policyOwner":"local", FabricVsan.ZONING_STATE:"disabled", FabricVsan.FCOE_VLAN:"200", FabricVsan.FC_ZONE_SHARING_MODE:"coalesce", FabricVsan.NAME:"VSAN_200"})

def createUCSPools(handle):
	handle.StartTransaction()
	obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root/org-DI_DCA"})
	mo = handle.AddManagedObject(obj, MacpoolPool.ClassId(), {MacpoolPool.NAME:"ESX-MAC-A", MacpoolPool.POLICY_OWNER:"local", MacpoolPool.DESCR:"MAC addresses for ESXi Hosts in Fabric A", MacpoolPool.DN:"org-root/org-DI_DCA/mac-pool-ESX-MAC-A", MacpoolPool.ASSIGNMENT_ORDER:"sequential"})
	mo_1 = handle.AddManagedObject(mo, MacpoolBlock.ClassId(), {MacpoolBlock.FROM:"00:25:B5:00:00:00", MacpoolBlock.TO:"00:25:B5:00:00:FF", MacpoolBlock.DN:"org-root/org-DI_DCA/mac-pool-ESX-MAC-A/block-00:25:B5:00:00:00-00:25:B5:00:00:FF"})
	handle.CompleteTransaction()

	handle.StartTransaction()
	obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root"})
	mo = handle.AddManagedObject(obj, FcpoolInitiators.ClassId(), {FcpoolInitiators.DN:"org-root/wwn-pool-ESXi-WWNN-POOL", FcpoolInitiators.ASSIGNMENT_ORDER:"sequential", FcpoolInitiators.PURPOSE:"node-wwn-assignment", FcpoolInitiators.POLICY_OWNER:"local", FcpoolInitiators.DESCR:"ESXi WWNN Pool", FcpoolInitiators.NAME:"ESXi-WWNN-POOL"})
	mo_1 = handle.AddManagedObject(mo, FcpoolBlock.ClassId(), {FcpoolBlock.FROM:"20:00:00:25:B5:00:00:00", FcpoolBlock.DN:"org-root/wwn-pool-ESXi-WWNN-POOL/block-20:00:00:25:B5:00:00:00-20:00:00:25:B5:00:00:FF", FcpoolBlock.TO:"20:00:00:25:B5:00:00:FF"})
	handle.CompleteTransaction()

	handle.StartTransaction()
	obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root"})
	mo = handle.AddManagedObject(obj, FcpoolInitiators.ClassId(), {FcpoolInitiators.DN:"org-root/wwn-pool-ESX-WWPN-A", FcpoolInitiators.ASSIGNMENT_ORDER:"sequential", FcpoolInitiators.PURPOSE:"port-wwn-assignment", FcpoolInitiators.POLICY_OWNER:"local", FcpoolInitiators.DESCR:"ESXi WWPN Pool Fabric A", FcpoolInitiators.NAME:"ESX-WWPN-A"})
	mo_1 = handle.AddManagedObject(mo, FcpoolBlock.ClassId(), {FcpoolBlock.FROM:"20:00:00:25:B5:02:10:00", FcpoolBlock.DN:"org-root/wwn-pool-ESX-WWPN-A/block-20:00:00:25:B5:02:10:00-20:00:00:25:B5:02:10:FF", FcpoolBlock.TO:"20:00:00:25:B5:02:10:FF"})
	handle.CompleteTransaction()

	obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root/org-DI_DCA"})
	handle.AddManagedObject(obj, ComputePool.ClassId(), {ComputePool.NAME:"main-server-pool", ComputePool.POLICY_OWNER:"local", ComputePool.DESCR:"main server pool", ComputePool.DN:"org-root/org-DI_DCA/compute-pool-main-server-pool"})

	handle.StartTransaction()
	obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root"})
	mo = handle.AddManagedObject(obj, UuidpoolPool.ClassId(), {UuidpoolPool.NAME:"main-uuid-pool", UuidpoolPool.DESCR:"main uuid pool", UuidpoolPool.PREFIX:"derived", UuidpoolPool.DN:"org-root/uuid-pool-main-uuid-pool", UuidpoolPool.ASSIGNMENT_ORDER:"sequential", UuidpoolPool.POLICY_OWNER:"local"})
	mo_1 = handle.AddManagedObject(mo, UuidpoolBlock.ClassId(), {UuidpoolBlock.FROM:"0000-000000000001", UuidpoolBlock.TO:"0000-000000000100", UuidpoolBlock.DN:"org-root/uuid-pool-main-uuid-pool/block-from-0000-000000000001-to-0000-000000000100"})
	handle.CompleteTransaction()

def ucsCreatePolicies(handle):
	#Create/set global policies
	handle.StartTransaction()
	obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root"})
	handle.AddManagedObject(obj, ComputePsuPolicy.ClassId(), {ComputePsuPolicy.POLICY_OWNER:"local", ComputePsuPolicy.REDUNDANCY:"grid", ComputePsuPolicy.DESCR:"", ComputePsuPolicy.DN:"org-root/psu-policy"}, True)
	obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root"})
	handle.AddManagedObject(obj, ComputeChassisDiscPolicy.ClassId(), {ComputeChassisDiscPolicy.REBALANCE:"user-acknowledged", ComputeChassisDiscPolicy.DN:"org-root/chassis-discovery", ComputeChassisDiscPolicy.ACTION:"4-link", ComputeChassisDiscPolicy.LINK_AGGREGATION_PREF:"port-channel", ComputeChassisDiscPolicy.POLICY_OWNER:"local", ComputeChassisDiscPolicy.NAME:"", ComputeChassisDiscPolicy.DESCR:""}, True)
	handle.CompleteTransaction()

	#Global QoS policy
	handle.StartTransaction()
	obj = handle.GetManagedObject(None, QosclassDefinition.ClassId(), {QosclassDefinition.DN:"fabric/lan/classes"})
	mo = handle.SetManagedObject(obj, QosclassDefinition.ClassId(), {QosclassDefinition.POLICY_OWNER:"local", QosclassDefinition.DESCR:""})
	mo_1 = handle.AddManagedObject(mo, QosclassEthBE.ClassId(), {QosclassEthBE.WEIGHT:"9", QosclassEthBE.NAME:"", QosclassEthBE.DN:"fabric/lan/classes/class-best-effort", QosclassEthBE.MTU:"normal", QosclassEthBE.MULTICAST_OPTIMIZE:"no"}, True)
	mo_2 = handle.AddManagedObject(mo, QosclassEthClassified.ClassId(), {QosclassEthClassified.DROP:"drop", QosclassEthClassified.WEIGHT:"none", QosclassEthClassified.NAME:"", QosclassEthClassified.COS:"1", QosclassEthClassified.DN:"fabric/lan/classes/class-bronze", QosclassEthClassified.ADMIN_STATE:"enabled", QosclassEthClassified.MTU:"9216", QosclassEthClassified.MULTICAST_OPTIMIZE:"no"}, True)
	mo_3 = handle.AddManagedObject(mo, QosclassEthClassified.ClassId(), {QosclassEthClassified.DROP:"drop", QosclassEthClassified.WEIGHT:"10", QosclassEthClassified.NAME:"", QosclassEthClassified.COS:"4", QosclassEthClassified.DN:"fabric/lan/classes/class-gold", QosclassEthClassified.ADMIN_STATE:"enabled", QosclassEthClassified.MTU:"normal", QosclassEthClassified.MULTICAST_OPTIMIZE:"no"}, True)
	mo_4 = handle.AddManagedObject(mo, QosclassEthClassified.ClassId(), {QosclassEthClassified.DROP:"drop", QosclassEthClassified.WEIGHT:"none", QosclassEthClassified.NAME:"", QosclassEthClassified.COS:"5", QosclassEthClassified.DN:"fabric/lan/classes/class-platinum", QosclassEthClassified.ADMIN_STATE:"enabled", QosclassEthClassified.MTU:"normal", QosclassEthClassified.MULTICAST_OPTIMIZE:"no"}, True)
	mo_5 = handle.AddManagedObject(mo, QosclassEthClassified.ClassId(), {QosclassEthClassified.DROP:"drop", QosclassEthClassified.WEIGHT:"best-effort", QosclassEthClassified.NAME:"", QosclassEthClassified.COS:"2", QosclassEthClassified.DN:"fabric/lan/classes/class-silver", QosclassEthClassified.ADMIN_STATE:"enabled", QosclassEthClassified.MTU:"9216", QosclassEthClassified.MULTICAST_OPTIMIZE:"no"}, True)
	handle.CompleteTransaction()

	#Configure NTP

    #Configure TimeZone

    #Configure SNMP Community

    #Configure SNMP Traps

    #Create single QoS Policy (add more)
    handle.StartTransaction()
	obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root/org-DI_DCA"})
	mo = handle.AddManagedObject(obj, EpqosDefinition.ClassId(), {EpqosDefinition.DN:"org-root/org-DI_DCA/ep-qos-Bronze", EpqosDefinition.DESCR:"", EpqosDefinition.NAME:"Bronze", EpqosDefinition.POLICY_OWNER:"local"})
	mo_1 = handle.AddManagedObject(mo, EpqosEgress.ClassId(), {EpqosEgress.PRIO:"bronze", EpqosEgress.HOST_CONTROL:"none", EpqosEgress.RATE:"line-rate", EpqosEgress.NAME:"", EpqosEgress.DN:"org-root/org-DI_DCA/ep-qos-Bronze/egress", EpqosEgress.BURST:"10240"}, True)
	handle.CompleteTransaction()

	handle.StartTransaction()
	obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root/org-DI_DCA"})
	mo = handle.AddManagedObject(obj, ComputeQual.ClassId(), {ComputeQual.DN:"org-root/org-DI_DCA/blade-qualifier-B200-M3-QUAL", ComputeQual.POLICY_OWNER:"local", ComputeQual.NAME:"B200-M3-QUAL", ComputeQual.DESCR:"B200 M3 Qualification Policy"})
	mo_1 = handle.AddManagedObject(mo, ComputePhysicalQual.ClassId(), {ComputePhysicalQual.DN:"org-root/org-DI_DCA/blade-qualifier-B200-M3-QUAL/physical", ComputePhysicalQual.MODEL:"UCSB-B200-M3"})
	handle.CompleteTransaction()

	obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root/org-DI_DCA"})
	handle.AddManagedObject(obj, ComputePoolingPolicy.ClassId(), {ComputePoolingPolicy.POLICY_OWNER:"local", ComputePoolingPolicy.DN:"org-root/org-DI_DCA/pooling-policy-B200-M3-PLCY", ComputePoolingPolicy.QUALIFIER:"B200-M3-QUAL", ComputePoolingPolicy.POOL_DN:"org-root/org-DI_DCA/compute-pool-main-server-pool", ComputePoolingPolicy.NAME:"B200-M3-PLCY", ComputePoolingPolicy.DESCR:"B200 M3 Server Pool Policy"})

	obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root/org-DI_DCA"})
	handle.AddManagedObject(obj, FirmwareComputeHostPack.ClassId(), {FirmwareComputeHostPack.BLADE_BUNDLE_VERSION:"", FirmwareComputeHostPack.DN:"org-root/org-DI_DCA/fw-host-pack-HOST_FW_PKG", FirmwareComputeHostPack.MODE:"staged", FirmwareComputeHostPack.UPDATE_TRIGGER:"immediate", FirmwareComputeHostPack.NAME:"HOST_FW_PKG", FirmwareComputeHostPack.STAGE_SIZE:"0", FirmwareComputeHostPack.IGNORE_COMP_CHECK:"yes", FirmwareComputeHostPack.POLICY_OWNER:"local", FirmwareComputeHostPack.DESCR:"B200-m3 Host Firmware Package", FirmwareComputeHostPack.RACK_BUNDLE_VERSION:""})

	obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root/org-DI_DCA"})
	handle.AddManagedObject(obj, LsmaintMaintPolicy.ClassId(), {LsmaintMaintPolicy.UPTIME_DISR:"user-ack", LsmaintMaintPolicy.SCHED_NAME:"", LsmaintMaintPolicy.DN:"org-root/org-DI_DCA/maint-MAINT-USERACK", LsmaintMaintPolicy.DESCR:"Maintenance Policy for User Ack", LsmaintMaintPolicy.POLICY_OWNER:"local", LsmaintMaintPolicy.NAME:"MAINT-USERACK"})

	handle.StartTransaction()
	obj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN:"org-root/org-DI_DCA"})
	mo = handle.AddManagedObject(obj, NwctrlDefinition.ClassId(), {NwctrlDefinition.POLICY_OWNER:"local", NwctrlDefinition.CDP:"enabled", NwctrlDefinition.NAME:"NTKCTRLPOLICY", NwctrlDefinition.DN:"org-root/org-DI_DCA/nwctrl-NTKCTRLPOLICY", NwctrlDefinition.MAC_REGISTER_MODE:"only-native-vlan", NwctrlDefinition.DESCR:"", NwctrlDefinition.UPLINK_FAIL_ACTION:"link-down"})
	mo_1 = handle.AddManagedObject(mo, DpsecMac.ClassId(), {DpsecMac.DN:"org-root/org-DI_DCA/nwctrl-NTKCTRLPOLICY/mac-sec", DpsecMac.POLICY_OWNER:"local", DpsecMac.NAME:"", DpsecMac.DESCR:"", DpsecMac.FORGE:"allow"}, True)
	handle.CompleteTransaction()



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
	#Need to figure this out - the python interpreter threw an error when you tried to capture this