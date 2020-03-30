"""Common processes and cargo types for quayside assembly and tow-out
installations"""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from marmot import Agent, process


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
            self.submit_action_log("Delay: No Wet Storage Available")

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
