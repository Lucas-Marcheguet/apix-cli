import sys

import click

from apixdev.cli.tools import abort_if_false, print_dict, print_list
from apixdev.core.exceptions import DownloadError, NoContainerFound
from apixdev.core.odoo import Odoo
from apixdev.core.project import Project


@click.command()
@click.argument("name")
@click.option("--local", "-l", is_flag=True, help="Create blank project")
def new(name, **kwargs):
    """Create new project from online database.

    `NAME` is the name of the database.
    """

    is_local = kwargs.get("local", False)
    database = False
    urls = []

    project = Project(name)

    if not is_local:
        odoo = Odoo.new()
        database = odoo.get_databases(name, strict=True, limit=1)

        if not database:
            click.echo(f"No '{name}' database found.")
            project.delete()
            sys.exit(1)

        urls = [
            ("manifest.yaml", database.manifest_url),
            ("repositories.yaml", database.repositories_url),
            ("docker-compose.yaml", database.compose_url),
        ]

        for filename, url in urls:
            try:
                project.download(filename, url)
            except DownloadError as error:
                click.echo(error)
                sys.exit(1)

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
def update(name):
    """Update the local project based on the manifest.

    `NAME` is the name of the local project.

    Note: Repositorie and requirements are updated.
    """

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        sys.exit(1)

    project.load_manifest()
    project.pull_repositories()
    project.merge_requirements()


@click.command()
@click.argument("name")
def merge(name):
    """Merge requirements from online manifest and local repositories.

    `NAME` is the name of the local project.
    """

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        sys.exit(1)

    project.merge_requirements()


@click.command()
@click.argument("name")
def pull(name):
    """Pull repositories."""

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        sys.exit(1)

    project.pull_repositories()


@click.command()
@click.argument("name")
def search(name):
    """Search for online project.

    `NAME` is the name of the online project.
    """

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
def delete(name):
    """Delete local project."""

    project = Project(name)
    project.delete()


@click.command()
@click.option("--detach", "-d", is_flag=True, help="Running on background (detach)")
@click.option("--reload", "-r", is_flag=True, help="Dev mode (auto reload)")
@click.argument("name")
def run(name, **kwargs):
    """Run project.

    `NAME` is the name of the local project.
    """

    run_on_background = kwargs.get("detach", False)
    auto_reload = kwargs.get("reload", False)
    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        sys.exit(1)

    stack = project.get_stack()

    if run_on_background:
        stack.run(run_on_background, False)
    else:
        # Run on foreground means auto shutdown stack when user exit container
        stack.run(run_on_background, auto_reload)
        stack.stop()


@click.command()
@click.option("--detach", "-d", is_flag=True, help="Run on background (detach)")
@click.argument("name")
def restart(name, **kwargs):
    """Restart project.

    `NAME` is the name of the local project.
    """

    run_on_background = kwargs.get("detach", False)
    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        sys.exit(1)

    stack = project.get_stack()
    stack.stop()

    if run_on_background:
        stack.run(run_on_background)
    else:
        # Run on foreground means auto shutdown stack when user exit container
        stack.run()
        stack.stop()


@click.command()
@click.argument("name")
def stop(name):
    """Stop project stack (all containers).

    `NAME` is the name of the local project.
    """

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        sys.exit(1)

    stack = project.get_stack()
    stack.stop()


@click.command()
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Are you sure you want to clear project containers (databsae will be lost) ?",
)
@click.argument("name")
def clear(name):
    """Stop project stack (all containers) and clear volumes.

    `NAME` is the name of the local project.
    """

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        sys.exit(1)

    stack = project.get_stack()
    stack.clear()


@click.command()
@click.argument("name")
@click.argument("service")
def logs(name, service="odoo"):
    """Show container logs.

    `NAME` is the name of the local project.

    `SERVICE` is the name of one of the stack's services, possible values: odoo, pg or redis.
    """

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        sys.exit(1)

    stack = project.get_stack()
    try:
        container = stack.get_container(service)
    except NoContainerFound as error:
        click.echo(error)
        sys.exit(1)
    container.logs()


@click.command()
@click.argument("name")
def bash(name, service="odoo"):
    """Attach to Odoo container bash.

    `NAME` is the name of the local project.
    """

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        sys.exit(1)

    stack = project.get_stack()
    try:
        container = stack.get_container(service)
    except NoContainerFound as error:
        click.echo(error)
        sys.exit(1)
    container.bash()


@click.command()
@click.argument("name")
@click.argument("database")
def shell(name, database):
    """Attach to Odoo shell.

    `NAME` is the name of the local project.

    `DATABASE` is the name of Odoo database.
    """

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        sys.exit(1)

    stack = project.get_stack()
    container = stack.get_odoo_container()
    container.shell(database)


@click.command()
@click.argument("name")
@click.argument("database")
@click.argument("modules")
def install_modules(name, database, modules):
    """Install modules on database.

    `NAME` is the name of the local project.

    `DATABASE` is the name of Odoo database.

    `MODULES` is the list of modules to install, comma separated.
    """

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        sys.exit(1)

    stack = project.get_stack()
    container = stack.get_odoo_container()
    container.install_modules(database, modules, install=True)


@click.command()
@click.argument("name")
@click.argument("database")
@click.argument("modules")
def update_modules(name, database, modules):
    """Update modules on database.

    `NAME` is the name of the local project.

    `DATABASE` is the name of Odoo database.

    `MODULES` is the list of modules to update, comma separated.
    """

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        sys.exit(1)

    stack = project.get_stack()
    container = stack.get_odoo_container()
    container.install_modules(database, modules, install=False)


@click.command()
@click.argument("name")
def status(name):
    """Show project containers and states.

    `NAME` is the name of the local project.
    """

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        sys.exit(1)

    stack = project.get_stack()
    containers = stack.get_containers()

    if not containers:
        click.echo(f"'{project}' stack is down.")
        sys.exit(1)

    print_list(containers)


@click.command()
@click.argument("name")
def locate(name):
    """Locate project on disk.

    `NAME` is the name of the local project.
    """
    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        sys.exit(1)

    click.echo(project.repositories_path)
    click.launch(project.repositories_path, locate=True)


@click.command()
@click.argument("name")
def last_backup(name):
    """Get last url backup for online project.

    `NAME` is the name of the local project.
    """

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        sys.exit(1)

    if not project.uuid:
        project.load_manifest()

    odoo = Odoo.new()
    url = odoo.get_last_backup_url(project.uuid)
    print_list([url])

    if url:
        click.launch(url)


@click.command()
@click.argument("name")
def repo(name):
    """Get repositories list with branches.

    `NAME` is the name of the local project.
    """

    project = Project(name)

    if not project.is_ready:
        click.echo(f"No '{project}' project found locally.")
        sys.exit(1)

    repositories = project.get_repo()
    print_dict(repositories)
