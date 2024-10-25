"""Processes and cargo types for component production and deliveries.
Adapted from components.py Floating Study - Author: Jake Nunemaker.
"""

from itertools import count

from marmot import Agent, process
from marmot._exceptions import AgentNotRegistered

from ORBIT.core.components import VesselStorage
from ORBIT.core.exceptions import MissingComponent

from .common import DryStorage


class ComponentSet:
    """Create a generic component."""

    def __init__(self, _type, area, left):

        self.type = _type
        self.area = area
        self.left = left
        self.arrived = None

        # size = (characteristic mass, characteristic size)


class Component:
    """Remake for custom components."""

    def __init__(
        self,
        turbine,
        line,
        section,
        diameter,
        length,
        mass,
        thickness,
        cost_rate,
        area,
    ):

        self.type = section + "_d" + str(diameter)
        self.area = area
        self.length = length
        self.mass = mass
        self.turb_id = turbine
        self.line_id = line
        self.thickness = thickness
        self.cost_rate = cost_rate


class Transport(Agent):
    _counter = count(1)

    # TODO: Clean up extra specs in Transport Object
    def __init__(self, type, vessel, target):
        """Creates an instance of Transport agent.

        Parameters
        ----------
        type : str
            Component type
        vessel : dict
            a vessel or
        capacity : int
            number of units that can be carried
        target : object
            other storage object

        """
        name = f"{type} Transport {next(self._counter)}"
        super().__init__(name)

        self.vessel = vessel
        self.day_rate = vessel["day_rate"]
        self.capacity = vessel["capacity"]
        self.target = target

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

        payload = {
            **kwargs,
            "agent": str(self),
            "action": action,
            "duration": float(duration),
            "cost": duration / 24 * self.day_rate,
        }

        self.env._submit_log(payload, level="ACTION")

    def available_capacity(self):
        """Returns the available capacity of the Transport Agent."""

        self.used_capacity = +1

        return self.capacity - self.used_capacity

    @process
    def transport_items(self, cargo, time, target, constraints):

        # Load the cargo
        # print(self.available_capacity)
        yield self.task(
            f"Transport {cargo.type} Components",
            time,
            constraints=constraints,
            suspendable=True,
        )

        cargo.arrived = self.env.now
        target.pending.append(cargo)
        target.update_pending()

        # Empty cargo
        self.used_capacity = 0

    @process
    def return_to_facility(self, cargo, time):

        yield self.task(
            f"Transport back to {cargo.type} site. ",
            time,
        )

    @property
    def storage(self):
        """Returns VesselStorage or MissingComponent"""

        try:
            return self._storage

        except AttributeError:
            return MissingComponent(self, "Transport Storage")

    def extract_storage_specs(self):
        """Extracts storage system specifications if found."""

        self._storage_specs = self.vessel.get("storage_specs", {})
        if self._storage_specs:
            self.trip_data = []
            self._storage = VesselStorage(self.env, **self._storage_specs)


class ComponentManufacturingDelivery(Agent):
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
        vessel,
        transit_constraints={},
    ):
        """
        Creates an instance of `ComponentManufacturingDelivery`.

        Parameters
        ----------

        """

        super().__init__(f"{component} Production Line {num}")

        self.type = component
        self.area = area
        self.sets = sets
        print("SETS: ", sets)
        self.takt = takt_time
        self.takt_day_rate = takt_day_rate
        self.transit = transit_time
        self.target = target
        self.constraints = transit_constraints
        # self.day_rate = vessel['day_rate']

        self.vessel = vessel

    @process
    def start(self):

        # initialize storage object
        storage = DryStorage(self.env, float("Inf"))

        # initialize transport agent
        # transport = Transport(self.type, self.vessel, self.target)
        # transport.extract_storage_specs()
        # self.env.register(transport)
        # set is an array of units
        used = 0
        # A set of components with a per unit takt time.
        for i in range(len(self.sets)):

            components = ComponentSet(self.type, self.area, self.env.now)
            # print("Component vars:", vars(components))
            # Manufacture and store component
            if self.takt:
                takt_time = self.takt * self.sets[i]

                start = self.env.now
                yield storage.put(components)
                delay = self.env.now - start

                if delay > 0:
                    self.submit_action_log(
                        f"Delay: No {self.type} space Available", delay
                    )

                yield self.task(
                    f"Manufacture {self.type} Components: {i}",
                    takt_time,
                    cost=takt_time * self.takt_day_rate / 24,
                    supply_storage=len(storage.items),
                )

            # Transport component
            if self.transit == 0:
                components.arrived = self.env.now
                self.target.pending.append(components)
                self.target.update_pending()

            else:
                transport = Transport(self.type, self.vessel, self.target)
                self.env.register(transport)
                # print(transport.storage)
                transport.transport_items(
                    components, self.transit, self.target, self.constraints
                )
        # Return to facility
        # transport.return_to_facility(self.type, self.transit)


class ComponentManufacturing(Agent):

    def __init__(
        self, component, num, area, sets, takt_time, takt_day_rate, target
    ):
        """
        Creates an instance of `ComponentManufacturing`.

        Parameters
        ----------
        """

        super().__init__(f"{component} Production {num}")

        self.type = component
        self.area = area

        self.sets = sets

        self.takt = takt_time
        self.takt_day_rate = takt_day_rate

        # set up local storage for completed items.
        self.storage = target

    @process
    def start(self):

        for i, c in enumerate(self.sets):

            # components = ComponentSet(self.type, self.area, self.env.now)
            # print("Component vars:", vars(components))
            components = c

            # Manufacture and store component
            # Assume this is a takt rate as hours per meter
            if self.takt < 10.0:
                takt_time = self.takt * components.length
            else:
                takt_time = self.takt

            yield self.task(
                f"{i+1}, Manufacture: {c.type}",
                takt_time,
                cost=takt_time * self.takt_day_rate / 24,
                supply_storage=len(self.storage.items) + 1,
            )

            start = self.env.now
            yield self.storage.put(components)
            # yield self.storage.put(1)
            delay = self.env.now - start

            if delay > 0:
                self.submit_action_log(
                    f"Delay: No {self.type} storage Available", delay
                )


@process
def transport_component_to_port(
    transport,
    sets,
    feed,
    target,
    transit_time,
    # transit_constraints
):
    storage = transport._storage
    # print("Port vars: ", vars(target))

    """
    if the transport is at the site use feed.get() to get items while the
     storage is not full. When full, begin transit.

       if the transport is at port use put() to put items in target until
        empty. When empty, return to site. """

    # print("Storage vars:", vars(storage))
    n = 1
    transport.at_site = True
    transport.at_port = False

    while len(target.items) <= sets:
        print(n)
        if transit_time == 0:
            print("No transit time specified, COMPONENT made at port")
            item = yield storage.get()

            item.arrived = transport.env.now
            target.pending.append(item)
            target.update_pending()

            yield transport.task(
                "Put cargo at Port Laydown.",
                0,
                cost=0,
                transport_storage=len(storage.items),
                port_storage=target.available_area,
                port_capacity=len(target.items)
            )

        else:
            # TODO: Fix the get() event that subtracts from storage while transport arrives at port.

            if transport.at_site:
                start = transport.env.now
                item = yield feed.get()
                delay = transport.env.now - start

                if delay > 0:
                    if n == 1:
                        transport.mobilize()
                    else:
                        transport.submit_action_log(
                            "Waiting for chain to load.", delay, cost_multiplier=0
                    )

                # Put item on ship
                yield storage.put(item)
                yield transport.task(
                    "Loading cargo",
                    0,
                    cost=0,
                    supply_storage=len(feed.items),
                    transport_storage=len(storage.items),
                )

                if len(storage.items) == storage.capacity:
                    yield transport.task(
                        "Transport Components",
                        transit_time,
                        constraints={},
                        suspendable=True,
                        supply_storage=len(feed.items),
                        transport_storage=len(storage.items),
                    )
                    transport.at_site = False
                    transport.at_port = True
            # Delivered to port
            else:
                yield transport.task(
                    "Arrive at Port.",
                    0,
                    cost=0,
                    supply_storage=len(feed.items),
                    transport_storage=len(storage.items),
                    port_storage=target.available_area,
                    port_capacity=len(target.items)+1
                )

                # unload all the items
                while len(storage.items) > 0:
                    item = yield storage.get()

                    item.arrived = transport.env.now
                    target.pending.append(item)
                    target.update_pending()

                    yield transport.task(
                        "Put cargo at Port Laydown.",
                        0,
                        cost=0,
                        supply_storage=len(feed.items),
                        transport_storage=len(storage.items),
                        port_storage=target.available_area,
                        port_capacity=len(target.items)+1
                    )

                yield transport.task(
                    "Return to site",
                    transit_time / 2,
                    constraints={},
                    suspendable=True,
                    supply_storage=len(feed.items),
                    transport_storage=len(storage.items),
                    port_storage=target.available_area,
                )
                transport.at_site = True
                transport.at_port = False

        # yield storage.put(1)

        # yield transport.submit_action_log(
        #            f"Load cargo Components", 0 )

        # yield transport.submit_action_log("Fully loaded")

        # while used <= self.vessel['capacity']:
        #    yield self.task(f"Loading Cargo: {self.type} on ", 0,cost=0)

        #    print(used)
        #    used+=1
        #    pass

        # print(transport.storage)
        # transport.transport_items(transit_time, target, transit_constraints
        # Return to facility
        # transport.return_to_facility(self.type, self.transit)

        # print(f"{n} load up ")
        # X = Transport(self.env, )
        # storage = transport.extract_storage_specs()
        # print(storage)
        n += 1
