"""Tests for the vessel simulation logic."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


import os

import simpy
import pytest

from tests.data import test_weather
from ORBIT.vessels import Vessel
from ORBIT.simulation import Environment, VesselStorage
from ORBIT.phases.install import (
    TurbineInstallation,
    MonopileInstallation,
    ArrayCableInstallation,
    ExportCableInstallation,
    ScourProtectionInstallation,
    OffshoreSubstationInstallation,
)
from ORBIT.simulation.logic import (
    get_item_from_storage,
    shuttle_items_to_queue,
    prep_for_site_operations,
)
from ORBIT.simulation.logic.vessel_logic import release_map

installations = [
    MonopileInstallation,
    TurbineInstallation,
    ArrayCableInstallation,
    OffshoreSubstationInstallation,
    ExportCableInstallation,
    ScourProtectionInstallation,
]
installations = [ArrayCableInstallation, ExportCableInstallation]
install_configs = ["array_cable_install", "export_cable_install"]

item_map = {}


def get_vessel(simulation):
    vessels = ("cable_lay_vessel", "wtiv", "feeder", "scour_vessel")
    for vessel in vessels:
        vessel = getattr(simulation, vessel, None)
        if vessel is None:
            continue
        return vessel


@pytest.mark.parametrize(
    "action_key,expected",
    (
        ("Monopile", "ReleaseMonopile"),
        ("Transition Piece", "ReleaseTP"),
        ("Tower Section", "ReleaseTowerSection"),
        ("Nacelle", "ReleaseNacelle"),
        ("Blade", "ReleaseBlade"),
        ("Topside", "ReleaseTopside"),
    ),
)
def test_release_map(action_key, expected):
    time, action = release_map(action_key)
    assert time
    assert action == expected
