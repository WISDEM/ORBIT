"""Provides the `ElectricalDesign class."""

__author__ = ["Sophie Bredenkamp"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = ""
__email__ = []

import numpy as np

from ORBIT.phases.design._cables import CableSystem


class ElectricalDesign(CableSystem):
    """
    Design phase for export cabling and offshore substation systems.

    Attributes
    ----------
    num_cables : int
        Total number of cables required for transmitting power.
    length : float
        Length of a single cable connecting the OSS to the interconnection
        in km.
    mass : float
        Mass of `length` in tonnes.
    cable : `Cable`
        Instance of `ORBIT.phases.design.Cable`. An export system will
        only require a single type of cable.
    total_length : float
        Total length of cable required to trasmit power.
    total_mass : float
        Total mass of cable required to transmit power.
    sections_cables : np.ndarray, shape: (`num_cables, )
        An array of `cable`.
    sections_lengths : np.ndarray, shape: (`num_cables, )
        An array of `length`.

    """

    #:
    expected_config = {
        "site": {"distance_to_landfall": "km", "depth": "m"},
        "landfall": {"interconnection_distance": "km (optional)"},
        "plant": {"capacity": "MW"},
        "export_system_design": {
            "cables": "str",
            "num_redundant": "int (optional)",
            "touchdown_distance": "m (optional, default: 0)",
            "percent_added_length": "float (optional)",
            "cable_crossings": {
                "crossing_number": "int (optional)",
                "crossing_unit_cost": "float (optional)",
            },
        },
        "substation_design": {
            "mpt_cost": "USD (optional)",
            "topside_fab_cost_rate": "USD/t (optional)",
            "topside_design_cost": "USD (optional)",
            "shunt_cost_rate": "USD/MW (optional)",
            "switchgear_cost": "USD (optional)",
            "dc_breaker_cost": "USD (optional)",
            "backup_gen_cost": "USD (optional)",
            "workspace_cost": "USD (optional)",
            "other_ancillary_cost": "USD (optional)",
            "converter_cost": "USD (optional)",
            "onshore_converter_cost": "USD (optional)",
            "topside_assembly_factor": "float (optional)",
            "oss_substructure_cost_rate": "USD/t (optional)",
            "oss_pile_cost_rate": "USD/t (optional)",
            "num_substations": "int (optional)",
        },
    }

    output_config = {
        "num_substations": "int",
        "offshore_substation_topside": "dict",
        "offshore_substation_substructure": "dict",
        "export_system": {
            "system_cost": "USD",
            "cable": {
                "linear_density": "t/km",
                "sections": [("length, km", "speed, km/h (optional)")],
                "number": "int (optional)",
                "diameter": "int",
                "cable_type": "str",
            },
        },
    }

    def __init__(self, config, **kwargs):
        """Creates an instance of ElectricalDesign."""

        config = self.initialize_library(config, **kwargs)
        self.config = self.validate_config(config)

        # CABLES
        super().__init__(config, "export", **kwargs)

        for name in self.expected_config["site"]:
            setattr(self, "".join(("_", name)), config["site"][name])
        self._depth = config["site"]["depth"]
        self._distance_to_landfall = config["site"]["distance_to_landfall"]
        self._plant_capacity = self.config["plant"]["capacity"]
        self._get_touchdown_distance()

        try:
            self._distance_to_interconnection = config["landfall"][
                "interconnection_distance"
            ]
        except KeyError:
            self._distance_to_interconnection = 3

        # SUBSTATION
        self._outputs = {}

    def run(self):
        """Main run function."""

        self.export_system_design = self.config["export_system_design"]
        self.offshore_substation_design = self.config.get(
            "offshore_substation_design", {}
        )

        # CABLES
        self._initialize_cables()
        self.cable = self.cables[[*self.cables][0]]
        self.compute_number_cables()
        self.compute_cable_length()
        self.compute_cable_mass()
        self.compute_total_cable()
        self.calc_crossing_cost()

        self._outputs["export_system"] = {"system_cost": self.total_cable_cost}
        for _, cable in self.cables.items():
            self._outputs["export_system"]["cable"] = {
                "linear_density": cable.linear_density,
                "sections": [self.length],
                "number": self.num_cables,
                "cable_power": cable.cable_power,
                "cable_type": cable.cable_type,
            }

        # SUBSTATION
        self.calc_num_substations()
        self.calc_substructure_length()
        self.calc_substructure_deck_space()
        self.calc_topside_deck_space()

        self.calc_mpt_cost()
        self.calc_topside_mass_and_cost()
        self.calc_shunt_reactor_cost()
        self.calc_switchgear_costs()
        self.calc_ancillary_system_cost()
        self.calc_assembly_cost()
        self.calc_substructure_mass_and_cost()
        self.calc_converter_cost()
        self.calc_dc_breaker_cost()
        self.calc_onshore_cost()

        self._outputs["offshore_substation_substructure"] = {
            "type": "Monopile",  # Substation install only supports monopiles
            "deck_space": self.substructure_deck_space,
            "mass": self.substructure_mass,
            "length": self.substructure_length,
            "unit_cost": self.substructure_cost,
        }

        self._outputs["offshore_substation_topside"] = {
            "deck_space": self.topside_deck_space,
            "mass": self.topside_mass,
            "unit_cost": self.substation_cost,
        }

        self._outputs["num_substations"] = self.num_substations

    @property
    def detailed_output(self):
        """Returns export system design outputs."""

        _output = {
            **self.design_result,
            "export_system_total_mass": self.total_mass,
            "export_system_total_length": self.total_length,
            "export_system_total_cost": self.total_cable_cost,
            "export_system_cable_power": self.cable.cable_power,
            "num_substations": self.num_substations,
            "substation_mpt_rating": self.mpt_rating,
            "substation_topside_mass": self.topside_mass,
            "substation_topside_cost": self.topside_cost,
            "substation_substructure_mass": self.substructure_mass,
            "substation_substructure_cost": self.substructure_cost,
            "total_substation_cost": self.total_substation_cost,
        }

        return _output

    @property
    def design_result(self):
        """
        Returns the results of self.run().
        """
        return self._outputs

    @property
    def total_cable_cost(self):
        """Returns total export system cable cost."""

        return sum(self.cost_by_type.values()) + self.crossing_cost

    def compute_number_cables(self):
        """
        Calculate the total number of required and redundant cables to
        transmit power to the onshore interconnection.

        Parameters
        ----------
        num_redundant : int
        """

        _num_redundant = self._design.get("num_redundant", 0)

        if (
            self.cable.cable_type == "HVDC-monopole"
            or self.cable.cable_type == "HVDC-bipole"
        ):
            num_required = 2 * np.ceil(
                self._plant_capacity / self.cable.cable_power
            )
            num_redundant = 2 * _num_redundant
        else:
            num_required = np.ceil(
                self._plant_capacity / self.cable.cable_power
            )
            num_redundant = _num_redundant

        self.num_cables = int(num_required + num_redundant)

    def compute_cable_length(self):
        """
        Calculates the total distance an export cable must travel.
        """

        added_length = 1.0 + self._design.get("percent_added_length", 0.0)
        self.length = round(
            (
                self.free_cable_length
                + (self._distance_to_landfall - self.touchdown / 1000)
                + self._distance_to_interconnection
            )
            * added_length,
            10,
        )

    def compute_cable_mass(self):
        """
        Calculates the total mass of a single length of export cable.
        """

        self.mass = round(self.length * self.cable.linear_density, 10)

    def compute_total_cable(self):
        """
        Calculates the total length and mass of cables required to fully
        connect the OSS to the interconnection point.
        """

        self.total_length = round(self.num_cables * self.length, 10)
        self.total_mass = round(self.num_cables * self.mass, 10)

    @property
    def sections_cable_lengths(self):
        """
        Creates an array of section lengths to work with `CableSystem`

        Returns
        -------
        np.ndarray
            Array of `length` with shape (`num_cables`, ).
        """
        return np.full(self.num_cables, self.length)

    @property
    def sections_cables(self):
        """
        Creates an array of cable names to work with `CableSystem`.

        Returns
        -------
        np.ndarray
            Array of `cable.name` with shape (`num_cables`, ).
        """

        return np.full(self.num_cables, self.cable.name)

    def calc_crossing_cost(self):
        """Compute cable crossing costs"""
        self._crossing_design = self.config["export_system_design"].get(
            "cable_crossings", {}
        )
        self.crossing_cost = self._crossing_design.get(
            "crossing_unit_cost", 500000
        ) * self._crossing_design.get("crossing_number", 0)

    @property
    def total_substation_cost(self):
        """Returns the total substation cost."""

        return (
            self.topside_cost + self.substructure_cost + self.substation_cost
        )

    def calc_num_substations(self):
        """Computes number of substations"""

        self._design = self.config.get("substation_design", {})

        hvac_substation_capacity = 1200  # MW

        if (
            self.cable.cable_type == "HVDC-monopole"
            or self.cable.cable_type == "HVDC-bipole"
        ):
            self.num_substations = self._design.get(
                "num_substations", int(self.num_cables / 2)
            )
        else:
            self.num_substations = self._design.get(
                "num_substations",
                int(np.ceil(self._plant_capacity / hvac_substation_capacity)),
            )

    @property
    def substation_cost(self):
        """Returns total procuremet cost of the topside."""

        return (
            self.mpt_cost
            + self.shunt_reactor_cost
            + self.switchgear_cost
            + self.converter_cost
            + self.dc_breaker_cost
            + self.ancillary_system_cost
            + self.land_assembly_cost
        ) / self.num_substations

    def calc_mpt_cost(self):
        """Computes transformer cost

        Parameters
        ----------
        mpt_cost : int | float
        """

        mpt_cost = self._design.get("mpt_cost", 2.87e6)

        self.num_mpt = self.num_cables

        if (
            self.cable.cable_type == "HVDC-monopole"
            or self.cable.cable_type == "HVDC-bipole"
        ):
            self.mpt_cost = 0
            self.mpt_rating = 0  # added by NSR

        else:
            self.mpt_cost = self.num_mpt * mpt_cost

            self.mpt_rating = (
                round((self._plant_capacity * 1.15 / self.num_mpt) / 10.0)
                * 10.0
            )

    def calc_shunt_reactor_cost(self):
        """Computes shunt reactor cost

        Parameters
        ----------
        shunt_cost_rate : int | float
        """

        touchdown = self.config["site"]["distance_to_landfall"]
        shunt_cost_rate = self._design.get("shunt_cost_rate", 1e4)

        if (
            self.cable.cable_type == "HVDC-monopole"
            or self.cable.cable_type == "HVDC-bipole"
        ):
            compensation = 0
        else:
            for _, cable in self.cables.items():
                compensation = touchdown * cable.compensation_factor  # MW
        self.shunt_reactor_cost = (
            compensation * shunt_cost_rate * self.num_cables
        )

    def calc_switchgear_costs(self):
        """Computes switchgear cost

        Parameters
        ----------
        switchgear_cost : int | float
        """

        switchgear_cost = self._design.get("switchgear_cost", 4e6)

        if (
            self.cable.cable_type == "HVDC-monopole"
            or self.cable.cable_type == "HVDC-bipole"
        ):
            num_switchgear = 0
        else:
            num_switchgear = self.num_cables

        self.switchgear_cost = num_switchgear * switchgear_cost

    def calc_dc_breaker_cost(self):
        """Computes HVDC circuit breaker cost

        Parameters
        ----------
        dc_breaker_cost : int | float
        """

        dc_breaker_cost = self._design.get("dc_breaker_cost", 10.5e6)

        if (
            self.cable.cable_type == "HVDC-monopole"
            or self.cable.cable_type == "HVDC-bipole"
        ):
            num_dc_breakers = self.num_cables
        else:
            num_dc_breakers = 0

        self.dc_breaker_cost = num_dc_breakers * dc_breaker_cost

    def calc_ancillary_system_cost(self):
        """
        Calculates cost of ancillary systems.

        Parameters
        ----------
        backup_gen_cost : int | float
        workspace_cost : int | float
        other_ancillary_cost : int | float
        """

        backup_gen_cost = self._design.get("backup_gen_cost", 1e6)
        workspace_cost = self._design.get("workspace_cost", 2e6)
        other_ancillary_cost = self._design.get("other_ancillary_cost", 3e6)

        self.ancillary_system_cost = (
            backup_gen_cost + workspace_cost + other_ancillary_cost
        ) * self.num_substations

    def calc_converter_cost(self):
        """Computes converter cost"""

        if self.cable.cable_type == "HVDC-monopole":
            self.converter_cost = self.num_substations * self._design.get(
                "converter_cost", 127e6
            )

        elif self.cable.cable_type == "HVDC-bipole":
            self.converter_cost = self.num_substations * self._design.get(
                "converter_cost", 296e6
            )
        else:
            self.converter_cost = 0

    def calc_assembly_cost(self):
        """
        Calculates the cost of assembly on land.

        Parameters
        ----------
        topside_assembly_factor : int | float
        """

        _design = self.config.get("substation_design", {})
        topside_assembly_factor = _design.get("topside_assembly_factor", 0.075)
        self.land_assembly_cost = (
            self.switchgear_cost
            + self.shunt_reactor_cost
            + self.ancillary_system_cost
        ) * topside_assembly_factor

    def calc_substructure_mass_and_cost(self):
        """
        Calculates the mass and associated cost of the substation substructure.

        Parameters
        ----------
        oss_substructure_cost_rate : int | float
        oss_pile_cost_rate : int | float
        """

        _design = self.config.get("substation_design", {})
        substructure_mass = 0.4 * self.topside_mass
        oss_pile_cost_rate = _design.get("oss_pile_cost_rate", 0)
        oss_substructure_cost_rate = _design.get(
            "oss_substructure_cost_rate", 3000
        )

        substructure_pile_mass = 8 * substructure_mass**0.5574
        self.substructure_cost = (
            substructure_mass * oss_substructure_cost_rate
            + substructure_pile_mass * oss_pile_cost_rate
        )

        self.substructure_mass = substructure_mass + substructure_pile_mass

    def calc_substructure_length(self):
        """
        Calculates substructure length as the site depth + 10m
        """

        self.substructure_length = self.config["site"]["depth"] + 10

    def calc_substructure_deck_space(self):
        """
        Calculates required deck space for the substation substructure.

        Coming soon!
        """

        self.substructure_deck_space = 1

    def calc_topside_deck_space(self):
        """
        Calculates required deck space for the substation topside.

        Coming soon!
        """

        self.topside_deck_space = 1

    def calc_topside_mass_and_cost(self):
        """
        Calculates the mass and cost of the substation topsides.

        Parameters
        ----------
        topside_fab_cost_rate : int | float
        topside_design_cost: int | float
        """

        _design = self.config.get("substation_design", {})
        # topside_fab_cost_rate = _design.get("topside_fab_cost_rate", 14500)
        # topside_design_cost = _design.get("topside_design_cost", 4.5e6)

        self.topside_mass = (
            3.85 * (self.mpt_rating * self.num_mpt) / self.num_substations
            + 285
        )
        if self.cable.cable_type == "HVDC-monopole":
            self.topside_cost = _design.get("topside_design_cost", 294e6)
        elif self.cable.cable_type == "HVDC-bipole":
            self.topside_cost = _design.get("topside_design_cost", 476e6)
        else:
            self.topside_cost = _design.get("topside_design_cost", 107.3e6)

    def calc_onshore_cost(self):
        """Minimum Cost of Onshore Substation Connection"""

        if self.cable.cable_type == "HVDC-monopole":
            self.onshore_converter_cost = (
                self.num_substations
                * self._design.get("onshore_converter_cost", 157e6)
            )
            self.ais_cost = 0
            self.onshore_construction = 87.3e6
            self.onshore_compensation = 0
        elif self.cable.cable_type == "HVDC-bipole":
            self.onshore_converter_cost = (
                self.num_substations
                * self._design.get("onshore_converter_cost", 350e6)
            )
            self.ais_cost = 0
            self.onshore_construction = 100e6
            self.onshore_compensation = 0
        else:
            self.onshore_converter_cost = 0
            self.ais_cost = self.num_cables * 9.33e6
            self.onshore_compensation = self.num_cables * (31.3e6 + 8.66e6)
            self.onshore_construction = 5e6 * self.num_substations

        self.onshore_cost = (
            self.onshore_converter_cost
            + self.onshore_construction
            + self.onshore_compensation
            + self.mpt_cost
            + self.ais_cost
        )

        self._outputs["export_system"][
            "onshore_construction_cost"
        ] = self.onshore_cost
