"""Common supply chain classes and related processes."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2021, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from itertools import count

from marmot import Agent, process
from marmot._exceptions import AgentNotRegistered

from ORBIT.core.cargo import Monopile, TransitionPiece


@process
def get_component_set(agent, laydown, _type):

    start = agent.env.now
    laydown.update_pending()
    yield laydown.get(lambda x: x.type == _type)
    delay = agent.env.now - start

    if delay > 0:
        agent.submit_action_log(
            f"Delay: Waiting for {_type} Component Set", delay
        )


class ComponentSet:
    def __init__(self, _type, area, left):

        self.type = _type
        self.area = area
        self.left = left
        self.arrived = None


class Transport(Agent):
    _counter = count(0)

    def __init__(self, type, day_rate):

        name = f"{type} Transport {next(self._counter)}"
        super().__init__(name)
        self.day_rate = day_rate

    @process
    def transport_items(self, cargo, time, target, constraints):
        """"""

        yield self.task(
            f"Transport {cargo.type} Components",
            time,
            constraints=constraints,
            suspendable=True,
        )

        cargo.arrived = self.env.now
        target.pending.append(cargo)
        target.update_pending()

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


class ComponentDelivery(Agent):
    """"""

    def __init__(
        self,
        component,
        num,
        area,
        sets,
        target,
        takt_time,
        takt_day_rate,
        transit_time,
        transit_constraints={},
        transit_day_rate=0,
    ):
        """
        Creates an instance of `ComponentDelivery`.

        Parameters
        ----------

        """

        super().__init__(f"{component} Delivery {num}")
        Transport._counter = count(0)

        self.type = component
        self.area = area
        self.sets = sets
        self.takt = takt_time
        self.takt_day_rate = takt_day_rate
        self.transit = transit_time
        self.target = target
        self.constraints = transit_constraints
        self.day_rate = transit_day_rate

    @process
    def start(self):
        for _ in range(self.sets):
            if self.takt:
                yield self.task(
                    f"Manufacture {self.type} Components",
                    self.takt,
                    cost=self.takt * self.takt_day_rate / 24,
                )

            components = ComponentSet(self.type, self.area, self.env.now)

            if self.transit == 0:
                components.arrived = self.env.now
                self.target.pending.append(components)
                self.target.update_pending()

            else:
                transport = Transport(self.type, self.day_rate)
                self.env.register(transport)
                transport.transport_items(
                    components, self.transit, self.target, self.constraints
                )


class MonopileAssemblyLine(Agent):
    """Substructure Assembly Line Class."""

    def __init__(
        self, assigned, laydown, time, target, num, day_rate, monopile, tp
    ):
        """
        Creates an instance of `SubstructureAssemblyLine`.

        Parameters
        ----------
        assigned : list
            List of assigned tasks. Can be shared with other assembly lines.
        time : int | float
            Hours required to assembly one substructure.
        target : simpy.Store
            Target storage.
        num : int
            Assembly line number designation.
        """

        super().__init__(f"Substructure Assembly Line {num}")

        self.assigned = assigned
        self.time = time
        self.target = target
        self.laydown = laydown
        self.day_rate = day_rate
        self.monopile = monopile
        self.tp = tp

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

    @process
    def assemble_substructure(self):
        """Simulation process for assembling a substructure."""

        yield self.task("Substructure Assembly", self.time)
        monopile = Monopile(**self.monopile)
        tp = TransitionPiece(**self.tp)

        start = self.env.now
        yield self.target.put(monopile)
        yield self.target.put(tp)
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
                yield get_component_set(self, self.laydown, "Monopile")
                yield self.assemble_substructure()

            except IndexError:
                break
