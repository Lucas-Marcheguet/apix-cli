import click

from apixdev.cli.tools import print_dict
from apixdev.core.exceptions import CommandNotImplemented
from apixdev.core.settings import settings


@click.command()
def view():
    """Resume configuration"""

    vals = settings.get_vars()
    print_dict(vals, False)


@click.command()
@click.argument("key")
@click.argument("value")
def set_value(key, value):
    """Set a value"""
    settings.set_vars({key: value})


@click.command()
def clear():
    """Clear all parameters"""
    raise CommandNotImplemented("clear")


@click.command()
def edit():
    """
    Edit config.ini.
    """
    _ = click.edit(
        require_save=True,
        extension="ini",
        filename=settings.filepath,
    )
