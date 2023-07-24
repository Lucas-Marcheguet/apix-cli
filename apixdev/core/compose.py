import os

import requests
import yaml

from apixdev.core.tools import dict_merge, nested_set


class Compose:
    _name = "docker-compose.yaml"

    def __init__(self, content, name=None):
        self._content = content

        if name:
            self._name = name

    @classmethod
    def from_path(cls, path):
        name = os.path.basename(path)
        with open(path, mode="rb") as file:
            return cls(yaml.safe_load(file.read()), name)

    def from_content(self, content):
        self._content = yaml.safe_load(content)

    @classmethod
    def from_url(cls, url):
        response = requests.get(url)
        return cls(yaml.safe_load(response.content))

    def get_path(self, path):
        res = os.path.join(path, self._name)
        return res

    def update_dict(self, vals):
        dict_merge(self._content, vals)

    def update(self, chain, value):
        keys = chain.split("/")
        vals = {}

        nested_set(vals, keys, value)
        dict_merge(self._content, vals)

    def save(self, filepath):
        assert self._content, "No content to save."

        with open(filepath, mode="wb") as file:
            yaml.dump(self._content, file, encoding="utf-8")

    def extract(self, chain):
        keys = chain.split("/")

        def dive(vals, keys):
            for key in keys:
                vals = vals.get(key, {})
            return vals

        res = dive(self._content, keys)

        return res
