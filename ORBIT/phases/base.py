"""Provides the `BasePhase` class."""

__author__ = ["Jake Nunemaker", "Rob Hammond"]
__copyright__ = "Copyright 2019, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


import os
from abc import ABC, abstractmethod

from ORBIT.library import initialize_library, extract_library_data


class BasePhase(ABC):
    """
    Base Phase Class.

    This class is not intended to be instantiated, but define the required
    interfaces for all phases defined by subclasses. Many of the methods below
    should be overwritten in subclasses.

    Attributes
    ----------
    phase : str
        Name of the phase that is being used.
    total_phase_cost : float
        Calculates the total phase cost. Should be implemented in each subclass.
    detailed_output : dict
        Creates the detailed output dictionary. Should be implemented in each
        subclass.
    phase_dataframe : pd.DataFrame

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
        """
        Consistent handling of kwargs for Phase and subclasses.
        """

        phase_name = kwargs.get("phase_name", None)
        if phase_name is not None:
            self.phase = phase_name

    @abstractmethod
    def run(self):
        """Main run function for phase."""

        pass

    @property
    @abstractmethod
    def total_phase_cost(self):
        """Returns total phase cost in $USD."""

        pass

    @property
    @abstractmethod
    def total_phase_time(self):
        """Returns total phase time in hours."""

        pass

    @property
    @abstractmethod
    def detailed_output(self):
        """Returns detailed phase information."""

        pass
