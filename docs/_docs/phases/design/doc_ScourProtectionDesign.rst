Scour Protection Design Methodology
===================================

For details of the code implementation, please see
:doc:`Scour Protection Design API <api_ScourProtectionDesign>`.

Scour Protection Height Calculation
-----------------------------------
This module is based on the an offshore wind turbine design white paper from
DNVGL (2014) [1]_. Below is an illustration to highlight how the amount of the
scouring protection design parameters being considered.

::

|____________________________________________|
|               |         |                  |
|               |         |                  |
|               |<-- D -->|                  |
|               |         |                  |
|               |         |                  |
|               |   M     |                  |
|               |   O     |                  |
|               |   N     |                  |
|               |   O     |                  |
|               |   P     |                  |
|               |   I     |     r            |
|               |   L |---|--------------|   |
|               |   E     |                  |
|               |         |                  |
|  -------------|---------|--------------    |
|   ////////////|/////////|//////////// |    |
|   ////////////|/////////|// Scour   / |    |
|   ////////////|/////////|// Protec- / S    |
|   ////////////|/////////|// tion    / |    |
|   ////////////|/////////|//////////// |    |
|   ______________________________________   |
|               |         |   Seafloor       |
|               |         |                  |
|____________________________________________|

Terms:
 * :math:`S =` scour protection height
 * :math:`D =` monopile diameter
 * :math:`r =` radius of scour protection from the center of the monopile
 * :math:`\phi =` scour angle

Default Assumptions:
 * :math:`\frac{S}{D} = 1.3`
 * :math:`r = \frac{D}{2} + \frac{S}{\tan(\phi)}`
 * :math:`\phi = 33.5`
   * scour angle for medium density sand

References
----------
.. [1] Det Norske Veritas AS. (2014, May). Design of Offshore Wind Turbine
       Structures. Retrieved from
       https://rules.dnvgl.com/docs/pdf/DNV/codes/docs/2014-05/Os-J101.pdf
