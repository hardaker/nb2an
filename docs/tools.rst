NetBox data access tools
========================

The *nb2an* package contains a number of tools to access NetBox
configuration from within a shell.

.. _nb_racks:

`nb-racks`: Display the racks from NetBox
-----------------------------------------

Many later tools taken an option netbox rack number to evaluate. This
tools gives you a numbered list of all your racks.

::

   $ nb-racks
   Id  Name                      Site                 Location             #devs
   1   Rack1                     SEA                  DC1 Room 42          24
   2   Rack2                     AMS                  DC2 Room 1           10
   3   Rack3                     MIA                  DC9 Room Q            6

.. _nb_devices:

`nb-devices`: List the devices from Netbox
------------------------------------------

This tools lets all of the devices found in a rack, or if no rack number
is specified, will list all the devices in NetBox. Devices will be
listed in rack order from the top down, optionally with blank spots
listed when *-b* is specified.

::

   $ nb-devices 3
   Id  Pos Name                      Type
   40  40  firewall                  firewall-XX.YY
   41  39  switch                    Cisco ZZ
   42  38  webserver                 cpu2817
   43  37  backend1                  cpu2817
   44  36  database                  cpu2817
   45  35  backend2                  cpu2817

.. _nb_device:

`nb-device`: Show all the properties of a device in YAML form
-------------------------------------------------------------

`nb-device` dumps the details of a particular device, given its *Id*
which can be found from the first column of `nb-devices`. This
information will be critical when building a mapping file to be passed
to `np-update-ansible`. The output is a YAML structured array.

::

   $ nb-device 40
   airflow: null
   asset_tag: 31337
   cluster: null
   ...
   device_type:
     display: firewall-XX.YY
     id: 2
     manufacturer:
       display: firewall
       id: 2
   ...

`nb-parameters`: Show certain parameters of a device list
---------------------------------------------------------

`nb-parameters` dumps a formatted list of variables for all the
devices in the system or just a rack.

::

   $ nb-parameters device_type.display asset_tag
   firewall:
     device_type.display:    firewall-XX.YY
     asset_tag:              31337
   ...

It can also output `FSDB <https://github.com/gawseed/pyfsdb>`__ (tab
separated) formatted code as well:

::

   $ nb-parameters -f device_type.display asset_tag
   #fsdb -F t name device_type_display asset_tag
   firewall	firewall-XX.YY	31337
   ...


`nb-outlets`: Display the outlets used by rack devices
------------------------------------------------------

Displays the outlets used in the rack by devices. This is unfinished
(works but will change)

`nb-networks`:
--------------

Displays networks used in the rack by devices. This is unfinished (works
but will change)

`nb-check-ansible`:
-------------------

TBD
