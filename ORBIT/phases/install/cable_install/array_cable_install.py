"""Provides the `ArrayCableInstallation` class."""

__author__ = "Rob Hammond"
__copyright__ = "Copyright 2019, National Renewable Energy Laboratory"
__maintainer__ = "Rob Hammond"
__email__ = "robert.hammond@nrel.gov"


from ORBIT import defaults
from ORBIT.vessels import Vessel
from ORBIT.simulation import Environment, VesselStorageContainer
from ORBIT.phases.install import InstallPhase
from ORBIT.vessels.components import CarouselSystem

from .process import (
    transport,
    get_carousel_from_port,
    lay_bury_full_array_cable_section,
)


class ArrayCableInstallation(InstallPhase):
    """
    Single vessel array cable installation simulation.

    Attributes
    ----------
    x

    Methods
    -------
    x
    """

    expected_config = {
        "port": {
            "num_cranes": "int",
            "monthly_rate": "int | float (optional)",
        },
        "array_cable_lay_vessel": "str",
        "site": {"distance": "int | float"},
        "plant": {"num_turbines": "int"},
        "array_system": {
            "cables": {
                "name (variable)": {
                    "linear_density": "int | float",
                    "cable_sections": [("float", "int")],
                }
            }
        },
    }

    def __init__(self, config, weather=None, **kwargs):
        """
        Creates an instance of SingleVesselArrayCableInstallation

        Parameters
        ----------
        config : dict
            A configuration dictionary matching the `expected_config` template.
        weather : str, default: None
            <pathname>/<filename> to weather profile used to determine weather
            delays.
        """

        self.config = self.initialize_library(config, **kwargs)
        self.extract_phase_kwargs(**kwargs)
        self.env = Environment(weather)
        self.init_logger(**kwargs)
        self.setup_simulation(**kwargs)

    def setup_simulation(self, **kwargs):
        """
        Sets up the required simulation infrastructures.
            - creates a port
            - initializes a cable installation vessel
            - initializes the cable carousel(s)
            - initializes vessel storage
        """

        self.initialize_port()
        self.initialize_cable_installation_vessel()
        self.initialize_carousels()

        self.env.process(
            install_array_cables(
                env=self.env,
                vessel=self.cable_lay_vessel,
                port=self.port,
                num_cables=self.num_sections,
                distance_to_site=self.config["site"]["distance"],
                **kwargs,
            )
        )

    def initialize_cable_installation_vessel(self):
        """
        Creates a cable installation vessel.
        """

        # Get vessel specs
        try:
            cable_lay_specs = self.config["array_cable_lay_vessel"]
        except KeyError:
            raise Exception('"array_cable_lay_vessel" is undefined.')

        # Vessel name and costs
        name = "Array Cable Installation Vessel"
        cost = cable_lay_specs["vessel_specs"].get(
            "day_rate", defaults["array_cable_install_day_rate"]
        )
        self.agent_costs[name] = cost

        # Vessel storage
        try:
            storage_specs = cable_lay_specs["storage_specs"]
        except KeyError:
            raise Exception(
                "Storage specifications must be set for the array cable "
                "laying vessel."
            )

        self.cable_lay_vessel = Vessel(name, cable_lay_specs)
        self.cable_lay_vessel.storage = VesselStorageContainer(
            self.env, **storage_specs
        )

        # Vessel starting location
        self.cable_lay_vessel.at_port = True
        self.cable_lay_vessel.at_site = False

    def initialize_carousels(self):
        """
        Creates the cable carousel(s) required for installation.
        """

        self.carousels = CarouselSystem(
            self.config["array_system"]["cables"],
            self.cable_lay_vessel.max_cargo,
        )
        self.carousels.create_carousels()

        self.num_sections = 0
        for carousel in list(self.carousels.carousels.values())[::-1]:
            self.num_sections += len(carousel.section_lengths)
            c = carousel.__dict__
            c["type"] = "Carousel"
            self.port.put(c)

    @property
    def detailed_output(self):
        """Returns detailed outputs."""

        outputs = {
            **self.agent_efficiencies,
            **self.get_max_cargo_weight_utilzations([self.cable_lay_vessel]),
        }

        return outputs


def install_array_cables(
    env, vessel, port, num_cables, distance_to_site, **kwargs
):
    """
    Simulation of the installation of array cables.
    NOTE: This does not support cable splicing scenarios.

    Parameters
    ----------
    env : Simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable laying vessel.
    port : Simpy.FilterStore
        Simulation port object.
    num_cables : int
        Number of cable sections to be installed.
    distance_to_site : int or float
        Distance between port and offshore wind site.

    Raises
    ------
    Exception
        Vessel is lost at sea if not at sea or at port.
    """

    while num_cables:
        if vessel.at_port:
            yield env.process(
                get_carousel_from_port(env, vessel, port, **kwargs)
            )
            vessel.update_trip_data(deck=False, items=False)
            yield env.process(
                transport(env, vessel, distance_to_site, False, True, **kwargs)
            )
        elif vessel.at_site:
            while vessel.carousel.section_lengths:

                # Retrieve the cable section length and mass and install
                _len = vessel.carousel.section_lengths.pop(0)
                _mass = vessel.carousel.section_masses.pop(0)

                yield env.process(
                    lay_bury_full_array_cable_section(
                        env, vessel, _len, _mass, **kwargs
                    )
                )

                num_cables -= 1

            # Go back to port once the carousel is depleted.
            yield env.process(
                transport(env, vessel, distance_to_site, True, False, **kwargs)
            )

        else:
            raise Exception("Vessel is lost at sea.")

    env.logger.debug(
        "Single vesssel array cable installation complete!",
        extra={
            "agent": vessel.name,
            "time": env.now,
            "type": "Status",
            "action": "Complete",
        },
    )
