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
    REQUEST_TYPE_GET = 'GET'
    REQUEST_TYPE_POST = 'POST'
    ALLOWED_REQUEST_TYPES = (REQUEST_TYPE_GET, REQUEST_TYPE_POST, )

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

    def _query(self, request_type, endpoint, data):
        """
        Queries specified WHM Server's JSON API.

        :param: request_type: The HTTP request type, it can be ``GET``
        or ``POST``
        :type request_type: str
        :param endpoint: API endpoint.
        :type endpoint: str
        :param data: HTTP GET params..
        :type data: dict

        :rtype: dict
        """
        for k, v in data.items():
            if isinstance(v, bool):
                data[k] = 1 if v else 0

        url = '/json-api/{}'.format(endpoint)
        if request_type == self.REQUEST_TYPE_GET:
            url = '{}?{}'.format(url, urllib.urlencode(data))

        connection = HTTPSConnection(self.get_hostname(), self.get_port())
        connection.request(
            method=request_type,
            url=url,
            headers=self.get_auth_header()
        )
        response = connection.getresponse()
        data = json.loads(response.read())
        connection.close()

        return data[data.keys()[1]]

    def _query_get(self, params):
        """
        :type payload: dict
        """
        endpoint = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
        return self._query(self.REQUEST_TYPE_GET, endpoint, params)

    def _query_post(self, payload):
        """
        :type payload: dict
        """
        endpoint = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
        return self._query(self.REQUEST_TYPE_POST, endpoint, payload)

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
        return self._query_get({'transfer_session_id': transfer_session_id})

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
        return self._query_get({'user': user, 'generate': generate})

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
        return self._query_get({'user': user, 'domain': domain})

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
        return self._query_get({'user': user})

    def add_configclusterserver(self, name, user, key):
        """
        Add Config Cluster Server
        Adds a server to a configuration cluster.

        https://documentation.cpanel.net/display/SDK/WHM+API+1+Functions+-+add_configclusterserver

        :param name: The remote configuration cluster server's name.
        :type name: str
        :param user: The username for the server's root-level account.
        :type user: str
        :param key: A truncated version of the server's remote access key.
        :type key:str

        :returns: metadata
        :rtype: dict
        """
        self._query_post({'name': name, 'user': user, 'key': key})

    def adddns(self, domain, ip, template, trueowner):
        """
        Add DNS
        Creates a DNS zone. When you call this function, the system uses the
        domain name and IP address that you supply. WHM's standard zone
        template determines all other zone information.
        Generates the DNS zone's MX record, domain PTR, and A records
        automatically.

        https://documentation.cpanel.net/display/SDK/WHM+API+1+Functions+-+adddns

        :param domain: The new zone's domain. (A valid domain name on the
        server.)
        :type domain: str
        :param ip: The domain's IP address. (A valid IP address.)
        :type ip: str
        :param template: The zone file template. If you do not use this
        parameter, the function uses the standard zone file template. (
            * standard
            * simple
            * standardvirtualftp
            * The name of a custom zone template file in the
            /var/cpanel/zonetemplates directory.)
        :type template: str
        :param trueowner: The new zone's owner. (A valid cPanel or WHM
        username.)
        :type trueowner: str

        :returns: Metadata
        :rtype: dict
        """
        allowed_template = (
            'standard',
            'simple',
            'standardvirtualftp',
            '/var/cpanel/zonetemplates'
        )
        if (template not in allowed_template[0:2]
            or not template.startswith(allowed_template[-1])):
            raise ValueError()

        return self._query_post({
            'domain': domain,
            'ip': ip,
            'template': template,
            'trueowner': trueowner
        })

    def addips(self, ips, netmask, excludes):
        """
        Add IPs
        Adds an IP address or addresses to the server.

        https://documentation.cpanel.net/display/SDK/WHM+API+1+Functions+-+addips

        :param ips: The IPv4 address or addresses. (A valid IPv4 address or
        address range in Class C CIDR format.)
        :type ips: list
        :param netmask: The IPv4 address' netmask. (A valid IPv4 netmask
        address.)
        :type netmask
        :param excludes: An IPv4 address or addresses to exclude.
        :type excludes: list

        :returns: Output of messages
        :rtype: dict
        """
        return self._query_post({
            'ips': ','.join(ips),
            'netmask': netmask,
            'excludes': ','.join(excludes)
        })

    def addpkg(self, name, featurelist='default', quota='unlimited', ip='n',
               cgi=True, frontpage=True, cpmod=None, language='EN',
               maxftp='unlimited', maxsql='unlimited', maxpop='unlimited',
               maxlists='unlimited', maxsub='unlimited', maxpark='unlimited',
               maxaddon='unlimited', hasshell=False, bwlimit='unlimited',
               MAX_EMAIL_PER_HOUR='unlimited',
               MAX_DEFER_FAIL_PERCENTAGE='unlimited', digestauth=False,
               _PACKAGE_EXTENSIONS=list):
        """
        Add PKG
        Creates a hosting plan (package).

        https://documentation.cpanel.net/display/SDK/WHM+API+1+Functions+-+addpkg

        :param name: The new hosting plan's name. (A valid hosting plan name.)
        :param featurelist: The hosting plan's feature list. If you do not
        use this parameter, the function assigns the default feature list
        to the account. (A valid feature list name on the server.)
        :type featurelist: str
        :param quota: The hosting plan's disk space quota. This parameter
        defaults to 0 (unlimited). (A positive integer between one and
        999,999 that represents the maximum disk space that the account
        may use, in Megabytes (MB).0 — The hosting plan's disk space
        is unlimited.)
        :type quota: int
        :param ip: Whether the account has a dedicated IP address. This
        parameter defaults to n. (
            * y — The account has a dedicated IP address.
            * n — The account does not have a dedicated IP addr
        )
        :type ip: str
        :param cgi: Whether CGI access is enabled for the account. This
        parameter defaults to ``True``.
        :type cgi: bool
        :param frontpage: Whether Microsoft® FrontPage Extensions are enabled for the
        account.
        :type frontpage: bool
        :param cpmod: The hosting plan's cPanel theme. This parameter
        defaults to the server's default cPanel theme. (
            * x3
            * paper_lantern
        )
        :type cpmod: str
        :param language: The hosting plan's default locale. This value
        defaults to the server's default locale. (A two-letter ISO-3166 code.)
        :param maxftp: The hosting plan's maximum number of FTP accounts.
        This parameter defaults to ``unlimited``. (
            * A positive integer between one and 999,999.
            * 0, unlimited, or null — The account has unlimited FTP accounts.
        )
        :type maxftp: str
        :param maxsql: The hosting plan's maximum number of each available
        type of SQL database. For example, if you set this value to 5 and
        the system administrator allows MySQL® and PostgreSQL databases,
        you can create up to 5 MySQL databases and up to 5 PostgreSQL
        databases. parameter defaults to ``unlimited``. (
            * A positive integer between one and 999,999.
            * 0, unlimited, or null — The account has unlimited databases.
        )
        :type maxsql: str
        :param maxpop: The hosting plan's maximum number of email accounts.
        This parameter defaults to ``unlimited.`` (
            * A positive integer between one and 999,999.
            * 0, unlimited, or null — The account has unlimited email accounts.
        )
        :param maxlists: The hosting plan's maximum number of mailing lists.
        This parameter defaults to ``unlimited``. (
            * A positive integer between one and 999,999.
            * 0, unlimited, or null — The account has unlimited mailing lists.
        )
        :type maxlists: str
        :param maxsub: The hosting plan's maximum number of subdomains.
        This parameter defaults to unlimited. (
            * A positive integer between one and 999,999.
            * 0, unlimited, or null — The account has unlimited subdomains.
        )
        :type maxsub: str
        :param maxpark: The hosting plan's maximum number of parked domains.
        This parameter defaults to ``unlimited``. (
            * A positive integer between one and 999,999.
            * 0, unlimited, or null — The account has unlimited parked domains.
        )
        :type maxpark: str
        :param maxaddon: The hosting plan's maximum number of addon domains.
        This parameter defaults to ``unlimited``. (
            * A positive integer between one and 999,999.
            * 0, unlimited, or null — The account has unlimited addon domains.
        )
        :type maxaddon: str
        :param hasshell: Whether the account has shell access.
        This parameter defaults to `False`.
        :type hasshell: bool
        :param bwlimit: The hosting plan's maximum bandwidth use.
        This parameter defaults to ``unlimited``. (
            * A positive integer between one and 999,999 that represents the
            maximum bandwidth use, in Megabytes (MB).
            * 0, unlimited, or null — The account has unlimited bandwidth.
        )
        :type bwlimit: str
        :param MAX_EMAIL_PER_HOUR: The maximum number of emails that the
        account can send in one hour. This parameter defaults to ``unlimited``.(
            * A positive integer.
            * 0 or unlimited — The account can send an unlimited number of emails.
        )
        :type MAX_EMAIL_PER_HOUR: str
        :param MAX_DEFER_FAIL_PERCENTAGE: The percentage of failed or
        deferred email messages that the account can send per hour before
        outgoing mail is rate-limited. (
            * A positive integer.
            * 0 or unlimited — The account can send an unlimited number
            of failed or deferred messages.
        )
        :type MAX_DEFER_FAIL_PERCENTAGE: int
        :param digestauth: Whether to enable Digest Authentication for
        accounts on the hosting plan. This parameter defaults to ``False``.
        :type digestauth: bool
        :param _PACKAGE_EXTENSIONS: The hosting plan's package extensions.
        If you do not provide a value, the hosting plan will not
        include package extensions. A list of one or more
        package extensions on the server.
        :type _PACKAGE_EXTENSIONS: list

        :returns: The new hosting plan's name.
        :rtype: dict
        """
        return self._query_post({
            'name': name,
            'featurelist': featurelist,
            'quota': quota,
            'ip': ip,
            'cgi': cgi,
            'frontpage': frontpage,
            'cpmod': cpmod,
            'language': language,
            'maxftp': maxftp,
            'maxsql': maxsql,
            'maxpop': maxpop,
            'maxlists': maxlists,
            'maxsub': maxsub,
            'maxpark': maxpark,
            'maxaddon': maxaddon,
            'hasshell': hasshell,
            'bwlimit': bwlimit,
            'MAX_EMAIL_PER_HOUR': MAX_EMAIL_PER_HOUR,
            'MAX_DEFER_FAIL_PERCENTAGE': MAX_DEFER_FAIL_PERCENTAGE,
            'digestauth': digestauth,
            '_PACKAGE_EXTENSIONS': '_PACKAGE_EXTENSIONS'
        })

    def createacct(self, username, domain):
        """
        Create Cpanel Account
        Creates a hosting account and sets up its associated domain information.

        https://documentation.cpanel.net/display/SDK/WHM+API+1+Functions+-+createacct

        :type username: str
        :type domain: str

        :rtype: dict
        """
        return self._query_get({
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
        return self._query_get({
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
        return self._query_get({'user': user, 'bwlimit': bwlimit})
