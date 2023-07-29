import json
import logging
import os
import subprocess

import pandas
import requirements as req_tool
from packaging.specifiers import SpecifierSet

_logger = logging.getLogger(__name__)


def dict_to_string(vals):
    """Transform dict to string."""

    return ", ".join([f"{key}: {value}" for key, value in vals.items()])


def dict_to_dataframe(vals):
    """Return Pandas dataframe from dict."""
    dataframe = pandas.DataFrame(vals)

    return dataframe


def run_external_command(cmd, **kwargs):
    """Run system command and return result."""

    result = kwargs.pop("result", True)

    if isinstance(cmd, str):
        cmd = cmd.split(" ")

    try:
        if result:
            res = subprocess.check_output(cmd, **kwargs)
        else:
            subprocess.call(cmd, **kwargs)
            res = True
    except FileNotFoundError as error:
        _logger.error(error)
        return False

    return res


def text_to_list(data):
    """Transform string to list."""

    res = data.split("\n")

    return list(filter(bool, map(str.strip, res)))


def list_to_text(items, separator="\n\n", default=""):
    """Transform items list to string."""

    return separator.join(items) if items else default


def deduplicate(items):
    """Deduplicate items."""

    return list(set(items))


def get_requirements_from_path(path):
    """Recursively extract all requirements from root path"""

    requirements = []

    for root, _, files in os.walk(path):
        for file in files:
            if file == "requirements.txt":
                with open(os.path.join(root, file), encoding="utf8") as tmp:
                    requirements += tmp.readlines()

    requirements = list({e.strip() for e in requirements})
    _logger.debug("Read requirements from path: %s", requirements)

    return requirements


def filter_requirements(items):
    """Cleans and eliminates duplicate requirements"""

    requirements = "\n".join(deduplicate(items))

    reqs = {}
    res = []

    for item in req_tool.parse(requirements):
        # Dict used to merge packages by name
        reqs.setdefault(item.name, [])
        reqs[item.name] += [SpecifierSet("".join(specs)) for specs in item.specs]

    for name, specs in reqs.items():
        if not name:
            continue

        if not specs:
            res.append(name)
            continue

        # Sort specifiers and keep only last one
        # FIXME: Not perfect IMHO, errors possible, fix it !
        specs = sorted({*specs}, key=str)
        res.append("".join([name, str(specs[-1])]))

    _logger.debug("Filtered requirements: %s", requirements)
    return res


def nested_set(dic, keys, value):
    """Update nested dict."""
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value


def dict_merge(dct, merge_dct):
    """Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for key, _ in merge_dct.items():
        if (
            key in dct
            and isinstance(dct[key], dict)
            and isinstance(merge_dct[key], dict)
        ):  # noqa
            dict_merge(dct[key], merge_dct[key])
        else:
            dct[key] = merge_dct[key]


def bytes_to_json(data):
    """Convert stdout bytes to json array."""

    res = data.rstrip().decode("utf8").replace("'", '"').replace("\n", ",")
    res = "[" + res + "]"
    res = res.replace(",]", "]")
    json_data = json.loads(res)

    return json_data


def convert_stdout_to_json(content):
    """Convert stdout bytes to json array."""

    try:
        data = json.loads(content)
    except json.decoder.JSONDecodeError:
        content = content.decode("utf8")
        content = content.strip().rstrip().lstrip()
        content = f"[{content}]"
        content = content.replace("}", "},").replace("},]", "}]")

        data = json.loads(content)

    return data


def split_var(key, separator="."):
    """Split vars."""

    section, key = key.split(separator)
    return section, key


def add_separator(items, separator="."):
    """Add separator."""

    return separator.join(items)


def unmerge_sections(vals):
    """Unmerge sections.

    eg: [section.key] ==> [section][key]
    """

    tmp = {}
    for k, value in vals.items():
        section, key = split_var(k)
        curr = tmp.setdefault(section, {})
        curr[key] = value

    _logger.debug("_unmerge_sections: %s", tmp)
    return tmp


def merge_sections(vals):
    """Merge sections.

    eg: [section][key] ==> [section.key]
    """
    _logger.debug("merge sections (before): %s", vals)
    tmp = {}
    for section in vals.keys():
        tmp.update({add_separator([section, k]): v for k, v in vals[section]})

    _logger.debug("merge sections: %s", tmp)
    return tmp

    # {self._add_dot(section, k):v for k,v in vals[section].items()}
