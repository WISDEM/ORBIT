Scour Protection Design Methodology
===================================

For details of the code implementation, please see
:doc:`Scour Protection Design API <api_ScourProtectionDesign>`.

Scour Protection Design
-----------------------

This module calculates the required scour protection material for a fixed
substructure to avoid seabed erosion around the installation. It is based on
a DNV GL `standard <https://rules.dnvgl.com/docs/pdf/DNV/codes/docs/2014-05/Os-J101.pdf>`_
and geometric calculations.

The potential depth of the a free forming scour pit is calculated using a
simplified version of the relationship presented in the DNV GL report (equation
J.5):

:math:`\frac{S}{D} = 1.3`

where :math:`S` is the calculated depth of the scour pit and :math:`D` is the
overall diameter of the substructure. The default value (1.3) is a conservative
assumption and may be overridden by the user as follows:

.. code-block:: python

   config = {
       ...

       "scour_protection_design": {
           "scour_depth_equilibrium": 1.2
       }

       ...
   }

The radius of the scour pit is then calculated using the soil friction
angle (:math:`\phi`) and a simple geometric relationship:

:math:`r = \frac{D}{2} + \frac{S}{tan(\phi)}`

The default value for :math:`\phi` is 33.5deg, representing the soil
friction angle for medium density sand. The total volume of scour
protection material is then calculated as follows,

:math:`V = \pi * t * r^2`

where :math:`t` represents the depth of the scour protection material. This
value defaults to 1m in the code, which represents an appropriate initial
assumption and not a complete design. For sites that exhibit greater seafloor
currents, the scour protection layer may be as thick as 2m, whereas calmer
sites may only need 0.3-0.5m of material. In the abscense of a geotechnical
study, this value is difficult to calculate and is instead presented to user as
a configurable input so the cost impacts of different thicknesses can be
investigated.

Terms:
 * :math:`S =` Scour depth
 * :math:`D =` Monopile diameter
 * :math:`r =` Radius of scour protection from the center of the monopile
 * :math:`\phi =` Soil friction angle

Default Assumptions:
 * :math:`\frac{S}{D} = 1.3`
 * :math:`\phi = 33.5`
   * Angle for medium density sand

References
----------
.. [1] Det Norske Veritas AS. (2014, May). Design of Offshore Wind Turbine
       Structures. Retrieved from
       https://rules.dnvgl.com/docs/pdf/DNV/codes/docs/2014-05/Os-J101.pdf

.. [2] Draft Construction and Operations Plan for Vineyard Wind Project Appendices.
       Retrieved from
       https://www.boem.gov/sites/default/files/renewable-energy-program/State-Activities/MA/Vineyard-Wind/Vineyard-Wind-COP-Volume-III-Appendix-III-K.pdf
