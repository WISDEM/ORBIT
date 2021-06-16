"""Common supply chain classes and related processes."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2021, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from copy import deepcopy
from itertools import count

import simpy
from marmot import Agent, process
from marmot._exceptions import AgentNotRegistered


class OrbitAgent(Agent):
    """"""

    def submit_action_log(self, action, duration, **kwargs):
        """
        Submits a log representing a completed `action` performed over time
        `duration`.

        This method overwrites the default `submit_action_log` in
        `marmot.Agent`, adding operation cost to every submitted log within
        ORBIT.

        Parameters
        ----------
        action : str
            Performed action.
        duration : int | float
            Duration of action.

        Raises
        ------
        AgentNotRegistered
        """

        if self.env is None:
            raise AgentNotRegistered(self)

        else:
            payload = {
                **kwargs,
                "agent": str(self),
                "action": action,
                "duration": float(duration),
                "cost": duration / 24 * self.day_rate,
            }

            self.env._submit_log(payload, level="ACTION")


class ComponentSet:
    def __init__(self, _type, left):

        self.type = _type
        self.left = left
        self.arrived = None


class Transport(OrbitAgent):
    _counter = count(0)

    def __init__(self, type, day_rate):

        name = f"{type} Transport {next(self._counter)}"
        super().__init__(name)
        self.day_rate = day_rate

    @process
    def transport_items(self, cargo, time, target, constraints):
        """
        Transport items in `cargo` for `time` to `target`.

        Parameters
        ----------
        cargo : list
            List of cargo items.
        time : int | float
            Time required to transport items.
        target : simpy.Store
        constraints : dict
        """

        yield self.task(
            f"Transport {cargo[0].type} Components",
            time,
            constraints=constraints,
            suspendable=True,
        )

        for c in cargo:
            c.arrived = self.env.now
            target.put(c)


class ComponentDelivery(Agent):
    """"""

    def __init__(
        self,
        component,
        num,
        takt_time,
        takt_day_rate,
        num_parallel=1,
        transit_time=0,
        transit_constraints={},
        transit_day_rate=0,
    ):
        """
        Creates an instance of `SupplyChain`.

        Should contain the following sub tasks:
        - Component delivery (without modeling the laydown area directly)
        - Manufacture (can be subclassed with component specific tasks)

        Parameters
        ----------
        component : str
            Component to be manufactured.
        num : int
            Number of component sets to be manufactured.
        takt_time : int | float
            Time to manufacture component set.
        takt_day_rate : int | float
            Day rate for component manufacturing lines.
        num_parallel : int (optional)
            Number of parallel assembly lines.
            Default: 1
        transit_time : int | float (optional)
            Time to transit components from foreign port to local staging area.
            Default: 0h
        transit_constraints : dict (optional)
            Constraints associated with transporting components.
            Default: {}
            Format: {'waveheight': le(3)}
        transit_day_rate : int | float (optional)
            Transport day rate.
            Default: 0 $/day
        """

        super().__init__(f"{component} Supply Chain")
        Transport._counter = count(0)

        self.type = component
        self.num = num
        self.takt = takt_time
        self.takt_day_rate = takt_day_rate
        self.num_parallel = num_parallel
        self.transit = transit_time
        self.constraints = transit_constraints
        self.day_rate = transit_day_rate

    def initialize_staging_area(self):
        """"""

        self.staging_area = simpy.Store(self.env, capacity=float("inf"))

    @process
    def start(self):

        for _ in range(self.num):
            if self.takt:
                yield self.task(
                    f"Manufacture {self.type} Components",
                    self.takt,
                    cost=self.takt
                    * self.takt_day_rate
                    * self.num_parallel
                    / 24,
                )

            components = []
            for _ in range(self.num_parallel):
                components.append(ComponentSet(self.type, self.env.now))

            if self.transit == 0:

                for c in components:
                    c.arrived = self.env.now
                    self.staging_area.put(c)

            else:
                transport = Transport(self.type, self.day_rate)
                self.env.register(transport)
                transport.transport_items(
                    components,
                    self.transit,
                    self.staging_area,
                    self.constraints,
                )


class AssemblyLine(OrbitAgent):
    """Assembly Line Class."""

    _counter = count(0)
    outputs = [1]
    component = "Generic"

    def __init__(self, assigned, pull_from, time, target, day_rate):
        """
        Creates an instance of `AssemblyLine`.

        Parameters
        ----------
        assigned : list
            List of assigned tasks. Can be shared with other assembly lines.
        time : int | float
            Hours required to assembly one component set.
        target : simpy.Store
            Target storage.

        """

        super().__init__(
            f"{self.component} Assembly Line {next(self._counter)}"
        )

        self.assigned = assigned
        self.pull_from = pull_from
        self.time = time
        self.target = target
        self.day_rate = day_rate

    @process
    def assemble(self):
        """Simulation process for assembling a substructure."""

        yield self.task(f"{self.component} Assembly", self.time)

        for o in self.outputs:
            yield self.target.put(deepcopy(o))

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
                yield self.pull_from.get()
                yield self.assemble()

            except IndexError:
                break
