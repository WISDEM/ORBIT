__author__ = "Jake Nunemaker, Sophie Bredenkamp"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "Jake.Nunemaker@nrel.gov"


import warnings
from copy import deepcopy
from itertools import product

import pytest

from ORBIT.core.library import extract_library_specs
from ORBIT.phases.design import ElectricalDesign, OffshoreSubstationDesign

# OSS TESTING

base = {
    "site": {"distance_to_landfall": 50, "depth": 30},
    "plant": {"capacity": 500},
    "export_system_design": {"cables": "XLPE_630mm_220kV"},
    "landfall": {},
    "substation_design": {},
}


@pytest.mark.parametrize(
    "distance_to_landfall,depth,plant_cap,cable",
    product(
        range(10, 201, 50),
        range(10, 51, 10),
        range(100, 2001, 500),
        ["XLPE_630mm_220kV", "XLPE_800mm_220kV", "XLPE_1000mm_220kV"],
    ),
)
def test_parameter_sweep(distance_to_landfall, depth, plant_cap, cable):
    config = {
        "site": {"distance_to_landfall": distance_to_landfall, "depth": depth},
        "plant": {"capacity": plant_cap},
        "export_system_design": {"cables": cable},
        "substation_design": {},
    }

    o = ElectricalDesign(config)
    o.run()

    # Check valid substructure length
    assert 10 <= o._outputs["offshore_substation_substructure"]["length"] <= 80

    # Check valid substructure mass
    assert (
        200 <= o._outputs["offshore_substation_substructure"]["mass"] <= 2700
    )

    # Check valid topside mass
    assert 200 <= o._outputs["offshore_substation_topside"]["mass"] <= 5500

    # Check valid substation cost
    assert 1e6 <= o.total_substation_cost <= 1e9


def test_ac_oss_kwargs():
    test_kwargs = {
        "mpt_cost": 13500,
        # "topside_fab_cost_rate": 17000,    # breaks
        "topside_design_cost": 7e6,
        "shunt_cost_rate": 40000,
        "switchgear_cost": 15e5,
        "backup_gen_cost": 2e6,
        "workspace_cost": 3e6,
        "other_ancillary_cost": 4e6,
        "topside_assembly_factor": 0.09,
        "oss_substructure_cost_rate": 7250,
        "oss_pile_cost_rate": 2500,
        "num_substations": 4,
    }

    o = ElectricalDesign(base)
    o.run()
    base_cost = o.detailed_output["total_substation_cost"]

    for k, v in test_kwargs.items():
        config = deepcopy(base)
        config["substation_design"] = {}
        config["substation_design"][k] = v

        o = ElectricalDesign(config)
        o.run()
        cost = o.detailed_output["total_substation_cost"]
        print("passed")
        assert cost != base_cost


def test_dc_oss_kwargs():
    test_kwargs = {"converter_cost": 300e6, "dc_breaker_cost": 300e6}

    dc_base = deepcopy(base)
    dc_base["export_system_design"]["cables"] = "HVDC_2000mm_320kV"
    o = ElectricalDesign(dc_base)
    o.run()
    base_cost = o.detailed_output["total_substation_cost"]

    for k, v in test_kwargs.items():
        config = deepcopy(base)
        config["export_system_design"]["cables"] = "HVDC_2000mm_320kV"
        config["substation_design"] = {}
        config["substation_design"][k] = v

        o = ElectricalDesign(config)
        o.run()
        cost = o.detailed_output["total_substation_cost"]
        print("passed")
        assert cost != base_cost


def test_new_old_hvac_substation():
    """Temporary test until ElectricalDesign is merged with new release"""

    config = deepcopy(base)
    config["export_system_design"] = {"cables": "HVDC_2000mm_320kV"}
    config["plant"]["capacity"] = 1000  # MW
    config["plant"]["num_turbines"] = 200
    config["turbine"] = {"turbine_rating": 5}

    new = ElectricalDesign(config)
    new.run()

    old = OffshoreSubstationDesign(config)
    old.run()

    # same values
    assert new.num_substations == old.num_substations
    assert new.topside_mass == old.topside_mass
    assert new.ancillary_system_costs == old.ancillary_system_costs
    assert new.substructure_mass == old.substructure_mass

    # different values
    assert new.substation_cost != old.substation_cost
    assert new.mpt_rating != old.mpt_rating
    assert new.num_mpt != old.num_mpt
    assert new.mpt_cost != old.mpt_cost
    assert new.topside_cost != old.topside_cost
    assert new.shunt_reactor_cost != old.shunt_reactor_cost


def test_hvdc_substation():
    config = deepcopy(base)
    config["export_system_design"] = {"cables": "HVDC_2000mm_320kV"}
    o = ElectricalDesign(config)
    o.run()
    assert o.converter_cost != 0
    assert o.shunt_reactor_cost == 0
    assert o.dc_breaker_cost != 0
    assert o.switchgear_cost == 0
    assert o.mpt_cost == 0
    # assert o.num_cables / o.num_converters == 2  # breaks

    config = deepcopy(base)
    config["export_system_design"] = {"cables": "HVDC_2500mm_525kV"}

    o = ElectricalDesign(config)
    o.run()

    # assert o.num_converters == o.num_cables    # breaks


def test_onshore_substation():
    config = deepcopy(base)
    o = ElectricalDesign(config)
    o.run()
    assert o.onshore_cost == pytest.approx(95.487e6, abs=1e2)  # 109.32e6

    config_mono = deepcopy(config)
    config_mono["export_system_design"] = {"cables": "HVDC_2000mm_320kV"}
    o_mono = ElectricalDesign(config_mono)
    o_mono.run()
    assert o_mono.onshore_cost == 244.3e6

    config_bi = deepcopy(config)
    config_bi["export_system_design"] = {"cables": "HVDC_2500mm_525kV"}
    o_bi = ElectricalDesign(config_bi)
    o_bi.run()
    assert o_bi.onshore_cost == 450e6


# EXPORT CABLE TESTING


def test_export_kwargs():
    test_kwargs = {
        "num_redundant": 2,
        "touchdown_distance": 50,
        "percent_added_length": 0.15,
        # "interconnection_distance": 6,
    }

    o = ElectricalDesign(base)
    o.run()
    base_cost = o.total_cost

    for k, v in test_kwargs.items():
        config = deepcopy(base)
        config["export_system_design"] = {"cables": "XLPE_630mm_220kV"}
        config["export_system_design"][k] = v

        o = ElectricalDesign(config)
        o.run()
        cost = o.total_cost

        assert cost != base_cost


config = extract_library_specs("config", "export_design")


def test_export_system_creation():
    export = ElectricalDesign(config)
    export.run()

    assert isinstance(export.num_cables, int)
    assert export.length
    assert export.mass
    assert export.cable
    assert export.total_length
    assert export.total_mass
    assert export.num_substations
    assert export.topside_mass
    assert export.substructure_mass


def test_number_cables():
    export = ElectricalDesign(config)
    export.run()

    assert export.num_cables == 9


def test_cable_length():
    export = ElectricalDesign(config)
    export.run()

    length = (0.02 + 3 + 30) * 1.01
    assert export.length == length


def test_cable_mass():
    export = ElectricalDesign(config)
    export.run()

    length = (0.02 + 3 + 30) * 1.01
    mass = length * export.cable.linear_density
    assert export.mass == pytest.approx(mass, abs=1e-6)


def test_total_cable():
    export = ElectricalDesign(config)
    export.run()

    length = 0.02 + 3 + 30
    length += length * 0.01
    mass = length * export.cable.linear_density
    assert export.total_mass == pytest.approx(mass * 9, abs=1e-10)
    assert export.total_length == pytest.approx(length * 9, abs=1e-10)


def test_cables_property():
    export = ElectricalDesign(config)
    export.run()

    assert (
        export.sections_cables == export.cable.name
    ).sum() == export.num_cables


def test_cable_lengths_property():
    export = ElectricalDesign(config)
    export.run()

    cable_name = export.cable.name
    assert (
        export.cable_lengths_by_type[cable_name] == export.length
    ).sum() == export.num_cables


def test_total_cable_len_property():
    export = ElectricalDesign(config)
    export.run()

    cable_name = export.cable.name
    assert export.total_cable_length_by_type[cable_name] == pytest.approx(
        export.total_length, abs=1e-10
    )


def test_design_result():
    export = ElectricalDesign(config)
    export.run()

    _ = export.cable.name
    cables = export.design_result["export_system"]["cable"]

    assert cables["sections"] == [export.length]
    assert cables["number"] == 9
    assert cables["linear_density"] == export.cable.linear_density


def test_floating_length_calculations():
    base = deepcopy(config)
    base["site"]["depth"] = 250
    base["export_system_design"]["touchdown_distance"] = 0

    sim = ElectricalDesign(base)
    sim.run()

    base_length = sim.total_length

    with_cat = deepcopy(config)
    with_cat["site"]["depth"] = 250

    new = ElectricalDesign(with_cat)
    new.run()

    assert new.total_length < base_length


def test_HVDC_cable():
    base = deepcopy(config)
    base["export_system_design"] = {"cables": "HVDC_2000mm_320kV"}

    sim = ElectricalDesign(base)
    sim.run()

    assert sim.num_cables % 2 == 0

    base = deepcopy(config)
    base["export_system_design"] = {"cables": "HVDC_2500mm_525kV"}

    sim = ElectricalDesign(base)
    sim.run()

    assert sim.num_cables % 2 == 0


def test_num_crossing():
    base_sim = ElectricalDesign(config)
    base_sim.run()

    cross = deepcopy(config)
    cross["export_system_design"]["cable_crossings"] = {"crossing_number": 2}

    cross_sim = ElectricalDesign(cross)
    cross_sim.run()

    assert cross_sim.crossing_cost != base_sim.crossing_cost


def test_cost_crossing():
    base_sim = ElectricalDesign(config)
    base_sim.run()

    cross = deepcopy(config)
    cross["export_system_design"]["cable_crossings"] = {
        "crossing_number": 1,
        "crossing_unit_cost": 100000,
    }

    cross_sim = ElectricalDesign(cross)
    cross_sim.run()

    assert cross_sim.crossing_cost != base_sim.crossing_cost


def test_deprecated_landfall():

    base = deepcopy(config)

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        sim = ElectricalDesign(base)
        sim.run()

    deprecated = deepcopy(base)
    deprecated["landfall"] = {"interconnection_distance": 4}

    with pytest.deprecated_call():
        sim = ElectricalDesign(deprecated)
        sim.run()
