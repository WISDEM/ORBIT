"""Tests for the vessel simulation logic."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2019, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


import simpy

from tests.data import test_weather
from tests.vessels import WTIV_SPECS, FEEDER_SPECS
from ORBIT.vessels import Vessel
from ORBIT.simulation import Environment, VesselStorage
from ORBIT.simulation.logic import (
    get_item_from_storage,
    shuttle_items_to_queue,
    prep_for_site_operations,
)

# TODO: Write tests for vessel logic statements.
# Will likely involve simplifying several methods so they can be more easily
# tested at a unit level.
