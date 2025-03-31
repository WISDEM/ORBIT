.. _managertoc:

Project Manager
=============

The following pages cover the methodology behind the project manager.

.. note::

    Page currently under construction.

Overview
--------
The ``ProjectManager`` is the primary system for interacting with ORBIT to simulate
a wind project. Users can customize their project by specifying a a wide variety of
parameters as a dictionary (see :doc:`ProjectManager tutorial <tutorial/project_manager>`).
For more details of the code implementation, please see :doc:`Project Manager API <api_ProjectManager>`.

It instantiates a class aggregates project parameters, specifies a start date, and interprets a weather
profile, and it employs a collection of decorators, `methods`, and `classmethods` to run the simulation.
Among these methods are `design_phases` and `install_phases` that serve as components to the simulation.
Additionally, some methods search and catch key errors to avoid simulation issues, export progress logs,
and save the outputs.

Run
---
This method checks to see if a design or install phase is instatiated prior to running them. Depending on
which design phases are specified, each phase is run in no particular order and the results are added to
`.design_results` dictionary. Conversely, the install phases can be run sequentially or as overlapped
processes (see example: :doc:`Overlapping install <examples>`). It is worth noting, that ORBIT
has built in logic to determine any dependency between install phases.

Properties
----------
The `@property` decorators allow the ``ProjectManager`` to access and manipulate the attributes of certain classes. Of the
several properties some important ones are:

.. toctree::
    :maxdepth: 2
    :caption: Contents:

- capex_categories: CapEx Categories
- npv: Net Present Value
- turbine_capex: CapEx of the Wind Turbine.
- bos_capex: BOS CapEx includes the System CapEx and Installation CapEx.
- system_capex: Total system procurement cost.
- installation_capex: Total installation cost.
- project_capex: Project Capex includes, site auction, site assessment, construction plan, and installation plan costs.
- soft_capex_breakdown: Soft CapEx Categories

Finally, these attributes are collected in an `output` dictionary.

Class Methods
-------------
The `@classmethod` decorator allows the ``ProjectManager`` to access and modify class-level attributes.

- register_design_phase: Add a custom design phase to the ``ProjectManager`` class.
- register_install_phase: Add a custom install phase to the ``ProjectManager`` class.

Soft CapEx Methodology
-----------------------
The methodology outlined in Beiter et al. (2016) applies multipliers
(or assumed factors) to the magnitude of capital expenditure (CapEx)
components in order to derive the Soft CapEx components. The factors used are
consistent with those used in Stehly et al. (2024), enabling the soft costs to
scale in proportion to the other costs calculated within ORBIT. Soft Capex is
calculated using the default multipliers and parameters from Stehly et al. (2024).
Users can specify any of the :py:attr:`soft_capex_factors` below if they prefer to
override the default values. Additionally, users can assign $/kW values for
any calculated Soft CapEx component, ending with :math:`\_capex`, for
simplicity. The soft CapEx component's definitions and their calculations
are provided below.

Construction Insurance
~~~~~~~~~~~~~~~~~~~~~~
All risk property, delays in start-up, third party liability, and broker's fees.

:py:attr:`construction_insurance_factor` = 0.0115

:math:`construction\_insurance\_capex = construction\_insurance\_factor \quad \times`
:math:`\hspace{10em} (turbine\_capex + bos\_capex + project\_capex )`

Commissioning
~~~~~~~~~~~~~
Cost to integrate and commission the project.

:py:attr:`commissioning_factor` = 0.0115

:math:`commissioning\_capex = commissioning\_factor \quad \times`
:math:`\hspace{10em} (turbine\_capex + bos\_capex + project\_capex )`

Decommissioning
~~~~~~~~~~~~~~~
Surety bond lease to ensure that the burden for removing offshore structures
at the end of their useful life does not fall on taxpayers.

:py:attr:`decommissioning_factor` = 0.175

:math:`decommissioning\_capex = decommissioning\_factor \times installation\_capex`

Procurement Contingency
~~~~~~~~~~~~~~~~~~~~~~~
Provision for an unforeseen event or circumstance during the procurement process.

:py:attr:`procurement_contingency_factor` = 0.0575

:math:`procurement\_contingency\_capex = procurement\_contingency\_factor \quad \times`
:math:`\hspace{10em} (turbine\_capex + bos\_capex + project\_capex - installation\_capex)`


Installation Contingency
~~~~~~~~~~~~~~~~~~~~~~~~
Provision for an unforeseen event or circumstance during the installation process.

:py:attr:`installation_contingency_factor` = 0.0345

:math:`installation\_contingency\_capex = installation\_contingency\_factor \times installation\_capex`

Construction Financing
~~~~~~~~~~~~~~~~~~~~~~
Additional expenses incurred from interest on loans used to fund a construction
project, calculated based on the borrowing period and the project's spending schedule.

The spend schedule is based on industry data from a U.S. project.

:py:attr:`spend_schedule` =

+----------+-----------------+
| Year     | Amount          |
+==========+=================+
|    0     | 0.25            |
+----------+-----------------+
|    1     | 0.25            |
+----------+-----------------+
|    2     | 0.30            |
+----------+-----------------+
|    3     | 0.10            |
+----------+-----------------+
|    4     | 0.10            |
+----------+-----------------+
|    5     | 0.00            |
+----------+-----------------+

.. note::
    The Amount in the spend schedule must sum to 1.0 (100%).

:py:attr:`interest_during_construction` = 0.044

:py:attr:`tax_rate` = 0.26

:py:attr:`construction_financing_factor` =

.. math::

    \sum_{k=0}^{n-1} spend\_schedule_k \times (1 + (1 - tax\_rate) \times ((1+ interest\_during\_construction)^{k+0.5} - 1)

where *k* is the current year and *n* is the total number of years in :py:attr:`spend_schedule`.

:math:`construction\_financing\_capex = (construction\_financing\_factor - 1) \quad \times`
:math:`\hspace{10em} (construction\_insurance\_capex + commissioning\_capex \quad +`
:math:`\hspace{11em} decommissioning\_capex + procurement\_contingency\_capex \quad +`
:math:`\hspace{12em} installation\_contingency\_capex + turbine\_capex + bos\_capex)`

References
----------
- Stehly, T., Duffy, P., & Mulas Hernando, D. (2024). Cost of Wind Energy Review: 2024 Edition. https://doi.org/10.2172/2479271
- Beiter, P., Musial, W., Kilcher, L., Sirnivas, S., Stehly, T., Gevorgian, V., Mooney, M., Scott, G., Smith, A., Damiani, R., & Maness, M. (2016). A Spatial-Economic Cost-Reduction Pathway Analysis for U.S. Offshore Wind Energy Development from 2015-2030. https://doi.org/10.2172/1324526
