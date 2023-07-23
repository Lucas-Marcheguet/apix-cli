import click


def print_list(items, index=True):
    click.echo("{} item(s) found".format(len(items)))
    for i, item in enumerate(items, 1):
        if isinstance(item, dict):
            # print_dict(item)
            click.echo("{}.\t {o}".format(i, o=dict_to_string(item)))
        else:
            click.echo("{}.\t {o}".format(i, o=item))


def print_dict(vals, index=True):
    for i, key in enumerate(vals.keys(), 1):
        if index:
            click.echo("{}.\t {}: {}".format(i, key, vals[key]))
        else:
            click.echo("{}: {}".format(key, vals[key]))


def dict_to_string(vals):
    return ", ".join(["{}: {}".format(k, v) for k, v in vals.items()])


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()
