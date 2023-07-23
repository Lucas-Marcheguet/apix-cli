import logging
import os

from apixdev.cli.tools import dict_to_string
from apixdev.core.common import SingletonMeta
from apixdev.core.settings import vars

_logger = logging.getLogger(__name__)


class Docker(metaclass=SingletonMeta):
    _odoo = None
    _path = ""

    def __init__(self):
        pass

    def get_odoo_instance(self, name):
        return "{}_odoo_1".format(name)

    def _exec_cmd(self, action, ctx):
        cmd_name = "_cmd_{}".format(action)
        cmd, args, options = self._get_default_cmd(action)
        custom_command = getattr(self, cmd_name, False)

        # run custom command if exists
        if custom_command:
            cmd, args, options = custom_command(cmd, args, options, **ctx)

        options.update({"_cwd": ctx["project_path"]})

        _logger.info(
            "Action {} on project {}\n\tOptions: {}.".format(
                action, ctx["project_name"], dict_to_string(options)
            )
        )

        cmd(*args, **options)

    # default cmd, e.g. start / clear / ps
    def _get_default_cmd(self, name):
        values = vars.COMMANDS.get(name)
        if not values:
            raise NotImplementedError("Command {} not implemented.".format(name))

        return values["cmd"], values.get("args", []), values.get("params", {})

    def _cmd_stop(self, cmd, args, options, **ctx):
        """Custom stop command"""
        if ctx.get("clear"):
            args.append("-v")

        return cmd, args, options

    def _cmd_logs(self, cmd, args, options, **ctx):
        """Custom logs command"""
        args.append(self.get_odoo_instance(ctx["project_name"]))

        return cmd, args, options

    def _cmd_bash(self, cmd, args, options, **ctx):
        """Custom bash command"""
        args.insert(2, self.get_odoo_instance(ctx["project_name"]))

        return cmd, args, options

    def _cmd_shell(self, cmd, args, options, **ctx):
        """Custom bash command"""
        args.insert(2, self.get_odoo_instance(ctx["project_name"]))
        args.append('"odoo shell -d {} --no-http"'.format(ctx["project_name"]))

        return cmd, args, options

    def _cmd_odoo_update(self, cmd, args, options, **ctx):
        """Custom bash command"""
        args.insert(2, self.get_odoo_instance(ctx["project_name"]))
        args.append(
            '"odoo -d {o[project_name]} -u {o[module]} --stop-after-init --no-http"'.format(
                o=ctx
            )
        )

        return cmd, args, options

    def _cmd_cloc(self, cmd, args, options, **ctx):
        """Custom cloc command"""
        repo_path = self.get_repo_path(ctx["project_name"])
        extra_path = options.get("path", False)
        if extra_path:
            args = (
                [extra_path]
                if os.path.exists(extra_path)
                else [os.path.join(repo_path, extra_path)]
            )
        else:
            args = [repo_path]

        return cmd, args, options

    def project_cmd(self, name, action, **kwargs):
        """Run command for project"""
        if name not in self.get_local_projects():
            raise ValueError("Project not found")

        ctx = {"project_name": name, "project_path": self.get_project_path(name)}
        ctx.update({k: kwargs.get(k, False) for k in ["clear", "path", "module"]})

        return self._exec_cmd(action, ctx)
