.. _manager:

ProjectManager
==============

``ProjectManager`` is the primary system for interacting with ORBIT. It
provides the ability to configure and run one or multiple modules at a time,
allowing the user to customize ORBIT to fit the needs of a specific project.
It also provides a helper method to detail what inputs are required to run the
desired configuration. The example below shows how to import
``ProjectManager``, configure a simple project with two phases, and return the
required configuration parameters.

.. code-block:: python

   from ORBIT import ProjectManager

   phases = [
       "MonopileDesign",       # Returns monopile sizing given site information
       "MonopileInstallation"  # Simulates the installation of monopiles
   ]

   expected_config = ProjectManager.compile_input_dict(phases)
   expected_config

   >>>

   {
       'site': {
           'depth': 'm',
           'mean_windspeed': 'm/s'
       },

       'turbine': {
           'rotor_diameter': 'm',
           'hub_height': 'm',
           'rated_windspeed': 'm/s'
       },

       'monopile_design': {'air_density': 'kg/m3 (optional)',
                     'load_factor': 'float (optional)',
                     'material_factor': 'float (optional)',
                     'monopile_density': 'kg/m3 (optional)',
                     'monopile_modulus': 'Pa (optional)',
                     'monopile_steel_cost': 'USD/t (optional)',
                     'monopile_tp_connection_thickness': 'm (optional)',
                     'soil_coefficient': 'N/m3 (optional)',
                     'tp_steel_cost': 'USD/t (optional)',
                     'transition_piece_density': 'kg/m3 (optional)',
                     'transition_piece_length': 'm (optional)',
                     'transition_piece_thickness': 'm (optional)',
                     'turb_length_scale': 'm (optional)',
                     'weibull_scale_factor': 'float (optional)',
                     'weibull_shape_factor': 'float (optional)',
                     'yield_stress': 'Pa (optional)'},
       ...

       'design_phases': ['MonopileDesign'],
       'install_phases': ['MonopileInstallation']
   }

``expected_config`` contains all parameters that are required to run the
``MonopileDesign`` and ``MonopileInstallation`` phases (as well as the optional
ones in the ``monopile_design`` sub dictionary). The returned dictionary can
now be filled out and the model can be ran:

.. code-block:: python

   ...

   config = {
       'site': {
           'depth': 20,
           'mean_windspeed': 9.5,
       },

       'turbine': {
           'rotor_diameter': 205,
           'hub_height': 125,
           'rated_windspeed': 11
       },

       'monopile_design': {},

       'design_phases': ['MonopileDesign'],
       'install_phases': ['MonopileInstallation']
   }

   project = ProjectManager(config)
   project.run()

   # .design_results returns the results of all design phases that were ran
   project.design_results

   >>>

   {
       'monopile': {
           'diameter': 7.11,            # m
           'thickness': 0.078,          # m
           'embedment_length': 55.84,   # m
           'length': 85.84,             # m
           'mass': 640.57,              # t
           'deck_space': 5.58,          # m2
           'type': 'Monopile'
       }
   }

.. note::

  To include weather in the simulation, pass an hourly pandas DataFrame into
  ``ProjectManager``. Eg. ``ProjectManager(config, weather=weather_df)``. All
  installation phases will use this time series.

Design Modules
--------------

For a more detailed description of design modules and the interaction with
installation modules, please see the :ref:`Design Phases <design_modules>`
documentation.
