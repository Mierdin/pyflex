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
