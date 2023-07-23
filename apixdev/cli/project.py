import click

from apixdev.cli.tools import abort_if_false, print_list
from apixdev.core.odoo import Odoo
from apixdev.core.project import Project


@click.group()
def project():
    """Manage apix project"""


@click.command()
@click.argument("name")
@click.option("--local", "-l", is_flag=True, help="Create blank project")
def new(name, **kwargs):
    """Create new project"""

    is_local = kwargs.get("local", False)
    database = False
    urls = []

    project = Project(name)

    if not is_local:
        odoo = Odoo.new()
        database = odoo.get_databases(name, strict=True, limit=1)

        urls = [
            ("manifest.yaml", database.manifest_url),
            ("repositories.yaml", database.repositories_url),
            ("docker-compose.yaml", database.compose_url),
        ]

        for name, url in urls:
            project.download(name, url)

        project.pull_repositories()
        project.merge_requirements()


@click.command()
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Are you sure you want to overwrite project ?",
)
@click.argument("name")
def update(name, **kwargs):
    """Update project"""

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        return False

    project.load_manifest()
    project.pull_repositories()
    project.merge_requirements()


@click.command()
@click.argument("name")
def merge(name, **kwargs):
    """Merge requirements"""

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        return False

    project.merge_requirements()


@click.command()
@click.argument("name")
def pull(name, **kwargs):
    """Pull repositories"""

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        return False

    project.pull_repositories()


@click.command()
@click.argument("name")
def search(name, **kwargs):
    """Search for online project"""

    odoo = Odoo.new()
    databases = odoo.get_databases(name, strict=False)
    results = sorted(databases.mapped("name"))

    print_list(results)


@click.command()
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Are you sure you want to delete project ?",
)
@click.argument("name")
def delete(name, **kwargs):
    """Delete local project"""

    project = Project(name)
    project.delete()


project.add_command(new)
project.add_command(update)
project.add_command(search)
project.add_command(delete)
project.add_command(merge)
project.add_command(pull)
