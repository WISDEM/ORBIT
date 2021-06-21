.. _changelog:

ORBIT Changelog
===============

1.0.5
-----

- Added initial floating offshore substation installation module.
- Added option to specific floating cable depth in cable design modules.
- Bugfix in ``project.total_capex``.

1.0.4
-----

- Added ability to directly prescribe weather downtime through the
  ``availability`` keyword
- Added support for generating linear models using ``ParametricManager``

1.0.2
-----

- Added ``ProjectManager.capex_breakdown``.

1.0.1
-----

- Default behavior of ``ParametricManager`` has been changed. Input parameters
  are now zipped together and ran as a discrete set of configs. To use the past
  functionality (finding the product of all input parameters), use the option
  ``product=True``
- Bugfix: Added port costs to floating substructure installation modules.
- Revised docs for running the Example notebooks and added link to a tutorial
  about working with jupyter notebooks.

1.0.0
-----

- New feature: ``ParametricManager`` for running parametric studies.
- Added procurement cost inputs and total cost methods to installation phases.
  Design phases are now only used to fill in the design and do not return a
  cost associated with the design.
- Refactored aggregation project level outputs in ``ProjectManager``.
- Revised Net Present Value calculation to utilize new project outputs.
- Added ``load_config`` and ``save_config`` functions.
- Moved ``ORBIT.library`` to ``OBRIT.core.library``.
- Centralized model defaults to ``ORBIT.core.defaults``.
- ``ProjectManager.project_actions`` renamed to ``ProjectManager.actions``
- ``ProjectManager.project_logs`` renamed to ``ProjectManager.logs``
- ``ProjectManager.run_project()`` renamed to ``ProjectManager.run()``
- Moved documentation hosting to gh-pages.

0.5.1
-----

- Process time kwargs should now be passed through ``ProjectManager`` in a
  dictionary named ``processes`` in the config.
- Revised ``prep_for_site_operations`` and related processes to allow for
  dynamically positioned vessels.
- Updated WISDEM API to include floating functionality.

0.5.0
-----

- Initial release of floating substructure functionality in ORBIT.
- New design modules: ``MooringSystemDesign``, ``SparDesign`` and
  ``SemiSubmersibleDesign``.
- New installation modules: ``MooringSystemInstallation`` and
  ``MooredSubInstallation``
- Cable design and installation modules modified to calculate catenary lengths
  of suspended cable at depths greater than 60m.

0.4.3
-----

- New feature: Cash flow and net present value calculation within
  ``ProjectManager``.
- Revised ``CustomArraySystemDesign`` module.
- Revised assumptions in ``MonopileDesign`` module to bring results in line
  with industry numbers.

0.4.2
-----

- New feature: Phase dependencies in ``ProjectManager``.
- New feature: Windspeed constraints at multiple heights, including automatic
  interpolation/extrapolation of configured windspeed profiles.
- Added option to define ``mobilization_days`` and ``mobilization_mult`` in a
  ``Vessel`` configuration file.
- Added option for pre-installation trenching operations to
  ``ArrayCableInstallation`` and ``ExportCableInstallation``.
- Revised ``OffshoreSubstationDesign`` to scale the size of the substations
  with the user-configured number of substations.
- Bugfix in the returned argument order of ``ProjectManager.run_install_phase``
  where the cost of a prior phase would be incorrectly applied as the elapsed
  time.

0.4.1
-----

- Modified installation to require version of marmot-agents that has an
  internal copy of simpy.
- Added/expanded ``detailed_outputs`` for all modules.
- Standardized naming of weight/mass terms to mass throughout the model.
- Cleanup in ``ProjectManager``.

0.4.0
-----

- Vessel mobilization added to all vessels in all installation modules.
  Defaults to 7 days at 50% day-rate.
- Cable lay, bury and simulataneous lay/bury methods are not flagged as
  suspendable to avoid unrealistic project delays.
- Cost of onshore transmission construction added to
  ``ExportCableInstallation``.
- Simplified ``ArrayCableInstallation``, ``ExportCableInstallation`` modules.
- Removed `pandas` from the internals of the model, though it is still useful
  for tabulating the project logs.
- Revised package structure. Functionally formerly in ORBIT.simulation or
  ORBIT.vessels has been moved to ORBIT.core.
- ``InstallPhase`` cleaned up and slimmed down.
- ``Environment`` and associated functionality has been replaced with
  ``marmot.Environment``.
- Logging functionality revised. No longer uses the base python logging module.
- ``Vessel`` now inherits from ``marmot.Agent``.
- Tasks that were in ``ORBIT.vessels.tasks`` have been moved to their
  respective modules and restructured with ``marmot.process`` and
  ``Agent.tasks``.
- Modules inputs cleaned up. ``type`` parameters are no longer required for
  monopile, transition piece or turbine component definitions.
- Removed old/irrelevant tests.

0.3.5
-----

- Added 'per kW' properties to ``ProjectManager`` CAPEX results.

0.3.4
-----

- Added configuration to ``ProjectManager`` that allows exceptions to be caught
  within individual modules and allows the project as a whole to continue.
- Fixed installation process when installing from GitHub.

0.3.3
-----

- Added configuration for multiple tower sections in ``TurbineInstallation``.
- Added configuration for seperate lay/burial in ``ArrayCableInstallation`` and
  ``ExportCableInstallation``.
- Overhauled test suite and associated library.
- Bugfix in ``CableCarousel``.
- Expanded WISDEM Fixed API.

0.3.2
-----

- Initial release of fixed substructure WISDEM API
- Material cost for monopiles and transition pieces added to ``MonopileDesign``
- Updated ``ProjectManager`` to allow user to override default ``DesignPhase``
  results
- Moved config validation to ``BasePhase`` and added call to
  ``self.validate_config`` for all current modules
- Config validation logic reworked so dicts of optional values are not
  required
- Added method to resolve project capacity in ``ProjectManager``. A user can
  now input ``plant.num_turbines`` and ``turbine.turbine_rating`` and
  ``plant.capacity`` will be added to the config.
- Added initial set of standardized inputs to ``ProjectManager``:

  - ``self.installation_capex``
  - ``self.installation_time``
  - ``self.project_days``
  - ``self.bos_capex``
  - ``self.turbine_capex``
  - ``self.total_capex``

0.3.1
-----

- Updated README
