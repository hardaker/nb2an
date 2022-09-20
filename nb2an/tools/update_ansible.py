#!/usr/bin/python3

"""Updates ansible YAML files with information from netbox"""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType
from logging import debug, info, warning, error, critical
import logging
import sys
import os
import re
import yaml
import shutil
import subprocess
import ruamel.yaml

import nb2an.netbox
import nb2an.dotnest

FUNCTION_KEY = "__function"

def fn_replace(dn, definition: dict):
    "A function to do internal string replacements"
    if not keys_present(definition, ['value', 'search', 'replacement']):
        return
    value = dn.get(definition['value'])
    search = definition['search']
    replacement = definition['replacement']
    newvalue = re.sub(search, replacement, value,
                      count=definition.get('count', 0))
    return newvalue


functions = {
    'replace': fn_replace,
}


def keys_present(definition: dict, keys: list[str]):
    for key in keys:
        if key not in definition:
            error(f"Failed to find key '{key}' in {definition}")
            return False
    return True

def parse_args():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description=__doc__,
        epilog="Exmaple Usage: update",
    )

    parser.add_argument(
        "-n", "--noop", action="store_true", help="Don't actually make changes"
    )

    parser.add_argument(
        "--log-level",
        "--ll",
        default="info",
        help="Define the logging verbosity level (debug, info, warning, error, fotal, critical).",
    )

    parser.add_argument(
        "-r", "--racks", default=[], type=int, nargs="*", help="Racks to update"
    )

    parser.add_argument(
        "-d", "--ansible-directory", type=str, help="The ansible directory to verify"
    )

    parser.add_argument(
        "-D",
        "--devices",
        default=[],
        type=str,
        nargs="*",
        help="Process only these NetBox device names",
    )

    parser.add_argument(
        "-c",
        "--changes-file",
        default=None,
        type=FileType("r"),
        help="The changes definition file to use",
    )

    parser.add_argument(
        "-w",
        "--whitespace-hack",
        action="store_true",
        help="Try a multi-run with yaml-edit and whitespace ignoring diff to patch minimally",
    )

    args = parser.parse_args()
    log_level = args.log_level.upper()
    logging.basicConfig(level=log_level, format="%(levelname)-10s:\t%(message)s")
    return args


def process_changes(changes, yaml_struct, nb_data):
    dn = nb2an.dotnest.DotNest(nb_data)
    for item in changes:
        if isinstance(changes[item], dict):

            # check if it's a special dict with instructions
            if FUNCTION_KEY in changes[item]:
                function_name = changes[item][FUNCTION_KEY]
                if function_name not in functions:
                    error(f"function '{function_name}' is unknown")
                    exit(1)

                try:
                    fn = functions[function_name]
                    value = fn(dn, changes[item])
                    yaml_struct[item] = value
                    continue
                except Exception:
                    debug(f"failed to call function {function_name}")

            if item not in yaml_struct:
                yaml_struct[item] = {}  # TODO: allow list creation
            process_changes(changes[item], yaml_struct[item], nb_data)
            if yaml_struct[item] == {}:
                # nothing added, drop it again
                del yaml_struct[item]
        elif isinstance(changes[item], str):
            try:
                value = dn.get(changes[item])
                yaml_struct[item] = value
            except Exception:
                debug(f"skipping {changes[item]}: failed to find netbox value")


def process_host(
    nb: nb2an.netbox.Netbox,
    hostname: str,
    yaml_file: str,
    changes: dict = None,
):
    info(f"modifying {yaml_file}")

    # load the original YAML
    with open(yaml_file) as original:
        yaml_data = original.read()

        yaml_parser = ruamel.yaml.YAML()
        yaml_parser.indent(mapping=2, sequence=4, offset=2)
        yaml_parser.preserve_quotes = True
        yaml_parser.width = 4096
        yaml_struct = yaml_parser.load(yaml_data)

    if changes:
        nb_data = nb.get_devices_by_name(hostname, link_other_information=True)
        if not nb_data or len(nb_data) != 1:
            info(f"not processing changes for {hostname} as no netbox data found")
        else:
            nb_data = nb_data[0]
            process_changes(changes, yaml_struct, nb_data)

        for item in changes:
            debug(f"setting: {item} to {changes[item]}")

    # write the YAML back out
    with open(yaml_file, "w") as modified:
        yaml_parser.dump(yaml_struct, modified)


def process_devices(nb, ansible_directory, racks=[], changes=True):
    devices = nb.get_devices(racks, link_other_information=True)

    for device in devices:
        name = nb.fqdn(device["name"])
        debug(f"starting: {name}")

        device_yaml = os.path.join(ansible_directory, "host_vars", name + ".yml")
        if os.path.exists(device_yaml):
            process_host(nb, name, device_yaml, changes=changes)


def main():
    args = parse_args()
    nb = nb2an.netbox.Netbox()
    config = nb.get_config()

    ansible_directory = args.ansible_directory
    if not ansible_directory:
        ansible_directory = config.get("ansible_directory")
    host_vars = os.path.join(ansible_directory, "host_vars")

    if not ansible_directory:
        error("Failed to find ansible_directory in args or .nb2an config")
        exit(1)

    changes = None
    if not args.noop and args.changes_file:
        changes = yaml.safe_load(args.changes_file.read())

    # maybe copy the info to a separate set of files
    if args.whitespace_hack:
        shutil.copytree(host_vars, host_vars + ".nb2an-bkup")

    process_devices(nb, ansible_directory, racks=args.racks, changes=changes)

    # put the original back
    if args.whitespace_hack:
        # move the original data back
        os.rename(host_vars, host_vars + ".nb2an-modified")
        os.rename(host_vars + ".nb2an-bkup", host_vars)

        # generate a patch
        subprocess.run(["diff", "-wBuZE", host_vars, host_vars + ".nb2an-modified"])


if __name__ == "__main__":
    main()
