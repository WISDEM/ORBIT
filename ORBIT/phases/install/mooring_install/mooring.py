"""Installation strategies for mooring systems."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


import simpy
from marmot import le, process

from ORBIT.core import Cargo, Vessel
from ORBIT.core._defaults import process_times as pt
from ORBIT.phases.install import InstallPhase


class MooringSystemInstallation(InstallPhase):
    """Module to model the installation of mooring systems at sea."""

    phase = "Mooring System Installation"

    #:
    expected_config = {
        "mooring_install_vessel": "dict | str",
        "site": {"depth": "m", "distance": "km"},
        "plant": {"num_turbines": "int"},
        "mooring_system": {
            "num_lines": "int",
            "line_diam": "m, float",
            "line_mass": "t",
            "line_length": "m",
            "anchor_mass": "t",
            "anchor_type": "str",
        },
    }

    def __init__(self, config, weather=None, **kwargs):
        """
        Creates an instance of `MooringSystemInstallation`.

        Parameters
        ----------
        config : dict
            Simulation specific configuration.
        weather : np.array
            Weather data at site.
        """

        super().__init__(weather, **kwargs)

        config = self.initialize_library(config, **kwargs)
        self.config = self.validate_config(config)
        self.extract_defaults()

        self.setup_simulation(**kwargs)

    def setup_simulation(self, **kwargs):
        """"""

        self.initialize_port()
        self.initialize_installation_vessel()
        self.initialize_components()

    def initialize_installation_vessel(self):
        """Initializes the mooring system installation vessel."""

        vessel_specs = self.config.get("mooring_install_vessel", None)
        name = vessel_specs.get("name", "Mooring System Installation Vessel")

        vessel = Vessel(name, vessel_specs)
        self.env.register(vessel)

        vessel.initialize()
        vessel.at_port = True
        vessel.at_site = False
        self.vessel = vessel

    def initialize_components(self):
        """Initializes the Cargo components at port."""
        pass


@process
def install_mooring_system(vessel, port, distance, **kwargs):
    """
    Logic for the Mooring System Installation Vessel.

    Parameters
    ----------
    """

    pass


class MooringLine(Cargo):
    pass


class MooringAnchor(Cargo):
    pass


f
