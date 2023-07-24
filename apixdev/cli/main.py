import click

from apixdev.cli.config import config
from apixdev.cli.images import images
from apixdev.cli.project import (
    bash,
    clear,
    delete,
    install_modules,
    logs,
    merge,
    new,
    pull,
    run,
    search,
    shell,
    show,
    stop,
    update,
    update_modules,
)
from apixdev.cli.projects import projects
from apixdev.core.settings import settings

# try:
#     settings.check()
# except ExternalDependenciesMissing as error:
#     click.echo(error)
#     sys.exit(1)

if not settings.is_ready:
    click.echo("Please fill configuration to continue :")
    settings.set_config()


@click.group()
def cli():
    """ApiX command line tool."""


@click.group()
def project():
    """Manage apix project"""


project.add_command(new)
project.add_command(update)
project.add_command(search)
project.add_command(delete)
project.add_command(merge)
project.add_command(pull)
project.add_command(run)
project.add_command(stop)
project.add_command(clear)
project.add_command(show)
project.add_command(logs)
project.add_command(bash)
project.add_command(shell)
project.add_command(install_modules)
project.add_command(update_modules)


cli.add_command(project)
cli.add_command(projects)
cli.add_command(images)
cli.add_command(config)
