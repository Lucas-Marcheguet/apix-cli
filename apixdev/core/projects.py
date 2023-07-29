import os

from apixdev.core.project import Project
from apixdev.core.settings import settings


class Projects:
    def __init__(self, path):
        self.path = path

    @classmethod
    def from_path(cls, path=None):
        """Return Projects object from path."""
        if not path:
            path = settings.workdir
        instance = cls(path)
        return instance.get_all()

    def get_all(self):
        """Return all projects find in workdir path."""
        projects = list(map(Project, os.listdir(self.path)))
        projects = list(filter(lambda project: project.is_ready, projects))

        return projects
