Phase Start Dates
=================

Default Configuration
---------------------

By default, ``ProjectManager`` will run phases in the order that they are
defined in the lists ``'design_phases'``, then ``'install_phases'`` located in
the project configuration. This order also determines the sequence of phases in
the outputs, including the project level action log ``.project_dataframe``. If
the project is configured with a weather file, any installation phases will
start at the beginning of the weather profile.

.. code-block:: python

   config = {
       ...

       'design_phases': ['MonopileDesign', 'ArraySystemDesign'],
       'install_phases': [
           'MonopileInstallation',
           'TurbineInstallation'
       ]
   }

   >>>

   # ProjectManager will run the above phases in this order:
   # - MonopileDesign
   # - ArraySystemDesign
   # - MonopileInstallation
   # - TurbineInstallation

Defining Start Dates
--------------------

Installation phases can also be defined with optional start dates that will
determine which portion of the weather file to use and will affect the sequence
of outputs. This feature also allows phases to overlap if required.

.. code-block::


   {
      ...

      'design_phases': ['MonopileDesign', 'ArraySystemDesign'],
      'install_phases': {
         'MonopileInstallation': '03/01/2019',
         'TurbineInstallation': '05/01/2019'
      }
   }

In the example above, the turbine installation will start two months after
the monopile installation and use the weather profile starting on May 1st, 2019.
If any defined start dates fall outside of the bounds of a configured weather
profile, ``WeatherProfileError`` will be raised. If a simulation reaches the
end of a weather profile before it completes, ``WeatherProfileExhuasted`` will
be raised.

.. warning::

   At this time, ORBIT does not have any constraints on overlapping phases, so
   it is possible to configure an unrealistic project (eg. turbine installation
   completes before substructure installation).

.. note::

   It should also be noted that overlapping phases do not affect one another.
   Port constraints (eg. number of cranes available for loading) are applied per
   installation phase.
