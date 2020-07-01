Mooring System Installation Methodology
=======================================

For details of the code implementation, please see
:doc:`Mooring System Installation API <api_MooringSystemInstallation>`.

Overview
--------

The ``MooringSystemInstallation`` module simulates the installation of mooring
lines and anchors at site for a floating offshore wind project. The mooring
system installation is simulated using a multi-purpose support vessel that
transports the components to site and performs the onsite installation
procedures.

Configuration
-------------

The primary configuration parameters available for this module are the
installation vessel and the mooring system configuration. An example of these
parameters is presented below.

.. code-block:: python

   config = {


       "mooring_install_vessel": "example_support_vessel",
       "mooring_system": {
           "num_lines": 4,      # per substructure
           "line_mass": 500,    # t
           "anchor_mass": 500,  # t
           "anchor_type": "Drag Embedment",  # or "Suction Pile"
       }
       ...
   }

Processes
---------

The default times associated with the installation procedure are listed in the
table below.

+---------------------------+---------------------------------+--------------+
|          Process          |            Inputs               |  Default     |
+===========================+=================================+==============+
| Loadout                   | ``mooring_system_load_time``    | 5h           |
+---------------------------+---------------------------------+--------------+
| Transit                   | ``vessel.transit_speed``        | calculated   |
+---------------------------+---------------------------------+--------------+
| Survey                    | ``mooring_site_survey_time``    | 3h           |
+---------------------------+---------------------------------+--------------+
| Install Anchor (repeated) | | ``suction_pile_install_time`` | calculated   |
|                           | | ``drag_embed_install_time``   |              |
+---------------------------+---------------------------------+--------------+
| Install Line (repeated)   | NA                              | calculated   |
+---------------------------+---------------------------------+--------------+
| Transit                   | ``vessel.transit_speed``        | calculated   |
+---------------------------+---------------------------------+--------------+
