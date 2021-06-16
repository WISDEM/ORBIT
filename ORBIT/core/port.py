"""Provides the `Port` class."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


import simpy


class Port:
    """Port Class"""

    def __init__(self, env, num_cranes=1, **kwargs):
        """
        Creates an instance of Port.

        Parameters
        ----------
        env : simpy.Environment
            SimPy environment that simulation runs on.
        """

        self.env = env
        self.crane = simpy.Resource(self.env, num_cranes)


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
