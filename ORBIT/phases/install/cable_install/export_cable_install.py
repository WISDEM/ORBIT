"""Provides the `ExportCableInstallation` class."""

__author__ = "Rob Hammond"
__copyright__ = "Copyright 2019, National Renewable Energy Laboratory"
__maintainer__ = "Rob Hammond"
__email__ = "robert.hammond@nrel.gov"


from types import SimpleNamespace

from ORBIT import defaults
from ORBIT.vessels import Vessel
from ORBIT.simulation import Environment, VesselStorageContainer
from ORBIT.phases.install import InstallPhase
from ORBIT.vessels.components import CarouselSystem

from .process import (
    transport,
    dig_trench,
    onshore_work,
    position_onsite,
    splice_cable_process,
    get_carousel_from_port,
    lay_bury_cable_section,
    connect_cable_section_to_target,
)


class ExportCableInstallation(InstallPhase):
    """
    Export cable installation simulation object

    Attributes
    ----------
    x
    """

    expected_config = {
        "port": {
            "num_cranes": "int",
            "monthly_rate": "int | float (optional)",
        },
        "export_cable_lay_vessel": "str",
        "trench_dig_vessel": "str | dict",
        "site": {
            "distance": "int",
            "distance_to_landfall": "float",
            "distance_to_beach": "float",
            "distance_to_interconnection": "float",
        },
        "export_system": {
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
        Creates an instance of SingleVesselExportCableInstallation.

        Parameters
        ----------
        config : dict
            A configuration dictionary matching the `expected_config` template.
        weather : str, default: `None`.
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
        self.intialize_trench_dig_vessel()
        self.initialize_carousels()

        self.distances = SimpleNamespace(
            **{
                el.replace("distance_to_", "")
                if el != "distance"
                else "site": self.config["site"].get(el, None)
                for el in (
                    "distance",
                    "distance_to_beach",
                    "distance_to_landfall",
                    "distance_to_interconnection",
                )
            }
        )

        self.env.process(
            install_export_cables(
                env=self.env,
                cable_vessel=self.cable_lay_vessel,
                trench_vessel=self.trench_dig_vessel,
                port=self.port,
                cable_length=self.cable_length,
                num_sections=self.num_sections,
                distances=self.distances,
                **kwargs,
            )
        )

    def intialize_trench_dig_vessel(self):
        """
        Creates a trench digging "vessel".
        .. note:: It is important to note that this is not a vessel, but a
        multifaceted onshore operation but for the sake of naming consistency
        we will call this a vessel.
        """

        # Get the vessel specs
        try:
            trench_dig_specs = self.config["trench_dig_vessel"]
        except KeyError:
            raise Exception('"trench_dig_vessel" is undefined.')

        # Vessel name and costs
        name = "Trench Dig Vessel"
        cost = trench_dig_specs["vessel_specs"].get(
            "day_rate", defaults["trench_day_rate"]
        )
        self.agent_costs[name] = cost
        self.trench_dig_vessel = Vessel(name, trench_dig_specs)

    def initialize_cable_installation_vessel(self):
        """
        Creates a cable installation vessel.
        """

        # Get vessel specs
        try:
            cable_lay_specs = self.config["export_cable_lay_vessel"]
        except KeyError:
            raise Exception('"export_cable_lay_vessel" is undefined.')

        # Vessel name and costs
        name = "Export Cable Installation Vessel"
        cost = cable_lay_specs["vessel_specs"].get(
            "day_rate", defaults["export_cable_install_day_rate"]
        )
        self.agent_costs[name] = cost

        # Vessel storage
        try:
            storage_specs = cable_lay_specs["storage_specs"]
        except KeyError:
            raise Exception(
                "Storage specifications must be set for the export cable "
                "laying vessel."
            )

        self.cable_lay_vessel = Vessel(name, cable_lay_specs)
        self.cable_lay_vessel.storage = VesselStorageContainer(
            self.env, **storage_specs
        )

        # Vessel starting location
        self.cable_lay_vessel.at_port = True
        self.cable_lay_vessel.at_site = False

    def initialize_carousels(self, **kwargs):
        """
        Creates the cable carousel(s) required for installation.
        """

        self.carousels = CarouselSystem(
            self.config["export_system"]["cables"],
            self.cable_lay_vessel.max_cargo,
        )
        self.carousels.create_carousels()

        # Get the cable length. For export there is only one distance
        cable = self.config["export_system"]["cables"][
            [*self.config["export_system"]["cables"]][0]
        ]
        self.cable_length = cable["cable_sections"][0][0]

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


def install_trench(env, vessel, trench_length, **kwargs):
    """
    Simulation of the installation of array cables.
    NOTE: This does not support cable splicing scenarios.

    Parameters
    ----------
    env : Simpy.Environment
        Simulation environment
    trench_length : int or float
        Distance between onshore substation and landfall, km.
    """

    yield env.process(dig_trench(env, vessel, trench_length, **kwargs))


def install_export_cables(
    env,
    cable_vessel,
    trench_vessel,
    port,
    cable_length,
    num_sections,
    distances,
    **kwargs,
):
    """
    Simulation of the installation of export cables.

    Parameters
    ----------
    env : Simpy.Environment
        Simulation environment
    cable_vessel : Vessel
        Cable laying vessel.
    trench_vessel : Vessel
        Trench digging operation.
    port : Simpy.FilterStore
        Simulation port object
    cable_length : float
        Length of a full cable section.
    num_sections : int
        Number of individual cable sections (could be spliced) to install to
        connect the wind farm to its onshore interconnection point.
    distances : SimpleNamespace
        The collection of distances required for export cable installation:
        site : int or float
            Distance to site, km.
        landfall : int or float
            Distance between from the offshore substation and landfall, km.
        beach : int or float
            Distance between where a vessel anchors offshore and the landfall
            site, km.
        interconnection : int or float
            Distance between landfall and the onshore substation, km.

    Raises
    ------
    Exception
        Vessel is lost at sea if not at sea or at port.
    """

    yield env.process(
        install_trench(
            env=env,
            vessel=trench_vessel,
            trench_length=distances.interconnection,
            **kwargs,
        )
    )

    splice_required = False
    new_start = True

    while num_sections:  # floats aren't exact
        if cable_vessel.at_port:
            yield env.process(
                get_carousel_from_port(env, cable_vessel, port, **kwargs)
            )
            cable_vessel.update_trip_data(deck=False, items=False)
            yield env.process(
                transport(
                    env, cable_vessel, distances.site, False, True, **kwargs
                )
            )
        elif cable_vessel.at_site:
            while cable_vessel.carousel.section_lengths:

                # Retrieve the cable section length and mass and install
                _len = cable_vessel.carousel.section_lengths.pop(0)
                _mass = cable_vessel.carousel.section_masses.pop(0)
                num_sections -= 1

                if new_start:
                    _pct_to_install = (
                        distances.beach + distances.interconnection
                    ) / _len
                    remaining_connection_len = cable_length
                    # TODO: Need error handling here to allow for a splice in
                    # the middle of onshore OR user needs to ensure the vessel
                    # can actually fit the full length
                    yield env.process(
                        onshore_work(
                            env,
                            cable_vessel,
                            distances.beach,
                            distances.interconnection,
                            _mass * _pct_to_install,
                            **kwargs,
                        )
                    )
                    new_start = False

                    # Keep track of what's left overall
                    remaining_connection_len -= _len * _pct_to_install

                    # Keep track of what's left in the cable section
                    _len_remaining = _len * (1 - _pct_to_install)
                    _mass_remaining = _mass * (1 - _pct_to_install)

                    # If there is cable still left in the section, install it
                    if round(_len_remaining, 10) > 0:
                        yield env.process(
                            lay_bury_cable_section(
                                env,
                                cable_vessel,
                                _len_remaining,
                                _mass_remaining,
                                **kwargs,
                            )
                        )
                        remaining_connection_len -= _len_remaining

                        # If an individual connection is complete, then finish
                        # the individual installation; otherwise return to port
                        # for the remaing cable
                        if round(remaining_connection_len, 10) == 0:
                            yield env.process(
                                position_onsite(env, cable_vessel, **kwargs)
                            )
                            yield env.process(
                                connect_cable_section_to_target(
                                    env, cable_vessel, **kwargs
                                )
                            )
                            new_start = True
                        else:
                            splice_required = True
                            yield env.process(
                                transport(
                                    env,
                                    cable_vessel,
                                    distances.site,
                                    True,
                                    False,
                                    **kwargs,
                                )
                            )
                    else:
                        splice_required = True
                        yield env.process(
                            transport(
                                env,
                                cable_vessel,
                                distances.site,
                                True,
                                False,
                                **kwargs,
                            )
                        )

                elif splice_required:
                    yield env.process(
                        splice_cable_process(env, cable_vessel, **kwargs)
                    )
                    yield env.process(
                        lay_bury_cable_section(
                            env, cable_vessel, _len, _mass, **kwargs
                        )
                    )
                    remaining_connection_len -= _len

                    if round(remaining_connection_len, 10) == 0:
                        yield env.process(
                            position_onsite(env, cable_vessel, **kwargs)
                        )
                        yield env.process(
                            connect_cable_section_to_target(
                                env, cable_vessel, **kwargs
                            )
                        )
                        new_start = True
                        splice_required = False

                    else:
                        # The carousel has no more cable because there aren't
                        # incomplete sections unless the whole cable can't fit
                        # on the carousel.
                        splice_required = True  # enforcing that it stays True

                    # go back to port
                    yield env.process(
                        transport(
                            env,
                            cable_vessel,
                            distances.site,
                            True,
                            False,
                            **kwargs,
                        )
                    )

            # go back to port
            yield env.process(
                transport(
                    env, cable_vessel, distances.site, True, False, **kwargs
                )
            )

        else:
            raise Exception("Vessel is lost at sea.")

    env.logger.debug(
        "Single vessel export cable installation complete!",
        extra={
            "agent": cable_vessel.name,
            "time": env.now,
            "type": "Status",
            "action": "Complete",
        },
    )
