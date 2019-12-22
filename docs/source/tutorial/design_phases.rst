Design Phases
=============

There are two types of modules within ORBIT, design phases and installation
phases. Installation phases require a number of inputs, setup a simulation and
model the installation of offshore wind components. Alternatively, design
phases model the design of an offshore wind components and can produce inputs.
Within the context of ``ProjectManager``, a design phase can remove inputs from
the required configuration for a project. The following example will illustrate
this feature and how it is used within ``ProjectManager``.

.. warning::

   Design phase modules in ORBIT are intended to capture broad scaling trends
   for offshore wind components and do not represent the required fidelity of a
   full design.

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
           'weight': 'float'
       },

       'transition_piece': {
           'type': 'Transition Piece',
           'deck_space': 'float',
           'weight': 'float'
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