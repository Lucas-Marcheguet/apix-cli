import click

from apixdev.cli.tools import print_list
from apixdev.core.images import Images


@click.group()
def images():
    """Manage Docker images"""


@click.command()
def ls():
    """List local projects"""

    items = Images.ls()
    print_list(items)


images.add_command(ls)
