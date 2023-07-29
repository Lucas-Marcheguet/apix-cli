import click

import apixdev.cli.config as config_cmd
import apixdev.cli.images as images_cmd
import apixdev.cli.project as project_cmd
import apixdev.cli.projects as projects_cmd
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
    """Manage project"""


@click.group()
def projects():
    """Manage projects"""


@click.group()
def images():
    """Manage Docker images"""


@click.group()
def config():
    """View and edit configuration"""


project.add_command(project_cmd.new)
project.add_command(project_cmd.update)
project.add_command(project_cmd.search)
project.add_command(project_cmd.delete)
project.add_command(project_cmd.merge)
project.add_command(project_cmd.pull)
project.add_command(project_cmd.run)
project.add_command(project_cmd.restart)
project.add_command(project_cmd.stop)
project.add_command(project_cmd.clear)
project.add_command(project_cmd.show)
project.add_command(project_cmd.logs)
project.add_command(project_cmd.locate)
project.add_command(project_cmd.bash)
project.add_command(project_cmd.shell)
project.add_command(project_cmd.install_modules)
project.add_command(project_cmd.update_modules)
project.add_command(project_cmd.last_backup)

projects.add_command(projects_cmd.ls)
projects.add_command(projects_cmd.stop)

images.add_command(images_cmd.ls)

config.add_command(config_cmd.view)
config.add_command(config_cmd.clear)
config.add_command(config_cmd.set_value)
config.add_command(config_cmd.edit)

cli.add_command(project)
cli.add_command(projects)
cli.add_command(images)
cli.add_command(config)
