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
    return ", ".join(["{}: {}".format(k,v) for k,v in vals.items()])


def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], dict)):  #noqa
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]

  