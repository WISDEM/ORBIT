"""Common processes and cargo types for Mooring System supply chain and
installation.
"""

__author__ = "Nick Riccobono"
__copyright__ = "Copyright 2024, National Renewable Energy Laboratory"
__maintainer__ = "Nick Riccobono"
__email__ = "nicholas.riccobono@nrel.gov"


import numpy as np
import simpy
from marmot import Agent, process
from marmot._exceptions import AgentNotRegistered

from ORBIT.core.vessel import VesselStorage
from ORBIT.core.exceptions import MissingComponent


class Chain:
    """Chain Class."""

    def __init__(self):
        """Creates an instance of `Chain`."""

        pass


class Rope:
    """Rope Class."""

    def __init__(self):
        """Creates an instance of `Rope`."""

        pass


class DryStorage(simpy.FilterStore):
    """Dry Storage at each supplier used to store completed items."""

    def __init__(self, env, capacity):
        """
        Creates an instance of WetStorage.

        Parameters
        ----------
        capacity : int
            Number of items that can be stored.
        """
        super().__init__(env, capacity)


class LaydownArea(simpy.FilterStore):
    """Laydown Area Class. Used for Storage. """

    def __init__(self, env, area, trigger_assembly=0, buffer=0, **kwargs):
        """
        Creates an instance of LaydownArea.

        Parameters
        ----------
        area : int | float
            Available area in m2.
        """

        self.buffer = buffer
        self.env = env
        self.pending = []
        self.max_area = area
        self._trigger = trigger_assembly
        super().__init__(self.env)

    @property
    def available_area(self):
        """Returns available area for component storage."""

        return self.max_area - self.used_area

    @property
    def used_area(self):
        """ Return the used area. """

        return sum([i.area for i in self.items])

    @property
    def utilization(self):
        """ Return the utilization factor. """
        return self.used_area / self.max_area

    def update_pending(self):
        """ Update pending status. """
        print("Updating pending self vars:", len(self.items)+1)
        items = [c.type for c in self.items]
        pending = [c.type for c in self.pending]
        self.buffer = max([self.buffer, *[p.area for p in self.pending]])

        for item in np.unique(pending):
            if items and item not in items:
                idx = pending.index(item)
                self.pending.insert(0, self.pending.pop(idx))

        try:
            if self.pending[0].type not in items:
                available = self.available_area

            else:
                available = self.available_area - self.buffer

            if self.pending[0].area <= available:
                component = self.pending.pop(0)
                self.put(component)
                if self.env.now > component.arrived:
                    self.env._submit_log(
                        {
                            "agent": f"{component.type} Component Set",
                            "action": "Delay: Waiting for Laydown",
                            "duration": self.env.now - component.arrived,
                            "cost": 0,
                            "storage": self.available_area,
                        },
                        level="ACTION",
                    )

        except IndexError:
            pass

        if self.used_area > self._trigger:
            try:
                self.start_assembly.succeed()

            except RuntimeError:
                pass


class ChainAssemblyLine(Agent):
    """Mooring Chain Assembly Line Class."""

    def __init__(self, assigned, laydown, time, target, num, day_rate):
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

        super().__init__(f"Mooring Chain Assembly Line {num}")

        self.assigned = assigned
        self.time = time
        self.target = target
        self.laydown = laydown
        self.day_rate = day_rate

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
    def assemble_chain(self):
        """Simulation process for assembling a substructure."""

        yield self.task("Chain Assembly", self.time)
        chain = Chain()

        start = self.env.now
        yield self.target.put(chain)
        delay = self.env.now - start

        if delay > 0:
            self.submit_action_log("Delay: No Chain Storage Available", delay)

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
                yield get_component_set(self, self.laydown, "Chain")
                yield self.assemble_chain()

            except IndexError:
                break


class Transport(Agent):
    """ Transport class agent. """
    def __init__(self, name, config, avail=1):
        """Creates an instance of Transport. Based on Vessel(Agent)."""
        super().__init__(name)
        self._specs = config
        self.day_rate = config.get("day_rate", 0)

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
                "cost": self.operation_cost(duration, **kwargs),
            }

            self.env._submit_log(payload, level="ACTION")

    def operation_cost(self, hours, **kwargs):
        """
        Returns cost of an operation of duration `hours`.

        Parameters
        ----------
        hours : int | float
            Duration of operation in hours.
        mult : int | float
            Multiplier to use for the operation cost.
            Default: 1.
        """

        mult = kwargs.get("cost_multiplier", 1.0)
        return (self.day_rate / 24) * hours * mult

    def load_cargo(self):
        """ Task that representings loading cargo. """

        yield self.task("Load Cargo", 0.5)

    def initialize(self, mobilize=False):
        """ initialize. """
        self.extract_storage_specs()
        if mobilize:
            self.mobilize()

    def mobilize(self):
        """
        Submits an action log representing the cost to mobilize the vessel at
        the start of an installation based on the vessel day rate.
        """

        days = self._specs.get("mobilization_days", 0)
        mult = self._specs.get("mobilization_mult", 0)

        self.submit_action_log("Mobilize", days * 24, cost_multiplier=mult)
        self.at_port = False
        self.at_site = True

    @property
    def storage(self):
        """Returns VesselStorage or MissingComponent. """

        try:
            return self._storage

        except AttributeError:
            return MissingComponent(self, "Transport Storage")

    def extract_storage_specs(self):
        """Extracts storage system specifications if found."""

        self._storage_specs = self._specs.get("storage_specs", {})
        if self._storage_specs:
            self.trip_data = []
            self._storage = VesselStorage(self.env, **self._storage_specs)

    def transport_items(self, time, target, constraints):

        yield self.task(
            "Transport (TYPE) Components",
            time,
            constraints=constraints,
            suspendable=True,
        )
        print("VARS OF target", vars(target))
        # cargo.arrived = self.env.now
        # target.pending.append(cargo)
        # target.update_pending()


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
