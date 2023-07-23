import logging
import sys
from pathlib import Path

try:
    from sh import docker as docker
except ImportError:
    print("please install Docker before running this program.")
    docker = None

try:
    from sh import docker_compose as docker_compose
except ImportError:
    print("please install Docker Compose before running this program.")
    docker_compose = None

VERSION = "0.1.0"

HOME_PATH = Path.home()

CONFIG_PATH = ".config/apix"
CONFIG_FILE = "config.ini"

LOGGING_FILE = "apix.log"
LOGGING_LEVEL = logging.INFO

DEFAULT_PORT = 443
DEFAULT_PROTOCOL = "jsonrpc+ssl"
DEFAULT_TIMEOUT = 6000
DEFAULT_PASSWORD = "admin"

MANDATORY_VALUES = [
    "apix.database",
    "apix.url",
    "apix.user",
    "apix.password",
    "apix.token",
    "local.workdir",
    "local.default_password",
    "git.remote_url",
    "git.remote_login",
    "git.remote_token",
    # "scaffold.odoo-template",
    # "scaffold.docker-template",
    "docker.repository",
]
IGNORED_VALUES = ["password"]
BACKUP_URL = "{}/web/database/backup"
RESTORE_URL = "{}/web/database/restore"
LOCAL_URL = "http://localhost:8069"
ODOORPC_OPTIONS = ["port"]

COMPOSE_TEMPLATE_FILE = "docker-compose.yaml"

COMPOSE_TEMPLATE_VALS = {
    "services": {
        "odoo": {
            "image": "apik/odoo-saas:15.0-enterprise",
            "environment": {"CUSTOM_REQUIREMENTS": []},
        }
    }
}

COMMANDS = {
    "start": {
        "args": ["up", "-d"],
        "cmd": docker_compose,
    },
    "stop": {
        "args": ["down"],
        "cmd": docker_compose,
    },
    "clear": {
        "args": ["down", "-v"],
        "cmd": docker_compose,
    },
    "ps": {
        "args": ["ps"],
        "cmd": docker_compose,
        "params": {"_tee": "out", "_out": sys.stdout},
    },
    "ps2": {
        "args": ["compose", "ps", "--format", "json"],
        "cmd": docker,
        "params": {"_tee": "out", "_out": "_buffer"},
    },
    "logs": {
        "args": ["logs", "-f"],
        "cmd": docker,
        "params": {"_tee": "out", "_out": sys.stdout},
    },
    "bash": {
        "args": ["exec", "-it", "bash"],
        "cmd": docker,
        "params": {
            "_fg": True,
        },
    },
    "shell": {
        "args": ["exec", "-it", "bash", "-c"],
        "cmd": docker,
        "params": {
            "_fg": True,
        },
    },
    "odoo_update": {
        "args": ["exec", "-it", "bash", "-c"],
        "cmd": docker,
        "params": {
            "_fg": True,
        },
    },
}
