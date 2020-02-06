"""Provides the base `InstallPhase` class."""

__author__ = ["Jake Nunemaker", "Rob Hammond"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = ["Jake Nunemaker", "Rob Hammond"]
__email__ = ["jake.nunemaker@nrel.gov", "robert.hammond@nrel.gov"]


from abc import abstractmethod

import numpy as np
import simpy
from marmot import Environment

from ORBIT.core import Port
from ORBIT.phases import BasePhase


class InstallPhase(BasePhase):
    """BasePhase subclass for install modules."""

    def __init__(self, weather, **kwargs):
        """
        Creates an instance of `InstallPhase`.

        Parameters
        ----------
        weather : np.ndarray
            Weather profile at site.
        """

        self.extract_phase_kwargs(**kwargs)
        self.initialize_environment(weather, **kwargs)

    def initialize_environment(self, weather, **kwargs):
        """
        Initializes a `marmot.Environment` at `self.env`.

        Parameters
        ----------
        weather : np.ndarray
            Weather profile at site.
        """

        env_name = kwargs.get("env_name", "Environment")
        self.env = Environment(name=env_name, state=weather)

    @abstractmethod
    def setup_simulation(self):
        """
        Sets up the required simulation infrastructure

        Generally, this creates the port, initializes the items to be
        installed, and initializes the vessel(s) used for the installation.
        """

        pass

    def initialize_port(self):
        """
        Initializes a Port object with N number of cranes.
        """

        cranes = self.config["port"]["num_cranes"]

        self.port = Port(self.env)
        self.port.crane = simpy.Resource(self.env, cranes)

    def run(self, until=None):
        """
        Runs the simulation on self.env.

        Parameters
        ----------
        until : int, optional
            Number of steps to run.
        """

        self.env._submit_log({"message": "SIMULATION START"}, "DEBUG")
        self.env.run(until=until)
        self.append_phase_info()
        self.env._submit_log({"message": "SIMULATION END"}, "DEBUG")

    def append_phase_info(self):
        """Appends phase information to all logs in `self.env.logs`."""

        for l in self.env.logs:
            l["phase"] = self.phase

    @property
    def port_costs(self):
        """Cost of port rental."""

        port = getattr(self, "port", None)

        if port is None:
            return 0

        else:
            key = "port_cost_per_month"
            rate = self.config["port"].get("monthly_rate", self.defaults[key])

            months = self.total_phase_time / (8760 / 12)
            return months * rate

    @property
    def total_phase_cost(self):
        """Returns total phase cost in $USD."""

        return self.action_costs + self.port_costs

    @property
    def action_costs(self):
        """Returns sum cost of all actions."""

        return np.nansum([a["cost"] for a in self.env.actions])

    @property
    def total_phase_time(self):
        """Returns total phase time in hours."""

        return max([a["time"] for a in self.env.actions])

    @property
    @abstractmethod
    def detailed_output(self):
        """Returns detailed phase information."""

        pass

    # @property
    # def agent_efficiencies(self):
    #     """
    #     Returns a summary of agent operational efficiencies.
    #     """

    #     logs = self.logs.loc[self.logs["level"] == "INFO"]
    #     grouped = (
    #         logs.groupby(["agent", "type"])
    #         .sum()["duration"]
    #         .unstack()
    #         .fillna(0.0)
    #     )

    #     if "Operations" not in grouped.columns:
    #         raise Exception("'Operations' not found in action types.")

    #     if "Delay" not in grouped.columns:
    #         grouped["Delay"] = 0.0

    #     grouped["Total"] = grouped["Operations"] + grouped["Delay"]
    #     _efficiencies = (grouped["Operations"] / grouped["Total"]).to_dict()
    #     efficiencies = {
    #         k + "_operational_efficiency": v for k, v in _efficiencies.items()
    #     }

    #     return efficiencies

    # @staticmethod
    # def get_max_cargo_weight_utilzations(vessels):
    #     """
    #     Returns a summary of cargo weight efficiencies for list of input `vessels`.

    #     Parameters
    #     ----------
    #     vessels : list
    #         List of vessels to calculate efficiencies for.
    #     """

    #     outputs = {}

    #     for vessel in vessels:

    #         storage = getattr(vessel, "storage", None)
    #         if storage is None:
    #             print("Vessel does not have storage capacity.")
    #             continue

    #         outputs[
    #             f"{vessel.name}_cargo_weight_utilization"
    #         ] = vessel.max_cargo_weight_utilization

    #     return outputs

    # @staticmethod
    # def get_max_deck_space_utilzations(vessels):
    #     """
    #     Returns a summary of deck space efficiencies for list of input `vessels`.

    #     Parameters
    #     ----------
    #     vessels : list
    #         List of vessels to calculate efficiencies for.
    #     """

    #     outputs = {}

    #     for vessel in vessels:

    #         storage = getattr(vessel, "storage", None)
    #         if storage is None:
    #             print("Vessel does not have storage capacity.")
    #             continue

    #         outputs[
    #             f"{vessel.name}_deck_space_utilization"
    #         ] = vessel.max_deck_space_utilization

    #     return outputs
