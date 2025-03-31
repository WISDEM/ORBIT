Vessels and Cable Definitions
=============================

Most installation modules require individual vessels, cables or turbines to be
defined to complete the required configuration. These definitions are composed
of several nested dictionaries (representing vessel subcomponents) that can be
cumbersome to define within the project level configuration. As such, there are
helper libraries included with ORBIT that allow vessels/cables to be defined
elsewhere and referenced with their name. By default, these libraries are
located at:

.. code-block::

   /path/to/orbit/library/cables/
   /path/to/orbit/library/vessels/
   /path/to/orbit/library/turbines/

External Libraries
------------------

It is possible to have ORBIT look in external folders for library items. To
configure an external library, use the ``initialize_library`` function. It is
recommended that any proprietary vessel or cable files be located outside
of the main repository.

.. code-block:: python

   from ORBIT.core.library import initialize_library
   initialize_library("path/to/external/library/")

.. note::

   If an external library is defined, ORBIT will search for a configured
   library item there first and then search the library defined within ORBIT if
   the item is not found. This is so that generic library items do not need to
   be copied to the external library but can still be used within a project
   definition.

File Format
-----------

Both vessels and cables are stored as ``.yaml`` files to preserve their
dictionary format. They can be referenced in project configurations using the
filename preceding ``.yaml``. For a filename of ``example_wtiv.yaml``, see the
example below:

.. code-block:: python

   config = {
       'wtiv': 'example_wtiv',

       'design_phases': ['MonopileDesign', 'ArraySystemDesign'],
       'install_phases': [
           'MonopileInstallation',
           'TurbineInstallation'
       ]
   }

For help on working with ``.yaml`` files, please see this
`tutorial <https://pyyaml.org/wiki/PyYAMLDocumentation>`_.

Vessel Configurations
---------------------

Throughout installation modules in ORBIT, there are several processes that
require the operating vessel to have a specific subcomponent. For example, all
offshore lifts require the vessel to have a crane onboard, otherwise the vessel
isn't able to perform the operation. These contraints translate into how
vessels are defined. Within a vessel definition (either a ``dict`` or a
``.yaml`` file), subcomponents are defined with another dictionary:

.. code-block:: python

   vessel = {
       'crane_specs': {  # <-- Vessel will be able to perform crane operations
           'max_lift': 500,
           'max_windspeed': 15,
           ...
       },

       ...

   }

In the example above, a vessel without ``'crane_specs'`` would not be able to
perform any crane operations. If a vessel is configured that can't complete an
operation in a phase, a ``MissingComponent`` error will be raised. The
following subcomponents and their use cases are available to be configured:

- ``'vessel_specs'`` - General vessel parameters including day rate.
- ``'transport_specs'`` - Transit related parameters and constraints.
- ``'storage_specs'`` - Storage related parameters. Required to transport items
  on deck.
- ``'jacksys_specs'`` - Jacking system related parameters. Currently required
  for all fixed substructure and turbine installations.
- ``'crane_specs'`` - Crane related parameters and constraints. Required for
  any offshore lifts.
