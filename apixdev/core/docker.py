import subprocess

from apixdev.core.exceptions import NoContainerFound
from apixdev.core.settings import vars
from apixdev.core.tools import convert_stdout_to_json

DOCKER_COMPOSE_RUN_BACKGROUND = "docker-compose up -d"
DOCKER_COMPOSE_RUN = "docker-compose run --rm --service-ports odoo bash"
DOCKER_COMPOSE_DOWN = "docker-compose down"
DOCKER_LOGS = "docker logs -f {}"
DOCKER_EXEC = "docker exec -it {} {}"

ODOO_MODULES = "odoo -d {} --stop-after-init {} {}"
ODOO_SHELL = "odoo shell -d {}"


class Stack:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.service_count = 3

    @property
    def is_running(self):
        services = self._inspect_services()

        if vars.DOCKER_SERVICES_COUNT < len(services):
            return False

        states = map(lambda item: item.get("state", False), services)

        if not all(map(lambda item: bool(item in ["running"]), states)):
            return False

        return True

    def run(self, run_on_background=False):
        if run_on_background:
            cmd = DOCKER_COMPOSE_RUN_BACKGROUND
        else:
            cmd = DOCKER_COMPOSE_RUN

        subprocess.call(cmd.split(" "), cwd=self.path)

    def stop(self, clear=False):
        cmd = DOCKER_COMPOSE_DOWN.split(" ")

        if clear:
            cmd.append("-v")

        subprocess.call(cmd, cwd=self.path)

    def clear(self):
        self.stop(True)

    # def ps(self):
    #     print(self.is_running)
    #     print(self._get_container_names())

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
        return self._get_container_names()

    def get_container(self, service_name):
        container_name = self._get_container_name(service_name)
        if not container_name:
            raise NoContainerFound(service_name)
        return Container(self, service_name, container_name)

    def get_odoo_container(self):
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
        return self.stack.path

    @property
    def is_running(self):
        return self.stack.is_running

    def logs(self):
        if not self.is_running:
            return False

        cmd = DOCKER_LOGS.format(self.name).split(" ")
        subprocess.call(cmd, cwd=self.path)

    def bash(self):
        if not self.is_running:
            return False

        cmd = DOCKER_EXEC.format(self.name, "bash").split(" ")
        subprocess.call(cmd, cwd=self.path)


class OdooContainer(Container):
    def __init__(self, stack, name):
        super().__init__(stack, "odoo", name)

    def install_modules(self, database, modules, **kwargs):
        if not self.is_running:
            return False

        odoo_arg = "-u" if not kwargs.get("install", False) else "-i"
        odoo_cmd = ODOO_MODULES.format(database, odoo_arg, modules)
        cmd = DOCKER_EXEC.format(self.name, odoo_cmd).split()

        subprocess.call(cmd, cwd=self.path)

    def shell(self, database):
        if not self.is_running:
            return False

        cmd = DOCKER_EXEC.format(self.name, ODOO_SHELL.format(database)).split(" ")
        subprocess.call(cmd, cwd=self.path)
