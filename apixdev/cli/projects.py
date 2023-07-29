import click

from apixdev.cli.tools import abort_if_false, print_list
from apixdev.core.exceptions import CommandNotImplemented
from apixdev.core.projects import Projects


@click.command()
def ls():
    """List local projects"""

    projects = Projects.from_path()
    print_list(projects)


@click.command()
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Are you sure you want to stop all projects?",
)
def stop():
    """Stop all projects"""
    raise CommandNotImplemented("stop")
