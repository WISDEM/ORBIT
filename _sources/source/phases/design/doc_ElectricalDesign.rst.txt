Electrical System Design Methodology
====================================

For details of the code implementation, please see
:doc:`Electrical System Design API <api_ElectricalDesign>`.

Overview
--------

Below is an overview of the process used to design an export cable system and
offshore substation in ORBIT using the ElectricalDesign module. This module is to be
used in place of both the ExportSystemDesign module and the OffshoreSubstationDesign
module as it codesigns the export cables and offshore substation. Depending on whether
HVAC or HVDC cables are selected, different components will contribute to the final BOS.
For more detail on the helper classes used to support this design please see :doc:`Cabling Helper Classes
<doc_CableHelpers>`, specifically :class:`Cable` and :class:`CableSystem`.


Number of Required Cables
---------
The number of export cables required for HVAC is calculated by dividing the windfarm's
capacity by the configured export cable's power rating and adding any user
defined redundnacy as seen below.

:math:`num\_cables = \lceil\frac{plant\_capacity}{cable\_power}\rceil + num\_redundant`

For HVDC cables (both monopole and bipole), the number of cables is twice the number as
calculated abpve because HVDC systems require a pair of cables per implementation.
The equation for this calculation is shown below.

:math:`num\_cables = 2 * \lceil\frac{plant\_capacity}{cable\_power}\rceil + num\_redundant`

Export Cable Length
---------
The total length of the export cables is calculated as the sum of the site
depth, distance to landfall and distance to interconnection multiplied by the
user defined :py:attr`percent_added_length` to account for any exclusions or
geotechnical design considerations that make a straight line cable route
impractical.

:math:`length = (d + distance_\text{landfall} + distance_\text{interconnection}) * (1 + length_\text{percent_added})`

Cable Crossing Cost
---------
Optional inputs for both number of cable crossings and unit cost per cable
crossing.  The default number of cable crossings is 0 and cost per cable
crossing is $500,000. This cost includes materials, installation, etc. Crossing
cost is calculated as product of number of crossings and unit cost.

Number of Required Power Transformer, Tranformer Rating, and Cost
---------
The number of main power transformers (MPT) required is assumed to be equal to the number
of required export cables. The transformer rating is calculated by dividing the
windfarm's capacity by the number of MPTs. MPTs are only required if the
export cables are HVAC. The default cost of the MPT is $2.87m per HVAC cable. Therefore, the total MPT cost is
proportional to the number of cables. Note: Previous versions may have used curve-fits to
calculate total MPT cost based on the windfarm's capacity. The MPT unit cost ($/cable) can
be ovewritten by the user by setting (``mpt_unit_cost``) to the desired cost. If the export cables
are HVDC, then the cost of power transformers will be $0.

Number of Shunt Reactors, Reactive Power Compensation, and Cost
---------
The shunt reactor cost is dependent on the amount of reactive power compensation
required based on the distance of the substation to shore. This model assumes
one shunt reactor for each HVAC export cable. An HVDC export systems do not require
reactive power compensation. The default cost rate of the shunt reactors is $10k per HVAC cable. The total cost is proportional
to the number of cables multipled by a cable-specific compensation factor. The default cost rate
can be overwritten by the user by setting (``shunt_unit_cost``) to the desired cost. The shunt
reactor cost is $0 for HVDC systems.

Number of Required Switchgears and Cost
---------
The number of switchgear relays required is assumed to be equal to the number of
required export cables. Switchgear cost is only necessary if HVAC export cables
are chosen. The default cost is $4m per cable for HVAC. The default cost can be overwritten by the user by
setting (``switchgear_cost``) to the desired cost. Switchgear cost is equal to $0 for HVDC export
cables.

Number of Circuit Breakers and Cost
---------
The number of circuit breakers required is assumed to be equal to the number of required
export cables. Breakers are only necssary if HVDC export cables are chosen. The default cost is
$10.6m per HVDC cable. The default cost can be overwritten by the user by setting (``dc_breaker_cost``)
to the desired cost. Breaker cost is $0 for HVAC cables.

Number of Required AC\DC Converters and Cost
---------
AC\DC converters are only required for HVDC export cables. The number of converters
is assumed to be equal to the number of HVDC export cables.

Ancillary System Cost
---------
Costs are included such as a backup generator, workspace cost, and miscellous to
capture any additional features outside the main components. The user can define each
variable by setting (``backup_gen_cost``), (``workspace_cost``), and (``other_ancillary_cost``).

Assembly Cost (On Land)
----------
The majority of the electrical components are located on the offshore substation platform, but
they must be assembled on land. Therefore, an assembly factor of 7.5% is added to the components cost.
Those components include switchgear, shut reactors, and ancillary costs. The user can change the
factor by setting (``topside_assembly_factor``) to the desired percentage.

Substation Topside Mass and Cost
----------
We assume that the topside design cost is a fixed amount based on the export cables (either HVDC or HVAC).
The user can specify the topside cost by setting (``topside_design_cost``). The mass of the topside is
determined by a curve fit.

Substation Substructure Mass and Cost
----------
The mass and cost associated with the substructure of the offshore substation are based on
curve fits. The topside mass will drive the mass/size of the substructure. Then, the cost of the
substructure is determined by its mass. The substructure has a default cost rate of $3000 per ton of
steel. The value can be overwritten by setting (``oss_substructure_cost_rate``) to the desired cost rate.

Onshore Cost
---------
The onshore cost is considered to be the minimum cost of interconnection. This includes
the major required hardware for a cable connection onshore. For HVDC cables, it includes
the converter cost, DC breaker cost, and transformer cost. For HVAC, it includes the
transformer cost and switchgear cost. The onshore costs may or may not be included in the BOS
of the wind farm. Therefore, this cost is not included in the total ``system_capex``
calculated by ProjectManager.

Design Result
---------
The result of this design module (:py:attr:`design_result`) includes the
specifications for both the export cables and offshore substation. This includes
a list of cable sections and their lengths and masses that represent the export
cable system, as well as the offshore substation substructure and topside mass
and cost, and number of substations. This result can then be passed to the
:doc:`export cable installation module <../install/export/doc_ExportCableInstall>` and
:doc:`offshore substation installation module <../install/oss/doc_OffshoreSubstationInstall>`
to simulate the installation of the export system.
