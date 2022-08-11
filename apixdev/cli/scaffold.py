import click
import getpass
import os

from apixdev.apix import apix
from apixdev.cli.common import abort_if_false



@click.group()
def scaffold():
    """Scaffold functions"""
    pass


@click.command()
@click.argument('name')
def module(name):
    """Generates an Odoo module skeleton"""
    
    if os.path.exists(os.path.join(os.getcwd(), name)):
        raise click.UsageError('Module {} already exists.'.format(name))


    apix.scaffold_module(name)




scaffold.add_command(module)

