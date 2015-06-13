try:  # Python3
    import urllib.request as urllib
    from http.client import HTTPSConnection
except ImportError:
    import urllib
    from httplib import HTTPSConnection
