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

`nb-device`:
------------

`nb-device` dumps the details of a particular device, given its *Id*
which can be found from the first column of `nb-devices`. This
information will be critical when building a mapping file to be passed
to `np-update-ansible`. The output is a YAML structured array.

::

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

`nb-outlets`:
-------------

Displays the outlets used in the rack by devices. This is unfinished
(works but will change)

`nb-networks`:
--------------

Displays networks used in the rack by devices. This is unfinished (works
but will change)

`nb-check-ansible`:
-------------------

TBD
