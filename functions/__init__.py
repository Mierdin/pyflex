__version__ = (1,0)

import sys

if sys.version_info < (2, 6):
    raise RuntimeError('You need Python 2.6+ for this module.')