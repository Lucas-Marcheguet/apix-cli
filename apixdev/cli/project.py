import click

from apixdev.cli.tools import print_list
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
@click.argument("name")
def update(name, **kwargs):
    """Update project"""

    database = False
    urls = []

    project = Project(name)

    if project.is_ready:
        project.load_manifest()
    else:
        odoo = Odoo.new()
        database = odoo.get_database_from_uuid(name, strict=True, limit=1)

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
@click.argument("name")
def search(name, **kwargs):
    """Search for online project"""

    odoo = Odoo.new()
    databases = odoo.get_databases(name, strict=False)
    results = sorted(databases.mapped("name"))

    print_list(results)


project.add_command(new)
project.add_command(update)
project.add_command(search)
