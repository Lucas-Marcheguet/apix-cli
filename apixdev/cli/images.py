import click

from apixdev.cli.tools import print_list
from apixdev.core.images import Images


@click.command()
def ls():
    """List local docker images"""

    items = Images.ls()
    print_list(items)
