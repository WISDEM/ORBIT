.. _changelog:

ORBIT Changelog
===============

Unreleased
----------
- Allow for a Pandas DataFrame to be passed directly to the ``CustomArraySystemDesign.layout_data``
  configuration input.
- Move the matplotlib import from the import section of ``/ORBIT/phases/design/array_system_design.py``
  to the ``CustomArraySystemDesign.plot_array_system`` for missing module error handling.
- Adds a general layout ``DataFrame`` creation method as ``ArraySystemDesign.create_layout_df()`` that
  is called by the ``save_layout`` method to maintain backwards compatibility, but opens up the ability
  gather the layout without saving it to a file.
- Updated default `soft_capex` factors. `PR #201 <https://github.com/WISDEM/ORBIT/pull/201>`_
    - `construction_insurance_factor` updated from 0.115 to 0.0207 based on industry benchmarking, resulting in higher construction insurance costs.
    - `interest_during_construction` updated from 4.4% to 6.5% based on financial assumptions from the 2025 Annual Technology Baseline (ATB), increasing construction financing costs.
    - `decommissioning_factor` updated from 0.175 to 0.2 based on industry benchmarking, leading to higher decommissioning costs than in previous versions.
- Updated default `project_capex` values. `PR #201 <https://github.com/WISDEM/ORBIT/pull/201>`_
    - `site_auction_price` increased from 100M to 105M USD to account for rent fees before operation.
    - `site_assessment_cost`, `construction_plan_cost`, and `installation_plan_cost` increased from 50M, 1M, and 0.25M USD to 200M, 25M, and 25M USD, respectively.
    - Total `project_capex` excluding `site_auction_price` now sums to 250M USD, aligning with DevEx recommendations based on industry benchmarking.
    - These updates lead to higher default total project costs than in previous versions.
- Included onshore substation costs in BOS CapEx and project breakdown. `PR #201 <https://github.com/WISDEM/ORBIT/pull/201>`_
    - The `ElectricalDesign` module previously calculated onshore substation costs but did not include them in `capex_breakdown` or `bos_capex`.
    - These costs are now incorporated when `ElectricalDesign` is used, resulting in higher `bos_capex`, `soft_capex`, and `total_capex` than in prior versions.
- Cable configuration file updates. `PR #201 <https://github.com/WISDEM/ORBIT/pull/201>`_
    - Added a new dynamic cable configuration file for floating cases: `library/cables/XLPE_1200mm_220kV_dynamic.yaml`.
    - Updated cost values for `library/cables/XLPE_630mm_66kV.yaml` and `library/cables/XLPE_630mm_66kV_dynamic.yaml` based on industry benchmarking.
    - All cable cost updates are expressed in 2024 USD for consistency with other library configuration files.

1.2.4
-----
- Support Python 3.14

1.2.3
-----
- Adjusted the recent np.trapz fix to be compatible with numpy < 2.0

1.2.2
-----
- Replaced the deprecated `numpy.trapz` with `numpy.trapezoid`.
- Deprecates Python 3.9 support in preparation for EOL and seamless benedict compatibility.

1.2.1
-----
- Removed `wisdem_api.py` because WISDEM now uses orbit as a pip installed package.
- Added Python 3.12 and 3.13 to the workflow files.
- Moved matplotlib as an optional dependency

1.2
---
- New cable ``library/cables/XLPE_1200mm_220kV.yaml`` Is a 220kV cable that can carry ~400MW of HVAC power.
- Fixed frozen python-benedict version
    - ``ParametricManager`` can still use '.' as a keypath separator (no change to user inputs) and is compatible with latest python-benedict
- Updated various default costs to 2024 USD. `PR #187 <https://github.com/WISDEM/ORBIT/pull/187>`_
    - Cost rates for different models were determined by benchmarking the costs through industry outreach,
      along with adjustments based on commodity prices, inflation, and labor indices.
    - ORBIT assumes a procurement year of 2024 in the files:
        - ``defaults/common_costs.yaml`` represents all the design related costs.
        - ``ORBIT/manager.py`` includes project related costs
        - ``library/cables/*`` shows all the cables with updated `cost_per_km`
        - ``library/vessels/*`` shows all the vessels with updated `day_rate`
    - Added ``defaults/costs_by_procurement_year.csv`` which provides the default costs for other procurement year,
      but in 2024 USD.
- Bug Fix: Characteristic Impedance calculation correction. `Issue #186 <https://github.com/WISDEM/ORBIT/issues/186>`_
    - There were some documentation typos and a units error in the calculation, where mH (10^-3) was divided by nF (10^-9)
    - Updated several tests with new values that correlate to the latest cable power capacity
- Updated WISDEM API (`wisdem_api.py`)
    - Match some variable names and inputs that have diverged over time.
    - Caught turbine_capex double count in WISDEM when using `total_capex` from ORBIT.
    - Updated some tests.
- Enhanced ``ProjectManager``: `PR #177 <https://github.com/WISDEM/ORBIT/pull/177>`_
    - Improvements made to `soft_capex` calculations because previous versions
     used default `$/kW` values from the 2018 Cost of Wind Energy Review unless provided by
     the user. Those default values are out of date and do not scale with the size of the
     project which is not entirely accurate.
    - `soft_capex` is now calculated as sum of `construction_insurance_capex`, `decommissioning_capex`,
      `commissioning_capex`, `procurement_contingency_capex`, `installation_contingency_capex`,
      `construction_financing_capex`. NOTE: user can still specify the same `$/kW` values if they choose.
    - New factors were implemented to calculated updated project_parameters if the user does not specify
    any inputs.

1.1
---

New features
~~~~~~~~~~~~
- Enhanced ``MooringSystemDesign``:
    - Can specify catenary or semitaut mooring systems. (use `mooring_type`)
    - Can specify drag embedment or suction pile anchors. (use `anchor_type`)
    - Description: This class received some new options that the user can
      specify to customize the mooring system. By default, this design uses
      catenary mooring lines and suction pile anchors. The new semitaut mooring
      lines use interpolation to calculate the geometry and cost based on
      (Cooperman et al. 2022, https://www.nrel.gov/docs/fy22osti/82341.pdf).
    - See ``5. Example Floating Project`` for more details.
- New ``ElectricalDesign``:
    - Now has HVDC or HVAC transmission capabilities.
    - New tests created ``test_electrical_export.py``
    - Description: This class combines the elements of ``ExportSystemDesign`` and the
      ``OffshoreSubstationDesign`` modules. Its purpose is to represent the
      entire export system more accurately by linking the type of cable
      (AC versus DC) and substation’s components (i.e. transformers versus converters).
      Most export and substation component costs were updated to include a per-unit cost
      rather than a per-MW cost rate and they can be added to the project config file too.
      Otherwise, those per-unit costs use default and were determined with the help of
      industry experts.
        - This module’s components’ cost scales with number of cables and
          substations rather than plant capacity.
        - The offshore substation cost is calculated based on the cable type
          and number of cables, rather than scaling function based on plant capacity.
        - The mass of an HVDC and HVAC substation are assumed to be the same.
          Therefore, the substructure mass and cost functions did not change.
        - An experimental onshore cost function was also added to account for
          the duplicated interconnection components. Costs will vary depending
          on the cable type.
    - See new example ``Example - Using HVDC or HVAC`` for more details.
- Enhanced ``FloatingOffshoreSubStation``:
    - Fixed the output substructure type from Monopile to Floating. (use `oss_substructure_type`)
    - Removes any pile or fixed-bottom substructure geometry.
    - See ``Example 5. Example Floating Project`` for more details.
- Updated ``MoredSubInstallation``:
    - Uses an AHTS vessel which must be added to project config file.
    - See ``example/example_floating_project.yaml`` (use `ahts_vessel`)
- New ``22MW_generic.yaml`` turbine.
    - Based on the IEA - 22 MW reference wind turbine.
    - See ``library/turbines`` for more details.
- New cables:
    - Varying HVDC ratings
    - Varying HVDC and HVAC "dynamic" cables for floating projects.
    - See ``library/cables`` for all the cables and more details.

Updated default values
~~~~~~~~~~~~~~~~~~~~~~
- ``defaults/process_times.yaml``
    - `drag_embedment_install_time`` increased from 5 to 12 hours.
- ``phases/install/quayside_assembly_tow/common.py``:
    - lift and attach tower section time changed from 12 to 4 hours per section,
    - lift and attach nacelle time changed from 7 to 12 hours.
- ``library/cables/XLPE_500mm_132kV.yaml``:
    - `cost_per_km` changed from $200k to $500k.
- ``library/vessels/example_cable_lay_vessel.yaml``:
    - `min_draft` changed from 4.8m to 8.5m,
    - `overall_length` changed from 99m to 171m,
    - `max_mass` changed 4000t to 13000t,
- ``library/vessels/example_towing_vessel.yaml``:
    - `max_waveheight` changed from 2.5m to 3.0m,
    - `max_windspeed` changed 20m to 15m,
    - `transit_speed` changed 6km/h to 14 km/h,
    - `day_rate` changed $30k to $35k

Improvements
~~~~~~~~~~~~
- All design classes have new tests to track total cost to flag any changes that may
  impact final project cost.
- Relocated all the get design costs in each design class to `common_cost.yaml`.
- Fully adopted `pyproject.toml` for managing all possible tool settings, and
  removed the tool-specific files from the top-level of the directory.
- Replaced flake8 and pylint with ruff to adopt a cleaner, faster, and easier
  to manage linting and autoformatting workflow. As a result, some of the more
  onerous checks have been removed to discourage the use of
  `git commit --no-verify`. This change has also added in other rules that
  discourage Python anti-patterns and encourage modern Python usage.
- NOTE: Users may wish to run
  `git config blame.ignoreRevsFile .git-blame-ignore-revs` to ignore the
  reformatting edits in their blame.

1.0.8
-----

- Added explicit methods for adding custom design or install phases to
  ``ProjectManager``.
- Added WOMBAT compatibility for custom array system files.
- Fixed bug in custom array cable system design that breaks for plants with
  more than two substations.

1.0.7
-----

- Added ``SupplyChainManager``.
- Added ``JacketInstallation`` module.
- Added option to use dynamic supply chain in ``MonopileInstallation`` module.

1.0.6
-----

- Expanded tutorial and examples.
- Added templates for design and install modules.
- Added ports to library pathing.
- Misc. bugfixes.

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
