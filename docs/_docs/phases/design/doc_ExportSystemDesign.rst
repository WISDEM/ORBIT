Export System Design Methodology
================================

For details of the code implementation, please see
:doc:`Export System Design API <api_ExportSystemDesign>`.

Overview
--------
For more details on the helper classes used to support
this design please see: :doc:`Cabling Helper Classes <doc_CableHelpers>`,
specifically :class:`Cable` and :class:`CableSystem`.

Below is an overview of the whole process to create an export cabling
system. In the following sections, each piece will be reviewed in
greater detail.

.. image:: ../../../images/process_diagrams/ExportSystemDesign.png


Determine the number of required export cables
----------------------------------------------
To fully connect the windfarm we must determine the minimum required cables by
dividing the windfarm's capacity by an individual cable's power rating and then
add any user defined redundnacy as can be seen below.

:py:attr:`num_cables` :math:`\ =\ \lceil` :py:attr:`plant_capacity` :math:`/` :py:attr:`cable_power` :math:`\rceil\ +` :py:attr:`num_redundant`.


Determine the length of a single export cable
---------------------------------------------
To determine the total length of a single export cable the site depth, distance
between the site and landfall and the distance to the interconnection point must
be added, then add on any exclusions, which are given by a percentage of three
above components. This can be seen below.

:py:attr:`length` :math:`\ =\ ((` :py:attr:`depth` :math:`\ /\ `1000) +` :py:attr:`distance_to_landfall` :math:`+` :py:attr:`distance_to_interconnection` :math:`)\ *\ (1\ +` :py:attr:`percent_added_length` :math:`)`

Using the length of a single export cable the mass of each cable can be
computed from the the cable's :py:attr:`linear_density`. Using the length,
mass, and number of cables a :py:attr:`design_result` can be exported and
passed to the
:doc:`export cable installation simulation <../install/export/doc_ExportCableInstall>`.

References
----------
