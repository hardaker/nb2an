#!/usr/bin/python3

"""List devices in a rack"""

import requests
import nb2an.netbox
import collections

try:
    from rich import print
except Exception:
    pass

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType
from logging import debug, info, warning, error, critical
import logging
import sys


def parse_args():
    "Parse the command line arguments."
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description=__doc__,
        epilog="Exmaple Usage: ",
    )

    parser.add_argument(
        "--log-level",
        default="info",
        help="Define the logging verbosity level (debug, info, warning, error, fotal, critical).",
    )

    parser.add_argument("rack", type=str, help="Rack choice")

    args = parser.parse_args()
    log_level = args.log_level.upper()
    logging.basicConfig(level=log_level, format="%(levelname)-10s:\t%(message)s")
    return args


def main():
    args = parse_args()

    by_outlet = {}
    by_device = collections.defaultdict(list)

    nb = nb2an.netbox.Netbox()
    r = nb.get("/dcim/devices/?rack_id=" + args.rack)
    for device in r:
        outlets = nb.get_outlets_by_device_id(device["id"])
        print(f"{device['display']}:")
        for outlet in outlets:
            print(f"  - {outlet['device']['display']}.{outlet['display']}")
            by_outlet[outlet["display"]] = outlet["device"]["display"]
            by_device[outlet["device"]["display"]].append(outlet["display"])

    # print(by_outlet)
    # print(by_device)


if __name__ == "__main__":
    main()
