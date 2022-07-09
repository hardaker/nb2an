#!/usr/bin/python3

"""List devices in a rack"""

import requests
import nb2an.netbox

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
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter,
                            description=__doc__,
                            epilog="Exmaple Usage: ")

    parser.add_argument("-b", "--blanks", action="store_true",
                        help="Show blank areas with blank lines")

    parser.add_argument("--log-level", default="info",
                        help="Define the logging verbosity level (debug, info, warning, error, fotal, critical).")

    parser.add_argument("rack", type=int, nargs="*", default=None,
                        help="Rack choice (all if not)")

    args = parser.parse_args()
    log_level = args.log_level.upper()
    logging.basicConfig(level=log_level,
                        format="%(levelname)-10s:\t%(message)s")
    return args


def main():
    args = parse_args()

    devices = nb2an.netbox.Netbox().get_devices(args.rack)
    print(f"{'Id':<3} {'Pos':<3} {'Name':<25} {'Type':<20}")
    last_spot = None
    for device in sorted(devices, key=lambda x: x['position'] or 0,
                         reverse=True):
        position = int(device['position'] or 0)
        if last_spot and args.blanks:
            for blank in range(last_spot-1, position, -1):
                print(blank)

        print(f"{device['id']:<3} {position:<3} {device['display']:<25} {device['device_type']['display']:<20}")
        last_spot = position

if __name__ == "__main__":
    main()


