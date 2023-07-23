import os
import subprocess
from shutil import rmtree

import requests
from requests.exceptions import HTTPError

from apixdev.core.compose import Compose
from apixdev.core.settings import Settings
from apixdev.core.tools import (
    filter_requirements,
    get_requirements_from_path,
    list_to_text,
    text_to_list,
)

settings = Settings()


class Project:
    def __init__(self, name, path=None):
        self.root_path = settings.workdir
        self.path = path or os.path.join(self.root_path, name)
        self.name = name

        os.makedirs(self.path, exist_ok=True)

    def __repr__(self) -> str:
        return f"Project({self.name})"

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_path(cls, path):
        name = os.path.basename(path)
        instance = cls(name, path)

        return instance

    @property
    def compose_file(self):
        return os.path.join(self.path, "docker-compose.yaml")

    @property
    def repositories_file(self):
        return os.path.join(self.path, "repositories.yaml")

    @property
    def manifest_file(self):
        return os.path.join(self.path, "manifest.yaml")

    @property
    def env_file(self):
        return os.path.join(self.path, ".env")

    @property
    def repositories_path(self):
        return os.path.join(self.path, "repositories")

    @property
    def is_ready(self):
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
            print("remove %s" % filepath)
            os.remove(filepath)

        try:
            response = requests.get(url, headers=headers, allow_redirects=False)
            response.raise_for_status()
        except HTTPError as error:
            code = error.response.status_code
            raise Exception(
                f"Error while trying to download {filename} from {url} (HTTP {code})."
            )

        with open(filepath, "wb") as file:
            file.write(response.content)

        return True

    def pull_repositories(self):
        if not self.repositories_file:
            return False

        env_file = self.env_file if os.path.exists(self.env_file) else settings.env_file

        # gitaggregate(f"-c {self.repositories_file}", _cwd=self.path)
        # gitaggregate(
        #     [
        #         "-c",
        #         "repositories.yaml",
        #         "--expand-env",
        #         "--env-file",
        #         settings.env_file,
        #     ],
        #     _cwd=self.path,
        #     _in=sys.stdin,
        #     _out=sys.stdout,
        # )

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

        print(self.uuid)

        keys = [
            (self.compose_file, "docker_compose_url"),
            (self.repositories_file, "repositories_url"),
        ]

        for filename, key in keys:
            url = manifest.extract(key)
            self.download(filename, url, True)

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
