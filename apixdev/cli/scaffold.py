import os

import click

from apixdev.apix import apix


@click.group()
def scaffold():
    """Scaffold functions"""


@click.command()
@click.argument("name")
def module(name):
    """Generates an Odoo module skeleton"""

    if os.path.exists(os.path.join(os.getcwd(), name)):
        raise click.UsageError("Module {} already exists.".format(name))

    apix.scaffold_module(name)


scaffold.add_command(module)
