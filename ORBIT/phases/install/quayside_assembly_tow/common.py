"""Common processes and cargo types for quayside assembly and tow-out
installations"""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from marmot import Agent, le, process


class Substructure:
    """Floating Substructure Class."""

    def __init__(self):
        """Creates an instance of `Substructure`."""

        pass


class SubstructureAssemblyLine(Agent):
    """Substructure Assembly Line Class."""

    def __init__(self, assigned, time, target, num):
        """
        Creates an instance of `SubstructureAssemblyLine`.

        Parameters
        ----------
        assigned : list
            List of assigned tasks. Can be shared with other assembly lines.
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
        substructure = Substructure()

        start = self.env.now
        yield self.target.put(substructure)
        delay = self.env.now - start

        if delay > 0:
            self.submit_action_log("Delay: No Wet Storage Available", delay)

    @process
    def start(self):
        """
        Trigger the assembly line to run. Will attempt to pull a task from
        self.assigned and timeout for the assembly time. Shuts down after
        self.assigned is empty.
        """

        while True:
            try:
                _ = self.assigned.pop(0)
                yield self.assemble_substructure()

            except IndexError:
                break


class TurbineAssemblyLine(Agent):
    """Turbine Assembly Line Class."""

    def __init__(self, feed, target, turbine, num):
        """
        Creates an instance of `TurbineAssemblyLine`.

        Parameters
        ----------
        feed : simpy.Store
            Storage for completed substructures.
        target : simpy.Store
            Target storage.
        num : int
            Assembly line number designation.
        """

        super().__init__(f"Turbine Assembly Line {num}")

        self.feed = feed
        self.target = target
        self.turbine = turbine

    @process
    def start(self):
        """
        Trigger the assembly line to run. Will attempt to pull a task from
        self.assigned and timeout for the assembly time. Shuts down after
        self.assigned is empty.
        """

        while True:
            start = self.env.now
            sub = yield self.feed.get()
            delay = self.env.now - start

            if delay > 0:
                self.submit_action_log(
                    "Delay: No Substructures in Wet Storage", delay
                )

            yield self.assemble_turbine()

    @process
    def assemble_turbine(self):
        """
        Turbine assembly process. Follows a similar process as the
        `TurbineInstallation` modules but has fixed lift times + fasten times
        instead of calculating the lift times dynamically.
        """

        yield self.prepare_for_assembly()

        sections = self.turbine["tower"].get("sections", 1)
        for _ in range(sections):
            yield self.lift_and_attach_tower_section()

        yield self.lift_and_attach_nacelle()

        for _ in range(3):
            yield self.lift_and_attach_blade()

        yield self.mechanical_completion()

        start = self.env.now
        yield self.target.put(1)
        delay = self.env.now - start

        if delay > 0:
            self.submit_action_log(
                "Delay: No Assembly Storage Available", delay
            )

        self.submit_debug_log("Assembly delievered to installation groups.")

    @process
    def prepare_for_assembly(self):
        """
        Task representing time associated with preparing a substructure for
        turbine assembly.
        """

        yield self.task("Prepare for Turbine Assembly", 12)

    @process
    def lift_and_attach_tower_section(self):
        """
        Task representing time associated with lifting and attaching a tower
        section at quayside.
        """

        yield self.task(
            "Lift and Attach Tower Section",
            7,
            constraints={"windspeed": le(15)},
        )

    @process
    def lift_and_attach_nacelle(self):
        """
        Task representing time associated with lifting and attaching a nacelle
        at quayside.
        """

        yield self.task(
            "Lift and Attach Nacelle", 7, constraints={"windspeed": le(15)}
        )

    @process
    def lift_and_attach_blade(self):
        """
        Task representing time associated with lifting and attaching a turbine
        blade at quayside.
        """

        yield self.task(
            "Lift and Attach Blade", 3.5, constraints={"windspeed": le(15)}
        )

    @process
    def mechanical_completion(self):
        """
        Task representing time associated with performing mechanical compltion
        work at quayside.
        """

        yield self.task("Mechanical Completion", 24)
