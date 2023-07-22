import logging
import os

from git import GitCommandError, Repo

_logger = logging.getLogger(__name__)

REQUIRED_VALUES = ["url", "branch", "path"]


class GitRepository:
    def __init__(self, name, **kwargs):
        self.name = name

        for k, v in kwargs.items():
            self.__dict__[k] = v

    @property
    def _path(self):
        return os.path.join(self.path, self.name)

    def check(self):
        return all([self.__dict__.get(k, False) for k in REQUIRED_VALUES])

    def exists(self):
        return os.path.exists(self._path)

    def clone(self):
        # Repository doesn't exists locally, clone
        if not self.exists():
            if not self.check():
                raise ValueError("Missing parameters.")

            self._repo = Repo.clone_from(
                self.url, self._path, branch=self.branch, progress=None, env=None
            )
        else:
            try:
                _logger.info("Reset end pull repository")
                self._repo = Repo(self._path)
                self._repo.git.reset("--hard")
                self._repo.remotes.origin.pull()
            except GitCommandError as err:
                _logger.error(err)
                raise ValueError(err)
