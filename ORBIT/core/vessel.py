"""Provides the `Vessel` class."""

__author__ = ["Jake Nunemaker", "Rob Hammond"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"

from collections import Counter, namedtuple

import numpy as np
from marmot import Agent, le

from ORBIT.vessels.tasks import defaults

from .components import Crane, JackingSys, VesselStorage

Trip = namedtuple("Trip", "cargo_weight deck_space items")


class MissingComponent(Exception):
    """Error for a missing component on a vessel."""

    def __init__(self, vessel, component):
        """
        Creates an instance of MissingComponent.

        Parameters
        ----------
        vessel : Vessel
        component : str
            Missing required component.
        """

        self.vessel = vessel
        self.component = component

        self.message = (
            f"{vessel} is missing required component(s) '{component}'."
        )

    def __str__(self):

        return self.message


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
        # self.extract_vessel_specs()

    @property
    def crane(self):
        # TODO: Add crane.setter type check?
        if self._crane:
            return self._crane

        else:
            raise MissingComponent(self, "Crane")

    @property
    def jacksys(self):
        # TODO: Add jacksys.setter type check?
        if self._jacksys:
            return self._jacksys

        else:
            raise MissingComponent(self, "Jacking System")

    @property
    def storage(self):
        # TODO: Add storage.setter type check?
        if self._storage:
            return self._storage

        else:
            return MissingComponent(self, "Vessel Storage")

    def extract_vessel_specs(self):
        """
        Extracts vessel specifications from self.config.
        """

        self.extract_transport_specs()
        self.extract_jacksys_specs()
        self.extract_crane_specs()
        self.extract_storage_specs()

        # TODO:
        # cable_lay_specs = vessel_specs.get("cable_lay_specs", None)
        # if cable_lay_specs:
        #     self.extract_cable_lay_specs(cable_lay_specs)

        # scour_protection_specs = vessel_specs.get(
        #     "scour_protection_install_specs", None
        # )
        # if scour_protection_specs:
        #     self.extract_scour_protection_specs(scour_protection_specs)

    def extract_transport_specs(self):
        """Extracts and defines transport related specifications."""

        self._transport_specs = self.config.get("transport_specs", None)
        self.transit_speed = self._transport_specs.get("transit_speed", None)

    def extract_crane_specs(self):
        """
        TODO:
        """

        self._crane_specs = self.config.get("crane_specs", None)
        if self._crane_specs:
            self._crane = Crane(self._crane_specs)

        else:
            self._crane = None

    def extract_jacksys_specs(self):
        """
        TODO:
        """

        self._jacksys_specs = self.config.get("jacksys_specs", None)
        if self._jacksys_specs:
            self._jacksys = JackingSys(self._jacksys_specs)

        else:
            self._jacksys = None

    def extract_storage_specs(self):
        """
        Extracts and defines storage system specifications.
        """

        self._storage_specs = self.config.get("storage_specs", None)
        if self._storage_specs:
            self.trip_data = []
            self._storage = VesselStorage(self.env, **self._storage_specs)

        else:
            self._storage = None

    # def extract_cable_lay_specs(self, cable_lay_specs):
    #     """
    #     Extracts and defines cable lay system specifications.

    #     Parameters
    #     ----------
    #     cable_lay_specs : dict
    #         Dictionary containing cable lay system specifications.
    #     """

    #     self.cable_lay_speed = cable_lay_specs.get(
    #         "cable_lay_speed", defaults["cable_lay_speed"]
    #     )
    #     self.max_cable_diameter = cable_lay_specs.get(
    #         "max_cable_diameter", None
    #     )

    # def extract_scour_protection_specs(self, scour_protection_specs):
    #     """
    #     Extracts and defines scour protection installation specifications.

    #     Parameters
    #     ----------
    #     scour_protection_specs : dict
    #         Dictionary containing scour protection installation specifications.
    #     """

    #     self.scour_protection_install_speed = scour_protection_specs.get(
    #         "scour_protection_install_speed", 10
    #     )

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
        TODO: Returns dictionary with 'max_windspeed' and 'max_waveheight'
        for transit.
        """

        _dict = {
            "windspeed": le(self._transport_specs["max_windspeed"]),
            "waveheight": le(self._transport_specs["max_waveheight"]),
        }

        return _dict

    @property
    def operational_limits(self):
        """
        TODO: Returns dictionary with 'max_windspeed' and 'max_waveheight'
        for operations.
        """

        crane = getattr(self, "crane", None)
        if crane is None:
            max_windspeed = self._transport_specs["max_windspeed"]

        else:
            max_windspeed = self._crane_specs["max_windspeed"]

        _dict = {
            "max_windspeed": le(max_windspeed),
            "max_waveheight": le(self._transport_specs["max_waveheight"]),
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
