import subprocess

from apixdev.core.exceptions import NoContainerFound
from apixdev.core.settings import vars
from apixdev.core.tools import convert_stdout_to_json


class Stack:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.service_count = 3

    @property
    def is_running(self):
        """Check if every containers running as excepted."""
        services = self._inspect_services()

        if vars.DOCKER_SERVICES_COUNT < len(services):
            return False

        states = map(lambda item: item.get("state", False), services)

        if not all(map(lambda item: bool(item in ["running"]), states)):
            return False

        return True

    def run(self, run_on_background=False):
        """Run docker-compose stack."""
        if run_on_background:
            cmd = vars.DOCKER_COMPOSE_RUN_BACKGROUND
        else:
            cmd = vars.DOCKER_COMPOSE_RUN

        subprocess.call(cmd.split(" "), cwd=self.path)

    def stop(self, clear=False):
        """Stop docker-compose stack."""
        cmd = vars.DOCKER_COMPOSE_DOWN.split(" ")

        if clear:
            cmd.append("-v")

        subprocess.call(cmd, cwd=self.path)

    def clear(self):
        """Stop and clear docker-compose stack."""
        self.stop(True)

    def _convert_container_info(self, vals_list):
        def apply(vals):
            name = vals.get("Name", vals.get("Names", ""))
            return {
                "name": name,
                "state": vals.get("State", ""),
            }

        return list(map(apply, vals_list))

    def _inspect_services(self):
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

    def _get_container_names(self):
        if not self.is_running:
            return []

        services = self._inspect_services()
        return list(map(lambda item: item.get("name", False), services))

    def _get_container_name(self, service):
        names = self._get_container_names()
        container = list(filter(lambda item: service in item, names))

        if not container:
            return False

        return container[0]

    def get_containers(self):
        """Return containers names"""
        return self._get_container_names()

    def get_container(self, service_name):
        """Return container object"""
        container_name = self._get_container_name(service_name)
        if not container_name:
            raise NoContainerFound(service_name)
        return Container(self, service_name, container_name)

    def get_odoo_container(self):
        """Return Odoo specialized container"""
        container_name = self._get_container_name("odoo")
        if not container_name:
            raise NoContainerFound("odoo")
        return OdooContainer(self, container_name)


class Container:
    def __init__(self, stack, service, name):
        self.stack = stack
        self.service = service
        self.name = name

    @property
    def path(self):
        """Path"""
        return self.stack.path

    @property
    def is_running(self):
        """Checks if parent stack is running"""
        return self.stack.is_running

    def logs(self):
        """Show container logs"""
        if not self.is_running:
            return False

        cmd = vars.DOCKER_LOGS.format(self.name).split(" ")
        subprocess.call(cmd, cwd=self.path)

    def bash(self):
        """Attach to container bash"""
        if not self.is_running:
            return False

        cmd = vars.DOCKER_EXEC.format(self.name, "bash").split(" ")
        subprocess.call(cmd, cwd=self.path)


class OdooContainer(Container):
    def __init__(self, stack, name):
        super().__init__(stack, "odoo", name)

    def install_modules(self, database, modules, **kwargs):
        """Install modules list to Odoo database"""
        if not self.is_running:
            return False

        odoo_arg = "-u" if not kwargs.get("install", False) else "-i"
        odoo_cmd = vars.ODOO_MODULES.format(database, odoo_arg, modules)
        cmd = vars.DOCKER_EXEC.format(self.name, odoo_cmd).split()

        subprocess.call(cmd, cwd=self.path)

    def shell(self, database):
        """Attach to Odoo Shell"""
        if not self.is_running:
            return False

        cmd = vars.DOCKER_EXEC.format(
            self.name, vars.ODOO_SHELL.format(database)
        ).split(" ")
        subprocess.call(cmd, cwd=self.path)
