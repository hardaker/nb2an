#!/usr/bin/python3

import requests
import nb2an.netbox

try:
    from rich import print
except Exception:
    pass


def main():
    # args = parse_args()

    racks = nb2an.netbox.Netbox().get_racks()
    print(f"{'Id':<3} {'Name':<25} {'Site':<20} {'Location':<20} {'#devs'}")
    for rack in racks:
        print(
            f"{rack['id']:<3} {rack['display']:<25} {rack['site']['display']:<20} {rack['location']['display']:<20} {rack['device_count']}"
        )


if __name__ == "__main__":
    main()
