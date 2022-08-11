import click
import getpass
import logging
import os

import apixdev.config as cfg

path = os.path.join(cfg.HOME_PATH, cfg.CONFIG_PATH)
filename = os.path.join(path, cfg.LOGGING_FILE)

if not os.path.isdir(path):
    os.makedirs(path)

logging.basicConfig(filename=filename, level=cfg.LOGGING_LEVEL)


from apixdev.apix import apix
from apixdev.cli.project import project
from apixdev.cli.projects import projects
from apixdev.cli.config import config
from apixdev.cli.scaffold import scaffold


if not apix.is_ready:
    click.echo("Please fill configuration to continue :")
    apix.set_config()


@click.group()
def cli():

    """Apix Developper Toolkit, a powerfull command line tool."""
    


cli.add_command(project)
cli.add_command(projects)
cli.add_command(config)
cli.add_command(scaffold)