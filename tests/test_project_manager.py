__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


import datetime as dt
from copy import deepcopy

import pandas as pd
import pytest

from ORBIT import ProjectManager
from tests.data import test_weather
from ORBIT.phases import DesignPhase, InstallPhase
from ORBIT.manager import ProjectProgress
from ORBIT.core.library import extract_library_specs
from ORBIT.core.exceptions import (
    MissingInputs,
    PhaseNotFound,
    WeatherProfileError,
    PhaseDependenciesInvalid,
)

weather_df = pd.DataFrame(test_weather).set_index("datetime")

config = extract_library_specs("config", "project_manager")
complete_project = extract_library_specs("config", "complete_project")
complete_floating_project = extract_library_specs(
    "config", "complete_floating_project"
)


# Top Level
@pytest.mark.parametrize("weather", (None, weather_df))
def test_complete_run(weather):

    project = ProjectManager(config, weather=weather)
    project.run()

    actions = pd.DataFrame(project.actions)

    phases = ["MonopileInstallation", "TurbineInstallation"]
    assert all(p in list(actions["phase"]) for p in phases)


# Module Integrations
def test_for_required_phase_structure():
    """
    Automated integration test to verify that all classes listed in
    ProjectManager.possible_phases are structured correctly.
    """

    for p in ProjectManager._install_phases:

        assert isinstance(p.expected_config, dict)

    for p in ProjectManager._design_phases:

        assert isinstance(p.expected_config, dict)
        assert isinstance(p.output_config, dict)


# TODO: Expand these tests


# Config Management
def test_phase_specific_definitions():
    """Tests that phase specific information makes it to phase_config."""

    project = ProjectManager(config)

    phase_config = project.create_config_for_phase("MonopileInstallation")

    assert phase_config["wtiv"]["name"] == "Phase Specific WTIV"
    assert phase_config["site"]["distance"] == 500

    phase_config = project.create_config_for_phase("TurbineInstallation")

    assert phase_config["wtiv"]["name"] == "Example WTIV"
    assert phase_config["site"]["distance"] == 50

    project.run()


def test_expected_config_merging():
    """Tests for merging of expected configs."""

    config1 = {
        "site": {"distance": "float", "depth": "float"},
        "plant": {"num_turbines": "int"},
    }

    config2 = {
        "site": {"distance": "float", "wave_height": "float"},
        "monopile": {"diameter": "float"},
    }

    config = ProjectManager.merge_dicts(config1, config2)

    assert config == {
        "site": {
            "distance": "float",
            "depth": "float",
            "wave_height": "float",
        },
        "plant": {"num_turbines": "int"},
        "monopile": {"diameter": "float"},
    }


def test_find_key_match():
    class SpecificTurbineInstallation(InstallPhase):
        expected_config = {}

    TestProjectManager = deepcopy(ProjectManager)
    TestProjectManager.register_install_phase(SpecificTurbineInstallation)

    phase_dict = TestProjectManager.phase_dict()
    assert "SpecificTurbineInstallation" in phase_dict.keys()

    tests = [
        ("TurbineInstallation", "TurbineInstallation"),
        ("TurbineInstallation_Test", "TurbineInstallation"),
        ("TurbineInstallation Test", "TurbineInstallation"),
        ("TurbineInstallation Test_1", "TurbineInstallation"),
        ("SpecificTurbineInstallation", "SpecificTurbineInstallation"),
        ("SpecificTurbineInstallation_Test", "SpecificTurbineInstallation"),
        ("SpecificTurbineInstallation Test", "SpecificTurbineInstallation"),
        ("SpecificTurbineInstallation Test_1", "SpecificTurbineInstallation"),
    ]

    for test in tests:

        i, expected = test
        response = TestProjectManager.find_key_match(i)

        assert response.__name__ == expected

    fails = [
        "DifferentTurbineInstallation",
        "Other TurbineInstallation",
        "Extra Different TurbineInstallation_1",
    ]

    for f in fails:

        assert TestProjectManager.find_key_match(f) is None


# Overlapping Install Phases
def test_install_phase_start_parsing__dates():

    config_mixed_starts = deepcopy(config)
    config_mixed_starts["install_phases"] = {
        "MonopileInstallation": "10/22/2010",
        "TurbineInstallation": "10/22/2009",
        "ArrayCableInstallation": ("MonopileInstallation", 0.5),
    }

    project = ProjectManager(config_mixed_starts, weather=weather_df)
    defined, depends = project._parse_install_phase_values(
        config_mixed_starts["install_phases"]
    )
    assert len(defined) == 2
    assert len(depends) == 1

    assert defined["MonopileInstallation"] == 8761
    assert defined["TurbineInstallation"] == 1


def test_install_phase_start_parsing__ints():

    config_mixed_starts = deepcopy(config)
    config_mixed_starts["install_phases"] = {
        "MonopileInstallation": 0,
        "TurbineInstallation": 100,
        "ArrayCableInstallation": ("MonopileInstallation", 0.5),
    }

    project = ProjectManager(config_mixed_starts, weather=weather_df)
    defined, depends = project._parse_install_phase_values(
        config_mixed_starts["install_phases"]
    )
    assert len(defined) == 2
    assert len(depends) == 1

    assert defined["MonopileInstallation"] == 0
    assert defined["TurbineInstallation"] == 100


@pytest.mark.parametrize("weather", (None, weather_df))
@pytest.mark.parametrize("defined", (0, "10/22/2009"))
@pytest.mark.parametrize(
    "amount_str, diff",
    [
        ("hours=10", 10),
        ("days=1", 24),
        ("days=1;hours=10", 34),
        ("weeks=1", 168),
        ("weeks=1;days=1;hours=10", 202),
    ],
)
def test_dependent_install_phases_fixed_amounts(
    weather,
    defined,
    amount_str,
    diff,
):

    new = deepcopy(config)
    new["install_phases"] = {
        "MonopileInstallation": defined,
        "TurbineInstallation": ("MonopileInstallation", amount_str),
    }

    project = ProjectManager(new, weather=weather)
    project.run()

    diff_calc = (
        project.phase_starts["TurbineInstallation"]
        - project.phase_starts["MonopileInstallation"]
    )

    assert diff_calc == diff


@pytest.mark.parametrize("input_val", (-1, 1.2, "years=10", "days:10"))
def test_dependent_install_phases_bad_inputs(input_val):

    new = deepcopy(config)
    new["install_phases"] = {
        "MonopileInstallation": 0,
        "TurbineInstallation": ("MonopileInstallation", input_val),
    }

    project = ProjectManager(new)

    with pytest.raises(ValueError):
        project.run()


@pytest.mark.parametrize("weather", (None, weather_df))
@pytest.mark.parametrize("defined", (0, "10/22/2009"))
@pytest.mark.parametrize("input_val", (0.5, "hours=10", "days=1;hours=10"))
def test_dependent_install_phases_phase_dates(weather, defined, input_val):

    new = deepcopy(config)
    new["install_phases"] = {
        "MonopileInstallation": defined,
        "TurbineInstallation": ("MonopileInstallation", input_val),
    }

    project = ProjectManager(new, weather=weather)
    project.run()

    phase_dates = project.phase_dates
    for p in ["MonopileInstallation", "TurbineInstallation"]:
        assert p in phase_dates

        for key in ["start", "end"]:
            _ = dt.datetime.strptime(
                phase_dates[p][key],
                project.date_format_long,
            )
            assert True


def test_chained_dependencies():

    config_chained = deepcopy(config)
    config_chained["spi_vessel"] = "test_scour_protection_vessel"
    config_chained["scour_protection"] = {
        "tonnes_per_substructure": 200,
        "cost_per_tonne": 45,
    }
    config_chained["install_phases"] = {
        "ScourProtectionInstallation": 0,
        "MonopileInstallation": ("ScourProtectionInstallation", 0.1),
        "TurbineInstallation": ("MonopileInstallation", 0.5),
    }

    project = ProjectManager(config_chained)
    project.run()

    df = pd.DataFrame(project.actions)
    sp = list(df.loc[df["phase"] == "ScourProtectionInstallation"]["time"])
    mp = list(df.loc[df["phase"] == "MonopileInstallation"]["time"])
    tu = list(df.loc[df["phase"] == "TurbineInstallation"]["time"])

    assert min(sp) == 0
    assert min(mp) == (max(sp) - min(sp)) * 0.1
    assert min(tu) == (max(mp) - min(mp)) * 0.5 + min(mp)


@pytest.mark.parametrize(
    "m_start, t_start",
    [(0, 0), (0, 100), (100, 100), (100, 200)],
)
def test_index_starts(m_start, t_start):
    """
    Tests functionality related to passing index starts into 'install_phases'
    sub-dict.
    """
    _target_diff = t_start - m_start

    config_with_index_starts = deepcopy(config)
    config_with_index_starts["install_phases"] = {
        "MonopileInstallation": m_start,
        "TurbineInstallation": t_start,
    }

    project = ProjectManager(config_with_index_starts)
    project.run()

    df = pd.DataFrame(project.actions)

    _m = df.loc[df["phase"] == "MonopileInstallation"].iloc[0]
    _t = df.loc[df["phase"] == "TurbineInstallation"].iloc[0]

    _diff = (_t["time"] - _t["duration"]) - (_m["time"] - _m["duration"])
    assert _diff == _target_diff


@pytest.mark.parametrize(
    "m_start, t_start, expected",
    [
        (0, 0, 0),
        (0, 1000, 1000),
        ("03/01/2010", "03/01/2010", 0),
        ("03/01/2010", "05/01/2010", 1464),
    ],
)
def test_start_dates_with_weather(m_start, t_start, expected):

    config_with_defined_starts = deepcopy(config)
    config_with_defined_starts["install_phases"] = {
        "MonopileInstallation": m_start,
        "TurbineInstallation": t_start,
    }

    project = ProjectManager(config_with_defined_starts, weather=weather_df)
    project.run()
    df = pd.DataFrame(project.actions)

    _m = df.loc[df["phase"] == "MonopileInstallation"].iloc[0]
    _t = df.loc[df["phase"] == "TurbineInstallation"].iloc[0]

    _diff = (_t["time"] - _t["duration"]) - (_m["time"] - _m["duration"])
    assert _diff == expected


@pytest.mark.parametrize(
    "m_start, t_start",
    [
        (0, "03/01/2010"),
        ("03/01/2010", 0),
    ],
)
def test_mixed_start_date_types(m_start, t_start):

    config_with_defined_starts = deepcopy(config)
    config_with_defined_starts["install_phases"] = {
        "MonopileInstallation": m_start,
        "TurbineInstallation": t_start,
        "ArrayCableInstallation": ("MonopileInstallation", 0.5),
    }

    with pytest.raises(ValueError):
        project = ProjectManager(config_with_defined_starts, weather_df)
        project.run()


def test_duplicate_phase_definitions():
    config_with_duplicates = deepcopy(config)
    config_with_duplicates["MonopileInstallation_1"] = {
        "plant": {"num_turbines": 5}
    }

    config_with_duplicates["MonopileInstallation_2"] = {
        "plant": {"num_turbines": 5},
        "site": {"distance": 100},
    }

    config_with_duplicates["install_phases"] = {
        "MonopileInstallation_1": 0,
        "MonopileInstallation_2": 800,
        "TurbineInstallation": 1600,
    }

    project = ProjectManager(config_with_duplicates)
    project.run()

    df = (
        pd.DataFrame(project.actions)
        .groupby(["phase", "action"])
        .count()["time"]
    )

    assert df.loc[("MonopileInstallation_1", "Drive Monopile")] == 5
    assert df.loc[("MonopileInstallation_2", "Drive Monopile")] == 5
    assert df.loc[("TurbineInstallation", "Attach Tower Section")] == 10


def test_custom_install_phases():

    # Not a subclass
    class CustomInstallPhase:
        pass

    with pytest.raises(ValueError):
        ProjectManager.register_design_phase(CustomInstallPhase)

    # Wrong subclass
    class CustomDesignPhase(DesignPhase):
        pass

    with pytest.raises(ValueError):
        ProjectManager.register_install_phase(CustomDesignPhase)

    # Name already taken
    class MonopileInstallation(InstallPhase):
        pass

    with pytest.raises(ValueError):
        ProjectManager.register_install_phase(MonopileInstallation)

    # Bad name format
    class MonopileInstallation_Custom(InstallPhase):
        pass

    with pytest.raises(ValueError):
        ProjectManager.register_install_phase(MonopileInstallation_Custom)

    # Successful registration
    class CustomInstallPhase(InstallPhase):
        pass

    ProjectManager.register_install_phase(CustomInstallPhase)
    assert (
        ProjectManager.find_key_match("CustomInstallPhase")
        == CustomInstallPhase
    )


def test_custom_design_phases():

    # Not a subclass
    class CustomDesignPhase:
        pass

    with pytest.raises(ValueError):
        ProjectManager.register_design_phase(CustomDesignPhase)

    # Wrong subclass
    class CustomInstallPhase(InstallPhase):
        pass

    with pytest.raises(ValueError):
        ProjectManager.register_design_phase(CustomInstallPhase)

    # Name already taken
    class MonopileDesign(DesignPhase):
        pass

    with pytest.raises(ValueError):
        ProjectManager.register_install_phase(MonopileDesign)

    # Bad name format
    class MonopileDesign_Custom(DesignPhase):
        pass

    with pytest.raises(ValueError):
        ProjectManager.register_install_phase(MonopileDesign_Custom)

    # Successful registration
    class CustomDesignPhase(DesignPhase):
        pass

    ProjectManager.register_design_phase(CustomDesignPhase)
    assert (
        ProjectManager.find_key_match("CustomDesignPhase") == CustomDesignPhase
    )


# Design Phase Interactions
def test_design_phases():

    config_with_design = deepcopy(config)

    # Add MonopileDesign
    config_with_design["design_phases"] = ["MonopileDesign"]

    # Add required parameters
    config_with_design["site"]["mean_windspeed"] = 9
    config_with_design["turbine"]["rotor_diameter"] = 200
    config_with_design["turbine"]["rated_windspeed"] = 10
    config_with_design["monopile_design"] = {}

    # Remove monopile sub dictionary
    _ = config_with_design.pop("monopile")
    project = ProjectManager(config_with_design)
    project.run()

    assert isinstance(project.config["monopile"], dict)

    project = ProjectManager(config_with_design)
    project.run()


# Outputs
def test_resolve_project_capacity():

    # Missing turbine rating
    config1 = {"plant": {"capacity": 600, "num_turbines": 40}}

    project1 = ProjectManager(config1)
    assert project1.config["plant"]["capacity"] == config1["plant"]["capacity"]
    assert (
        project1.config["plant"]["num_turbines"]
        == config1["plant"]["num_turbines"]
    )
    assert project1.config["turbine"]["turbine_rating"] == 15

    # Missing plant capacity
    config2 = {
        "plant": {"num_turbines": 40},
        "turbine": {"turbine_rating": 15},
    }

    project2 = ProjectManager(config2)
    assert project2.config["plant"]["capacity"] == 600
    assert (
        project2.config["plant"]["num_turbines"]
        == config2["plant"]["num_turbines"]
    )
    assert (
        project2.config["turbine"]["turbine_rating"]
        == config2["turbine"]["turbine_rating"]
    )

    # Missing number of turbines
    config3 = {"plant": {"capacity": 600}, "turbine": {"turbine_rating": 15}}

    project3 = ProjectManager(config3)
    assert project3.config["plant"]["capacity"] == config3["plant"]["capacity"]
    assert project3.config["plant"]["num_turbines"] == 40
    assert (
        project3.config["turbine"]["turbine_rating"]
        == config3["turbine"]["turbine_rating"]
    )

    # Test for float precision
    config4 = {
        "plant": {"capacity": 600, "num_turbines": 40},
        "turbine": {"turbine_rating": 15.0},
    }

    project4 = ProjectManager(config4)
    assert project4.config["plant"]["capacity"] == config4["plant"]["capacity"]
    assert (
        project4.config["plant"]["num_turbines"]
        == config4["plant"]["num_turbines"]
    )
    assert (
        project4.config["turbine"]["turbine_rating"]
        == config4["turbine"]["turbine_rating"]
    )

    # Non matching calculated value
    config5 = {
        "plant": {"capacity": 700, "num_turbines": 40},
        "turbine": {"turbine_rating": 15.0},
    }

    with pytest.raises(AttributeError):
        _ = ProjectManager(config5)

    # Test for not enough information
    config6 = {"plant": {"capacity": 600}}

    project6 = ProjectManager(config6)
    assert project6.config["plant"]["capacity"] == config6["plant"]["capacity"]

    with pytest.raises(KeyError):
        _ = project6.config["turbine"]["turbine_rating"]

    with pytest.raises(KeyError):
        _ = project6.config["plant"]["num_turbines"]


# Exceptions
def test_incomplete_config():

    incomplete_config = deepcopy(config)
    _ = incomplete_config["site"].pop("depth")

    with pytest.raises(MissingInputs):
        project = ProjectManager(incomplete_config)
        project.run()


def test_wrong_phases():

    wrong_phases = deepcopy(config)
    wrong_phases["install_phases"].append("IncorrectPhaseName")

    with pytest.raises(PhaseNotFound):
        project = ProjectManager(wrong_phases)
        project.run()


def test_bad_dates():

    bad_dates = deepcopy(config)
    bad_dates["install_phases"] = {
        "MonopileInstallation": "03/01/2015",
        "TurbineInstallation": "05/01/2015",
    }

    with pytest.raises(WeatherProfileError):
        project = ProjectManager(bad_dates, weather=weather_df)
        project.run()


def test_no_defined_start():

    missing_start = deepcopy(config)
    missing_start["install_phases"] = {
        "MonopileInstallation": ("TurbineInstallation", 0.1),
        "TurbineInstallation": ("MonopileInstallation", 0.1),
    }

    with pytest.raises(ValueError):
        project = ProjectManager(missing_start)
        project.run()


def test_circular_dependencies():

    circular_deps = deepcopy(config)
    circular_deps["spi_vessel"] = "test_scour_protection_vessel"
    circular_deps["scour_protection"] = {
        "tonnes_per_substructure": 200,
        "cost_per_tonne": 45,
    }
    circular_deps["install_phases"] = {
        "ScourProtectionInstallation": 0,
        "MonopileInstallation": ("TurbineInstallation", 0.1),
        "TurbineInstallation": ("MonopileInstallation", 0.1),
    }

    with pytest.raises(PhaseDependenciesInvalid):
        project = ProjectManager(circular_deps)
        project.run()


def test_dependent_phase_ordering():

    wrong_order = deepcopy(config)
    wrong_order["spi_vessel"] = "test_scour_protection_vessel"
    wrong_order["scour_protection"] = {
        "tonnes_per_substructure": 200,
        "cost_per_tonne": 45,
    }
    wrong_order["install_phases"] = {
        "ScourProtectionInstallation": ("TurbineInstallation", 0.1),
        "TurbineInstallation": ("MonopileInstallation", 0.1),
        "MonopileInstallation": 0,
    }

    project = ProjectManager(wrong_order)
    project.run()

    assert len(project.phase_times) == 3


def test_ProjectProgress():

    data = [
        ("Export System", 10),
        ("Offshore Substation", 20),
        ("Array String", 15),
        ("Array String", 25),
        ("Turbine", 5),
        ("Turbine", 10),
        ("Turbine", 15),
        ("Turbine", 20),
        ("Turbine", 25),
        ("Substructure", 6),
        ("Substructure", 9),
        ("Substructure", 14),
        ("Substructure", 22),
        ("Substructure", 26),
    ]

    progress = ProjectProgress(data)

    assert progress.parse_logs("Export System") == [10]

    turbines = progress.parse_logs("Turbine")
    assert len(turbines) == 5

    chunks = list(progress.chunk_max(turbines, 2))
    assert chunks[0] == 10
    assert chunks[1] == 20
    assert chunks[2] == 25

    assert progress.complete_export_system == 20
    times, _ = progress.complete_array_strings
    assert times == [15, 26]

    times, turbines = progress.energize_points
    assert times == [20, 26]
    assert sum(turbines) == 5


def test_ProjectProgress_with_incomplete_project():

    project = ProjectManager(config)
    project.run()

    _ = project.progress.parse_logs("Substructure")
    _ = project.progress.parse_logs("Turbine")

    with pytest.raises(ValueError):
        _ = project.progress.complete_export_system

    with pytest.raises(ValueError):
        _ = project.progress.complete_array_strings


def test_ProjectProgress_with_complete_project():

    project = ProjectManager(complete_project)
    project.run()

    _ = project.progress.parse_logs("Substructure")
    _ = project.progress.parse_logs("Turbine")
    _ = project.progress.parse_logs("Array String")
    _ = project.progress.parse_logs("Export System")
    _ = project.progress.parse_logs("Offshore Substation")

    _ = project.progress.complete_export_system
    _ = project.progress.complete_array_strings

    _ = project.progress.energize_points

    new = deepcopy(complete_project)
    new["plant"]["num_turbines"] = 61

    # Uneven strings
    project = ProjectManager(new)
    project.run()

    _ = project.progress.energize_points


def test_monthly_expenses():

    project = ProjectManager(complete_project)
    project.run()
    _ = project.monthly_expenses

    # Still report expenses for "incomplete" project
    config = deepcopy(complete_project)
    _ = config["install_phases"].pop("TurbineInstallation")

    project = ProjectManager(config)
    project.run()

    _ = project.monthly_expenses


def test_monthly_revenue():

    project = ProjectManager(complete_project)
    project.run()
    _ = project.monthly_revenue

    # Can't generate revenue with "incomplete" project
    config = deepcopy(complete_project)
    _ = config["install_phases"].pop("TurbineInstallation")

    project = ProjectManager(config)
    project.run()

    with pytest.raises(ValueError):
        _ = project.monthly_revenue


def test_cash_flow():

    project = ProjectManager(complete_project)
    project.run()
    _ = project.cash_flow

    # Can't generate revenue with "incomplete" project but cash flow will still
    # be reported
    config = deepcopy(complete_project)
    _ = config["install_phases"].pop("TurbineInstallation")

    project = ProjectManager(config)
    project.run()

    cash_flow = project.cash_flow
    assert all(v <= 0 for v in cash_flow.values())


def test_npv():

    project = ProjectManager(complete_project)
    project.run()
    baseline = project.npv

    config = deepcopy(complete_project)
    config["project_parameters"] = {"ncf": 0.35}
    project = ProjectManager(config)
    project.run()
    assert project.npv != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"offtake_price": 70}
    project = ProjectManager(config)
    project.run()
    assert project.npv != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"project_lifetime": 30}
    project = ProjectManager(config)
    project.run()
    assert project.npv != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"discount_rate": 0.03}
    project = ProjectManager(config)
    project.run()
    assert project.npv != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"opex_rate": 120}
    project = ProjectManager(config)
    project.run()
    assert project.npv != baseline


def test_soft_costs():

    project = ProjectManager(complete_project)
    baseline = project.soft_capex

    config = deepcopy(complete_project)
    config["project_parameters"] = {"construction_insurance": 50}
    project = ProjectManager(config)
    project.run()
    assert project.soft_capex != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"construction_financing": 190}
    project = ProjectManager(config)
    project.run()
    assert project.soft_capex != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"procurement_contingency": 320}
    project = ProjectManager(config)
    project.run()
    assert project.soft_capex != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"installation_contingency": 320}
    project = ProjectManager(config)
    project.run()
    assert project.soft_capex != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"decommissioning": 50}
    project = ProjectManager(config)
    project.run()
    assert project.soft_capex != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"commissioning": 50}
    project = ProjectManager(config)
    project.run()
    assert project.soft_capex != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"construction_insurance_factor": 0.02}
    project = ProjectManager(config)
    project.run()
    assert project.soft_capex != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"construction_financing_factor": 1.2}
    project = ProjectManager(config)
    project.run()
    assert project.soft_capex != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {
        "spend_schedule": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0.5, 5: 0.5}
    }
    project = ProjectManager(config)
    project.run()
    assert project.soft_capex != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"tax_rate": 0.35}
    project = ProjectManager(config)
    project.run()
    assert project.soft_capex != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"interest_during_construction": 0.06}
    project = ProjectManager(config)
    project.run()
    assert project.soft_capex != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"procurement_contingency_factor": 0.1}
    project = ProjectManager(config)
    project.run()
    assert project.soft_capex != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"commissioning_factor": 0.3}
    project = ProjectManager(config)
    project.run()
    assert project.soft_capex != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"installation_contingency_factor": 0.7}
    project = ProjectManager(config)
    project.run()
    assert project.soft_capex != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"decommissioning_factor": 0.7}
    project = ProjectManager(config)
    project.run()
    assert project.soft_capex != baseline


def test_project_costs():

    project = ProjectManager(complete_project)
    baseline = project.project_capex

    config = deepcopy(complete_project)
    config["project_parameters"] = {"site_auction_price": 50e6}
    project = ProjectManager(config)
    assert project.project_capex != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"site_assessment_cost": 25e6}
    project = ProjectManager(config)
    assert project.project_capex != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"construction_plan_cost": 25e6}
    project = ProjectManager(config)
    assert project.project_capex != baseline

    config = deepcopy(complete_project)
    config["project_parameters"] = {"installation_plan_cost": 25e6}
    project = ProjectManager(config)
    assert project.project_capex != baseline


def test_capex_categories():

    project = ProjectManager(complete_project)
    project.run()
    baseline = project.capex_breakdown
    _ = project.capex_breakdown_per_kw

    new_config = deepcopy(complete_project)
    new_config["install_phases"]["ExportCableInstallation_1"] = 0
    new_project = ProjectManager(new_config)
    new_project.run()
    new_breakdown = new_project.capex_breakdown

    assert new_breakdown["Export System"] > baseline["Export System"]
    assert (
        new_breakdown["Export System Installation"]
        > baseline["Export System Installation"]
    )


def test_total_capex():
    """Test total capex for baseline fixed and floating project."""

    fix_project = ProjectManager(complete_project)
    fix_project.run()

    assert fix_project.total_capex == pytest.approx(
        1593220043.059402, abs=1e-1
    )

    flt_project = ProjectManager(complete_floating_project)
    flt_project.run()

    assert flt_project.total_capex == pytest.approx(
        4087665127.1458263, abs=1e-1
    )


def test_construction_financing_factor_exception():
    """Test the construction financing factor method for soft capex."""

    config = deepcopy(complete_project)
    config["project_parameters"] = {
        "spend_schedule": {0: 0.15, 1: 0.25, 2: 0.3, 3: 0.1, 4: 0.1, 5: 0.0}
    }  # does not sum to 1.0

    with pytest.raises(ValueError):

        project = ProjectManager(config)
        project.construction_financing_factor()


def test_deprecated_warnings():

    config = deepcopy(complete_project)
    config["project_parameters"] = {"contingency": 88}
    with pytest.deprecated_call():
        project = ProjectManager(config)
        project.run()
