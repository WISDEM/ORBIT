"""Provides the `VesselStorage` and `VesselStorageContainer` classes."""

__author__ = ["Jake Nunemaker", "Rob Hammond"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


import simpy

from ORBIT.simulation.exceptions import (
    ItemNotFound,
    DeckSpaceExceeded,
    InsufficientAmount,
    CargoWeightExceeded,
    ItemPropertyNotDefined,
)


class VesselStorageContainer(simpy.Container):
    """Vessel Storage Class"""

    required_keys = ["weight", "deck_space"]

    def __init__(self, env, max_cargo, max_deck_load, **kwargs):
        """
        Creates an instance of VesselStorage.

        Parameters
        ----------
        env : simpy.Environment
            SimPy environment that simulation runs on.
        max_cargo : int | float
            Maximum weight the storage system can carry (t).
        """

        self.max_cargo_weight = max_cargo
        super().__init__(env, self.max_cargo_weight)
        self.deck_space = 0

        # Only needed for port interactions
        self.max_deck_space = 1
        self.max_deck_load = max_deck_load

    @property
    def current_cargo_weight(self):
        """
        Returns current cargo weight in tonnes.
        NOTE: Only necessary to interact with port.
        """

        return self.level

    @property
    def current_deck_space(self):
        """
        Returns current deck space used in m2.
        NOTE: Only necessary to interact with port.
        """

        return self.deck_space

    def put_item(self, item):
        """
        A wrapper for simpy.Container.put that checks VesselStorageContainer
        constraints and triggers self.put() if successful.

        Items put into the instance should be a dictionary with the following
        attributes:
         - name
         - weight (t)
         - length (km)

        Parameters
        ----------
        item : dict
            Dictionary of item properties.
        """

        if any(x not in item.keys() for x in self.required_keys):
            raise ItemPropertyNotDefined(item, self.required_keys)

        if self.current_deck_space + item["deck_space"] > self.max_deck_space:
            raise DeckSpaceExceeded(
                self.max_deck_space, self.current_deck_space, item
            )

        if self.current_cargo_weight + item["weight"] > self.max_cargo_weight:
            raise CargoWeightExceeded(
                self.max_cargo_weight, self.current_cargo_weight, item
            )

        self.deck_space += item["deck_space"]
        self.put(item["weight"])

    def get_item(self, item_type, item_amount):
        """
        Checks if there is enough of item, otherwise returns an error.

        Parameters
        ----------
        item_type : str
            Short, descriptive name of the item being accessed.
        item_amount : int or float
            Amount of the item to be loaded into storage.
        """

        if self.current_cargo_weight < item_amount:
            raise InsufficientAmount(
                self.current_cargo_weight, item_type, item_amount
            )

        return self.get(item_amount)
