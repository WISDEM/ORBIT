"""Installation strategies for gravity-base substructures."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from marmot import process

from ORBIT.core import WetStorage
from ORBIT.phases.install import InstallPhase

from .common import TowingGroup, TurbineAssemblyLine, SubstructureAssemblyLine


class GravityBasedInstallation(InstallPhase):
    """
    Installation module to model the quayside assembly, tow-out and
    installation of gravity based foundations.
    """

    phase = "Gravity Based Foundation Installation"

    #:
    expected_config = {
        "towing_vessel": "str",
        "towing_vessel_groups": {
            "towing_vessels": "int",
            "stabilization_vessels": "int",
            "num_groups": "int (optional)",
        },
        "substructure": {"takt_time": "int | float (optional, default: 0)"},
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
        Creates an instance of GravityBasedInstallation.

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
        """
        Sets up simulation infrastructure.
        - Initializes substructure production
        - Initializes turbine assembly processes
        - Initializes towing groups
        """

        self.initialize_substructure_production()
        self.initialize_turbine_assembly()
        self.initialize_towing_groups()

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

        num = self.config["plant"]["num_turbines"]
        to_assemble = [1] * num

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

        distance = self.config["site"]["distance"]
        self.installation_groups = []

        vessel = self.config["towing_vessel"]
        num_groups = self.config["towing_vessel_groups"].get("num_groups", 1)
        towing = self.config["towing_vessel_groups"]["towing_vessels"]
        stabilization = self.config["towing_vessel_groups"][
            "stabilization_vessels"
        ]

        for i in range(num_groups):
            g = TowingGroup(vessel, num=i + 1)
            self.env.register(g)
            g.initialize()
            self.installation_groups.append(g)

            install_moored_substructures_from_storage(
                g,
                self.assembly_storage,
                distance,
                towing,
                stabilization,
                **kwargs,
            )

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
def install_gbf_substructures_from_storage(
    group, feed, distance, towing_vessels, stabilization_vessels, **kwargs
):
    """
    Process logic for the towing vessel group.

    Parameters
    ----------
    group : TowingGroup
    feed : simpy.Store
        Completed assembly storage.
    distance : int | float
        Distance from port to site.
    towing_vessels : int
        Number of vessels to use for towing to site.
    stabilization_vessels : int
        Number of vessels to use for substructure stabilization during final
        installation at site.
    """

    while True:

        start = group.env.now
        assembly = yield feed.get()
        delay = group.env.now - start

        if delay > 0:
            group.submit_action_log(
                "Delay: No Completed Assemblies Available", delay
            )

        yield group.group_task("Release from Quay-Side", 4, num_vessels=3)
        yield group.group_task("Transit", 10, num_vessels=towing_vessels)
        yield group.group_task(
            "Installation", 10, num_vessels=stabilization_vessels
        )
        yield group.group_task("Transit", 10, num_vessels=towing_vessels)
