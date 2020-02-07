"""`ExportCableInstallation` and related processes."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from math import ceil

from marmot import process

from ORBIT.core import Vessel
from ORBIT.core.logic import position_onsite
from ORBIT.core._defaults import process_times as pt
from ORBIT.phases.install import InstallPhase
from ORBIT.core.exceptions import InsufficientCable

from .common import SimpleCable as Cable
from .common import (
    lay_cable,
    bury_cable,
    pull_in_cable,
    landfall_tasks,
    lay_bury_cable,
    splice_process,
    terminate_cable,
    load_cable_on_vessel,
)


class ExportCableInstallation(InstallPhase):

    phase = "Export Cable Installation"

    #:
    expected_config = {
        "landfall": {
            "trench_length": "int | float (optional)",
            "distance_to_interconnection": "int | float (optional)",
        },
        "export_cable_install_vessel": "str | dict",
        "export_cable_bury_vessel": "str | dict (optional)",
        "site": {"distance": "int | float"},
        "export_system": {
            "cable": {
                "linear_density": "int | float",
                "length": "int | float",
                "number": "int (optional)",
            }
        },
    }

    def __init__(self, config, weather=None, **kwargs):
        """
        Creates an instance of ExportCableInstallation.

        Parameters
        ----------
        config : dict
            Simulation specific configuration.
        weather : np.ndarray
            Weather profile at site.
        """

        super().__init__(weather, **kwargs)

        config = self.initialize_library(config, **kwargs)
        self.config = self.validate_config(config)
        self.extract_defaults()

        self.extract_distances()
        self.setup_simulation(**kwargs)

    def setup_simulation(self, **kwargs):
        """
        Setup method for the ExportCableInstallation phase.
        - Extracts key inputs
        - Performs onshore infrastructure construction
        - Routes to specific setup scripts based on configured strategy.
        """

        system = self.config["export_system"]
        self.cable = Cable(system["cable"]["linear_density"])
        self.length = system["cable"]["length"]
        self.number = system["cable"].get("number", 1)

        self.initialize_installation_vessel()
        self.initialize_burial_vessel()

        # Perform onshore construction
        self.onshore_construction(**kwargs)

        # Perform cable installation
        install_export_cables(
            self.install_vessel,
            length=self.length,
            cable=self.cable,
            number=self.number,
            distances=self.distances,
            burial_vessel=self.bury_vessel,
            **kwargs,
        )

    def extract_distances(self):
        """Extracts distances from input configuration or default values."""

        site = self.config["site"]["distance"]
        try:
            trench = self.config["landfall"]["trench_length"]

        except KeyError:
            trench = 1

        try:
            interconnection = self.config["landfall"][
                "distance_to_interconnection"
            ]

        except KeyError:
            interconnection = 2

        self.distances = {
            "site": site,
            "trench": trench,
            "interconnection": interconnection,
        }

    def onshore_construction(self, **kwargs):
        """
        Performs onshore construction prior to the installation of the export
        cable system.

        Parameters
        ----------
        construction_time : int | float
            Amount of time onshore construction takes.
            Default: 48h
        construction_rate : int | float
            Day rate of onshore construction.
            Default: 50000 USD/day
        """

        construction_time = kwargs.get(
            "onshore_construction_time", pt["onshore_construction_time"]
        )
        construction_rate = self.defaults["onshore_construction_rate"]

        _ = self.env.timeout(construction_time)
        self.env.run()
        self.env._submit_log(
            {
                "action": "Onshore Construction",
                "agent": "Onshore Construction",
                "duration": construction_time,
                "cost": construction_time * construction_rate,
                "location": "Landfall",
            },
            level="ACTION",
        )

    def initialize_installation_vessel(self):
        """Creates the export cable installation vessel."""

        # Vessel name and costs
        vessel_specs = self.config.get("export_cable_install_vessel", None)
        name = vessel_specs.get("name", "Export Cable Installation Vessel")

        vessel = Vessel(name, vessel_specs)
        self.env.register(vessel)

        vessel.extract_vessel_specs()
        self.install_vessel = vessel

    def initialize_burial_vessel(self):
        """Creates the export cable burial vessel."""

        # Vessel name and costs
        vessel_specs = self.config.get("export_cable_bury_vessel", None)
        if vessel_specs is None:
            self.bury_vessel = None
            return

        name = vessel_specs.get("name", "Export Cable Burial Vessel")

        vessel = Vessel(name, vessel_specs)
        self.env.register(vessel)

        vessel.extract_vessel_specs()
        self.bury_vessel = vessel

    @property
    def detailed_output(self):
        """Returns detailed outputs."""

        # TODO: 
        # outputs = {
        #     **self.agent_efficiencies,
        #     **self.get_max_cargo_weight_utilzations([self.cable_lay_vessel]),
        # }

        # return outputs
        return {}


@process
def install_export_cables(
    vessel, length, cable, number, distances, burial_vessel=None, **kwargs
):
    """
    Simulation of the installation of export cables.

    Parameters
    ----------
    vessel : Vessel
        Cable installation vessel.
    length : float
        Full length of an export cable.
    cable : SimpleCable | Cable
        Cable type to use.
    number : int
        Number of export cables.
    distances : dict
        Distances required for export cable installation simulation:
        site : int | float
            Distance between from the offshore substation and port. For
            simplicity, the cable landfall point is assumed to be at port.
        trench : int | float
            Trench length at landfall. Determines time required to tow the plow
            and pull-in cable (km).
        interconnection : int | float
            Distance between landfall and the onshore substation (km).
    burial_vessel : Vessel
        Optional configuration for burial vessel. If configured, the
        installation vessel only lays the cable on the seafloor and this
        vessel will bury them at the end of the simulation.
    """

    for _ in range(number):
        vessel.cable_storage.reset()
        splice_required = False
        remaining = length

        yield load_cable_on_vessel(vessel, cable, **kwargs)

        # At Landfall
        yield landfall_tasks(vessel, distances["trench"], **kwargs)

        while remaining > 0:
            if splice_required:
                yield splice_process(vessel, **kwargs)

            try:
                section = vessel.cable_storage.get_cable(remaining)

            except InsufficientCable as e:
                section = vessel.cable_storage.get_cable(e.current)

            if burial_vessel is None:
                yield lay_bury_cable(vessel, section, **kwargs)

            else:
                yield lay_cable(vessel, section, **kwargs)

            remaining -= ceil(section)
            if remaining > 0:
                splice_required = True
                distance = (remaining / length) * distances["site"]

                yield vessel.transit(distance)
                vessel.cable_storage.reset()
                yield load_cable_on_vessel(vessel, cable, **kwargs)
                yield vessel.transit(distance)

        # At Site
        yield position_onsite(vessel, **kwargs)
        yield pull_in_cable(vessel, **kwargs)
        yield terminate_cable(vessel, **kwargs)

        # Transit back to port
        yield vessel.transit(distances["site"])

    if burial_vessel is None:
        vessel.submit_debug_log(
            message="Export cable lay/burial process completed!"
        )

    else:
        vessel.submit_debug_log(message="Export cable lay process completed!")
        bury_export_cables(burial_vessel, length, number, **kwargs)


@process
def bury_export_cables(vessel, length, number, **kwargs):
    """
    Simulation for the burial of export cables if configured.

    Parameters
    ----------
    vessel : Vessel
        Performing vessel.
    length : float
        Full length of an export cable.
    number : int
        Number of export cables.
    """

    for _ in range(number):
        yield bury_cable(vessel, length, **kwargs)

    vessel.submit_debug_log(message="Export cable burial process completed!")
