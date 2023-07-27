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

    def __init__(self, url, db, user, password, **kwargs):
        self._url = url
        self._db = db
        self._user = user
        self._password = password

        for k, v in kwargs.items():
            self.__dict__[k] = v

        self._cr = self._connect()

    @classmethod
    def new(cls):
        return cls(*settings.odoo_credentials, **settings.odoo_options)

    def get_params(self):
        return {k: v for k, v in self.__dict__.items() if k in vars.ODOORPC_OPTIONS}

    def _connect(self):
        options = self.get_params()
        _logger.info("Odoorpc %s with %s", self._url, options)

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
        except odoorpc.error.RPCError as e:
            _logger.error(e)
            obj = None

        return obj

    @property
    def databases(self):
        return self._cr.env["saas.database"]

    def get_databases(self, name, **kwargs):
        Databases = self._cr.env["saas.database"]

        strict = kwargs.get("strict", True)
        options = {k: v for k, v in kwargs.items() if k in ["limit"]}

        operator = "=" if strict else "ilike"
        domain = [("name", operator, name)]
        ids = Databases.search(domain, **options)

        if ids:
            return Databases.browse(ids)
        return False

    def get_database_from_uuid(self, uuid):
        Databases = self._cr.env["saas.database"]
        domain = [("uuid", "=", uuid)]
        id = Databases.search(domain, limit=1)
        if id:
            return Databases.browse(id)
        return False

    def get_last_backup_url(self, uuid):
        database = self._cr.env["saas.database"].search([("uuid", "=", uuid)], limit=1)

        if not database:
            return False

        return database.action_get_last_backup().res["url"]
