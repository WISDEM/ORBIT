Available Outputs
=================

``ProjectManager`` is used to run a collection of ORBIT modules representing a
complete offshore wind project installation. The outputs of each module are
then aggregated into several different project-level outputs available via
the ``ProjectManager`` API.

System and Installation CapEx
-----------------------------

The two main outputs of ORBIT are the System CapEx (the total cost of procuring
the configured subsystems) and the Installation CapEx (the total cost of
installing the subsystems).

.. code-block:: python

   from ORBIT import ProjectManager
   config = {
       ...
   }

   project = ProjectManager(config)
   project.run()

   project.system_capex
   project.installation_capex

System CapEx is the sum of the unit costs (either user inputs or results from
design phases) multiplied by the configured number of turbines, cable section
lenghts or other appropriate unit. This output does not change based on the
installation simulation.

Installation CapEx is a dynamic result based on the installation simulation and
is based on the times associated with each subsystem installation, day rates of
any vessels/ports and any accrued weather delays.

BOS CapEx
---------

The balance-of-system CapEx (available as ``project.bos_capex``) is the sum of
the system and installation capex numbers and is one of the core outputs of the
ORBIT module.

Soft CapEx
----------

Soft CapEx (``project.soft_capex``) represents additional project level costs
associated with commissioning, decommissioning and financing of the project.
The cost factors can be input in the ``project_parameters`` subdict of an ORBIT
configuration. The default cost factors for these categories are derived from the
`2018 Cost of Wind Energy Review <https://www.nrel.gov/docs/fy20osti/74598.pdf>`_.

Project CapEx
-------------

Project CapEx (``project.project_capex``) includes the costs associated with
the lease area, the development of the construction operations plan and any
environmental review and other upfront project costs. There are default values
for all of these subcategories, however the values can also be overridden in the
``project_parameters`` subdict.

Total CapEx
-----------

Total CapEx (``project.total_capex``) is the sum of the BOS, Soft and Project
CapEx numbers. This represents complete project costs including all upfront
costs, financing, procurement and installation of BOS subsystems and the
procurement costs of the turbines.

.. note::

   ORBIT doesn't explicity model the procurement of turbines, however the
   Turbine CapEx is included within ``project.total_capex``. To configure the
   cost of the turbines, ``turbine_capex`` can be passed into the
   ``project_parameters`` subdict of an ORBIT config. The default is $1300/kW.

Actions
-------

A list of every step taken during the installation modules is available at
``project.actions``. The best way to view, sort and save these results is as
a pandas DataFrame. A few example use cases are presented below.

.. code-block:: python

   import pandas as pd
   df = pd.DataFrame(project.actions)

   # Sort by a specific phase
   df.loc[df["phase"]=="MonopileInstallation"]

   # Group by vessel and action to see where each vessel spent the most time
   df.groupby(["vessel", "action"]).sum()["duration"]

   # Save results to 'csv'
   df.to_csv("filename.csv")

Detailed Outputs
----------------

More detailed results from individual phases are available at
``project.detailed_outputs``.

Cash Flow and Net Present Value
-------------------------------

``ProjectManager`` also includes a basic cash flow and net present value model.
The project must have the array system, export system and the substation
installation modules configured for this model to be applicable. The model will
find the point in the project logs where the substation and export system
installations were completed and where each array system string was installed.
When all three of these conditions are met, the project can begin to generate
energy and produce revenue. The revenue generation is then superimposed on the
monthly spend of the installation modules for the ``project.cash_flow``.

The net present value of the project can then be calculated and is available at
``project.npv``. The underlying financial assumptions for this model are also
contained within the ``project_parameters`` subdict of the ORBIT configuration.
