import logging
from pathlib import Path

VERSION = "0.3.2"

HOME_PATH = Path.home()

CONFIG_PATH = ".config/apix"
CONFIG_FILE = "config.ini"

DEFAULT_TIMEOUT = 60
DOCKER_SERVICES_COUNT = 3

LOGGING_FILE = "apix.log"
LOGGING_LEVEL = logging.INFO

DEFAULT_PORT = 443
DEFAULT_PROTOCOL = "jsonrpc+ssl"
DEFAULT_TIMEOUT = 6000
DEFAULT_PASSWORD = "admin"
DEFAULT_NO_VERIFY = False

MANDATORY_VALUES = [
    "apix.database",
    "apix.url",
    "apix.user",
    "apix.password",
    "apix.token",
    "apix.no_verify",
    "local.workdir",
    "local.default_password",
    "git.remote_url",
    "git.remote_login",
    "git.remote_token",
    "docker.repository",
]
IGNORED_VALUES = ["password"]
BACKUP_URL = "{}/web/database/backup"
RESTORE_URL = "{}/web/database/restore"
LOCAL_URL = "http://localhost:8069"
ODOORPC_OPTIONS = [
    "port",
    "protocol",
]

EXTERNAL_DEPENDENCIES = {
    "docker": "docker --version",
    "docker-compose": "docker-compose --version",
}

DOCKER_COMPOSE_RUN_BACKGROUND = "docker-compose up -d"
DOCKER_COMPOSE_RUN = "docker-compose run --rm --service-ports odoo bash"
DOCKER_COMPOSE_DOWN = "docker-compose down"
DOCKER_LOGS = "docker logs -f {}"
DOCKER_EXEC = "docker exec -it {} {}"

ODOO_MODULES = "odoo -d {} --stop-after-init {} {}"
ODOO_SHELL = "odoo shell -d {}"
