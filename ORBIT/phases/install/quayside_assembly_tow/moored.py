"""Installation strategies for moored floating systems."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


import simpy
from marmot import le, process
from ORBIT.core import Vessel, WetStorage
from ORBIT.phases.install import InstallPhase

from .common import TowingGroup, TurbineAssemblyLine, SubstructureAssemblyLine


class MooredSubInstallation(InstallPhase):
    """
    Installation module to model the quayside assembly, tow-out and
    installation at sea of moored substructures.
    """

    phase = "Moored Substructure Installation"
    capex_category = "Substructure"

    #:
    expected_config = {
        "ahts_vessel": "str",
        "towing_vessel": "str",
        "towing_vessel_groups": {
            "towing_vessels": "int",
            "ahts_vessels": "int (optional, default: 1)",
            "num_groups": "int (optional)",
        },
        "substructure": {
            "takt_time": "int | float (optional, default: 0)",
            "towing_speed": "int | float (optional, default: 6 km/h)",
            "unit_cost": "USD",
        },
        "site": {"depth": "m", "distance": "km"},
        "plant": {"num_turbines": "int"},
        "turbine": "dict",
        "port": {
            "sub_assembly_lines": "int (optional, default: 1)",
            "sub_storage": "int (optional, default: inf)",
            "turbine_assembly_cranes": "int (optional, default: 1)",
            "assembly_storage": "int (optional, default: inf)",
            "monthly_rate": "USD/mo (optional)",
            "name": "str (optional)",
        },
    }

    def __init__(self, config, weather=None, **kwargs):
        """
        Creates an instance of MooredSubInstallation.

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

        self.setup_simulation(**kwargs)

    def setup_simulation(self, **kwargs):
        """
        Sets up simulation infrastructure.
        - Initializes substructure production
        - Initializes turbine assembly processes
        - Initializes towing groups
        """

        self.distance = self.config["site"]["distance"]
        self.num_turbines = self.config["plant"]["num_turbines"]

        self.initialize_port()
        self.initialize_substructure_production()
        self.initialize_turbine_assembly()
        self.initialize_queue()
        self.initialize_towing_groups()

    @property
    def system_capex(self):
        """Returns total procurement cost of the substructures."""

        return self.num_turbines * self.config["substructure"]["unit_cost"]

    def initialize_substructure_production(self):
        """
        Initializes the production of substructures at port. The number of
        independent assembly lines and production time associated with a
        substructure can be configured with the following parameters:

        - self.config["substructure"]["takt_time"]
        - self.config["port"]["sub_assembly_lines"]
        """

        try:
            storage = self.config["port"]["sub_storage"]

        except KeyError:
            storage = float("inf")

        self.wet_storage = WetStorage(self.env, storage)

        try:
            time = self.config["substructure"]["takt_time"]

        except KeyError:
            time = 0

        try:
            lines = self.config["port"]["sub_assembly_lines"]

        except KeyError:
            lines = 1

        to_assemble = [1] * self.num_turbines

        self.sub_assembly_lines = []
        for i in range(lines):
            a = SubstructureAssemblyLine(
                to_assemble, time, self.wet_storage, i + 1
            )

            self.env.register(a)
            a.start()
            self.sub_assembly_lines.append(a)

    def initialize_turbine_assembly(self):
        """
        Initializes turbine assembly lines. The number of independent lines
        can be configured with the following parameters:

        - self.config["port"]["turb_assembly_lines"]
        """

        try:
            storage = self.config["port"]["assembly_storage"]

        except KeyError:
            storage = float("inf")

        self.assembly_storage = WetStorage(self.env, storage)

        try:
            lines = self.config["port"]["turbine_assembly_cranes"]

        except KeyError:
            lines = 1

        turbine = self.config["turbine"]
        self.turbine_assembly_lines = []
        for i in range(lines):
            a = TurbineAssemblyLine(
                self.wet_storage, self.assembly_storage, turbine, i + 1
            )

            self.env.register(a)
            a.start()
            self.turbine_assembly_lines.append(a)

    def initialize_towing_groups(self, **kwargs):
        """
        Initializes towing groups to bring completed assemblies to site and
        stabilize the assembly during final installation.
        """

        self.installation_groups = []

        towing_vessel = self.config["towing_vessel"]
        num_groups = self.config["towing_vessel_groups"].get("num_groups", 1)
        num_towing = self.config["towing_vessel_groups"]["towing_vessels"]
        towing_speed = self.config["substructure"].get("towing_speed", 6)

        ahts_vessel = self.config["ahts_vessel"]
        num_ahts = self.config["towing_vessel_groups"]["ahts_vessels"]

        remaining_substructures = [1] * self.num_turbines

        for i in range(num_groups):
            g = TowingGroup(towing_vessel, ahts_vessel, i + 1)
            self.env.register(g)
            g.initialize()
            self.installation_groups.append(g)

            transfer_install_moored_substructures_from_storage(
                g,
                self.assembly_storage,
                self.distance,
                num_towing,
                num_ahts,
                towing_speed,
                remaining_substructures,
                **kwargs,
            )

    def initialize_queue(self):
        """
        Initializes the queue, modeled as a ``SimPy.Resource`` that towing
        groups join at site.
        """

        self.active_group = simpy.Resource(self.env, capacity=1)
        self.active_group.vessel = None
        self.active_group.activate = self.env.event()

    @property
    def detailed_output(self):
        """"""

        return {
            "operational_delays": {
                **{
                    k: self.operational_delay(str(k))
                    for k in self.sub_assembly_lines
                },
                **{
                    k: self.operational_delay(str(k))
                    for k in self.turbine_assembly_lines
                },
                **{
                    k: self.operational_delay(str(k))
                    for k in self.installation_groups
                },
            }
        }

    def operational_delay(self, name):
        """"""

        actions = [a for a in self.env.actions if a["agent"] == name]
        delay = sum(a["duration"] for a in actions if "Delay" in a["action"])

        return delay


@process
def transfer_install_moored_substructures_from_storage(
    group,
    feed,
    distance,
    towing_vessels,
    ahts_vessels,
    towing_speed,
    remaining_substructures,
    **kwargs,
):
    """
    Trigger the substructure installtions. Shuts down after
    self.remaining_substructures is empty.
    """

    while True:
        try:
            _ = remaining_substructures.pop(0)
            yield towing_group_actions(
                group,
                feed,
                distance,
                towing_vessels,
                ahts_vessels,
                towing_speed,
                **kwargs,
            )

        except IndexError:
            break


@process
def towing_group_actions(
    group,
    feed,
    distance,
    towing_vessels,
    ahts_vessels,
    towing_speed,
    **kwargs,
):
    """
    Process logic for the towing vessel group. Assumes there is an anchor tug boat with each group

    Parameters
    ----------
    group : Vessel
        Towing group.
    feed : simpy.Store
        Completed assembly storage.
    distance : int | float
        Distance from port to site.
    towing_vessels : int
        Number of vessels to use for towing to site.
    ahts_vessels : int
        Number of anchor handling tug vessels.
    towing_speed : int | float
        Configured towing speed (km/h).
    """

    towing_time = distance / towing_speed
    transit_time = distance / group.transit_speed

    start = group.env.now
    assembly = yield feed.get()
    delay = group.env.now - start

    if delay > 0:
        group.submit_action_log(
            "Delay: No Completed Turbine Assemblies",
            delay,
            num_vessels=towing_vessels,
            num_ahts_vessels=ahts_vessels,
        )

    yield group.group_task(
        "Ballast to Towing Draft",
        6,
        num_vessels=towing_vessels,
        num_ahts_vessels=ahts_vessels,
        constraints={
            "windspeed": le(group.max_windspeed),
            "waveheight": le(group.max_waveheight),
        },
    )

    yield group.group_task(
        "Tow Substructure",
        towing_time,
        num_vessels=towing_vessels,
        num_ahts_vessels=ahts_vessels,
        constraints={
            "windspeed": le(group.max_windspeed),
            "waveheight": le(group.max_waveheight),
        },
    )

    # At Site
    yield group.group_task(
        "Position Substructure",
        2,
        num_vessels=towing_vessels,
        num_ahts_vessels=ahts_vessels,
        constraints={"windspeed": le(15), "waveheight": le(2.5)},
    )

    yield group.group_task(
        "Ballast to Operational Draft",
        6,
        num_vessels=towing_vessels,
        num_ahts_vessels=ahts_vessels,
        constraints={"windspeed": le(15), "waveheight": le(2.5)},
    )

    yield group.group_task(
        "Connect Mooring Lines, Pre-tension and pre-stretch",
        20,
        num_vessels=towing_vessels,
        num_ahts_vessels=ahts_vessels,
        suspendable=True,
        constraints={"windspeed": le(15), "waveheight": le(2.5)},
    )

    yield group.group_task(
        "Check Mooring Lines",
        6,
        num_vessels=towing_vessels,
        num_ahts_vessels=ahts_vessels,
        suspendable=True,
        constraints={"windspeed": le(15), "waveheight": le(2.5)},
    )

    yield group.group_task(
        "Transit",
        transit_time,
        num_vessels=towing_vessels,
        num_ahts_vessels=ahts_vessels,
        suspendable=True,
        constraints={
            "windspeed": le(group.max_windspeed),
            "waveheight": le(group.max_waveheight),
        },
    )
