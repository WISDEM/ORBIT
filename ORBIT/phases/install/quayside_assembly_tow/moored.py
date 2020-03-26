"""Installation strategies for moored floating systems."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from marmot import Agent, process

from ORBIT.core import Cargo, WetStorage
from ORBIT.phases.install import InstallPhase


class MooredSubInstallation(InstallPhase):
    """
    TODO
    """

    phase = "Moored Substructure Installation"

    #:
    expected_config = {
        "tow_vessel_group": "dict | str",
        "substructure": {"takt_time": "int | float"},
        "site": {"depth": "m", "distance": "km"},
        "plant": {"num_turbines": "int"},
        "port": {
            "sub_assembly_lines": "int",
            "sub_storage_berths": "int",
            "turbine_assembly_cranes": "int",
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
        TODO
        """

        self.initialize_substructure_production()

    def initialize_substructure_production(self):
        """

        """

        self.wet_storage = WetStorage(self.env)

        time = self.config["substructure"]["takt_time"]
        lines = self.config["port"]["sub_assembly_lines"]
        num = self.config["plant"]["num_turbines"]

        to_assemble = [1] * num

        for i in range(lines):
            a = SubstructureAssemblyLine(
                to_assemble, time, self.wet_storage, i + 1
            )

            self.env.register(a)
            a.run()

    def initialize_substructure_storage(self):
        """

        """

    def initialize_turbine_assembly(self):
        """

        """
        pass

    def initialize_assembly_storage(self):
        """

        """
        pass

    def initialize_towing_groups(self):
        """

        """
        pass

    @property
    def detailed_output(self):
        """"""

        # TODO:
        return {}


class FloatingSubstructure:
    """"""

    def __init__(self):
        """
        TODO
        """
        pass


class SubstructureAssemblyLine(Agent):
    """"""

    def __init__(self, assigned, time, target, num):
        """
        Creates an instance of SubstructureAssemblyLine.

        Parameters
        ----------
        time : int | float
            Hours required to produce one substructure.
        target : simpy.Store
            Target storage.
        num : int
            Assembly line number designation.
        """

        super().__init__(f"Substructure Assembly Line {num}")

        self.assigned = assigned
        self.time = time
        self.target = target

    @process
    def assemble_substructure(self):
        """
        Simulation process for assembling a substructure.
        """

        yield self.task("Substructure Assembly", self.time)
        substructure = FloatingSubstructure()

        start = self.env.now
        yield self.target.put(substructure)
        delay = self.env.now - start

        if delay > 0:
            self.submit_action_log("Delay: No Wet Storage Available")

    @process
    def run(self):
        """"""

        while True:
            try:
                _ = self.assigned.pop(0)
                yield self.assemble_substructure()

            except IndexError:
                break
