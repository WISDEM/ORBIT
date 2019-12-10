"""Provides the ScourProtectionDesign class"""

__author__ = "Rob Hammond"
__copyright__ = "Copyright 2019, National Renewable Energy Laboratory"
__maintainer__ = "Rob Hammond"
__email__ = "robert.hammond@nrel.gov"

import numpy as np

from ORBIT.phases.design import DesignPhase


class ScourProtectionDesign(DesignPhase):
    """
    The design phase for the scouring protection used for fixed substructures.
    For more information please refer to [1]_.

    Parameters
    ----------
    config : dict
        Configuration dictionary with scour protection design inputs. See
        `expected_config` for expected data.

    Attributes
    ----------
    phi : float, default: 33.5
        Soil friction angle. Default is for medium density sand.
    equilibrium : float, default: 1.3
        Scour depth equilibrium (S).
    rock_density : float, default: 2600
        Density of rocks used for scouring protection in kg/(m^3).
    scour_depth : float
        Height of the scour protection.

    Other Attributes
    ----------------
    _design : dict
        Dictionary of specific scouring protection design parameters.
    num_turbines : int
        Number of turbines that need scouring protection.

    References
    ----------
    .. [1] Det Norske Veritas AS. (2014, May). Design of Offshore Wind Turbine
       Structures. Retrieved from
       https://rules.dnvgl.com/docs/pdf/DNV/codes/docs/2014-05/Os-J101.pdf
    """

    expected_config = {
        "substructure": {"diameter": "int | float"},
        "plant": {"num_turbines": "int"},
        "scour_protection_design": {
            "cost_per_tonne": "float",
            "rock_density": "float (optional)",
            "design_time": "int | float (optional)",
            "soil_friction_angle": "float (optional)",
            "scour_depth_equilibrium": "float (optional)",
        },
    }

    output_config = {"scour_protection": {"tonnes_per_substructure": "float"}}

    def __init__(self, config, **kwargs):
        """
        Initialization function.

        Parameters
        ----------
        config : dict
            Configuration dictionary for scour protection design phase.
        """

        config = self.initialize_library(config, **kwargs)
        self._design = config["scour_protection_design"]
        self.diameter = config["substructure"]["diameter"]
        self.num_turbines = config["plant"]["num_turbines"]

        try:
            self.phi = self._design["soil_friction_angle"]
        except KeyError:
            self.phi = 33.5

        try:
            self.equilibrium = self._design["scour_depth_equilibrium"]
        except KeyError:
            self.equilibrium = 1.3

        try:
            self.rock_density = self._design["rock_density"]
        except KeyError:
            self.rock_density = 2600

    def compute_scour_protection_tonnes_to_install(self):
        """
        Computes the amount of scour that needs to be installed at a
        substructure. For more information please refer to [1]_.

        Terms:
         * :math:`S =` scour protection height
         * :math:`D =` monopile diameter
         * :math:`r =` radius of scour protection from the center of the monopile
         * :math:`\\phi =` scour angle

        Assumptions:
         * :math:`\\frac{S}{D} = 1.3`
         * :math:`r = \\frac{D}{2} + \\frac{S}{\\tan(\\phi)}`
         * :math:`\\phi = 33.5` (scour angle for medium density sand)

        References
        ----------
        .. [1] Det Norske Veritas AS. (2014, May). Design of Offshore Wind Turbine
        Structures. Retrieved from
        https://rules.dnvgl.com/docs/pdf/DNV/codes/docs/2014-05/Os-J101.pdf
        """

        self.scour_depth = self.equilibrium * self.diameter

        r = self.diameter / 2 + self.scour_depth / np.tan(np.radians(self.phi))

        volume = np.pi * (r ** 2) * self.scour_depth

        self.scour_protection_tonnes = self.rock_density * volume / 1000.0

    def run(self):
        """
        Runs the required methods to be able to produce a `design_result`.
        """

        self.compute_scour_protection_tonnes_to_install()

    @property
    def total_phase_cost(self):
        """
        Returns the total cost of the phase in $USD
        """

        cost = (
            self._design["cost_per_tonne"]
            * self.scour_protection_tonnes
            * self.num_turbines
        )
        return cost

    @property
    def total_phase_time(self):
        """
        Returns the total time requried for the phase, in hours.
        """

        return self._design.get("design_time", 0.0)

    @property
    def detailed_output(self):
        """
        TODO: implement when detailed outputs required are defined
        """

        raise NotImplementedError()

    @property
    def design_result(self):
        """
        A dictionary of design results to passed to the scour protection
        installation simulation.

        Returns
        -------
        output : dict
             - ``scour_protection`` :`dict`
                - ``tonnes_per_substructure`` : `float`
        """

        output = {
            "scour_protection": {
                "tonnes_per_substructure": self.scour_protection_tonnes
            }
        }
        return output
