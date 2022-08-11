import os
import requests
import yaml

from apixdev.common import SingletonMeta
from apixdev.cli.tools import dict_merge

class Commpose(object):

    _name = 'docker-compose.yaml'

    def __init__(self):
        pass


    def from_path(self, path):
        with open(path, mode="rb") as file:
            self._content = yaml.safe_load(path, encoding="utf-8")        

    
    def from_content(self, content):
        self._content = yaml.safe_load(content)


    def from_url(self, url):
        response = requests.get(url)
        self._content = yaml.safe_load(response.content)


    def get_path(self, path):
        return os.path.join(path, self._name)


    def update(self, vals):
        dict_merge(self._content, vals)


    def save(self, path=None):
        assert self._content, "No content to save."

        with open(self.get_path(path), mode="wb") as file:
            yaml.dump(self._content, file, encoding="utf-8")