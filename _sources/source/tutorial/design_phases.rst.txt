.. _design_modules:


Design Modules
==============

There are two types of modules within ORBIT, design and installation.
Installation modules require a number of inputs, setup a simulation and
model the installation of offshore wind components. Alternatively, design
modules model the design of an offshore wind components and can produce inputs.
Within the context of ``ProjectManager``, a design module can remove inputs from
the required configuration for a project. The following example will illustrate
this feature and how it is used within ``ProjectManager``.

.. warning::

   Design phase modules in ORBIT are intended to capture broad scaling trends
   for offshore wind components and do not represent the required fidelity of a
   full engineering design.

Example
-------

Consider a simple project with one monopile installation phase:

.. code-block:: python

   from ORBIT import ProjectManager

   phases = [
       "MonopileInstallation",  # Monopile installation with one vessel
   ]

   required_config = ProjectManager.compile_input_dict(phases)
   required_config

   >>>

   {
       'wtiv': 'dict | str',

       'site': {'depth': 'float','distance': 'float'},
       'plant': {'num_turbines': 'int'},
       'turbine': {'hub_height': 'float'},

       'port': {
           'num_cranes': 'int',
           'monthly_rate': 'float',
           'name': 'str (optional)'
       },

       'monopile': {
           'type': 'Monopile',
           'length': 'float',
           'diameter': 'float',
           'deck_space': 'float',
           'mass': 'float'
       },

       'transition_piece': {
           'type': 'Transition Piece',
           'deck_space': 'float',
           'mass': 'float'
       },

       'design_phases': [],
       'install_phases': ['MonopileInstallation']
   }

In the required configuration for the above project, the user must fill in a
``'monopile'`` sub dictionary. Alternatively, a ``MonopileDesign`` phase could
be included in the phase list. This additional phase would effectively fill in
the ``'monopile'`` sub dictionary for the user:

.. code-block:: python

   ...

   phases = [
       "MonopileDesign",  # Basic monopile sizing based on turbine size and site
       "MonopileInstallation",  # Monopile installation with one vessel
   ]

   required_config = ProjectManager.compile_input_dict(phases)
   required_config

   >>>

   {

      ...

       'turbine': {
           'hub_height': 'float',
           'rotor_diameter': 'float',  # <-- Additional input from MonopileDesign
           'rated_windspeed': 'float'
       },

       ...
                                       # <-- 'monopile' no longer required

       'monopile_design': {
           'design_time': 'float (optional)',
           ...
       },

       'design_phases': ['MonopileDesign'],
       'install_phases': ['MonopileInstallation']
   }

.. note::

   There may be additional inputs required for a design phase. In this example,
   additional site level information (eg. ``turbine.rotor_diameter``) is added
   to the required configuration when the ``MonopileDesign`` phase is added to
   the phase list.

Overriding Values from a Design Phase
-------------------------------------

In the example above, the ``MonopileDesign`` phase will produce the input
parameters ``'monopile'`` and ``'transition_piece'``. It is also possible to
supply some of the values for these designs if known and let ``MonopileDesign``
fill in the rest. For example, if the user knows the dimensions of the monopile
but not the transition piece, the ``'monopile'`` dictionary can be added to the
project config above:

.. code-block:: python

   config {

       'turbine': {
           'hub_height': 130,
           'rotor_diameter': 154,  # <-- Additional input from MonopileDesign
           'rated_windspeed': 11
       },

       'monopile': {               # <-- 'monopile' isn't required but can be
           'type': 'Monopile',     #     added to include known project parameters.
           'mass': 800,            #     Other inputs produced by MonopileDesign will
           'length': 100           #     be added to the config.
       },

       ...

       'monopile_design': {
           'design_time': 'float (optional)',
           ...
       },

       'design_phases': ['MonopileDesign'],
       'install_phases': ['MonopileInstallation']
   }

   project = ProjectManager(config)
   project.run()

   project.config

   >>>

   {

   ...

       'monopile': {
           'type': 'Monopile',
           'mass': 800,
           'length': 100,
           'diameter': 8.512,      # <-- Additional inputs added by MonopileDesign
           'deck_space': 36.245    #
       },
   }
