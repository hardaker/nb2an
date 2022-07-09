#!/usr/bin/python3

"""Updates ansible YAML files with information from netbox"""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType
from logging import debug, info, warning, error, critical
import logging
import sys
import os
import nb2an.netbox

import ruamel.yaml

def parse_args():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter,
                            description=__doc__,
                            epilog="Exmaple Usage: update")

    parser.add_argument("-n", "--noop", action="store_true",
                        help="Don't actually make changes")

    parser.add_argument("--log-level", "--ll", default="info",
                        help="Define the logging verbosity level (debug, info, warning, error, fotal, critical).")

    parser.add_argument("-r", "--racks", default=[], type=int, nargs="*",
                        help="Racks to update")

    parser.add_argument("-d", "--ansible-directory",
                        type=str, help="The ansible directory to verify")

    args = parser.parse_args()
    log_level = args.log_level.upper()
    logging.basicConfig(level=log_level,
                        format="%(levelname)-10s:\t%(message)s")
    return args


def process_host(b: nb2an.netbox.Netbox, hostname: str, yaml_file: str, outlets: list,
                 make_changes: bool = True):
    debug(f"modifying {yaml_file}")
    with open(yaml_file) as original:
        yaml_data = original.read()

        yaml = ruamel.yaml.YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.preserve_quotes = True
        yaml_struct = yaml.load(yaml_data)

    with open(yaml_file, "w") as modified:
        yaml.dump(yaml_struct, modified)


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

    devices = nb.get_devices(args.racks)
    outlets = nb.get_outlets()

    for device in devices:
        name = nb.fqdn(device['name'])
        debug(f"starting: {name}")

        device_yaml = os.path.join(ansible_directory, "host_vars", name + ".yml")
        if os.path.exists(device_yaml):
            process_host(nb, name, device_yaml, outlets, make_changes=(not args.noop))


if __name__ == "__main__":
    main()
