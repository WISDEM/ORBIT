Monopile Design Methodology
===========================

For details of the code implementation, please see
:doc:`Monopile Design API <api_MonopileDesign>`.

Overview
--------

This module is based on initial pile dimension calculations from Arany (2017)
[#arany2017]_. Pile dimensions are chosen to withstand the bending moment from
the 50-year Extreme Operation Gust (EOG). This corresponds to wind scenario
U-3 in Section 2.2.1. This module is not intended to capture the complexities
of a full engineering design study for monopiles, but rather broadly capture
the scaling trends due to increased site depth, turbine size and material
parameters.

The 50-year extreme wind speed can be calculated using the following cumulative
density function.

:math:`U_{10,50-year}=K(-\ln(1-0.98^\frac{1}{52596}))^\frac{1}{S}`

where :math:`K` and :math:`S` are the Weibull scale and shape factors
respectively.

The mudline bending moment is calculated as:

:math:`M_{wind,EOG} = \gamma_LF_{wind,EOG}(S + z_{hub})`

where :math:`\gamma_L` is the load factor (defaults to 1.35),
:math:`F_{wind,EOG}` is the total wind load on the turbine, :math:`S` is the
water depth at site and :math:`z_{hub}` is the hub height of the turbine. The
derivation of :math:`F_{wind,EOG}` can be seen in detail in the
`ORBIT technical documentation <https://www.nrel.gov/docs/fy20osti/77081.pdf>`_.

Initial pile dimensions are then calculated using Arany (2017) [#arany2017]_,
API (2005) [#api2005]_, and Poulos and Davis (1980) [#PoulosDavis1980]_.

References
----------

.. [#arany2017] Laszlo Arany, S. Bhattacharya, John Macdonald,
    S.J. Hogan, Design of monopiles for offshore wind turbines in 10
    steps, Soil Dynamics and Earthquake Engineering,
    Volume 92, 2017, Pages 126-152, ISSN 0267-7261,

.. [#api2005] API, 2005, Recommended Practice for Planning, Designing and
   Constructing Fixed Offshore Platforms - Working Stress Design, Pages 68-71

.. [#PoulosDavis1980] Poulos and Davis, 1980, Pile foundation analysis and
   design. Rainbow-Bridge Book Co.
