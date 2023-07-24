import logging
import os
import subprocess
from shutil import rmtree

import requests
from requests.exceptions import HTTPError

from apixdev.core.compose import Compose
from apixdev.core.exceptions import DownloadError, NoContainerFound
from apixdev.core.settings import settings, vars
from apixdev.core.tools import (
    convert_stdout_to_json,
    filter_requirements,
    get_requirements_from_path,
    list_to_text,
    text_to_list,
)

_logger = logging.getLogger(__name__)


class Project:
    def __init__(self, name, path=None):
        self.root_path = settings.workdir
        self.path = path or os.path.join(self.root_path, name)
        self.name = name
        self.uuid = None

        os.makedirs(self.path, exist_ok=True)

    def __repr__(self) -> str:
        return f"Project({self.name})"

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_path(cls, path):
        """Load project from path"""
        name = os.path.basename(path)
        instance = cls(name, path)

        return instance

    @property
    def compose_file(self):
        """Complete filepath to docker-compose.yaml"""
        return os.path.join(self.path, "docker-compose.yaml")

    @property
    def repositories_file(self):
        """Complete filepath to repositories.yaml"""
        return os.path.join(self.path, "repositories.yaml")

    @property
    def manifest_file(self):
        """Complete filepath to manifest.yaml"""
        return os.path.join(self.path, "manifest.yaml")

    @property
    def env_file(self):
        """Complete filepath to .env file"""
        return os.path.join(self.path, ".env")

    @property
    def repositories_path(self):
        """Complete path to repositories"""
        return os.path.join(self.path, "repositories")

    @property
    def is_ready(self):
        """A project is considered ready if all 3 manifests are present"""
        files = [
            self.compose_file,
            self.repositories_file,
            self.manifest_file,
        ]
        return bool(all(map(os.path.exists, files)))

    def download(self, filename, url, force=False):
        filepath = os.path.join(self.path, filename)
        headers = {
            "X-Api-Token": settings.get_var("apix.token"),
        }

        if force and os.path.exists(filepath):
            _logger.info("Remove %s file", filepath)
            os.remove(filepath)

        try:
            response = requests.get(
                url,
                headers=headers,
                allow_redirects=False,
                timeout=vars.DEFAULT_TIMEOUT,
            )
            response.raise_for_status()
        except HTTPError as error:
            code = error.response.status_code
            raise DownloadError(filename, url, code) from error

        with open(filepath, "wb") as file:
            file.write(response.content)

        return True

    def pull_repositories(self):
        """Recursively pull code repositories"""
        if not self.repositories_file:
            return False

        env_file = self.env_file if os.path.exists(self.env_file) else settings.env_file

        args = [
            "gitaggregate",
            "-c",
            "repositories.yaml",
            "--expand-env",
            "--env-file",
            env_file,
        ]
        subprocess.call(args, cwd=self.path)

    def merge_requirements(self):
        compose = Compose.from_path(self.compose_file)

        requirements = get_requirements_from_path(self.repositories_path)
        requirements += text_to_list(
            compose.extract("services/odoo/environment/CUSTOM_REQUIREMENTS")
        )
        requirements = filter_requirements(requirements)

        text = list_to_text(requirements)
        compose.update("services/odoo/environment/CUSTOM_REQUIREMENTS", text)
        compose.save(self.compose_file)

    def load_manifest(self):
        manifest = Compose.from_path(self.manifest_file)
        self.uuid = manifest.extract("uuid")

        keys = [
            (self.compose_file, "docker_compose_url"),
            (self.repositories_file, "repositories_url"),
        ]

        for filename, key in keys:
            url = manifest.extract(key)
            self.download(filename, url, True)

    def run(self, **kwargs):
        detach = kwargs.get("detach", False)

        if detach:
            cmd = [
                "docker-compose",
                "up",
                "-d",
            ]
        else:
            cmd = [
                "docker-compose",
                "run",
                "--rm",
                "--service-ports",
                "odoo",
                "bash",
            ]

        subprocess.call(cmd, cwd=self.path)

    def down(self, clear=False):
        cmd = [
            "docker-compose",
            "down",
        ]

        if clear:
            cmd.append("-v")

        subprocess.call(cmd, cwd=self.path)

    def clear(self):
        return self.down(True)

    def _convert_container_info(self, vals_list):
        def apply(vals):
            name = vals.get("Name", vals.get("Names", ""))
            return {
                "name": name,
                "state": vals.get("State", ""),
            }

        return list(map(apply, vals_list))

    def _get_docker_services(self):
        # Method 1 : docker compose ps
        cmd = ["docker", "compose", "ps", "--format", "json"]
        res = subprocess.check_output(cmd, cwd=self.path)
        data = convert_stdout_to_json(res)

        if len(data) == vars.DOCKER_SERVICES_COUNT:
            return self._convert_container_info(data)

        # When the stack is not running in background,
        # the odoo container does not appear with the first ps command

        # Method 2 : docker ps + filtering on project name
        cmd = ["docker", "ps", "--format", "json"]
        res = subprocess.check_output(cmd, cwd=self.path)
        data = convert_stdout_to_json(res)

        data = list(
            filter(lambda item: item.get("Names", "").startswith(self.name), data)
        )

        return self._convert_container_info(data)

    @property
    def is_running(self):
        services = self._get_docker_services()

        if vars.DOCKER_SERVICES_COUNT < len(services):
            return False

        states = map(lambda item: item.get("state", False), services)

        if not all(map(lambda item: bool(item in ["running"]), states)):
            return False

        return True

    def _get_container_names(self):
        if not self.is_running:
            return []

        services = self._get_docker_services()
        return list(map(lambda item: item.get("name", False), services))

    def _get_container(self, service):
        names = self._get_container_names()
        container = list(filter(lambda item: service in item, names))

        if not container:
            return False

        return container[0]

    def ps(self):
        print(self.is_running)
        print(self._get_container_names())

    def logs(self, service="odoo"):
        if not self.is_running:
            return False

        container = self._get_container(service)
        cmd = ["docker", "logs", "-f", container]

        subprocess.call(cmd, cwd=self.path)

    def bash(self, service="odoo"):
        if not self.is_running:
            return False

        container = self._get_container(service)
        cmd = ["docker", "exec", "-it", container, "bash"]

        subprocess.call(cmd, cwd=self.path)

    def shell(self, database):
        if not self.is_running:
            return False

        odoo_cmd = ["odoo", "shell", "-d", database]
        container = self._get_container("odoo")
        cmd = ["docker", "exec", "-it", container] + odoo_cmd

        subprocess.call(cmd, cwd=self.path)

    def update_modules(self, database, modules, **kwargs):
        if not self.is_running:
            return False

        container = self._get_container("odoo")
        if not container:
            raise NoContainerFound("odoo")

        arg = "-u" if not kwargs.get("install", False) else "-i"
        odoo_cmd = ["odoo", "-d", database, "--stop-after-init", arg, modules]

        cmd = ["docker", "exec", "-it", container] + odoo_cmd

        subprocess.call(cmd, cwd=self.path)

    # def __del__(self):
    #     rmtree(self.path, ignore_errors=True)
    #     self.root_path = None
    #     self.path = None
    #     self.name = None

    def delete(self):
        rmtree(self.path, ignore_errors=True)
        self.root_path = None
        self.path = None
        self.name = None
