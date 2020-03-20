"""ORBIT specific marmot.Environment."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from marmot import Environment
from marmot._core import Constraint


class OrbitEnvironment(Environment):
    """ORBIT Specific Environment."""

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

        _constraints = {
            k: v for k, v in kwargs.items() if isinstance(v, Constraint)
        }
        ws = {}
        valid = {}

        for k, v in _constraints.items():
            if "windspeed" in k:
                ws[k] = v

            elif k in self.state.dtype.names:
                valid[k] = v

        valid = {**valid, **self.resolve_windspeed_constraints(ws)}
        return valid

    def resolve_windspeed_constraints(self, ws):
        """
        Resolves the applied windspeed constraints given the windspeed profiles
        that are present in `self.state`.

        Parameters
        ----------
        ws : dict
            Windspeed constraints in the format: `'windspeed_###m': Constraint`

        Returns
        -------
        valid_ws : dict
            Valid windspeed constraints.
        """

        if "windspeed" in self.state.dtype.names:
            if len(ws) > 1:
                raise ValueError(
                    "Multiple windspeed constraints applied to "
                    "the 'windspeed' column."
                )

            return {"windspeed": v for _, v in ws.items()}

    @property
    def windspeed_heights(self):
        """Returns heights of available windspeed profiles."""

        columns = [c for c in self.state.dtype.names if "windspeed" in c]
        return [float(c.split("_")[1].replace("m", "")) for c in columns]
