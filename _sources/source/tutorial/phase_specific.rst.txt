Phase Specific Configurations
=============================

By default, ``ProjectManager.compile_input_dict()`` returns the minimum
required configuration, combining the same parameter that is needed for
multiple phases into one input. This isn't always a desired outcome as there
are cases when inputs need to be different for each phase. For example, the
``distance_to_shore`` parameter may be different for each installation phase
if different ports are used to stage monopiles and turbines or the
installations may use different installation vessels. In these cases, it is
necessary to define phase specific input parameters.

Example
-------

Consider the following example with two installation phases:

.. code-block:: python

   config = {
       'wtiv': 'example_wtiv',
       'site': {
           'depth': 20,
           'distance': 100
       },

       ...

       'design_phases': [],
       'install_phases': [
           'MonopileInstallation',
           'TurbineInstallation'
       ]
   }

In the above configuration, the same input parameters for the site and the WTIV
will be used for both installations. In order to modify this configuration to
include phase specific inputs, the phase namespace (eg. ``TurbineInstallation``)
must be introduced into the configuration:

.. code-block:: python

   config = {
       'wtiv': 'example_wtiv',
       'site': {
           'depth': 20,
           'distance': 50
       },

       ...

       'TurbineInstallation': {        # <-- Turbine installation namespace
           'wtiv': 'other_wtiv',       # <-- Vessel defined specific to namespace
           'site': {
               'distance': 100         # <-- Distance to port defined specific
           }                           #     to namespace

       'design_phases': [],
       'install_phases': [
           'MonopileInstallation',
           'TurbineInstallation'
       ]
   }


In the above example, the turbine installation has inputs for the WTIV and site
distance defined specific to it's namespace. Notice that the structure of the
``TurbineInstallation`` follows the same structure as the overall
configuration. Any input parameter (no matter how many dictionaries down) can
be defined specific to each phase using this method. When the model is run with
``project.run()`` ORBIT will use the most specific parameter available
in the input configuration for each of the inputs. Phase specific parameters
always take precedence over the more general configuration.

.. .. note::

..    Using the concepts above and overlapping start dates, complex phase
..    sequencing can be modeled with ORBIT. For an example of this, please see this
..    `validation case <todo>`_.
