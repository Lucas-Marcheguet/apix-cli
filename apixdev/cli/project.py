import click
from tqdm import tqdm

from apixdev.apix import apix
from apixdev.cli import tools
from apixdev.cli.common import abort_if_false


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

    click.echo("Check if local project exists")
    apix.check_project(name)

    if not is_local:
        click.echo("Search for online database")
        database = apix.odoo.get_databases(name, strict=True, limit=1)

    click.echo("If not, create folders")
    apix.init_project(name)

    if not is_local:
        click.echo("Get repositories...")
        repositories = apix.get_repositories(database)
        # tools.print_list([v for k,v in repositories.items() if k in ['name', 'branch']])

        for repo in tqdm(repositories):
            try:
                apix.clone_repository(name, repo["name"], repo["url"], repo["branch"])
            except Exception as err:
                raise click.UsageError(err)

    click.echo("Generate docker-compose file")

    requirements = apix.get_requirements(name)
    vals = apix.prepare_compose_vals(database, requirements)
    apix.generate_compose_file(name, vals)


@click.command()
@click.argument("name")
@click.option("--path", "-p", help="Subfolder path (reprository)")
def cloc(name, **kwargs):
    """Count Lines of Code"""

    apix.project_cmd(name, "cloc", **kwargs)


@click.command()
@click.argument("name")
def status(name, **kwargs):
    """View project info"""

    apix.project_cmd(name, "ps", **kwargs)


@click.command()
@click.argument("name")
def logs(name, **kwargs):
    """View project logs"""

    apix.project_cmd(name, "logs", **kwargs)


@click.command()
@click.argument("name")
def restart(name, **kwargs):
    """Stop & start project"""

    apix.project_cmd(name, "stop", **kwargs)
    apix.project_cmd(name, "start", **kwargs)


@click.command()
@click.argument("name")
def search(name, **kwargs):
    """Search online project"""

    databases = apix.odoo.get_databases(name, strict=False)
    # items = apix.odoo.list_of(databases, ['name'])
    items = databases.read(["name"])

    tools.print_list(items)


@click.command()
@click.argument("name")
def start(name, **kwargs):
    """Start stack project"""
    apix.project_cmd(name, "start")


@click.command()
@click.argument("name")
def bash(name, **kwargs):
    """Open a bash"""
    apix.project_cmd(name, "bash")


@click.command()
@click.argument("name")
def shell(name, **kwargs):
    """Open a Shell"""
    apix.project_cmd(name, "shell")


@click.command()
@click.argument("name")
@click.argument("module")
def odoo_update(name, **kwargs):
    """Open a Shell"""
    apix.project_cmd(name, "odoo_update", **kwargs)


@click.command()
@click.argument("name")
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Are you sure you want to stop this project ?",
)
def stop(name, **kwargs):
    """Stop project"""
    apix.project_cmd(name, "stop", **kwargs)


project.add_command(status)
project.add_command(logs)
project.add_command(bash)
project.add_command(shell)
project.add_command(odoo_update)
project.add_command(stop)
project.add_command(start)
project.add_command(search)
project.add_command(new)
project.add_command(cloc)
