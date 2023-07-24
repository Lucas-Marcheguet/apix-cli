import logging
from pathlib import Path

try:
    from sh import docker
except ImportError:
    print("Please install Docker before running this program.")
    docker = None

try:
    from sh import docker_compose
except ImportError:
    print("Please install Docker Compose before running this program.")
    docker_compose = None

VERSION = "0.1.0"

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
