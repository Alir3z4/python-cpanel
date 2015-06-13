from base64 import b64encode
import inspect
import json

from cpanel.compat import urllib, HTTPSConnection


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

    def get_port(self):
        """
        :rtype: int
        """
        return self.port

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
            'Authorization': 'Basic ' + b64encode(
                '{}:{}'.format(self.get_username(),
                               self.get_password())
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
        for k, v in params.items():
            if isinstance(v, bool):
                params[k] = 1 if v else 0

        endpoint = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
        connection = HTTPSConnection(self.get_hostname(), self.get_port())
        connection.request(
            method='GET',
            url='/json-api/{}?{}'.format(endpoint, urllib.urlencode(params)),
            headers=self.get_auth_header()
        )
        response = connection.getresponse()
        data = json.loads(response.read())
        connection.close()

        return data[data.keys()[1]]

    def abort_transfer_session(self, transfer_session_id):
        """
        Abort Transfer Session
        Aborts an active transfer session.

        https://documentation.cpanel.net/display/SDK/WHM+API+1+Functions+-+abort_transfer_session

        :param transfer_session_id: The transfer session's ID.
        :type: str

        :returns: Only metadata.
        :rtype: dict
        """
        return self._query({'transfer_session_id': transfer_session_id})

    def accesshash(self, user, generate):
        """
        Access Hash
        Regenerates or retrieves a user's access hash.

        https://documentation.cpanel.net/display/SDK/WHM+API+1+Functions+-+accesshash

        :param user: The user's name.
        :type user: str

        :param generate: Whether to regenerate the access hash.
        :type generate: bool

        :returns: The user's access hash.
        :rtype: str
        """
        return self._query({'user': user, 'generate': generate})

    def accountsummary(self, user, domain):
        """
        Account Summary
        Retrieves a summary of a user's account.

        https://documentation.cpanel.net/display/SDK/WHM+API+1+Functions+-+accountsummary

        :param user: The account's username.
        :type user: str
        :param domain: The main domain for an account on the server.
        :type domain: str

        :returns: A dictionary of account data
        :rtype: dict
        """
        return self._query({'user': user, 'domain': domain})

    def acctcounts(self, user):
        """
        Account Counts
        Lists a reseller's total accounts, suspended accounts, and account
        creation limit.

        https://documentation.cpanel.net/display/SDK/WHM+API+1+Functions+-+acctcounts

        :param user: A reseller's username, to query that reseller.
        If you do not specify a value, the function lists information
        for the authenticated account.
        :type user: str

        :returns: Information for an account. Contains the account,
        suspended, active, and limit parameters.
        :rtype: dict
        """
        return self._query({'user': user})

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

    def passwd(self, user, password, db_pass_update=True):
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

    def limitbw(self, user, bwlimit='unlimited'):
        """
        Set Cpanel Account Bandwidth Limit
        Modifies the bandwidth usage (transfer) limit for a specific account.

        https://documentation.cpanel.net/display/SDK/WHM+API+1+Functions+-+limitbw

        :param user: The account's username.
        :type user: str

        :param bwlimit: The account's new bandwidth quota. This parameter
        defaults to unlimited.
        :type bwlimit: str

        :rtype: dict
        """
        return self._query({'user': user, 'bwlimit': bwlimit})
