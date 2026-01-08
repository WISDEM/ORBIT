Working with ORBIT Modules and Projects
=======================================

ORBIT is made up of many different modules representing the design and
installation of offshore wind components. Each module can be ran indepenently
or within a project using :ref:`ProjectManager <manager>`. Modules and
projects are configured with a set of nested dictionaries.

Running Individual Modules
--------------------------

To run a module indepenently:

.. code-block:: python

   from ORBIT.phases.install import MonopileInstallation
   config = {
       'site': {
           'depth': 20,
           'mean_windspeed': 9
       },

       'turbine': {
           'rotor_diameter': 130,
           'hub_height': 110,
       },

       # etc...
   }

   phase = MonopileInstallation(config)
   phase.run()
   print(phase.total_cost)

The inputs required for each module are stored in ``expected_config``.
For example:

.. code-block:: python

   from ORBIT.phases.install import MonopileInstallation
   MonopileInstallation.expected_config

   >>>

   {
       'site': {
           'depth': 'm',
           'mean_windspeed': 'm/s'
       },

       'turbine': {
           'rotor_diameter': 'm',
           'hub_height': 'm',
       },
       # etc...
   }

The returned nested dictionary can then be filled out by replacing the strings
('m', 'm/s', etc.) with the appropriate inputs for the analysis question.

.. note::

   `expected_config` will return the required unit of the input where applicable.

Loading and Saving Configurations
---------------------------------

There are utility functions within ORBIT that allow configurations to be saved
and loaded from a '.yaml' format. Yaml is a data format similar to json in that
it can store nested data structures. Yaml has several advantages though, the
primary being that it supports comments.

To load a configuration:

.. code-block:: python

   from ORBIT import load_config
   config = load_config("filepath/to/config.yaml")

To save a configuration:

.. code-block:: python

   from ORBIT import save_config
   save_config(config, "filepath/to/config.yaml")

.. note::

   It isn't required to use these utility functions. The standard yaml load and
   dump routines will work for converting python nested dictionaries to and from
   the yaml format. However, the ``load_config`` method supports scientific
   notation and the standard yaml routine does not.

Running Multiple Phases
-----------------------

To run multiple phases, see the :ref:`ProjectManager <manager>` documentation.
