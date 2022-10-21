#!/usr/bin/python3

"""Reports specific parameters from each device."""

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
        epilog="Exmaple Usage: nb-parameters display device.manufacturer.display",
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
        "-f", "--fsdb", action="store_true", help="Output data in FSDB format"
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
        "data_specifications",
        type=str,
        nargs="*",
        help="Data specifications to use in nb2an keying format",
    )

    args = parser.parse_args()
    log_level = args.log_level.upper()
    logging.basicConfig(level=log_level, format="%(levelname)-10s:\t%(message)s")
    return args


def process_devices(nb, racks=[], specifications=[], as_fsdb=False):
    devices = nb.get_devices(racks, link_other_information=True)

    if as_fsdb:
        import pyfsdb

        fh = pyfsdb.Fsdb(out_file_handle=sys.stdout)
        fh.out_column_names = ["name"] + [x for x in specifications]

    for device in devices:
        name = nb.fqdn(device["name"])
        dn = nb2an.dotnest.DotNest(device)

        # FSDB output
        if as_fsdb:
            row = [name]
            for specification in specifications:
                try:
                    row.append(dn.get(specification))
                except Exception:
                    row.append(None)
            fh.append(row)
            continue

        # human output
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

    process_devices(
        nb, racks=args.racks, specifications=args.data_specifications, as_fsdb=args.fsdb
    )


if __name__ == "__main__":
    main()
