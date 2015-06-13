import sys

if sys.version_info[0] == 2:
    import urllib
    from httplib import HTTPSConnection
else:
    import urllib.request as urllib
    from http.client import HTTPSConnection
