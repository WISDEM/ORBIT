"""`MooringSystemDesign` and related functionality."""

__author__ = "Jake Nunemaker, modified by Becca F."
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov & rebecca.fuchs@nrel.gov"

import numpy as np
from scipy.interpolate import interp1d
from ORBIT.phases.design import DesignPhase


class SemiTautMooringSystemDesign(DesignPhase):
    """Mooring System and Anchor Design."""

    expected_config = {
        "site": {"depth": "float"},
        "turbine": {"turbine_rating": "int | float"},
        "plant": {"num_turbines": "int"},
        "mooring_system_design": {
            "num_lines": "int | float (optional, default: 4)",
            "anchor_type": "str (optional, default: 'Drag Embedment')",
            "mooring_line_cost_rate": "int | float (optional)",
            "drag_embedment_fixed_length": "int | float (optional, default: .5km)",
        },
    }

    output_config = {
        "mooring_system": {
            "num_lines": "int",
            # "line_diam": "m, float", # this is not needed for mooring.py
            "line_mass": "t",  # you need this for mooring.py (mooring installation module)
            "line_cost": "USD",  # you can calculate this based on each rope&chain length & diameter.
            "line_length": "m",  # this can be calculated from rope length and chain length (which you get from an empirical eqn as function of depth)
            "anchor_mass": "t",  # you need this for mooring.py (mooring installation module)
            "anchor_type": "str",  # keep, changed default to drag embedment.
            "anchor_cost": "USD",  # this can be calculated also as a function of (depth?) from the empirical data you have.
        }
    }

    def __init__(self, config, **kwargs):
        """
        Creates an instance of MooringSystemDesign.

        Parameters
        ----------
        config : dict
        """

        config = self.initialize_library(config, **kwargs)
        self.config = self.validate_config(config)
        self.num_turbines = self.config["plant"]["num_turbines"]

        self._design = self.config.get("mooring_system_design", {})
        self.num_lines = self._design.get("num_lines", 4)
        self.anchor_type = self._design.get("anchor_type", "Drag Embedment")

        self._outputs = {}

    def run(self):
        """
        Main run function.
        """

        self.calculate_line_length_mass()
        self.determine_mooring_line_cost()
        self.calculate_anchor_mass_cost()

        self._outputs["mooring_system"] = {**self.design_result}

    def calculate_line_length_mass(self):
        """
        Returns the mooring line length and mass.
        """

        depth = self.config["site"]["depth"]

        # Input hybrid mooring system design from Cooperman et al. (2022), https://www.nrel.gov/docs/fy22osti/82341.pdf 'Assessment of Offshore Wind Energy Leasing Areas for Humboldt and Moorow Bay Wind Energy Areas, California
        depths = np.array([500, 750, 1000, 1250, 1500])
        rope_lengths = np.array([478.41, 830.34, 1229.98, 1183.93, 1079.62])
        rope_diameters = np.array(
            [0.2, 0.2, 0.2, 0.2, 0.2]
        )  # you need the diameter for the cost data
        chain_lengths = np.array([917.11, 800.36, 609.07, 896.42, 1280.57])
        chain_diameters = np.array([0.13, 0.17, 0.22, 0.22, 0.22])

        # Interpolate
        finterp_rope = interp1d(depths, rope_lengths)
        finterp_chain = interp1d(depths, chain_lengths)
        finterp_rope_diam = interp1d(depths, rope_diameters)
        finterp_chain_diam = interp1d(depths, chain_diameters)

        # Rope and chain length at project depth
        self.chain_length = finterp_chain(depth)
        self.rope_length = finterp_rope(depth)
        # Rope and chain diameter at project depth
        self.rope_diameter = finterp_rope_diam(depth)
        self.chain_diameter = finterp_chain_diam(depth)

        self.line_length = self.rope_length + self.chain_length

        chain_kg_per_m = 19900 * (
            self.chain_diameter**2
        )  # 19,900 kg/m^2 (diameter)/m (length)
        rope_kg_per_m = 797.8 * (
            self.rope_diameter**2
        )  # 797.8 kg/ m^2 (diameter) / m (length)
        self.line_mass = (self.chain_length * chain_kg_per_m) + (
            self.rope_length * rope_kg_per_m
        )  # kg
        # print('total hybrid line mass is ' + str(self.line_mass) + 'kg')
        # convert kg to metric tonnes
        self.line_mass = self.line_mass / 1e3

    def calculate_anchor_mass_cost(self):
        """
        Returns the mass and cost of anchors.

        TODO: Anchor masses are rough estimates based on initial literature
        review. Should be revised when this module is overhauled in the future.
        """

        if self.anchor_type == "Drag Embedment":
            self.anchor_mass = 20  # t.  This should be updated, but I don't have updated data right now for this.
            # Input hybrid mooring system design from Cooperman et al. (2022), https://www.nrel.gov/docs/fy22osti/82341.pdf 'Assessment of Offshore Wind Energy Leasing Areas for Humboldt and Moorow Bay Wind Energy Areas, California
            depths = np.array([500, 750, 1000, 1250, 1500])
            anchor_costs = np.array(
                [112766, 125511, 148703, 204988, 246655]
            )  # [USD]

            # interpolate anchor cost to project depth
            depth = self.config["site"]["depth"]
            finterp_anchor_cost = interp1d(depths, anchor_costs)
            self.anchor_cost = finterp_anchor_cost(
                depth
            )  # replace this with interp. function based on depth of hybrid mooring line

    def determine_mooring_line_cost(self):
        """Returns cost of one line mooring line."""
        # Input hybrid mooring system design from Cooperman et al. (2022), https://www.nrel.gov/docs/fy22osti/82341.pdf 'Assessment of Offshore Wind Energy Leasing Areas for Humboldt and Moorow Bay Wind Energy Areas, California
        depths = np.array([500, 750, 1000, 1250, 1500])  # [m]
        total_line_costs = np.array(
            [826598, 1221471, 1682208, 2380035, 3229700]
        )  # [USD]
        finterp_total_line_cost = interp1d(depths, total_line_costs)
        depth = self.config["site"]["depth"]
        self.line_cost = finterp_total_line_cost(depth)
        return self.line_cost

    @property
    def total_cost(self):
        """Returns the total cost of the mooring system."""

        return (
            self.num_lines
            * self.num_turbines
            * (self.anchor_cost + self.line_cost)
        )

    @property
    def detailed_output(self):
        """Returns detailed phase information."""

        return {
            "num_lines": self.num_lines,
            # "line_diam": self.line_diam,
            "line_mass": self.line_mass,
            "line_length": self.line_length,
            "line_cost": self.line_cost,
            "anchor_type": self.anchor_type,
            "anchor_mass": self.anchor_mass,
            "anchor_cost": self.anchor_cost,
            "system_cost": self.total_cost,
        }

    @property
    def design_result(self):
        """Returns the results of the design phase."""

        return {"mooring_system": self.detailed_output}
