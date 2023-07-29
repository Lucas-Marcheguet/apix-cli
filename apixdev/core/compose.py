import logging
import os

import requests
import yaml

from apixdev.core.tools import dict_merge, nested_set

_logger = logging.getLogger(__name__)


class Compose:
    _name = "docker-compose.yaml"

    def __init__(self, content, name=None):
        self._content = content

        if name:
            self._name = name

    @classmethod
    def from_path(cls, path):
        """Return Compose object from path."""

        name = os.path.basename(path)
        with open(path, mode="rb") as file:
            return cls(yaml.safe_load(file.read()), name)

    @classmethod
    def from_string(cls, content):
        """Return Compose object from YAML string."""

        content = yaml.safe_load(content)
        return cls(yaml.safe_load(content))

    @classmethod
    def from_url(cls, url):
        """Return Compose object from url."""

        response = requests.get(url, timeout=60)
        name = os.path.basename(url)

        return cls(yaml.safe_load(response.content), name)

    def get_path(self, path):
        "Return complete filepath."

        res = os.path.join(path, self._name)
        return res

    def update_dict(self, vals):
        """Merge values with content."""

        dict_merge(self._content, vals)

    def update(self, chain, value):
        """Update from chain and value."""

        keys = chain.split("/")
        vals = {}

        nested_set(vals, keys, value)
        dict_merge(self._content, vals)

    def save(self, filepath):
        """Save compose object to filepath."""

        assert self._content, "No content to save."

        if os.path.exists(filepath):
            _logger.debug("Remove '%s'", filepath)
            os.remove(filepath)

        with open(filepath, mode="wb") as file:
            yaml.dump(self._content, file, encoding="utf-8")

    def extract(self, chain):
        """Extract values from chain."""

        keys = chain.split("/")

        def dive(vals, keys):
            for key in keys:
                vals = vals.get(key, {})
            return vals

        res = dive(self._content, keys)

        return res
