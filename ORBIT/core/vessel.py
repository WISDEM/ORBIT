"""Provides the `Vessel` class."""

__author__ = ["Jake Nunemaker", "Rob Hammond"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"

from collections import Counter, namedtuple

import numpy as np
from marmot import Agent, le, process
from marmot._exceptions import AgentNotRegistered

from ORBIT.core.components import (
    Crane,
    JackingSys,
    CableCarousel,
    VesselStorage,
    ScourProtectionStorage,
)
from ORBIT.core.exceptions import ItemNotFound, MissingComponent

Trip = namedtuple("Trip", "cargo_weight deck_space items")


class Vessel(Agent):
    """Base Vessel Class"""

    def __init__(self, name, config):
        """
        Creates an instance of Vessel.

        Parameters
        ----------
        specs : dict
            Nested dictionary containing vessel specifications.
        """

        super().__init__(name)
        self.config = config
        self.extract_vessel_dayrate()

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
                "cost": self.operation_cost(duration),
            }

            self.env._submit_log(payload, level="ACTION")

    def extract_vessel_dayrate(self):
        """
        Extracts the day rate of the vessel. If it isn't found, resorts to
        default values.
        """

        try:
            self.day_rate = self.config["vessel_specs"]["day_rate"]

        except KeyError:
            self.day_rate = np.NaN

    def operation_cost(self, hours, mult=1.0):
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

        return (self.day_rate / 24) * hours * mult

    @property
    def crane(self):
        """Returns configured `Crane` or raises `MissingComponent`."""
        try:
            return self._crane

        except AttributeError:
            raise MissingComponent(self, "Crane")

    @property
    def jacksys(self):
        """Returns configured `JackSys` or raises `MissingComponent`."""
        try:
            return self._jacksys

        except AttributeError:
            raise MissingComponent(self, "Jacking System")

    @property
    def storage(self):
        """Returns configured `VesselStorage` or raises `MissingComponent`."""
        try:
            return self._storage

        except AttributeError:
            return MissingComponent(self, "Vessel Storage")

    @property
    def rock_storage(self):
        """Returns configured `ScourProtectionStorage` or raises `MissingComponent`."""
        try:
            return self._rock_storage

        except AttributeError:
            raise MissingComponent(self, "Scour Protection Storage")

    @property
    def cable_storage(self):
        """Returns configured `CableCarousel` or raises `MissingComponent`."""
        try:
            return self._cable_storage

        except AttributeError:
            raise MissingComponent(self, "Cable Storage")

    def extract_vessel_specs(self):
        """
        Extracts vessel specifications from self.config.
        """

        self.extract_transport_specs()
        self.extract_jacksys_specs()
        self.extract_crane_specs()
        self.extract_storage_specs()
        self.extract_cable_storage_specs()
        self.extract_scour_protection_specs()

    def extract_transport_specs(self):
        """Extracts and defines transport related specifications."""

        self._transport_specs = self.config.get("transport_specs", {})
        self.transit_speed = self._transport_specs.get("transit_speed", None)

    def extract_crane_specs(self):
        """Extracts crane specifications if found."""

        self._crane_specs = self.config.get("crane_specs", {})
        if self._crane_specs:
            self._crane = Crane(self._crane_specs)

    def extract_jacksys_specs(self):
        """Extracts jacking system specifications if found."""

        self._jacksys_specs = self.config.get("jacksys_specs", {})
        if self._jacksys_specs:
            self._jacksys = JackingSys(self._jacksys_specs)

    def extract_storage_specs(self):
        """Extracts storage system specifications if found."""

        self._storage_specs = self.config.get("storage_specs", {})
        if self._storage_specs:
            self.trip_data = []
            self._storage = VesselStorage(self.env, **self._storage_specs)

    def extract_cable_storage_specs(self):
        """Extracts and defines cable storage system specifications if found."""

        self._cable_storage_specs = self.config.get("cable_storage", {})
        if self._cable_storage_specs:
            self.trip_data = []
            self._cable_storage = CableCarousel(
                self.env, **self._cable_storage_specs
            )

    def extract_scour_protection_specs(self):
        """
        Extracts and defines scour protection installation specifications.

        Parameters
        ----------
        scour_protection_specs : dict
            Dictionary containing scour protection installation specifications.
        """

        self._sp_specs = self.config.get("spi_specs", {})

        _capacity = self._sp_specs.get("max_cargo_weight", None)
        if _capacity is None:
            capacity = self._storage_specs.get("max_cargo", None)

        else:
            capacity = _capacity

        if capacity:
            self._rock_storage = ScourProtectionStorage(self.env, capacity)

        self.scour_protection_install_speed = self._sp_specs.get(
            "scour_protection_install_speed", 10
        )

    @process
    def get_item_from_storage(
        self, _type, vessel=None, release=False, **kwargs
    ):
        """
        Retrieves an item which matches `item.type = _type` from `self.storage`
        or `vessel.storage` if configured.

        Parameters
        ----------
        _type : str
            Type of item to retrieve.
        vessel : Vessel | None
            Optional configuration to retrieve item from different vessel.
        release : bool
            If True, releases the vessel if it is empty.
        """

        if vessel is None:
            vessel = self

        try:
            item = vessel.storage.get_item(_type)

        except ItemNotFound as e:
            self.submit_debug_log(message="Item not found.")
            raise e

        action, time = item.release(**kwargs)
        yield self.task(
            action,
            time,
            constraints=self.transit_limits,
            cost=self.operation_cost(time),
        )

        if release and vessel.storage.any_remaining(_type) is False:
            vessel.release.succeed()

        return item

    @process
    def transit(self, distance, **kwargs):
        """
        Generic transit task.

        Parameters
        ----------
        distance : int | float
            Distance to transit for.
        """

        time = self.transit_time(distance)
        yield self.task(
            "Transit",
            time,
            constraints=self.transit_limits,
            suspendable=True,
            **kwargs,
        )

    def transit_time(self, distance):
        """
        Calculates transit time for a given distance.

        Parameters
        ----------
        distance : int | float
            Distance to travel (km).

        Returns
        -------
        transit_time : float
            Time required to travel 'distance' (h).
        """

        transit_time = distance / self.transit_speed

        return transit_time

    @property
    def transit_limits(self):
        """
        Returns dictionary of `marmot.Constraints` for 'windspeed' and
        'waveheight', representing the transit limits of the vessel.
        """

        _dict = {
            "windspeed": le(self._transport_specs["max_windspeed"]),
            "waveheight": le(self._transport_specs["max_waveheight"]),
        }

        return _dict

    @property
    def operational_limits(self):
        """
        Returns dictionary of `marmot.Constraints` for 'windspeed' and
        'waveheight', representing the operational limits of the vessel.
        """

        try:
            _ = getattr(self, "crane")
            max_windspeed = self._crane_specs["max_windspeed"]

        except MissingComponent:
            max_windspeed = self._transport_specs["max_windspeed"]

        _dict = {
            "windspeed": le(max_windspeed),
            "waveheight": le(self._transport_specs["max_waveheight"]),
        }

        return _dict

    def update_trip_data(self, cargo=True, deck=True, items=True):
        """
        Appends the current cargo utilization to the `self._cargo_utlization`.
        Used to collect cargo utilization statistics throughout a simulation.

        Parameters
        ----------
        items : bool
            Toggles optional item list collection.
        """

        storage = getattr(self, "storage", None)
        if storage is None:
            raise Exception("Vessel does not have storage capacity.")

        _cargo = storage.current_cargo_weight if cargo else np.NaN
        _deck = storage.current_deck_space if deck else np.NaN
        _items = dict(Counter(i for i in storage.items)) if items else np.NaN

        trip = Trip(cargo_weight=_cargo, deck_space=_deck, items=_items)

        self.trip_data.append(trip)

    @property
    def cargo_weight_list(self):
        """Returns cargo weights trips in self.trip_data."""

        return [trip.cargo_weight for trip in self.trip_data]

    @property
    def cargo_weight_utilizations(self):
        """Returns cargo weight utilizations for list of trips."""

        return np.array(self.cargo_weight_list) / self.max_cargo

    @property
    def deck_space_list(self):
        """Returns deck space used for trips in self.trip_data."""

        return [trip.deck_space for trip in self.trip_data]

    @property
    def deck_space_utilizations(self):
        """Returns deck space utilizations for list of trips."""

        return np.array(self.deck_space_list) / self.max_deck_space

    @property
    def max_cargo_weight_utilization(self):
        """Returns maximum cargo weight utilization."""

        if not self.trip_data:
            return np.NaN

        return np.max(self.cargo_weight_utilizations)

    @property
    def min_cargo_weight_utilization(self):
        """Returns minimum cargo weight utilization."""

        if not self.trip_data:
            return np.NaN

        return np.min(self.cargo_weight_utilizations)

    @property
    def mean_cargo_weight_utilization(self):
        """Returns mean cargo weight utilization."""

        if not self.trip_data:
            return np.NaN

        return np.mean(self.cargo_weight_utilizations)

    @property
    def median_cargo_weight_utilization(self):
        """Returns median cargo weight utilization."""

        if not self.trip_data:
            return np.NaN

        return np.median(self.cargo_weight_utilizations)

    @property
    def max_deck_space_utilization(self):
        """Returns maximum deck_space utilization."""

        if not self.trip_data:
            return np.NaN

        return np.max(self.deck_space_utilizations)

    @property
    def min_deck_space_utilization(self):
        """Returns minimum deck_space utilization."""

        if not self.trip_data:
            return np.NaN

        return np.min(self.deck_space_utilizations)

    @property
    def mean_deck_space_utilization(self):
        """Returns mean deck space utilization."""

        if not self.trip_data:
            return np.NaN

        return np.mean(self.deck_space_utilizations)

    @property
    def median_deck_space_utilization(self):
        """Returns median deck space utilization."""

        if not self.trip_data:
            return np.NaN

        return np.median(self.deck_space_utilizations)

    @property
    def max_items_by_weight(self):
        """Returns items corresponding to `self.max_cargo_weight`."""

        if not self.trip_data:
            return np.NaN

        i = np.argmax(self.cargo_weight_list)
        return self.trip_data[i].items

    @property
    def min_items_by_weight(self):
        """Returns items corresponding to `self.min_cargo_weight`."""

        if not self.trip_data:
            return np.NaN

        i = np.argmin(self.cargo_weight_list)
        return self.trip_data[i].items

    @property
    def max_items_by_space(self):
        """Returns items corresponding to `self.max_deck_space`."""

        if not self.trip_data:
            return np.NaN

        i = np.argmax(self.deck_space_list)
        return self.trip_data[i].items

    @property
    def min_items_by_space(self):
        """Returns items corresponding to `self.min_deck_space`."""

        if not self.trip_data:
            return np.NaN

        i = np.argmin(self.deck_space_list)
        return self.trip_data[i].items
