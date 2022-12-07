import os
import yaml
import requests
import collections
from typing import Union
from logging import debug, error
from rich import print

default_url = "https://netbox/api"
default_config_path = os.path.join(os.environ.get("HOME"), ".nb2an")


class Netbox:
    "An interface to Netbox to extract data needed for nb2an to function"

    def __init__(
        self,
        api_url=default_url,
        config_path=default_config_path,
        ansible_dir=None,
        suffix=None,
    ):
        self.config_path = config_path
        self.config = {}
        if os.path.exists(self.config_path):
            self.config = self.get_config()
        else:
            error(f"you must create a {self.config} configuration file first")
            exit(1)
        self.prefix = self.config.get("api_url", api_url)
        self.suffix = self.config.get("suffix", suffix)
        self.ansible_dir = self.config.get("ansible_dir", ansible_dir)
        self.url_cache = {}
        self.devices_by_id = {}
        self.devices_by_name = {}

        self.data = {}

    def get_config(self):
        debug(f"loading config from {self.config_path}")
        content = open(self.config_path).read()
        # debug(f"{content=}")
        results = yaml.safe_load(str(open(self.config_path).read()))
        return results

    def fqdn(self, hostname):
        if not self.suffix:
            return hostname
        if not hostname.endswith(self.suffix):
            hostname = hostname + self.suffix
        return hostname

    def shortname_name(self, hostname):
        if hostname.endswith(self.suffix):
            return hostname[0 : -len(self.suffix)]
        return hostname

    def get_cached_device_by_name(self, hostname):
        # try whatever they passed
        if hostname in self.devices_by_name:
            return self.devices_by_name[hostname]

        # try shorter
        shorter = self.shortname_name(hostname)
        if shorter in self.devices_by_name:
            return self.devices_by_name[shorter]

        # try longer
        fqdn = self.fqdn(hostname)
        if fqdn in self.devices_by_name:
            return self.devices_by_name[fqdn]

        return None  # whoops

    def get(self, url: str, use_cache: bool = True, strip_results: bool = True):
        "fetch data from a URL, and potentially cache the results"
        if not url.startswith("http"):
            url = self.prefix + url

        if use_cache and url in self.url_cache:
            debug(f"returning cached: {url}")
            return self.url_cache[url]
        debug(f"fetching: {url}")

        c = self.config
        headers = {"Authorization": f"Token {c['token']}"}
        auth = None
        if "user" in c and "password" in c:
            auth = (c["user"], c["password"])

        # debug(f"headers: {headers}")
        verify = self.config.get("verify", True)

        if not verify:
            # disable the warning screen if the user doesn't want validation
            import urllib3

            urllib3.disable_warnings()

        # get the contents
        r = requests.get(url, headers=headers, auth=auth, verify=verify)
        r.raise_for_status()

        # maybe cache them
        encoded_results = r.json()
        if strip_results:
            encoded_results = encoded_results["results"]
        if use_cache:
            self.url_cache[url] = encoded_results

        return encoded_results

    def get_racks(self):
        results = self.get("/dcim/racks")
        return results

    def get_devices(
        self,
        racknums: Union[list[int], int] = None,
        link_other_information: bool = False,
    ):
        if isinstance(racknums, int):
            racknums = [racknums]

        devices = []
        if racknums:
            for racknum in racknums:
                rack_devices = self.get("/dcim/devices/?rack_id=" + str(racknum))
                devices.extend(rack_devices)
        else:
            all_devices = self.get("/dcim/devices/")
            devices.extend(all_devices)

        if link_other_information:
            devices = self.link_device_data(devices)
        return devices

    def get_devices_by_id(
        self,
        devices: Union[list[int], int] = None,
        link_other_information: bool = False,
    ):
        "Given a device ID, grab the device's info from the API"
        if isinstance(devices, int):
            devices = [devices]

        # assume we want all devices
        if devices is None or devices == []:
            devices = [x["id"] for x in self.get_devices()]

        # grab each device in turn
        results = []
        for device in devices:
            debug(f"looking for device {device} by id")
            if device in self.devices_by_id:
                results.append(self.devices_by_id[device])
                continue

            the_devices = self.get("/dcim/devices/" + str(device), strip_results=False)
            results.append(the_devices)

        # link in other things
        if link_other_information:
            results = self.link_device_data(results)

        return results

    def get_devices_by_name(
        self,
        devices: Union[list[str], str] = None,
        link_other_information: bool = False,
    ):
        if isinstance(devices, str):
            devices = [devices]

        # assume we want all devices
        if devices is None or devices == []:
            devices = [x["id"] for x in self.get_devices()]

        results = []
        for device in devices:
            debug(f"looking for device {device} by name")
            cached = self.get_cached_device_by_name(device)
            if cached:
                results.append(cached)
                continue
            the_device = self.get("/dcim/devices/?name=" + str(device))
            if (not the_device or len(the_device) != 1) and device.endswith(
                self.suffix
            ):
                # retry without a FQDN suffix
                device = device[0 : -len(self.suffix)]
                the_device = self.get("/dcim/devices/?name=" + str(device))[0]
            elif not the_device:
                # retry WITH a FQDN
                device = self.fqdn(device)
                the_device = self.get("/dcim/devices/?name=" + str(device))[0]
            else:
                the_device = the_device[0]

            if the_device:
                results.append(the_device)

        if link_other_information:
            results = self.link_device_data(results)

        return results

    # generic grabber for things attached to a device
    def get_device_components_by_device_id(self, component: str, device_id: int):
        self.bootstrap_all_data()
        objects = self.data[component]

        results = []
        for obj in objects:
            try:
                if obj["connected_endpoint"]["device"]["id"] == device_id:
                    results.append(obj)

            except Exception:
                pass
        return results

    def get_device_components_by_device_name(self, component: str, device_name: int):
        self.bootstrap_all_data()
        objects = self.data[component]

        results = []
        for obj in objects:
            try:
                if obj["connected_endpoint"]["name"] == device_name:
                    results.append(obj)
            except Exception:
                pass
        return results

    # Outlets
    def get_outlets(self):
        self.bootstrap_all_data()
        return self.data["outlets"]

    @property
    def outlets(self):
        return self.get_outlets()

    def get_outlets_by_device_id(self, device: int):
        return self.get_device_components_by_device_id("outlets", device)

    def get_outlets_by_device_name(self, device: str):
        return self.get_device_components_by_device_name("outlets", device)

    # power ports
    def get_power_ports(self, device: int = None):
        self.bootstrap_all_data()
        return self.data["power_ports"]

    @property
    def power_ports(self):
        return self.get_power_ports()

    def get_power_ports_by_device_id(self, device: int):
        return self.get_device_components_by_device_id("power_ports", device)

    def get_power_ports_by_device_name(self, device: str):
        return self.get_device_components_by_device_name("power_ports", device)

    def get_addresses(self) -> dict:
        "Returns a nested dict of all registered hosts/interface/family = addresses"
        interface_addresses = collections.defaultdict(dict)
        for family in [4, 6]:
            r = self.get(f"/ipam/ip-addresses/?family={family}")
            for addr in r:
                host = addr["assigned_object"]["device"]["display"]
                endpoint = addr["assigned_object"]["name"]
                if endpoint not in interface_addresses[host]:
                    interface_addresses[host][endpoint] = {}
                interface_addresses[host][endpoint][addr["family"]["label"]] = addr[
                    "address"
                ]

        return dict(interface_addresses)

    def get_interfaces(self) -> list:
        r = self.get(f"/dcim/interfaces/?limit=100000000")

        interfaces = collections.defaultdict(dict)
        for interface in r:
            device = interface["device"]["name"]
            interfaces.setdefault(device,[]).append(interface)

        return interfaces

    def bootstrap_all_data(self) -> None:
        "pre-fetch all netbox data"
        if "interfaces" not in self.data:
            self.data["interfaces"] = self.get_interfaces()

        if "addresses" not in self.data:
            self.data["addresses"] = self.get_addresses()

        if "devices" not in self.data:
            self.data["devices"] = self.get_devices()

        self.data["outlets"] = self.get("/dcim/power-outlets/")
        self.data["power_ports"] = self.get("/dcim/power-ports/")

        if "power_ports" not in self.data:
            self.data["power_ports"] = self.get_power_ports()

    def link_device_data(self, devices=None) -> dict:
        self.bootstrap_all_data()
        if not devices:
            devices = self.data["devices"]

        for device in devices:
            if device["name"] in self.data["interfaces"]:
                device["interfaces"] = self.data["interfaces"][device["name"]]
            if device["name"] in self.data["addresses"]:
                device["addresses"] = self.data["addresses"][device["name"]]

            device["power_ports"] = []
            for port in self.data["power_ports"]:
                if port["device"]["name"] == device["name"]:
                    device["power_ports"].append(port)

            self.devices_by_id[device["id"]] = device
            self.devices_by_name[device["name"]] = device

        return devices

    def get_interfaces_by_device_name(self, device_name: str) -> dict:
        self.bootstrap_all_data()

        interfaces = self.data["interfaces"][device_name]
        return interfaces
