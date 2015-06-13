from base64 import b64encode
from http.client import HTTPSConnection
import inspect
import json

from cpanel.compat import urllib


class WHMAPIClient(object):
    hostname = None
    port = None
    username = None
    password = None
    auth_header = None

    def __init__(self, hostname, username, password, port=2087):
        """
        :type hostname: str
        :type username: str
        :type password: str
        :type port: int
        """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port

        self.set_auth_header(self.get_username(), self.get_password())

    def get_hostname(self):
        """
        :rtype: hostname
        """
        return self.hostname

    def get_username(self):
        """
        :rtype: str
        """
        return self.username

    def get_password(self):
        """
        :rtype: str
        """
        return self.password

    def set_auth_header(self, username, password):
        """
        :type username: str
        :type password: str
        """
        self.auth_header = {
            'Authorization:' 'Basic ' + b64encode(
                '{}:{}'.format(self.get_username(),
                               self.get_password()).decode('ascii')
            )
        }

    def get_auth_header(self):
        """
        :rtype: dict
        """
        return self.auth_header

    def _query(self, params):
        """
        Queries specified WHM Server's JSON API.

        :param params: HTTP GET params..
        :type params: dict

        :rtype: dict
        """
        endpoint = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
        connection = HTTPSConnection(self.get_hostname())
        connection.request(
            method='GET',
            url='/json-api/{}?{}'.format(endpoint, urllib.urlencode(params)),
            headers=self.get_auth_header()
        )
        response = connection.getresponse()
        data = response.read()
        connection.close()

        return json.loads(data)

    def createacct(self, username, domain):
        """
        Create Cpanel Account
        Creates a hosting account and sets up its associated domain information.

        https://documentation.cpanel.net/display/SDK/WHM+API+1+Functions+-+createacct

        :type username: str
        :type domain: str

        :rtype: dict
        """
        return self._query({
            'username': username,
            'domain': domain
        })

    def passwd(self, user, password, db_pass_update):
        """
        Set Cpanel Account Password
        Changes the password of a domain owner (cPanel) or reseller (WHM) account.

        https://documentation.cpanel.net/display/SDK/WHM+API+1+Functions+-+passwd

        :type user: str
        :type password: str
        :type db_pass_update: bool

        :rtype: dict
        """
        return self._query({
            'user': user,
            'pass': password,
            'db_pass_update': db_pass_update
        })
