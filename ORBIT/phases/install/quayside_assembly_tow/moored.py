"""Installation strategies for moored floating systems."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from marmot import process

from ORBIT.core import WetStorage
from ORBIT.phases.install import InstallPhase

from .common import TowingGroup, TurbineAssemblyLine, SubstructureAssemblyLine


class MooredSubInstallation(InstallPhase):
    """
    Installation module to model the quayside assembly, tow-out and
    installation at sea of moored substructures.
    """

    phase = "Moored Substructure Installation"

    #:
    expected_config = {
        "towing_vessel": "str",
        "towing_vessel_groups": {
            "vessels_for_towing": "int",
            "vessels_for_stabilization": "int",
            "num_groups": "int",
        },
        "substructure": {"takt_time": "int | float"},
        "site": {"depth": "m", "distance": "km"},
        "plant": {"num_turbines": "int"},
        "turbine": "dict",
        "port": {
            "sub_assembly_lines": "int",
            "sub_storage": "int (optional, default: 2)",
            "turbine_assembly_cranes": "int",
            "assembly_storage": "int (optional, default: 2)",
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

        storage = self.config["port"].get("sub_storage", 2)
        self.wet_storage = WetStorage(self.env, storage)

        time = self.config["substructure"]["takt_time"]
        lines = self.config["port"]["sub_assembly_lines"]
        num = self.config["plant"]["num_turbines"]

        to_assemble = [1] * num

        for i in range(lines):
            a = SubstructureAssemblyLine(
                to_assemble, time, self.wet_storage, i + 1
            )

            self.env.register(a)
            a.start()

    def initialize_turbine_assembly(self):
        """
        Initializes turbine assembly lines. The number of independent lines
        can be configured with the following parameters:

        - self.config["port"]["turb_assembly_lines"]
        """

        storage = self.config["port"].get("assembly_storage", 2)
        self.assembly_storage = WetStorage(self.env, storage)

        lines = self.config["port"]["turbine_assembly_cranes"]
        turbine = self.config["turbine"]
        for i in range(lines):
            a = TurbineAssemblyLine(
                self.wet_storage, self.assembly_storage, turbine, i + 1
            )

            self.env.register(a)
            a.start()

    def initialize_towing_groups(self, **kwargs):
        """
        Initializes towing groups to bring completed assemblies to site and
        stabilize the assembly during final installation.
        """

        distance = self.config["site"]["distance"]
        self.installation_groups = []

        vessel = self.config["towing_vessel"]
        num_groups = self.config["towing_vessel_groups"]["num_groups"]
        towing = self.config["towing_vessel_groups"]["vessels_for_towing"]
        stabilization = self.config["towing_vessel_groups"][
            "vessels_for_stabilization"
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

        # TODO:
        return {}


@process
def install_moored_substructures_from_storage(
    group,
    feed,
    distance,
    vessels_for_towing,
    vessels_for_stabilization,
    **kwargs,
):
    """
    Process logic for the towing vessel group.

    Parameters
    ----------
    group : Vessel
        Towing group.
    feed : simpy.Store
        Completed assembly storage.
    distance : int | float
        Distance from port to site.
    vessels_for_towing : int
        Number of vessels to use for towing to site.
    vessels_for_stabilization : int
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

        yield group.group_task("Transit", 10, num_vessels=vessels_for_towing)
        yield group.group_task(
            "Installation", 10, num_vessels=vessels_for_stabilization
        )
        yield group.group_task("Transit", 10, num_vessels=vessels_for_towing)
