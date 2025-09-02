ORBIT
=====

ORBIT is a tool developed by the National Renewable Energy Lab (NREL) for
performing process-based bottom up installation and cost modeling for the
offshore wind balance of system process. It is intended to be used for tradeoff
studies, installation logistics research, and for modeling overall balance of
system costs. Each module captures the main drivers of installation time and
cost in a highly customizable framework, allowing the user to override any
default values if they wish.

The primary structure of ORBIT relies on the :ref:`Project Manager <managertoc>`
to intrepret the user specified configuration. Refer to the
`library/project/config <https://github.com/WISDEM/ORBIT/tree/master/library/project/config>`.
The ``ProjectManager`` calls ``DesignPhase`` to include all the wind farm components that
comprise the balance of system, then it calls ``InstallationPhase`` to schedule all the installation
processes for each component. Available design phases can be found :ref:`here <design_phases>` and
installation phases can be found :ref:`here <install>`. Details about the design
and installation phases are presented throughout this documents page.

Design Phase
------------
ORBIT is very modular by design to allow a user to define an offshore wind
plant in many different configurations and simulate its design and
installation. Modules in ORBIT represent the design of different components for
an offshore wind plant (eg. substructures, array cabling system, etc.) as well
as the installation of these components (eg. monopile installation, turbine
installation, etc.). The modularity will allow for novel technologies or
installation strategies to be easily introduced and compared with baseline
methodologies as the industry develops.


Installation Phases
-------------------
In ORBIT, each installation phase of an offshore wind project development is
defined by a series of discrete processes that represent the installation of a
component. Durations and respective costs of each of these processes are then
calculated based on fundamental parameters of the project and defined vessels,
such as determining the length of time a specific offshore lift will require
depending on crane specifications and component mass.

These processes are then modeled using a Discrete Event Simulation (DES)
framework, where each process must satisfy operational constraints (weather or
vessel interactions) before it proceeds. In this way, weather delays can be
accounted for in the installation process, and the associated impact on project
risk and construction phase sequencing can be determined. The DES framework of
ORBIT is built using the python package `SimPy <https://simpy.readthedocs.io/en/latest/>`_.

Library
-------
A library directory includes data/specifications on cables, vessels, ports, turbines, and example
projects in the form of yaml files. Users can copy and modify or create entirely new yaml files
to customize their project. By sticking to the same file structure, users simply have to update the
name or reference to the data in their configuration file.
