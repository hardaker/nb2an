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


debug(f"plugins registered: {update_ansible_plugins}")
