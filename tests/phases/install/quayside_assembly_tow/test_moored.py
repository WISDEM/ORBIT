"""Tests for the `MooredSubInstallation` class and related infrastructure."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


import pandas as pd
import pytest

from tests.data import test_weather
from ORBIT.core.library import extract_library_specs
from ORBIT.phases.install import MooredSubInstallation

config = extract_library_specs("config", "moored_install")
multi_assembly = extract_library_specs(
    "config", "moored_install_multi_assembly"
)
multi_tow = extract_library_specs("config", "moored_install_multi_tow")
multi_assembly_multi_tow = extract_library_specs(
    "config", "moored_install_multi_assembly_multi_tow"
)
no_supply = extract_library_specs("config", "moored_install_no_supply")


def test_simulation_setup():
    sim = MooredSubInstallation(config)
    assert sim.config == config
    assert sim.env

    assert len(sim.sub_assembly_lines) == config["port"]["sub_assembly_lines"]
    assert (
        len(sim.turbine_assembly_lines)
        == config["port"]["turbine_assembly_cranes"]
    )
    assert (
        len(sim.installation_groups)
        == config["towing_vessel_groups"]["num_groups"]
    )
    assert sim.num_turbines == config["plant"]["num_turbines"]


@pytest.mark.parametrize(
    "weather", (None, test_weather), ids=["no_weather", "test_weather"]
)
@pytest.mark.parametrize(
    "config",
    (config, multi_assembly, multi_tow, multi_assembly_multi_tow, no_supply),
    ids=[
        "1 assembly, 1 tow",
        "3 assembly, 1 tow",
        "1 assembly, 3 tow",
        "3 assembly, 3 tow",
        "no supply",
    ],
)
def test_for_complete_logging(weather, config):
    sim = MooredSubInstallation(config, weather=weather)
    sim.run()

    df = pd.DataFrame(sim.env.actions)
    df = df.assign(shift=(df["time"] - df["time"].shift(1)))

    for vessel in df["agent"].unique():
        _df = df[df["agent"] == vessel].copy()
        _df = _df.assign(shift=(_df["time"] - _df["time"].shift(1)))
        assert (_df["shift"] - _df["duration"]).abs().max() < 1e-9

    assert ~df["cost"].isnull().any()
    _ = sim.agent_efficiencies
    _ = sim.detailed_output

    installed_mooring_lines = len(
        [a for a in sim.env.actions if a["action"] == "Position Substructure"]
    )
    assert installed_mooring_lines == sim.num_turbines
