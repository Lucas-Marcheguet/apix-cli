import click

from apixdev.cli.config import config
from apixdev.cli.images import images
from apixdev.cli.project import pj as project
from apixdev.cli.projects import projects
from apixdev.core.settings import settings

if not settings.is_ready:
    click.echo("Please fill configuration to continue :")
    settings.set_config()


@click.group()
def cli():
    """ApiX command line tool."""


cli.add_command(project)
cli.add_command(projects)
cli.add_command(images)
cli.add_command(config)
