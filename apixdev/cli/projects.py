import click
import getpass

from apixdev.apix import apix
from apixdev.cli.common import abort_if_false
import apixdev.cli.tools as tools



@click.group()
def projects():
    """Manage projects"""
    pass

@click.command()
def ps():
    """List local projects"""
    
    projects = apix.get_local_projects()
    tools.print_list(projects)



@click.command()
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to stop all projects?')
def stop():
    """Stop all projects"""
    raise NotImplementedError()


projects.add_command(ps)
projects.add_command(stop)
