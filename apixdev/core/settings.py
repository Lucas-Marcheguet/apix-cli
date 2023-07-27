import configparser
import getpass
import logging
import os
import subprocess

import apixdev.vars as vars
from apixdev.core.exceptions import ExternalDependenciesMissing

config_dir = os.path.join(vars.HOME_PATH, vars.CONFIG_PATH)
filename = os.path.join(config_dir, vars.LOGGING_FILE)

if not os.path.isdir(config_dir):
    os.makedirs(config_dir)

logging.basicConfig(filename=filename, level=vars.LOGGING_LEVEL)

_logger = logging.getLogger(__name__)

from apixdev.core.common import SingletonMeta  # noqa: E402


def check_system_dependencies(cmd):
    try:
        res = subprocess.check_output(cmd.split(" "))
        res = res.decode("utf8").strip()
    except FileNotFoundError:
        return False

    return res


class Settings(metaclass=SingletonMeta):
    def __init__(self, path, name="config.ini"):
        self._path = path
        self._name = name
        self._config = None

        self.docker_version = None
        self.docker_compose_version = None

        self._load()

    def check(self, raise_if_not_found=True):
        for name, cmd in vars.EXTERNAL_DEPENDENCIES.items():
            res = check_system_dependencies(cmd)
            if not res and raise_if_not_found:
                raise ExternalDependenciesMissing(name)
            _logger.error("Check failed: %s not found.", name)

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
            _logger.info("Load configuration from %s.", self.filepath)
            self._config.read(self.filepath)

    def logout(self):
        values = self._config["apix"]
        self._config["apix"] = {
            k: v for k, v in values.items() if k not in vars.MANDATORY_VALUES
        }
        self.save()

    def reload(self):
        self._config = None
        self._load()

    def save(self):
        _logger.info("Save configuration to %s.", self.filepath)

        with open(self.filepath, "w") as configfile:
            self._config.write(configfile)

    def _get_default_values(self):
        return {
            "apix.port": vars.DEFAULT_PORT,
            "apix.protocol": vars.DEFAULT_PROTOCOL,
            "apix.timeout": vars.DEFAULT_TIMEOUT,
            "apix.no_verify": vars.DEFAULT_NO_VERIFY,
            "local.default_password": vars.DEFAULT_PASSWORD,
        }

    def _prepare_config(self):
        return {
            "apix.url": "",
            "apix.port": "",
            "apix.protocol": "",
            "apix.timeout": "",
            "apix.no_verify": "",
            "apix.database": "",
            "apix.user": "",
            "apix.password": "",
        }

    def split_var(self, key, separator="."):
        section, key = key.split(separator)
        return section, key

    def _add_separator(self, items, separator="."):
        return separator.join(items)

    def merge_sections(self, vals):
        # [section][key] ==> [section.key]
        _logger.info("merge sections (before): %s", vals)
        tmp = dict()
        for section in vals.keys():
            tmp.update({self._add_separator([section, k]): v for k, v in vals[section]})

        _logger.info("merge sections: %s", tmp)
        return tmp

        # {self._add_dot(section, k):v for k,v in vals[section].items()}

    def unmerge_sections(self, vals):
        # [section.key] ==> [section][key]
        tmp = dict()
        for k, v in vals.items():
            section, key = self.split_var(k)
            curr = tmp.setdefault(section, dict())
            curr[key] = v

        _logger.info("unmerge_sections: %s", tmp)
        return tmp

    def set_vars(self, vals):
        _logger.info("set vars: %s", vals)
        vals = self.unmerge_sections(vals)
        self._config.read_dict(vals)

        self.save()

    def get_vars(self):
        return {section: self._config[section].items() for section in self._config}

    def get_var(self, name):
        section, key = self.split_var(name)
        return self._config.get(section, key)

    def get_boolean(self, name, default=False):
        section, key = self.split_var(name)
        return self._config.getboolean(section, key) or default

    def get_missing_values(self):
        _logger.error("missing values")

        missing_values = dict()

        vals = self.get_vars()
        vals = self.merge_sections(vals)

        missing_values = {
            k: ""
            for k in vars.MANDATORY_VALUES
            if k not in vals or not vals.get(k, False)
        }

        return missing_values.items()

    @property
    def odoo_credentials(self):
        return [
            self.get_var("apix.url"),
            self.get_var("apix.database"),
            self.get_var("apix.user"),
            self.get_var("apix.password"),
        ]

    @property
    def odoo_options(self):
        return {k: self.get_var("apix.%s" % k) for k in vars.ODOORPC_OPTIONS}

    def set_config(self):
        while not self.is_ready:
            vals = dict()
            for key, _ in self.get_missing_values():
                if "password" in key:
                    vals[key] = getpass.getpass(f"{key.capitalize()}: ")
                else:
                    vals[key] = input(f"{key.capitalize()}: ")
            self.set_vars(vals)

    @property
    def is_ready(self):
        return True if len(self.get_missing_values()) == 0 else False

    @property
    def workdir(self):
        return self.get_var("local.workdir")

    @property
    def env_file(self):
        return os.path.join(self._path, ".env")

    @property
    def no_verify(self):
        return self.get_boolean("apix.no_verify", False)


settings = Settings(config_dir)
