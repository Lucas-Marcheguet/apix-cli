from curses import meta
import logging
import configparser
import os
import odoorpc

import apixdev.config as cfg

_logger = logging.getLogger(__name__)



class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Config(object):

    def __init__(self, path, name='config.ini'):
        self._path = path
        self._name = name
        self._config = None
        
        self._load()


    @property
    def filepath(self):
        return os.path.join(self._path, self._name)

    
    def _load(self):
        self._config = configparser.ConfigParser()
        if not os.path.isdir(self._path):
            os.makedirs(self._path) 

        if not os.path.isfile(self.filepath):
            _logger.info("New configuration file.")

            vals = self._prepare_config()
            vals.update(self._get_default_values())

            self.set_vars(vals)
            
        else:
            _logger.info("Load configuration from {}.".format(self.filepath))
            self._config.read(self.filepath)


    def logout(self):
        values = self._config['apix']
        self._config['apix'] = {k:v for k,v in values.items() if k not in cfg.MANDATORY_VALUES}
        self.save()        


    def reload(self):
        self._config = None
        self._load()


    def save(self):
        _logger.info('Save configuration to {}.'.format(self.filepath))

        with open(self.filepath, 'w') as configfile:
            self._config.write(configfile)        


    def _get_default_values(self):
        return {
            'apix.port': cfg.DEFAULT_PORT,
            'apix.protocol': cfg.DEFAULT_PROTOCOL, 
            'apix.timeout': cfg.DEFAULT_TIMEOUT, 
            'local.default_password': cfg.DEFAULT_PASSWORD,  
        }

    
    def _prepare_config(self):
        return {
            'apix.url': '', 
            'apix.port': '', 
            'apix.protocol': '', 
            'apix.timeout': '', 
            'apix.database': '',
            'apix.user': '', 
            'apix.password': '',  
        }


    def split_var(self, key, separator="."):
        section, key = key.split(separator)
        return section, key

    
    def _add_separator(self, items, separator="."):
        return separator.join(items)


    def merge_sections(self, vals):
        # [section][key] ==> [section.key]
        _logger.info("merge sections (before): {}".format(vals))
        tmp = dict()
        for section in vals.keys():
            tmp.update({self._add_separator([section, k]):v for k,v in vals[section]})
        
        _logger.info("merge sections: {}".format(tmp))
        return tmp

        # {self._add_dot(section, k):v for k,v in vals[section].items()}


    def unmerge_sections(self, vals):
        # [section.key] ==> [section][key]
        tmp = dict()
        for k,v in vals.items():
            section, key = self.split_var(k)
            curr = tmp.setdefault(section, dict())
            curr[key] = v
        
        _logger.info("unmerge_sections: {}".format(tmp))
        return tmp


    def set_vars(self, vals):
        _logger.info("set vars: {}".format(vals))
        vals = self.unmerge_sections(vals)
        self._config.read_dict(vals)

        self.save()


    # def __getattr__(self, __name):
    #     return self._config.get('apix', __name)


    def get_vars(self):
        return {section:self._config[section].items() for section in self._config}

    def get_var(self, name):
        section, key = self.split_var(name)
        return self._config.get(section, key)



    # def get_vars(self, section, keys):
    #     return dict(filter(lambda item: item[0] in keys, self._config[section].items()))


    # def get_vars(self, section, keys):
    #     return dict(filter(lambda item: item[0] in keys, self._config[section].items()))


    # def get_vars(self):
    #     vals = dict()
    #     sections = ['apix']

    #     for section in sections:
    #         vals.update({"{}.{}".format(section,k):v for k,v in self._config[section].items() if k not in cfg.IGNORED_VALUES})

    #     return vals


    def get_missing_values(self):
        _logger.error('missing values')

        missing_values = dict()
        
        vals = self.get_vars()
        vals = self.merge_sections(vals)

        missing_values = {k:'' for k in cfg.MANDATORY_VALUES if k not in vals or not vals.get(k, False)}

        return missing_values.items()


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

        for k,v in kwargs.items():
            self.__dict__[k] = v

        self._cr = self._connect()


    @property
    def params(self):
        return {k:v for k,v in self.__dict__.items() if k in cfg.ODOORPC_OPTIONS}


    def _connect(self):
        _logger.info("Odoorpc {} with {}".format(self._url, self.params))
        obj = odoorpc.ODOO(self._url, **self.params)
        
        try:
            obj.login(self._db, self._user, self._password)
        except odoorpc.error.RPCError as e:
            _logger.error(e)
            obj = None

        return obj


    @property
    def databases(self):
        return self._cr.env['saas.database']

    
    # def list_of(self, records, fields):
    #     return [record for record in records]


    def get_databases(self, name, **kwargs):
        Databases = self._cr.env['saas.database']

        strict = kwargs.get('strict', True)
        options = {k:v for k,v in kwargs.items() if k in ['limit']}

        operator = '=' if strict else 'ilike'
        domain = [('name', operator, name)]
        ids = Databases.search(domain, **options)

        if ids:
            return Databases.browse(ids)
        return False