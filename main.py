from UcsSdk import *
handle = UcsHandle()
handle.Login("10.102.1.5", "admin", "password")

thisOrg = "org-root/org-DI_DCA"

orgObj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN : thisOrg})
