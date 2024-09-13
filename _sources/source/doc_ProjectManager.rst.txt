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
parameters as a dictionary (see tutorial: :ref:`Project Manager Tutorial <project_manager>`).
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
processes (see example: :ref:`Overlapping install <project_manager>`). It is worth noting, that ORBIT
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

Finally, these attributes are collected in an `output` dictionary.

References
----------
Stehly, Tyler, and Philipp Beiter. 2019. “2018 Cost of Wind Energy Review.” Renewable Energy. https://www.nrel.gov/docs/fy20osti/74598.pdf.
