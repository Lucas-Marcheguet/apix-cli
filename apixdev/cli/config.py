import click

from apixdev.cli.tools import print_dict
from apixdev.core.settings import settings


@click.group()
def config():
    """View and edit configuration"""


@click.command()
def view():
    """Resume configuration"""

    vals = settings.get_vars()
    print_dict(vals, False)


@click.command()
@click.argument("key")
@click.argument("value")
def set(key, value):
    """Set a value"""
    settings.set_vars({key: value})


@click.command()
def clear():
    """Clear all parameters"""
    raise NotImplementedError()


@click.command()
def edit():
    res = click.edit(
        require_save=True,
        extension="ini",
        filename=settings.filepath,
    )
    print(res)


config.add_command(view)
config.add_command(clear)
config.add_command(set)
config.add_command(edit)
