import configparser
import getpass
import logging
import os

import apixdev.vars as vars
from apixdev.core.exceptions import ExternalDependenciesMissing
from apixdev.core.tools import (
    merge_sections,
    run_external_command,
    split_var,
    unmerge_sections,
)

config_dir = os.path.join(vars.HOME_PATH, vars.CONFIG_PATH)

if not os.path.isdir(config_dir):
    os.makedirs(config_dir)

logging.basicConfig(level=vars.LOGGING_LEVEL)

_logger = logging.getLogger(__name__)

from apixdev.core.common import SingletonMeta  # noqa: E402, pylint: disable=C0413


class Settings(metaclass=SingletonMeta):
    def __init__(self, path, name="config.ini"):
        self._path = path
        self._name = name
        self._config = None

        self.docker_version = None
        self.docker_compose_version = None

        self._load()

    @property
    def filepath(self):
        """Configuration filepath."""
        return os.path.join(self._path, self._name)

    @property
    def odoo_credentials(self):
        """Odoo credentials property."""
        return [
            self.get_var("apix.url"),
            self.get_var("apix.database"),
            self.get_var("apix.user"),
            self.get_var("apix.password"),
        ]

    @property
    def odoo_options(self):
        """Odoo options property."""
        return {key: self.get_var(f"apix.{key}") for key in vars.ODOORPC_OPTIONS}

    @property
    def is_ready(self):
        """IS Ready property."""
        return bool(len(self._get_missing_values()) == 0)

    @property
    def workdir(self):
        """Workdir path property."""
        return self.get_var("local.workdir")

    @property
    def env_file(self):
        """ENV file property."""
        return os.path.join(self._path, ".env")

    @property
    def no_verify(self):
        """No verify property."""
        return self.get_boolean("apix.no_verify", False)

    def _get_default_values(self):  # pylint: disable=R0201
        return {
            "apix.port": vars.DEFAULT_PORT,
            "apix.protocol": vars.DEFAULT_PROTOCOL,
            "apix.timeout": vars.DEFAULT_TIMEOUT,
            "apix.no_verify": vars.DEFAULT_NO_VERIFY,
            "local.default_password": vars.DEFAULT_PASSWORD,
        }

    def _prepare_config(self):  # pylint: disable=R0201
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

    def _load(self):
        self._config = configparser.ConfigParser()
        if not os.path.isdir(self._path):
            os.makedirs(self._path)

        if not os.path.isfile(self.filepath):
            _logger.debug("New configuration file.")

            vals = self._prepare_config()
            vals.update(self._get_default_values())

            self.set_vars(vals)

        else:
            _logger.debug("Load configuration from %s.", self.filepath)
            self._config.read(self.filepath)

    def set_vars(self, vals):
        """Set values."""
        _logger.debug("set vars: %s", vals)
        vals = unmerge_sections(vals)
        self._config.read_dict(vals)

        self.save()

    def get_vars(self):
        """Return values."""
        return {section: self._config[section].items() for section in self._config}

    def get_var(self, name):
        """Return value."""
        section, key = split_var(name)
        return self._config.get(section, key)

    def get_boolean(self, name, default=False):
        """Return boolean value."""
        section, key = split_var(name)
        return self._config.getboolean(section, key) or default

    def _get_missing_values(self):
        _logger.debug("missing values")

        missing_values = {}

        vals = self.get_vars()
        vals = merge_sections(vals)

        missing_values = {
            k: ""
            for k in vars.MANDATORY_VALUES
            if k not in vals or not vals.get(k, False)
        }

        return missing_values.items()

    def reload(self):
        """Reload configuration from file."""
        self._config = None
        self._load()

    def save(self):
        """Save current configuration to file."""
        _logger.debug("Save configuration to %s.", self.filepath)

        with open(self.filepath, "w", encoding="utf8") as configfile:
            self._config.write(configfile)

    def check(self, raise_if_not_found=True):  # pylint: disable=R0201
        """Check external dependencies."""
        for name, cmd in vars.EXTERNAL_DEPENDENCIES.items():
            res = run_external_command(cmd)
            if not res and raise_if_not_found:
                raise ExternalDependenciesMissing(name)
            _logger.error("Check external dependencies failed: %s not found.", name)

    def set_config(self):
        """Prepare configuration and ask user to complete if necessary."""
        while not self.is_ready:
            vals = {}
            for key, _ in self._get_missing_values():
                if "password" in key:
                    vals[key] = getpass.getpass(f"{key.capitalize()}: ")
                else:
                    vals[key] = input(f"{key.capitalize()}: ")
            self.set_vars(vals)

    # def logout(self):
    #     values = self._config["apix"]
    #     self._config["apix"] = {
    #         k: v for k, v in values.items() if k not in vars.MANDATORY_VALUES
    #     }
    #     self.save()


settings = Settings(config_dir)
