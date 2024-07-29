Semi-Submersible Design Methodology
===================================

For details of the code implementation, please see
:doc:`Semi-Submersible Design API <api_SemiSubmersibleDesign>`.

Overview
--------

The semi-submersible design module in ORBIT is based on previous modeling
efforts undertaken by NREL, [#maness2017]_. The technical documentation for
this tool can be found `here <https://www.nrel.gov/docs/fy17osti/66874.pdf>_`.

Custom Semi-Submersible Design Methodology
==========================================
For details of the code implementation, please see
:doc:`Semi-Submersible Design API <api_SemiSubmersibleDesign>`.

(Custom) Overview
-----------------

This new addition to ORBIT's semi-submersible design capabilities by letting
the user specify all the dimensions of the platform. IEAt was designed based on
the IEA-15MW reference turbine and the VolturnUS-S Reference Platform developed
by the University of Maine.[#allen2020]_.The triangular base uses three steel
columns equipped with ballast material. Each column is connected to a
central-column, where the turbine is afixed, by pontoons and spars.
Additionally, this new model uses the methodology proposed in [#roach2023]_ to
scale the platform to other turbine sizes.

References
----------

.. [#maness2017] Michael Maness, Benjamin Maples, Aaron Smith,
    NREL Offshore Balance-of-System Model, 2017.
    `https://www.nrel.gov/docs/fy17osti/66874.pdf`

.. [#allen2020] Christopher Allen, Anthony Viselli, Habib Dagher,
    Andrew Goupee, Evan Gaertner, Nikhar Abbas, Matthew Hall,
    and Garrett Barter. Definition of the UMaine VolturnUS-S Reference Platform
    Developed for the IEA Wind 15-Megawatt Offshore Reference Wind Turbine.
    `https://www.nrel.gov/docs/fy20osti/76773.pdf`

.. [#roach2023] Kaylie Roach, Matthew Lackner, James Manwell. A New Method for
    Upscaling Semi-submersible Platforms for Floating Offshore Wind Turbines.
    `https://wes.copernicus.org/preprints/wes-2023-18/wes-2023-18.pdf`
