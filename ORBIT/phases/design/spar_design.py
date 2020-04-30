"""Provides the `SparDesign` class (from OffshoreBOS)."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from ORBIT.phases.design import DesignPhase


class SparDesign(DesignPhase):
    """Spar Substructure Design"""

    expected_config = {}

    def __init__(self, config, **kwargs):
        """
        Creates an instance of SparDesign.

        Parameters
        ----------
        config : dict
        """

        config = self.initialize_library(config, **kwargs)
        self.config = self.validate_config(config)
        self.extract_defaults()
        self._outputs = {}

    def run(self):
        """Main run function."""

        pass
