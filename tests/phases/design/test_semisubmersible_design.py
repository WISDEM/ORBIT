__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "Jake.Nunemaker@nrel.gov"


from copy import deepcopy
from itertools import product

import pytest

from ORBIT.core.library import extract_library_specs
from ORBIT.phases.design import (
    SemiSubmersibleDesign,
    CustomSemiSubmersibleDesign,
)

base = {
    "site": {"depth": 500},
    "plant": {"num_turbines": 50},
    "turbine": {"turbine_rating": 12},
    "semisubmersible_design": {},
}


@pytest.mark.parametrize(
    "depth,turbine_rating",
    product(range(100, 1201, 200), range(3, 15, 1)),
)
def test_parameter_sweep(depth, turbine_rating):

    config = {
        "site": {"depth": depth},
        "plant": {"num_turbines": 50},
        "turbine": {"turbine_rating": turbine_rating},
        "substation_design": {},
    }

    s = SemiSubmersibleDesign(config)
    s.run()

    assert s.detailed_output["stiffened_column_mass"] > 0
    assert s.detailed_output["truss_mass"] > 0
    assert s.detailed_output["heave_plate_mass"] > 0
    assert s.detailed_output["secondary_steel_mass"] > 0


def test_design_kwargs():

    test_kwargs = {
        "stiffened_column_CR": 3000,
        "truss_CR": 6000,
        "heave_plate_CR": 6000,
        "secondary_steel_CR": 7000,
    }

    s = SemiSubmersibleDesign(base)
    s.run()
    base_cost = s.total_cost

    for k, v in test_kwargs.items():

        config = deepcopy(base)
        config["semisubmersible_design"] = {}
        config["semisubmersible_design"][k] = v

        s = SemiSubmersibleDesign(config)
        s.run()
        cost = s.total_cost

        assert cost != base_cost


config_custom = extract_library_specs(
    "config", "semisubmersible_design_custom"
)


def test_calc_geometric_scale_factor():
    pass


def test_bouyant_column_volume():
    pass


def test_center_column_volume():
    pass


def test_pontoon_volume():
    pass


def test_strut_volume():
    pass


def test_substructure_steel_mass():
    pass


def test_ballast_mass():
    pass


def test_tower_interface_mass():
    pass


def test_substructure_steel_cost():
    pass


def test_substructure_mass():
    pass


def test_substructure_unit_cost():
    pass


def test_custom_design_kwargs():

    test_kwargs = {
        "column_diameter": 15,
        "wall_thickness": 0.1,
        "column_height": 20,
        "pontoon_length": 52,
        "pontoon_width": 15,
        "pontoon_height": 5,
        "strut_diameter": 1.0,
        "steel_density": 8500,
        "ballast_mass": 1000,
        "tower_interface_mass": 125,
        "steel_CR": 3000,
        "ballast_material_CR": 200,
    }

    cust = CustomSemiSubmersibleDesign(config_custom)
    cust.run()
    base_cost = cust.total_cost

    for k, v in test_kwargs.items():

        config = deepcopy(config_custom)
        config["semisubmersible_design"] = {}
        config["semisubmersible_design"][k] = v

        cust = CustomSemiSubmersibleDesign(config)
        cust.run()
        cost = cust.total_cost

        assert cost != base_cost
