import click

from apixdev.core.tools import dict_to_string


def print_list(items):
    """Echo list with click."""

    click.echo(f"{len(items)} item(s) found")
    for i, item in enumerate(items, 1):
        if isinstance(item, dict):
            click.echo(f"{i}.\t {dict_to_string(item)}")
        else:
            click.echo(f"{i}.\t {item}")


def print_dict(vals, index=True):
    """Echo dict with click."""

    for i, key in enumerate(vals.keys(), 1):
        if index:
            click.echo(f"{i}.\t {key}: {vals[key]}")
        else:
            click.echo(f"{key}: {vals[key]}")


def abort_if_false(ctx, _, value):
    """Confirm: Abort if false."""

    if not value:
        ctx.abort()
