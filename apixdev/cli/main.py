import click

from apixdev.core.settings import Settings

settings = Settings()

# from apixdev.apix import apix  # noqa: E402
# from apixdev.cli.config import config  # noqa: E402
from apixdev.cli.project import project  # noqa: E402
from apixdev.cli.projects import projects  # noqa: E402

# from apixdev.cli.scaffold import scaffold  # noqa: E402

if not settings.is_ready:
    click.echo("Please fill configuration to continue :")
    settings.set_config()


@click.group()
def cli():
    """Apix Developper Toolkit, a powerfull command line tool."""


cli.add_command(project)
cli.add_command(projects)
# cli.add_command(config)
# cli.add_command(scaffold)
