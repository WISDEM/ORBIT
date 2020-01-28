"""Provides the `Port` class."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


import simpy

from ORBIT.core.exceptions import ItemNotFound


class Port(simpy.FilterStore):
    """Port Class"""

    def __init__(self, env, **kwargs):
        """
        Creates an instance of Port.

        Parameters
        ----------
        env : simpy.Environment
            SimPy environment that simulation runs on.
        """

        capacity = kwargs.get("capacity", float("inf"))
        super().__init__(env, capacity)

    def get_item(self, _type):
        """
        TODO:
        Checks self.items for an item satisfying 'rule'. Returns item if found,
        otherwise returns an error.

        Parameters
        ----------
        rule : tuple
            Tuple defining the rule to filter items by.
            - ('key': 'value')

        Returns
        -------
        res : FilterStoreGet
            Response from underlying FilterStore. Call 'res.value' for the
            underlying dictionary.
        """

        target = None
        for i in self.items:
            if i.type == _type:
                target = i
                break

        if not target:
            raise ItemNotFound(_type)

        else:
            res = self.get(lambda x: x == target)
            return res.value
