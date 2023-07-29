import logging
import ssl
import urllib

import odoorpc

from apixdev.core.common import SingletonMeta
from apixdev.core.settings import settings, vars

_logger = logging.getLogger(__name__)


class Odoo(metaclass=SingletonMeta):
    _cr = None
    _url = ""
    _db = ""
    _user = ""
    _password = ""

    def __init__(self, url, dbname, user, password, **kwargs):
        self._url = url
        self._db = dbname
        self._user = user
        self._password = password

        for key, value in kwargs.items():
            self.__dict__[key] = value

        self._cr = self._connect()

    @classmethod
    def new(cls):
        """Return Odoo object with credentials and options."""
        return cls(*settings.odoo_credentials, **settings.odoo_options)

    @property
    def saas_database(self):
        """Return SaaS Database object."""

        return self._cr.env["saas.database"]

    def get_params(self):
        """Return Odoo options."""

        return {k: v for k, v in self.__dict__.items() if k in vars.ODOORPC_OPTIONS}

    def _connect(self):
        options = self.get_params()
        _logger.debug("Odoorpc %s with %s", self._url, options)

        # urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate
        # FIXME: definitely not the best solution...
        if settings.no_verify:
            myssl = ssl.create_default_context()
            myssl.check_hostname = False
            myssl.verify_mode = ssl.CERT_NONE

            opener_selfsigned = urllib.request.build_opener(
                urllib.request.HTTPSHandler(context=myssl)
            )
            options["opener"] = opener_selfsigned

        obj = odoorpc.ODOO(self._url, **options)

        try:
            obj.login(self._db, self._user, self._password)
        except odoorpc.error.RPCError as error:
            _logger.error(error)
            obj = None

        return obj

    def get_databases(self, name, **kwargs):
        """Search on ApiX databases."""

        strict = kwargs.get("strict", True)
        options = {k: v for k, v in kwargs.items() if k in ["limit"]}

        operator = "=" if strict else "ilike"
        domain = [("name", operator, name)]
        ids = self.saas_database.search(domain, **options)

        if ids:
            return self.saas_database.browse(ids)
        return False

    def get_database_by_uuid(self, uuid):
        """Get database object by UUID."""

        domain = [("uuid", "=", uuid)]
        ids = self.saas_database.search(domain, limit=1)
        if ids:
            return self.saas_database.browse(ids)
        return False

    def get_last_backup_url(self, uuid):
        """Get last backup url from ApiX database."""

        database = self.get_database_by_uuid(uuid)

        if not database:
            return False

        action = database.action_get_last_backup()

        return action.get("url", False)
