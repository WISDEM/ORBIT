"""Provides the `Port` class."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


import numpy as np
import simpy
from marmot import Agent, le, process

from ORBIT.core.exceptions import ItemNotFound


class Port:
    """Port Class"""

    def __init__(self, env, laydown_area=float("inf"), num_cranes=1, **kwargs):
        """
        Creates an instance of Port.

        Parameters
        ----------
        env : simpy.Environment
            SimPy environment that simulation runs on.
        """

        self.env = env
        self.crane = simpy.Resource(self.env, num_cranes)
        self.laydown = LaydownArea(self.env, laydown_area)

    # def get_item(self, _type):
    #     """
    #     Checks self.items for an item satisfying `item.type = _type`, otherwise
    #     returns `ItemNotFound`.

    #     Parameters
    #     ----------
    #     _type : str
    #         Type of item to match. Checks `item.type`.

    #     Returns
    #     -------
    #     res.value : FilterStoreGet.value
    #         Returned item.

    #     Raises
    #     ------
    #     ItemNotFound
    #     """

    #     target = None
    #     for i in self.items:
    #         try:
    #             if i.type == _type:
    #                 target = i
    #                 break

    #         except AttributeError:
    #             continue

    #     if not target:
    #         raise ItemNotFound(_type)

    #     else:
    #         res = self.get(lambda x: x == target)
    #         return res.value


class LaydownArea(simpy.FilterStore):
    """Laydown Area Class."""

    def __init__(self, env, area, buffer=0, **kwargs):
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
        super().__init__(self.env)

    @property
    def available_area(self):
        """Returns available area for component storage."""

        return self.max_area - self.used_area

    @property
    def used_area(self):
        """"""

        return sum([i.area for i in self.items])

    @property
    def utilization(self):

        return self.used_area / self.max_area

    def update_pending(self):
        """"""

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
                        },
                        level="ACTION",
                    )

        except IndexError:
            pass


class WetStorage(simpy.Store):
    """Storage infrastructure for floating substructures."""

    def __init__(self, env, capacity):
        """
        Creates an instance of WetStorage.

        Parameters
        ----------
        capacity : int
            Number of substructures or assemblies that can be stored.
        """

        super().__init__(env, capacity)


class DryStorage(simpy.FilterStore):
    """Storage infrastructure for fixed substructures."""

    def __init__(self, env, capacity):
        """
        Creates an instance of DryStorage.

        Parameters
        ----------
        capacity : int
            Number of substructures or assemblies that can be stored.
        """

        super().__init__(env, capacity)
