#!/usr/bin/python3

"""List networks in a rack"""

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
        "--ll",
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

    nb = nb2an.netbox.Netbox()
    r = nb.get("/dcim/devices/?rack_id=" + args.rack)

    interface_addresses = nb.get_addresses()
    interfaces = nb.get_interfaces()

    for device in sorted(r, key=lambda x: x["display"]):

        name = device["display"]
        print(f"{name}:")

        # get interfaces
        dev_interfaces = interfaces[name]

        for interface in dev_interfaces:
            interface = dev_interfaces[interface]
            other_end = ""
            if (
                "cable_peer" in interface
                and interface["cable_peer"]
                and "device" in interface["cable_peer"]
            ):
                other_end = interface["cable_peer"]["device"]["display"]

            ifname = ""
            if "display" in interface:
                ifname = interface["display"]

            ipv4 = ""
            if ifname in interface_addresses[name]:
                ipv4 = interface_addresses[name][ifname].get("IPv4", "")

            ipv6 = ""
            if ifname in interface_addresses[name]:
                ipv6 = interface_addresses[name][ifname].get("IPv6", "")

            print(
                f"  {interface['name']:<12} {other_end:<10} {ipv4:<20} {ipv6:<30} {interface['type']['label']}"
            )


if __name__ == "__main__":
    main()
