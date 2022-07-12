# nb2an: Netbox to Ansible

[NetBox](https://www.netbox.dev/) and
[Ansible](https://www.ansible.com/) both require a lot of manual
configuration, often with duplicate information. Keeping them in sync
can be a daunting challenge. The **nb2an** package provides utilities to
map NetBox values to ansible *host_vars* using a simple mapping file.

Read the [full documentation online](https://nb2an.readthedocs.io/en/latest/)

# Installation

You can use *pip* or *pipx* to install the nb2an tools:

    pipx install nb2an

# Usage

Updating your ansible data from netbox requires the following steps.

## Step 1: Create a nb2an configuration file

*nb2an* tools take a YAML-based master configuration file containing
your netbox API token (which you'll need to get from your NetBox
instance). In this configuration file you can set a number of variables.
Note that some of these can be overridden with command line options.

``` yaml
# Your netbox API token:
token: YOUR_NETBOX_API_TOKEN

# what the API path is for your netbox install
api_url: https://netbox/api/

# domain suffix of your ansible FQDNs
# (nb2an tools will check NetBox for simple and full names)
suffix: .example.com

# where th eroot of your ansible code is stored
ansible_directory: /home/user/ansible
```

## Step 2: create a YAML mapping file

The *nb-update-ansible* tool is designed to only update variables within
your ansible host_vars that you ask it to, leaving everything else
(including comments) the same. Note that formatting is overwritten by
default, but see below for how to make a patch instead (actually TBD).

The YAML file consists of a host_vars YAML structure that you'd like to
have updated. Currently this supports only dictionaries, but array
support is coming shortly. The value of each variable should be a dotted
notation of where to pull the information from in the netbox data for a
given device. See the *nb-device* tool below for how to get a dump of a
device for easier reading.

Here's an example mapping file, that updates or creates information in a
*host_info* section and a *netbox_info* section.

``` yaml
host_info:
    serial_number: serial
    site: site.name
    location: location.name
    rack: rack.display
    position: position
netbox_info:
    id: id
    site_url: site.url
```

## Step 3: Run *nb-update-ansible*

**Note:** don't forget to check in to your VC (*git*) any outstanding
changes you have to your files in *host_vars* before running this tool.

    $ np-update-ansible -c sample.yml
    INFO      : modifying /home/user/ansible/host_vars/firewall.example.com.yml

    $ cd /home/user/ansible/host_vars

    $ git diff
    diff --git a/host_vars/f1-lab.example.com.yml b/host_vars/f1-lab.example.com.yml
    --- a/host_vars/f1-lab.example.com.yml
    +++ b/host_vars/f1-lab.example.com.yml
    +host_info:
    +  serial_number: 00112233
    +  site: MIA
    +  location: DC9 Room Q
    +  rack: Rack1
    +  position: 40
    +netbox_info:
    +  id: 37
    +  device_url: https://netbox/api/device/37/
    +  site_url: https://netbox/api/dcim/sites/7/

Profit!

## Note about YAML formatting changes

*np-update-ansible* currently reformats the YAML file with a standard
yaml rewriter. Although it leaves comments in place, white-space changes
will occur. You have two options to handle this:

1.  Allow the formatter (python's *ruamel.yaml*) to rewrite the YAML
    files, as use their formatter as style convention (similar to how
    much of the planet is shifting to
    [black](https://pypi.org/project/black/) for formatting python
    code). One suggesting for starting with this is passing in an empty
    mapping file, or by using the *-n* flag, which has the same effect.
    Then check that in and make a second pass with a real mapping file
    in order to see what changes are actually made.

2.  Generate a diff from *np-update-ansible -n mapping.yml* and
    *np-update-ansible mapping.yml* and use the diff to view and apply
    changes. The recursive diff won't reformat much of the rest of the
    file because it'll only consist of changes *only* made by
    *np-update-ansible*.

    TODO: auto version of this coming...

# Data access with the nb-\* tools

The *nb2an* package contains a number of tools to access NetBox
configuration from within a shell.

## nb-racks: Display the racks from NetBox

Many later tools taken an option netbox rack number to evaluate. This
tools gives you a numbered list of all your racks.

    $ nb-racks
    Id  Name                      Site                 Location             #devs
    1   Rack1                     SEA                  DC1 Room 42          24
    2   Rack2                     AMS                  DC2 Room 1           10
    3   Rack3                     MIA                  DC9 Room Q            6

## nb-devices: List the devices from Netbox

This tools lets all of the devices found in a rack, or if no rack number
is specified, will list all the devices in NetBox. Devices will be
listed in rack order from the top down, optionally with blank spots
listed when *-b* is specified.

    $ nb-devices 3
    Id  Pos Name                      Type
    40  40  firewall                  firewall-XX.YY
    41  39  switch                    Cisco ZZ
    42  38  webserver                 cpu2817
    43  37  backend1                  cpu2817
    44  36  database                  cpu2817
    45  35  backend2                  cpu2817

## nb-device:

*nb-device* dumps the details of a particular device, given its *Id*
which can be found from the first column of *nb-devices*. This
information will be critical when building a mapping file to be passed
to *np-update-ansible*. The output is a YAML structured array.

    $ nb-device 40
    airflow: null
    asset_tag: null
    cluster: null
    ...
    device_type:
      display: firewall-XX.YY
      id: 2
      manufacturer:
        display: firewall
        id: 2
    ...

## nb-outlets:

Displays the outlets used in the rack by devices. This is unfinished
(works but will change)

## nb-networks:

Displays networks used in the rack by devices. This is unfinished (works
but will change)

## nb-check-ansible:

TBD
