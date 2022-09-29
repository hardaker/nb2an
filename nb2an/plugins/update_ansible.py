from logging import debug, info, warning, error, critical
import re
update_ansible_plugins = {}

from functools import wraps


def plugin(function):
    # register it
    fn_name = function.__name__
    fn_name = fn_name.replace("fn_", "", 1)
    update_ansible_plugins[fn_name] = function

    @wraps(function)
    def _wrap(*args, **kwargs):
        return function(*args, **kwargs)

    return _wrap


def keys_present(definition: dict, keys: list[str]):
    for key in keys:
        if key not in definition:
            error(f"Failed to find key '{key}' in {definition}")
            return False
    return True


@plugin
def fn_replace(dn, yaml_struct, definition, item):
    "A function to do internal string replacements before setting a value"
    if not keys_present(definition, ['value', 'search', 'replacement']):
        return
    value = dn.get(definition['value'])
    search = definition['search']
    replacement = definition['replacement']
    newvalue = re.sub(search, replacement, value,
                      count=definition.get('count', 0))
    yaml_struct[item] = newvalue


@plugin
def fn_delete(dn, yaml_struct, definition, item):
    "A plugin to remove a node"
    if item in yaml_struct:
        del yaml_struct[item]


@plugin
def fn_foreach_create_dict(dn, yaml_struct, definition, item):
    "iterates over a definition and applies it multiple times per array, replacing the contents of the original structure"
    # clear the existing content
    yaml_struct[item] = {}

    fn_foreach_augment_dict(dn, yaml_struct, definition, item)


@plugin
def fn_foreach_augment_dict(dn, yaml_struct, definition, item):
    "iterates over a definition and applies it multiple times per array, augmenting an existing structure."
    if not keys_present(definition, ['structure', 'array', 'keyname']):
        return

    # clear the existing content
    yaml_struct[item] = {}

    # for each item from the netbox array, create a structure
    array_name = definition['array']
    array = dn.get(definition['array'])
    starting_structure = definition['structure']
    for n, substructure in enumerate(array):
        replacement = {}
        keyvalue = dn.get(f"{array_name}.{n}.{definition['keyname']}")
        for subitem in starting_structure:
            path = f"{array_name}.{n}.{starting_structure[subitem]}"
            value = dn.get(path)
            replacement[subitem] = value
        yaml_struct[item][keyvalue] = replacement

