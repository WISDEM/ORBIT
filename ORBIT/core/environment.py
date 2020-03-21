"""ORBIT specific marmot.Environment."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from bisect import bisect

import numpy as np
from marmot import Environment
from marmot._core import Constraint
from numpy.lib.recfunctions import append_fields


class OrbitEnvironment(Environment):
    """ORBIT Specific Environment."""

    def __init__(self, name="Environment", state=None, alpha=0.1):
        """
        Creates an instance of Environment.

        Parameters
        ----------
        name : str
            Environment name.
            Default: 'Environment'
        state : array-like
            Time series representing the state of the environment throughout
            time or iterations.
        """

        super().__init__()

        self.name = name
        self.state = state
        self.alpha = alpha
        self._logs = []
        self._agents = {}
        self._objects = []

    def _find_valid_constraints(self, **kwargs):
        """
        Finds any constraitns in `kwargs` where the key matches a column name
        in `self.state` and the value type is `Constraint`.

        This method overrides the default method to handle windspeed
        constraints specifically, interpolating or extrapolating environment
        windspeed profiles to the input constraint height.

        Returns
        -------
        valid : dict
            Valid constraints that apply to a column in `self.state`.
        """

        c = {k: v for k, v in kwargs.items() if isinstance(v, Constraint)}
        constraints = self.resolve_windspeed_constraints(c)

        keys = set(self.state.dtype.names).intersection(
            set(constraints.keys())
        )
        valid = {k: v for k, v in constraints.items() if k in keys}

        return valid

    def resolve_windspeed_constraints(self, constraints):
        """
        Resolves the applied windspeed constraints given the windspeed profiles
        that are present in `self.state`.

        Parameters
        ----------
        constraints : dict
            Dictionary of constraints
        """

        ws = [k for k, _ in constraints.items() if "windspeed" in k]
        if not ws:
            return constraints

        if "windspeed" in self.state.dtype.names:
            if len(ws) > 1:
                raise ValueError(
                    "Multiple constraints applied to the 'windspeed' column."
                )

            v = constraints.pop(ws[0])
            return {**constraints, "windspeed": v}

        for k in ws:
            if k in self.state.dtype.names:
                continue

            val = k.split("_")[1].replace("m", "")
            height = float(val) if "." in val else int(val)
            loc = bisect(self.ws_heights, height)

            if loc == 0:
                self.ws_extrap(self.ws_heights[0], height)

            elif loc == len(self.ws_heights):
                self.ws_extrap(self.ws_heights[-1], height)

            else:
                h1 = self.ws_heights[loc - 1]
                h2 = self.ws_heights[loc]
                self.ws_interp(h1, h2, height)

        return constraints

    @property
    def ws_heights(self):
        """Returns heights of available windspeed profiles."""

        columns = [c for c in self.state.dtype.names if "windspeed" in c]

        heights = []
        for c in columns:
            val = c.split("_")[1].replace("m", "")
            heights.append(float(val) if "." in val else int(val))

        return sorted(heights)

    def ws_interp(self, h1, h2, h):
        """
        TODO
        """

        ts1 = self.state[f"windspeed_{h1}m"]
        ts2 = self.state[f"windspeed_{h2}m"]
        alpha = np.log(ts2.mean() / ts1.mean()) / np.log(h2 / h1)
        print(alpha)
        ts = ts1 * (h / h1) ** alpha

        self.state = np.array(append_fields(self.state, f"windspeed_{h}m", ts))

    def ws_extrap(self, h1, h):
        """
        TODO
        """

        ts1 = self.state[f"windspeed_{h1}m"]
        if h > h1:
            ts = ts1 * (h / h1) ** self.alpha

        else:
            ts = ts1 / ((h1 / h) ** self.alpha)

        self.state = np.array(append_fields(self.state, f"windspeed_{h}m", ts))
