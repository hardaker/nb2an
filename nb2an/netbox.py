import os
import yaml
import requests
import collections
from typing import Union
from logging import debug

default_url="https://netbox/api"
default_config_path=os.path.join(os.environ.get('HOME'),
                                     ".nb2an")

class Netbox():
    def __init__(self, api_url=default_url,
                 config_path=default_config_path,
                 ansible_dir=None,
                 suffix=None):
        self.config_path = config_path
        self.config = {}
        if os.path.exists(self.config_path):
            self.config = self.get_config()
        self.prefix = self.config.get("api_url", api_url)
        self.suffix = self.config.get("suffix", suffix)
        self.ansible_dir = self.config.get("ansible_dir", ansible_dir)

    def get_config(self):
        debug(f"loading config from {self.config_path}")
        content = open(self.config_path).read()
        #debug(f"{content=}")
        results = yaml.safe_load(str(open(self.config_path).read()))
        return results

    def fqdn(self, hostname):
        if not self.suffix:
            return hostname
        if not hostname.endswith(self.suffix):
            hostname = hostname + self.suffix
        return hostname

    def get(self, url: str):
        if not url.startswith("http"):
            url = self.prefix + url
        debug(f"fetching: {url}")

        c = self.config
        headers = {"Authorization": f"Token {c['token']}"}
        # auth=(c['user'], c['password']), 
        #debug(f"headers: {headers}")
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r.json()

    def get_racks(self):
        results = self.get("/dcim/racks")
        return results['results']

    def get_devices(self, racknums: Union[list[int], int] = None):
        if isinstance(racknums, int):
            racknums = [racknums]
        if racknums is None or racknums == []:
            racknums = [x['id'] for x in self.get_racks()]

        devices = []
        for racknum in racknums:
            rack_devices = self.get("/dcim/devices/?rack_id=" + str(racknum))
            devices.extend(rack_devices['results'])
        return devices

    def get_devices_by_id(self, devices: Union[list[int], int] = None):
        if isinstance(devices, int):
            devices = [devices]
        if devices is None or devices == []:
            devices = [x['id'] for x in self.get_devices()]

        results = []
        for device in devices:
            the_devices = self.get("/dcim/devices/" + str(device))
            results.append(the_devices)
        return results

    def get_devices_by_name(self, devices: Union[list[str], str] = None):
        if isinstance(devices, str):
            devices = [devices]
        if devices is None or devices == []:
            devices = [x['id'] for x in self.get_devices()]

        results = []
        for device in devices:
            the_device = self.get("/dcim/devices/?name=" + str(device))
            if not the_device and device.endswith(self.suffix):
                device = device[0:-len(self.prefix)]
                the_device = self.get("/dcim/devices/?name=" + str(device))
            elif not the_device:
                device = self.fqdn(device)
                the_device = self.get("/dcim/devices/?name=" + str(device))[0]

            results.extend(the_device['results'])
        return results

    def get_outlets(self, device: int = None):
        if device:
            outlets = self.get("/dcim/power-outlets/?device_id=" + str(device))
        else:
            outlets = self.get("/dcim/power-outlets/")

        return outlets['results']

    def get_addresses(self):
        "Returns a nested dict of all registered hosts/interface/family = addresses"
        interface_addresses = collections.defaultdict(dict)
        for family in [4,6]:
            r = self.get(f"/ipam/ip-addresses/?family={family}")
            for addr in r['results']:
                host = addr['assigned_object']['device']['display']
                endpoint = addr['assigned_object']['name']
                if endpoint not in interface_addresses[host]:
                    interface_addresses[host][endpoint] = {}
                interface_addresses[host][endpoint][addr['family']['label']] = \
                    addr['address']

        return dict(interface_addresses)

    def get_interfaces(self):
        r = self.get(f"/dcim/interfaces/")

        interfaces = collections.defaultdict(dict)
        for interface in r['results']:
            device = interface['device']['name']
            interfaces[device][interface['display']] = interface

        return interfaces

