Installation
============

You can use *pip* or *pipx* to install the nb2an tools:

::

   pipx install nb2an

.. _usage:

Usage
=====

Updating your ansible data from netbox requires the following steps.

Step 1: Create a nb2an configuration file
-----------------------------------------

The *nb2an* tools take a YAML-based master configuration file containing
your netbox API token (which you’ll need to get from your NetBox
instance). In this configuration file you can set a number of variables.
Note that some of these can be overridden with command line options.
Put this configuration in `${HOME}/.nb2an`:

.. code-block:: yaml

   # Your netbox API token:
   token: YOUR_NETBOX_API_TOKEN

   # what the API path is for your netbox install
   api_url: https://netbox/api/

   # domain suffix of your ansible FQDNs
   # (nb2an tools will check NetBox for simple and full names)
   suffix: .example.com

   # where the root of your ansible code is stored
   # nb2an can modify the host files inside host_vars after this path
   ansible_directory: /home/user/ansible

If you require HTTP's basic-auth, you can also add a *user* and
*password* configuration as well:

.. code-block:: yaml

   user: foo
   password: 'barily a password'

Step 2: create a YAML mapping file
----------------------------------

The `nb-update-ansible` tool is designed to only update variables within
your ansible host_vars that you ask it to, leaving everything else
(including comments) the same. Note that formatting is overwritten by
default, but see below for how to make a patch instead (actually TBD).

The YAML file consists of a host_vars YAML structure that you’d like to
have updated. Currently this supports only dictionaries, but array
support is coming shortly. The value of each variable should be a dotted
notation of where to pull the information from in the netbox data for a
given device. See the :ref:`nb_device` tool below for how to get a dump of a
device for easier reading.

Here’s an example mapping file, that updates or creates information in a
*host_info* section and a *netbox_info* section.

.. code-block:: yaml

   host_info:
       serial_number: serial
       site: site.name
       location: location.name
       rack: rack.display
       position: position
   netbox_info:
       id: id
       site_url: site.url

See the :ref:`advanced syntax` section for additional configuration
capabilities, such as for value modification via the `replace` function.

.. _np-update-ansible:

Step 3: Run *nb-update-ansible*
-------------------------------

**Note:** don’t forget to check in to your VC (*git*) any outstanding
changes you have to your files in *host_vars* before running this tool.

::

   $ np-update-ansible -c sample.yml
   INFO      : modifying /home/user/ansible/host_vars/firewall.example.com.yml

   $ cd /home/user/ansible/host_vars

   $ git diff
   diff --git a/host_vars/f1-lab.example.com.yml b/host_vars/firewall.example.com.yml
   --- a/host_vars/firewall.example.com.yml
   +++ b/host_vars/firewall.example.com.yml
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

Note about YAML formatting changes
----------------------------------

*np-update-ansible* currently reformats the YAML file with a standard
yaml rewriter. Although it leaves comments in place, white-space changes
will occur. You have two options to handle this:

1. Allow the formatter (python’s *ruamel.yaml* module) to rewrite the YAML
   files, as use their formatter as style convention (similar to how
   much of the planet is shifting to
   `black <https://pypi.org/project/black/>`__ for formatting python
   code). One suggesting for starting with this is passing in an empty
   mapping file, or by using the *-n* flag, which has the same effect.
   Then check that in and make a second pass with a real mapping file in
   order to see what changes are actually made.

2. Use `np-update-ansible` with its *-w* flag, which will make
   multiple passes and generate a white-space ignoring diff of your
   *host_vars* directory.  This will result it a patch that you can
   applie that will reduce the number of rewritten lines down to a
   much more restricted subset.  Essentially, the this diff won’t
   reformat much of the rest of the files because it’ll only consist
   of changes *only* made by *np-update-ansible*.
