try:
    import urllib.parse as urlparse
except ImportError:  # Python2
    import urlparse
try:  # Python3
    import urllib.request as urllib
except ImportError:
    import urllib
