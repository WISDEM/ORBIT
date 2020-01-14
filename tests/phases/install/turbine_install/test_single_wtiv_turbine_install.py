"""Tests for the `MonopileInstallation` class without feeder barges."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from copy import deepcopy

import pytest

from tests.data import test_weather
from tests.vessels import WTIV_SPECS
from ORBIT.vessels.tasks import defaults
from ORBIT.phases.install import TurbineInstallation

config = {
    "wtiv": WTIV_SPECS,
    "site": {"depth": 40, "distance": 50},
    "plant": {"num_turbines": 50},
    "port": {"monthly_rate": 100000, "num_cranes": 1},
    "turbine": {
        "hub_height": 80,
        "tower": {
            "type": "Tower",
            "deck_space": 100,
            "weight": 400,
            "length": 80,
        },
        "nacelle": {"type": "Nacelle", "deck_space": 200, "weight": 400},
        "blade": {"type": "Blade", "deck_space": 100, "weight": 100},
    },
}


def test_creation():

    sim = TurbineInstallation(config, print_logs=False)
    assert sim.config == config
    assert sim.env
    assert sim.env.logger


def test_port_creation():

    sim = TurbineInstallation(config, print_logs=False)
    assert sim.port
    assert sim.port.crane.capacity == config["port"]["num_cranes"]


@pytest.mark.parametrize("wtiv", [(WTIV_SPECS), ("example_wtiv")])
def test_vessel_creation(wtiv):

    _config = deepcopy(config)
    _config["wtiv"] = wtiv

    sim = TurbineInstallation(_config, print_logs=False)
    assert sim.wtiv
    assert sim.wtiv.jacksys
    assert sim.wtiv.crane


def test_turbine_creation():

    sim = TurbineInstallation(config, print_logs=False)
    assert sim.num_turbines == config["plant"]["num_turbines"]

    t = len(
        [item for item in sim.port.items if item["type"] == "Tower Section"]
    )
    assert sim.num_turbines == t

    n = len([item for item in sim.port.items if item["type"] == "Nacelle"])
    assert sim.num_turbines == n

    b = len([item for item in sim.port.items if item["type"] == "Blade"])
    assert sim.num_turbines * 3 == b


def test_logger_creation():

    sim = TurbineInstallation(config, log_level="INFO")
    assert sim.env.logger.level == 20

    sim = TurbineInstallation(config, log_level="DEBUG")
    assert sim.env.logger.level == 10


def test_full_run():

    sim = TurbineInstallation(config, log_level="INFO")
    sim.run()

    complete = float(sim.logs["time"].max())

    assert complete > 0

    sim = TurbineInstallation(config, weather=test_weather, log_level="INFO")
    sim.run()

    with_weather = float(sim.logs["time"].max())

    assert with_weather >= complete


def test_for_complete_logging():

    sim = TurbineInstallation(config, log_level="INFO")
    sim.run()

    df = sim.phase_dataframe.copy()
    df = df.loc[~df["agent"].isin(["Port"])]
    df = df.assign(shift=(df["time"] - df["time"].shift(1)))

    assert (df["duration"] - df["shift"]).max() < 1e-9


def test_for_complete_installation():

    sim = TurbineInstallation(config, log_level="INFO", print_logs=False)
    sim.run()

    installed_towers = len(
        sim.logs.loc[sim.logs["action"] == "AttachTowerSection"]
    )
    assert installed_towers == sim.num_turbines

    installed_nacelles = len(
        sim.logs.loc[sim.logs["action"] == "AttachNacelle"]
    )
    assert installed_nacelles == sim.num_turbines

    installed_blades = len(sim.logs.loc[sim.logs["action"] == "AttachBlade"])
    assert installed_blades == sim.num_turbines * 3


def test_for_efficiencies():

    sim = TurbineInstallation(config)
    sim.run()

    assert 0 <= sim.detailed_output["Example WTIV_operational_efficiency"] <= 1
    assert (
        0 <= sim.detailed_output["Example WTIV_cargo_weight_utilization"] <= 1
    )
    assert 0 <= sim.detailed_output["Example WTIV_deck_space_utilization"] <= 1


def test_kwargs():

    sim = TurbineInstallation(config, log_level="INFO", print_logs=False)
    sim.run()
    baseline = sim.total_phase_time

    keywords = [
        "tower_section_fasten_time",
        "tower_section_release_time",
        "tower_section_attach_time",
        "nacelle_fasten_time",
        "nacelle_release_time",
        "nacelle_attach_time",
        "blade_fasten_time",
        "blade_release_time",
        "blade_attach_time",
        "site_position_time",
        "crane_reequip_time",
    ]

    failed = []

    for kw in keywords:

        default = defaults[kw]
        kwargs = {kw: default + 2}

        new_sim = TurbineInstallation(
            config, log_level="INFO", print_logs=False, **kwargs
        )
        new_sim.run()
        new_time = new_sim.total_phase_time

        if new_time > baseline:
            pass

        else:
            failed.append(kw)

    if failed:
        raise Exception(f"'{failed}' not affecting results.")

    else:
        assert True


def test_multiple_tower_sections():

    sim = TurbineInstallation(config, log_level="INFO", print_logs=False)
    sim.run()
    baseline = len(sim.logs.loc[sim.logs["action"] == "AttachTowerSection"])

    two_sections = deepcopy(config)
    two_sections["turbine"]["tower"]["sections"] = 2

    sim2 = TurbineInstallation(
        two_sections, log_level="INFO", print_logs=False
    )
    sim2.run()
    new = len(sim2.logs.loc[sim2.logs["action"] == "AttachTowerSection"])

    assert new == 2 * baseline

    df = sim2.phase_dataframe.copy()
    df = df.loc[~df["agent"].isin(["Port"])]

    for vessel in df["agent"].unique():

        vl = df[df["agent"] == vessel].copy()
        vl = vl.assign(shift=(vl["time"] - vl["time"].shift(1)))

        assert (vl["shift"] - vl["duration"]).abs().max() < 1e-9
