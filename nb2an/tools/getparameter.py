#!/usr/bin/python3

"""Reports specific parameters from each device"""

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
from nb2an.plugins.update_ansible import update_ansible_plugins

def parse_args():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description=__doc__,
        epilog="Exmaple Usage: nb-parameter",
    )

    parser.add_argument(
        "--log-level",
        "--ll",
        default="info",
        help="Define the logging verbosity level (debug, info, warning, error, fotal, critical).",
    )

    parser.add_argument(
        "-r", "--racks", default=[], type=int, nargs="*", help="Racks to show"
    )

    parser.add_argument(
        "-D",
        "--devices",
        default=[],
        type=str,
        nargs="*",
        help="Process only these NetBox device names",
    )

    parser.add_argument("data_specifications", type=str, nargs="*",
                        help="Data specifications to use in nb2an keying format")

    args = parser.parse_args()
    log_level = args.log_level.upper()
    logging.basicConfig(level=log_level, format="%(levelname)-10s:\t%(message)s")
    return args


def process_changes(changes, yaml_struct, nb_data):
    dn = nb2an.dotnest.DotNest(nb_data)
    for item in changes:
        if isinstance(changes[item], dict):

            # check if it's a special dict with instructions
            if PLUGIN_KEY in changes[item]:
                function_name = changes[item][PLUGIN_KEY]
                if function_name not in update_ansible_plugins:
                    error(f"function '{function_name}' is unknown")
                    exit(1)

                try:
                    fn = update_ansible_plugins[function_name]
                    value = fn(dn, yaml_struct, changes[item], item)
                except Exception:
                    debug(f"failed to call function {function_name}")
            else:
                if item not in yaml_struct:
                    yaml_struct[item] = {}  # TODO: allow list creation
                process_changes(changes[item], yaml_struct[item], nb_data)


            # if nothing was added, drop it again
            if item in yaml_struct and yaml_struct[item] == {}:
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


def process_devices(nb, racks=[], specifications=[]):
    devices = nb.get_devices(racks, link_other_information=True)

    for device in devices:
        name = nb.fqdn(device["name"])
        dn = nb2an.dotnest.DotNest(device)
        print(f"{name}")
        for specification in specifications:
            try:
                print(f"  {specification:<40s}:  {dn.get(specification)}")
            except Exception:
                print(f"  {specification:<40s}:  [DNE]")

def main():
    args = parse_args()
    nb = nb2an.netbox.Netbox()
    config = nb.get_config()

    process_devices(nb, racks=args.racks, specifications=args.data_specifications)



if __name__ == "__main__":
    main()
