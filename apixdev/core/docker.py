class Stack:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.service_count = 3

    @property
    def is_running(self):
        return True

    def run(self):
        pass

    def stop(self):
        pass

    def clear(self):
        pass

    def _convert_container_info(self, data):
        pass

    def _inspect_services(self):
        pass

    def _get_container_names(self):
        pass

    def _get_container(self, service):
        pass


class Container:
    def __init__(self, stack, path, service):
        pass

    def logs(self):
        pass

    def bash(self):
        pass


class OdooService(Container):
    def __init__(self, stack, path):
        self.service = "odoo"

    def install_modules(self):
        pass

    def shell(self):
        pass
