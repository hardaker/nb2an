.. _advanced syntax:

Advanced Syntax
===============

The YAML replacement syntax allows for functions to be called at
points in the tree.  The current functions are described below, with
examples.

The function to be called is indicated by having a dictionary
structure in the YAML file with a special `__function` keyword.  When
`nb2an` discovers this keyword, the remaining specification is passed
to the function in question.

replace
-------

Consider the simple replacement block that adds the NETBOX url to 
ansible:

.. code-block:: yaml

    netbox_info:
      device_url: url


The problem with this example is that the URL added includes a `/api`
prefix that is not helpful to someone clicking on the link.  The
following allows the `url` value to be modified to drop the `/api`
portion of the URL:

.. code-block:: yaml

    netbox_info:
      device_url:
        __function: replace
        value: url
        search: /api
        replacement: ''

delete
------

Allows the deletion of a section of host_vars YAML that should no
longer be present.  For example:

.. code-block:: yaml

    netbox_info:
      old_subkey_name:
        __function: delete

        
foreach_create_dict
-------------------

This allows you to build more complex dictionary structures within the
host_vars YAML based on a list from netbox.  This is most useful when
you wish to loop over *power_ports* or *interfaces* for example.  The
following fields are needed as function arguments:

*keyname*
  The dictionary created will use this field for each key created in
  the dictionary.

*array*
  The element list from netbox to be iterated over.  It must be a list
  of items.

*structure*
  In the definition, a *structure* element must be present that will be
  used for each iteration in a list.  This is functionally a template
  to be inserted at each key element.

As an example, consider the following `nb2an.yml` structure:

.. code-block:: yaml

    power:
      __function: foreach_create_dict
      array: power_ports
      keyname: display
      structure:
        pdu: connected_endpoint.device.display
        outlet: connected_endpoint.display

With this in place, if you have two power ports defined in netbox for
a device, it would create entries under a common *power* node with
each one based on the power port's display name.  The resulting
structure might look like this:

.. code-block:: yaml

    power:
      __function: foreach_create_dict
      array: power_ports
      keyname: display
      structure:
        pdu: connected_endpoint.device.display
        outlet: connected_endpoint.display

This could produce a host_vars YAML definition containing a structure
like this:

.. code-block:: yaml

    power:
      left:
        pdu: RP1
        outlet: PO-1
      right:
        pdu: RP2
        outlet: PO-2
