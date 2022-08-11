import click
import getpass

from apixdev.apix import apix
from apixdev.cli import tools



@click.group()
def config():
    """View and edit configuration"""
    pass


@click.command()
def view():
    """Resume configuration"""
    
    vals = apix.config.get_vars()
    tools.print_dict(vals, False)


@click.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set a value"""
    apix.config.set_vars({key: value})    


@click.command()
def clear():
    """Clear all parameters"""
    raise NotImplementedError()
    


config.add_command(view)
config.add_command(clear)
config.add_command(set)
