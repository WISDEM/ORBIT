Electrical System Design Methodology
====================================

For details of the code implementation, please see
:doc:`Electrical System Design API <api_ElectricalDesign>`.

Overview
--------

Below is an overview of the process used to design an export cable system and
offshore substation in ORBIT. For more detail on the helper classes used to
support this design please see :doc:`Cabling Helper Classes <doc_CableHelpers>`,
specifically :class:`Cable` and :class:`CableSystem`.


Number of Required Cables
---------
The number of export cables required is calculated by dividing the windfarm's
capacity by the configured export cable's power rating and adding any user
defined redundnacy as seen below.

:math:`num\_cables = \lceil\frac{plant\_capacity}{cable\_power}\rceil + num\_redundant`


Export Cable Length
---------
The total length of the export cables is calculated as the sum of the site
depth, distance to landfall and distance to interconnection multiplied by the
user defined :py:attr`percent_added_length` to account for any exclusions or
geotechnical design considerations that make a straight line cable route
impractical.

:math:`length = (d + distance_\text{landfall} + distance_\text{interconnection}) * (1 + length_\text{percent_added})`


Number of Required Power Transformer and Tranformer Rating
---------
The number of power transformers required is assumed to be equal to the number
of required export cables. The transformer rating is calculated by dividing the
windfarm's capacity by the number of power transformers.


Shunt Reactors and Reactive Power Compensation
---------
The shunt reactor cost is dependent on the amount of reactive power compensation
required based on the distance of the substation to shore. There is assumed to be
one shunt reactor for each HVAC export cable. HVDC export systems do not require
reactive power compensation, thus the shunt reactor cost is zero for HVDC systems.


Number of Required Switchgears
---------
The number of shunt reactors required is assumed to be equal to the number of
required export cables.


Number of Required AC\DC Converters
---------
AC\DC converters are only required for HVDC export cables. The number of converters
is assumed to be equal to the number of HVDC export cables.


Cable Crossing Cost
---------
Optional inputs for both number of cable crossings and unit cost per cable
crossing.  The default number of cable crossings is 0 and cost per cable
crossing is $500,000. This cost includes materials, installation, etc. Crossing
cost is calculated as product of number of crossings and unit cost.


Design Result
---------
The result of this design module (:py:attr:`design_result`) includes the
specifications for both the export cables and offshore substation. This includes
a list of cable sections and their lengths and masses that represent the export
cable system, as well as the offshore substation substructure and topside mass
and cost, and number of substations. This result can then be passed to the
:doc:`export cable installation module <../install/export/doc_ExportCableInstall>` and
:doc:`offshore substation installation module <../install/export/doc_OffshoreSubstationInstall>`
to simulate the installation of the export system.
