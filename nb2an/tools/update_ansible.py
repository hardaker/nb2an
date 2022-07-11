#!/usr/bin/python3

"""Updates ansible YAML files with information from netbox"""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType
from logging import debug, info, warning, error, critical
import logging
import sys
import os
import yaml
import ruamel.yaml

import nb2an.netbox
import nb2an.dotnest


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
        "-c",
        "--changes-file",
        default=None,
        type=FileType("r"),
        help="The changes definition file to use",
    )

    args = parser.parse_args()
    log_level = args.log_level.upper()
    logging.basicConfig(level=log_level, format="%(levelname)-10s:\t%(message)s")
    return args


def process_changes(changes, yaml_struct, nb_data):
    dn = nb2an.dotnest.DotNest(nb_data)
    for item in changes:
        if isinstance(changes[item], dict):
            if item not in yaml_struct:
                yaml_struct[item] = {}  # TODO: allow list creation
            process_changes(changes[item], yaml_struct[item], nb_data)
        elif isinstance(changes[item], str):
            value = dn.get(changes[item])
            yaml_struct[item] = value


def process_host(
    nb: nb2an.netbox.Netbox,
    hostname: str,
    yaml_file: str,
    outlets: list,
    changes: dict = None,
):
    info(f"modifying {yaml_file}")

    # load the original YAML
    with open(yaml_file) as original:
        yaml_data = original.read()

        yaml_parser = ruamel.yaml.YAML()
        yaml_parser.indent(mapping=2, sequence=4, offset=2)
        yaml_parser.preserve_quotes = True
        yaml_struct = yaml_parser.load(yaml_data)

    if changes:
        nb_data = nb.get_devices_by_name(hostname)
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


def main():
    args = parse_args()
    nb = nb2an.netbox.Netbox()
    config = nb.get_config()

    ansible_directory = args.ansible_directory
    if not ansible_directory:
        ansible_directory = config.get("ansible_directory")

    if not ansible_directory:
        error("Failed to find ansible_directory in args or .nb2an config")
        exit(1)

    devices = nb.get_devices(args.racks, link_other_information=True)
    outlets = nb.get_outlets()

    changes = None
    if args.changes_file:
        changes = yaml.safe_load(args.changes_file.read())

    for device in devices:
        name = nb.fqdn(device["name"])
        debug(f"starting: {name}")

        device_yaml = os.path.join(ansible_directory, "host_vars", name + ".yml")
        if os.path.exists(device_yaml):
            process_host(nb, name, device_yaml, outlets, changes=changes)


if __name__ == "__main__":
    main()
