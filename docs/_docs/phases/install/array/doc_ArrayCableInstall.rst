Array Cabling System Installation Methodology
=============================================

For details of the code implementation, please see
:doc:`Array Cable Installation API <api_ArrayCableInstallation>`.

Overview
--------

The `ArrayCableInstallation` module simulates the installation of array cable
sections between turbines at site. This process one of the critical
installation phases in the construction of a wind farm as testing and final
commisioning of the turbines can't occur until it is complete.

The installation of cables offshore is a complex process, often very dependent
on geotechnical parameters of the seabed along the cable route. Modeling all of
these considerations is outside of the scope of ORBIT, but this module was
designed to be able to explore the impacts of the major design choices. The
following sections detail the different installation methods that are available
and in what circumstances they are applicable.

Input Structure
---------------

The design of the input data structure for this module allows the user to
define site specific array cable configurations. For each cable type, a list
of cable sections can be defined. The installation vessel will install each
section individually and the time to complete this operation is dynamic based
on the length and the linear density of the cable, site depth, etc.

For example,

.. code-block::

   {
       'array_system': {
           'cables': {'XLPE_400mm_33kV': {
               'cable_sections': [
                    (1.7958701547, 2),  # There are two 1.79km sections,
                    (1.118, 16),        # 16 1.118km sections
                    (1.2128290583, 2)   # and two 1.213km sections
               ],
               'linear_density': 35
           }
       }
   }

The installation of each section above will be modeled seperately. In the above
example, only one cable was used, though there could be additional defined
cables (with their own `cable_sections` key).

Configuration
-------------

ORBIT considers two installation strategies: a simultaneous lay/bury operation
using modern cable installation vessels; and a seperated operation where one
vessel lays the cable and another follows behind to bury it. A detailed
description of the applicability of each strategy is covered in the ORBIT
technical `report <todo>`_.

To configure the installation strategy, the `'strategy'` parameter must be
passed into the module:

.. code-block::

   {
       'array_system': {
           # 'strategy': 'lay'     # Vessel will lay the cable ont he seafloor
           # 'strategy': 'bury'    # Vessel will perform the burying operations
           'strategy': 'lay_bury'  # Vessel will perform simultaneous lay/bury operations

           'cables': {'XLPE_400mm_33kV': {
               ...
           }
       }
   }

Processes
---------

The speed at which a vessel can perform the operations of each installation
strategy is determined by the vessel properties, passed kwargs or the
default speed for the process.

+------------------+--------------------------+------------+
| Strategy         | Key                      | Default    |
+==================+==========================+============+
| Lay/Bury Cable   | ``cable_lay_bury_speed`` | 0.3 km/hr  |
+------------------+--------------------------+------------+
| Lay Cable        | ``cable_lay_speed``      | 1 km/hr    |
+------------------+--------------------------+------------+
| Bury Cable       | ``cable_bury_speed``     | 0.5 km/hr  |
+------------------+--------------------------+------------+

Other operations in the installation process are determined by default values:

+-----------------+----------------------------+---------+
|     Process     |            Key             | Default |
+=================+============================+=========+
| Position Onsite | ``site_position_time``     | 2h      |
+-----------------+----------------------------+---------+
| Prepare Cable   | ``cable_prep_time``        | 1h      |
+-----------------+----------------------------+---------+
| Lower Cable     | ``cable_lower_time``       | 1h      |
+-----------------+----------------------------+---------+
| Pull in Cable   | ``cable_pull_in_time``     | 5.5h    |
+-----------------+----------------------------+---------+
| Test Cable      | ``cable_termination_time`` | 5.5h    |
+-----------------+----------------------------+---------+

Configuration Examples
~~~~~~~~~~~~~~~~~~~~~~

Coming soon!

Process Diagrams
----------------

.. image:: ../../../../images/process_diagrams/ArrayCableInstall.png
