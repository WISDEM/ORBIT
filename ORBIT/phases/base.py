"""Provides the `BasePhase` class."""

__author__ = ["Jake Nunemaker", "Rob Hammond"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from abc import ABC, abstractmethod
from copy import deepcopy

from benedict import benedict

from ORBIT.core.library import initialize_library, extract_library_data
from ORBIT.core.defaults import common_costs
from ORBIT.core.exceptions import MissingInputs


class BasePhase(ABC):
    """
    Base Phase Class.

    This class is not intended to be instantiated, but define the required
    interfaces for all phases defined by subclasses. Many of the methods below
    should be overwritten in subclasses.

    Methods
    -------
    run()
        Runs the required internal methods to complete the phase. Should be
        implemented in each subclass.
    """

    def initialize_library(self, config, **kwargs):
        """
        Initializes the library if a path is given.

        Parameters
        ----------
        config : dict
            Configuration dictionary.
        library_path : str
            Path to the data library.
        """

        initialize_library(kwargs.get("library_path", None))
        return extract_library_data(config)

    def extract_phase_kwargs(self, **kwargs):
        """Consistent handling of kwargs for Phase and subclasses."""

        phase_name = kwargs.get("phase_name", None)
        if phase_name is not None:
            self.phase = phase_name

    @classmethod
    def _check_keys(cls, expected, config):
        """
        Basic recursive key check.

        Parameters
        ----------
        expected : dict
            Expected config.
        config : dict
            Possible phase_config.
        """

        missing = []

        for k, v in expected.items():

            if isinstance(k, str) and "variable" in k:
                continue

            if isinstance(v, str) and "optional" in v:
                continue

            if isinstance(v, dict):
                c = config.get(k, {})
                if not isinstance(c, dict):
                    raise TypeError(f"'{k}' must be type 'dict'.")

                _m = cls._check_keys(v, c)
                m = [f"{k}.{i}" for i in _m]
                missing.extend(m)
                continue

            c = config.get(k, None)
            if c is None:
                missing.append(k)

        return missing

    def validate_config(self, config):
        """
        Validates `config` against `self.expected_config`.

        Parameters
        ----------
        config : dict
            Input config.

        Raises
        ------
        MissingInputs
        """

        expected = deepcopy(getattr(self, "expected_config", None))
        if expected is None:
            raise AttributeError(f"'expected_config' not set for '{self}'.")

        missing = self._check_keys(expected, config)

        if missing:
            raise MissingInputs(missing)

        else:
            return benedict(config)

    def set_default_cost(self, design_name, key, subkey=None):
        """Return the cost value for a key in a design
        dictionary read from common_cost.yaml.
        """

        if (design_dict := common_costs.get(design_name, None)) is None:
            raise KeyError(f"No {design_name} in common_cost.yaml.")

        # expected = deepcopy(getattr(self, "expected_config", None))
        # if expected is None:
        #    raise AttributeError(f"'expected_config' not set for '{self}'.")
        # design_name = deepcopy(getattr(self,
        # f"expected_config.{design_name}"))

        if (cost_value := design_dict.get(key, None)) is None:
            raise KeyError(
                f"{key} not found in [{design_name}] common_costs.yaml."
            )

        if isinstance(cost_value, dict):
            if (sub_cost_value := cost_value.get(subkey, None)) is None:
                raise KeyError(
                    f"{subkey} not found in [{design_name}][{cost_value}]"
                    " common_costs."
                )

            return sub_cost_value

        else:
            return cost_value

    @abstractmethod
    def run(self):
        """Main run function for phase."""

        pass
