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
