"""Provides the `SemiSubmersibleDesign` class (from OffshoreBOS)."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from ORBIT.phases.design import DesignPhase


class SemiSubmersibleDesign(DesignPhase):
    """Semi-Submersible Substructure Design."""

    expected_config = {
        "site": {"depth": "m"},
        "plant": {"num_turbines": "int"},
        "turbine": {"turbine_rating": "MW"},
        "semisubmersible_design": {
            "stiffened_column_CR": "$/t (optional, default: 3120)",
            "truss_CR": "$/t (optional, default: 6250)",
            "heave_plate_CR": "$/t (optional, default: 6250)",
            "secondary_steel_CR": "$/t (optional, default: 7250)",
            "towing_speed": "km/h (optional, default: 6)",
        },
    }

    output_config = {
        "substructure": {
            "mass": "t",
            "unit_cost": "USD",
            "towing_speed": "km/h",
        },
    }

    def __init__(self, config, **kwargs):
        """
        Creates an instance of `SemiSubmersibleDesign`.

        Parameters
        ----------
        config : dict
        """

        config = self.initialize_library(config, **kwargs)
        self.config = self.validate_config(config)
        self._design = self.config.get("semisubmersible_design", {})

        self._outputs = {}

    def run(self):
        """Main run function."""

        substructure = {
            "mass": self.substructure_mass,
            "unit_cost": self.substructure_cost,
            "towing_speed": self._design.get("towing_speed", 6),
        }

        self._outputs["substructure"] = substructure

    @property
    def stiffened_column_mass(self):
        """
        Calculates the mass of the stiffened column for a single
        semi-submersible in tonnes. From original OffshoreBOS model.
        """

        rating = self.config["turbine"]["turbine_rating"]
        mass = -0.9581 * rating**2 + 40.89 * rating + 802.09

        return mass

    @property
    def stiffened_column_cost(self):
        """
        Calculates the cost of the stiffened column for a single
        semi-submersible. From original OffshoreBOS model.
        """

        cr = self._design.get("stiffened_column_CR", 3120)
        return self.stiffened_column_mass * cr

    @property
    def truss_mass(self):
        """
        Calculates the truss mass for a single semi-submersible in tonnes. From
        original OffshoreBOS model.
        """

        rating = self.config["turbine"]["turbine_rating"]
        mass = 2.7894 * rating**2 + 15.591 * rating + 266.03

        return mass

    @property
    def truss_cost(self):
        """
        Calculates the cost of the truss for a signle semi-submerisble. From
        original OffshoreBOS model.
        """

        cr = self._design.get("truss_CR", 6250)
        return self.truss_mass * cr

    @property
    def heave_plate_mass(self):
        """
        Calculates the heave plate mass for a single semi-submersible in
        tonnes. Source: original OffshoreBOS model.
        """

        rating = self.config["turbine"]["turbine_rating"]
        mass = -0.4397 * rating**2 + 21.545 * rating + 177.42

        return mass

    @property
    def heave_plate_cost(self):
        """
        Calculates the heave plate cost for a single semi-submersible. From
        original OffshoreBOS model.
        """

        cr = self._design.get("heave_plate_CR", 6250)
        return self.heave_plate_mass * cr

    @property
    def secondary_steel_mass(self):
        """
        Calculates the mass of the required secondary steel for a single
        semi-submersible. From original OffshoreBOS model.
        """

        rating = self.config["turbine"]["turbine_rating"]
        mass = -0.153 * rating**2 + 6.54 * rating + 128.34

        return mass

    @property
    def secondary_steel_cost(self):
        """
        Calculates the cost of the required secondary steel for a single
        semi-submersible. For original OffshoreBOS model.
        """

        cr = self._design.get("secondary_steel_CR", 7250)
        return self.secondary_steel_mass * cr

    @property
    def substructure_mass(self):
        """Returns single substructure mass."""

        return (
            self.stiffened_column_mass
            + self.truss_mass
            + self.heave_plate_mass
            + self.secondary_steel_mass
        )

    @property
    def substructure_cost(self):
        """Returns single substructure cost."""

        return (
            self.stiffened_column_cost
            + self.truss_cost
            + self.heave_plate_cost
            + self.secondary_steel_cost
        )

    @property
    def total_substructure_mass(self):
        """Returns mass of all substructures."""

        num = self.config["plant"]["num_turbines"]
        return num * self.substructure_mass

    @property
    def design_result(self):
        """Returns the result of `self.run()`."""

        if not self._outputs:
            raise Exception("Has `SemiSubmersibleDesign` been ran yet?")

        return self._outputs

    @property
    def total_cost(self):
        """Returns total phase cost in $USD."""

        num = self.config["plant"]["num_turbines"]
        return num * self.substructure_cost

    @property
    def detailed_output(self):
        """Returns detailed phase information."""

        _outputs = {
            "stiffened_column_mass": self.stiffened_column_mass,
            "stiffened_column_cost": self.stiffened_column_cost,
            "truss_mass": self.truss_mass,
            "truss_cost": self.truss_cost,
            "heave_plate_mass": self.heave_plate_mass,
            "heave_plate_cost": self.heave_plate_cost,
            "secondary_steel_mass": self.secondary_steel_mass,
            "secondary_steel_cost": self.secondary_steel_cost,
        }

        return _outputs


"""Provides the `CustomSemiSubmersibleDesign` class."""

__author__ = "Matt Shields"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Nick Riccobono"
__email__ = "nicholas.riccobono@nrel.gov"

import numpy as np

from ORBIT.phases.design import DesignPhase

"""
Based on semisub design from 15 MW RWT

[1]	C. Allen et al., “Definition of the UMaine VolturnUS-S Reference Platform
 Developed for the IEA Wind 15-Megawatt Offshore Reference Wind Turbine,”
 NREL/TP--5000-76773, 1660012, MainId:9434, Jul. 2020. doi: 10.2172/1660012.
[2]	K. L. Roach, M. A. Lackner, and J. F. Manwell, “A New Methodology for
 Upscaling Semi-submersible Platforms for Floating Offshore Wind Turbines,”
 Wind Energy Science Discussions, pp. 1–33, Feb. 2023,
 doi: 10.5194/wes-2023-18.
"""


class CustomSemiSubmersibleDesign(DesignPhase):
    """Customized Semi-Submersible Substructure Design."""

    expected_config = {
        "site": {"depth": "m"},
        "plant": {"num_turbines": "int"},
        "turbine": {"turbine_rating": "MW"},
        "semisubmersible_design": {
            "stiffened_column_CR": "$/t (optional, default: 3120)",
            "truss_CR": "$/t (optional, default: 6250)",
            "heave_plate_CR": "$/t (optional, default: 6250)",
            "secondary_steel_CR": "$/t (optional, default: 7250)",
            "towing_speed": "km/h (optional, default: 6)",
            "column_diameter": "m (optional, default: 12.5)",
            "wall_thickness": "m (optional, default: 0.045)",
            "column_height": "m (optional, default: 35)",
            "pontoon_length": "m (optional, default: 51.75)",
            "pontoon_width": "m (optional, default: 12.5)",
            "pontoon_height": "m (optional, default: 7)",
            "strut_diameter": "m (optional, 0.9)",
            "steel_density": "kg/m^3 (optional, default: 7980)",
            "ballast_mass": "tonnes (optional, default 0)",
            "tower_interface_mass": "tonnes (optional, default 100)",
            "steel_cost_rate": "$/tonne (optional, default: 4500)",
            "ballast_material_CR": "$/tonne (optional, default: 150)",
        },
    }

    output_config = {
        "substructure": {
            "mass": "t",
            "unit_cost": "USD",
            "towing_speed": "km/h",
        }
    }

    def __init__(self, config, **kwargs):
        """
        Creates an instance of `CustomSemiSubmersibleDesign`.

        Parameters
        ----------
        config : dict
        """

        config = self.initialize_library(config, **kwargs)
        self.config = self.validate_config(config)
        self._design = self.config.get("semisubmersible_design", {})

        self.num_columns = kwargs.get("number_columns", 3)

        self._outputs = {}

    def run(self):
        """Main run function."""

        self.calc_geometric_scale_factor()

        substructure = {
            "mass": self.substructure_mass,
            "unit_cost": self.substructure_unit_cost,
            "towing_speed": self._design.get("towing_speed", 6),
        }

        self._outputs["substructure"] = substructure

    def calc_geometric_scale_factor(self, **kwargs):
        """Calculates the geometric factor to scale the size of the semi-
        submersible. Upscaling methodology and parameters used are found on
        Lines 335-340 [2].
        """

        turbine_radius = float(self.config["turbine"]["rotor_diameter"] / 2)

        # IEA-15MW 120m radius
        ref_radius = kwargs.get("ref_radius", 120.0)

        # power-law parameter
        alpha = kwargs.get("alpha", 0.72)

        self.geom_scale_factor = (turbine_radius / ref_radius) ** alpha

    @property
    def bouyant_column_volume(self):
        """
        Returns the volume of a capped, hollow, cylindrical column,
        assuming the wall-thickness remains constant [2].
        """

        dc = self._design.get("column_diameter", 12.5) * self.geom_scale_factor
        hc = self._design.get("column_height", 35) * self.geom_scale_factor
        tc = self._design.get("wall_thickness", 0.045)

        return (np.pi / 4) * (hc * dc**2 - (hc - 2 * tc) * (dc - 2 * tc) ** 2)

    @property
    def center_column_volume(self):
        """
        Returns the volume of a hollow column between turbine and
        pontoons, assuming wall-thickness remains constant [2].
        """

        dc = 10.0  # fixed tower diameter
        hc = self._design.get("column_height", 35) * self.geom_scale_factor
        hp = self._design.get("pontoon_height", 7) * self.geom_scale_factor
        tc = self._design.get("wall_thickness", 0.045)

        return (np.pi / 4) * (
            (hc - hp) * dc**2 - (hc - hp) * (dc - 2 * tc) ** 2
        )

    @property
    def pontoon_volume(self):
        """
        Returns the volume of a single hollow rectangular pontoon that connects
        the central column to the outer columns, assuming wall-thickness
        reamins constant [2].
        """
        # TODO: Subtract semi-circular area from fairlead column?

        lp = self._design.get("pontoon_length", 51.75) * self.geom_scale_factor
        wp = self._design.get("pontoon_width", 12.5) * self.geom_scale_factor
        hp = self._design.get("pontoon_height", 7) * self.geom_scale_factor
        tp = self._design.get("wall_thickness", 0.045)

        return (hp * wp - (hp - 2 * tp) * (wp - 2 * tp)) * lp

    @property
    def strut_volume(self):
        """
        Returns the volume of a single solid strut that connects
        the central column to the outer columns.
        """

        lp = self._design.get("pontoon_length", 51.75) * self.geom_scale_factor
        ds = self._design.get("strut_diameter", 0.9) * self.geom_scale_factor

        return (np.pi / 4) * (ds**2) * lp

    @property
    def substructure_steel_mass(self):
        """Returns the total mass of structural steel in the substructure."""

        # TODO: Separate out different steels for each component

        density = self._design.get("steel_density", 7980)

        print(
            "Volumes: ",
            self.bouyant_column_volume,
            self.center_column_volume,
            self.pontoon_volume,
            self.strut_volume,
        )

        return (density / 1000) * (
            self.num_columns * self.bouyant_column_volume
            + self.center_column_volume
            + self.num_columns * self.pontoon_volume
            + self.num_columns * self.strut_volume
        )

    @property
    def ballast_mass(self):
        """Returns the mass of fixed ballast. Default value from [1]."""
        # TODO: Scale ballast mass with some factor?
        # Fixed/Fluid needs to be addressed because 11,300t of seawater is used
        # to submerge the platform.

        return self._design.get("ballast_mass", 2540)

    @property
    def tower_interface_mass(self):
        """Returns the mass of tower interface. Default value from [1]."""

        # TODO: Find a model to estimate the mass for a tower interface

        return self._design.get("tower_interface_mass", 100)

    @property
    def substructure_steel_cost(self):
        """Returns the total cost of structural steel of the substructure
        in $USD.
        """

        self.steel_cr = self._design.get("steel_cost_rate", 4500)

        return self.steel_cr * self.substructure_steel_mass

    @property
    def substructure_mass(self):
        """
        Returns the total mass of structural steel and iron ore ballast
        in the substructure.
        """

        return sum(
            [
                self.substructure_steel_mass,
                self.ballast_mass,
                self.tower_interface_mass,
            ]
        )

    @property
    def substructure_unit_cost(self):
        """
        Returns the total material cost of a single substructure.
        Does not include final assembly or transportation costs.
        """

        ballast_cr = self._design.get("ballast_cost_rate", 150)

        return (
            self.substructure_steel_cost
            + ballast_cr * self.ballast_mass
            + self.steel_cr * self.tower_interface_mass
        )

    @property
    def design_result(self):
        """Returns the result of `self.run()`."""

        if not self._outputs:
            raise Exception("Has `CustomSemiSubmersibleDesign` been ran yet?")

        return self._outputs

    @property
    def total_cost(self):
        """Returns total phase cost in $USD."""

        num = self.config["plant"]["num_turbines"]
        return num * self.substructure_unit_cost

    @property
    def detailed_output(self):
        """Returns detailed phase information."""

        _outputs = {
            "substructure_steel_mass": self.substructure_steel_mass,
            "substructure_steel_cost": self.substructure_steel_cost,
            "substructure_mass": self.substructure_mass,
            "substructure_cost": self.substructure_unit_cost,
            "ballast_mass": self.ballast_mass,
            "tower_interface_mass": self.tower_interface_mass,
        }

        return _outputs
