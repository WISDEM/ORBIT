__author__ = []
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = ""
__email__ = []

import numpy as np

from ORBIT.core.library import extract_library_specs
from ORBIT.phases.design import DesignPhase

INPUTS = {}


class ElectricalDesign(DesignPhase):
    """Template Design Phase"""

    expected_config = {
        "site": {"depth": "m"},
        "plant": {"num_turbines": "int", "capacity": "MW"},
        "turbine": {"turbine_rating": "MW"},
        "new_electrical_inputs": {"inputa": "optional", "inputb": "optional"},
        "export_system_design": {
            "cables": "str",
            "num_redundant": "int (optional)",
            "touchdown_distance": "m (optional, default: 0)",
            "percent_added_length": "float (optional)",
        },
    }

    output_config = {
        # "offshore_substation_topside": {
        #     "deck_space": "m2",
        #     "mass": "t",
        #     "unit_cost": "USD",
        # },
        # "offshore_substation_substructure": {
        #     "type": "Monopile",
        #     "deck_space": "m2",
        #     "mass": "t",
        #     "length": "m",
        #     "unit_cost": "USD",
        # },
        
        # "offshore_substation_electrical":{
        #     "switchgear": "int",
        #     "compensation": "int",
        #     "transformer": "int",
            
            
        # },
        
        "export_system": {
            "cable": {
                "linear_density": "t/km",
                "sections": [("length, km", "speed, km/h (optional)")],
                "number": "int (optional)",
                "diameter": "int",
            },
        },
    }

    def __init__(self, config, **kwargs):
        """Creates an instance of `TemplateDesign`."""

        config = self.initialize_library(config, **kwargs)
        self.config = self.validate_config(config)

        self._plant_capacity = self.config["plant"]["capacity"]
        # self.max_cable_capacity = 181.5 # MW , 220kV * 825A
        self._export_design = self.config["export_system_design"]
        self.initialize_cables()

    def run(self):
        """Main run function."""

        self.initialize_cables()
        self.cable = self.cables[[*self.cables][0]]
        self.compute_number_cables()
        self.compute_cable_diameter()
        self.compute_cable_length()
        
    def compute_number_cables(self):
        """
        Calculate the total number of required and redundant cables to
        transmit power to the onshore interconnection.
        """

        num_required = np.ceil(self._plant_capacity / self.cable.cable_power)
        num_redundant = self._design.get("num_redundant", 0)

        self.num_cables = int(num_required + num_redundant)
        
    def compute_cable_current(self):
        """Computes cable diameter."""
        
        cable_cap = self._plant_capacity / self.num_cables
        self.cable_current = cable_cap / self.cable.rated_voltage  # cable_voltage
        
        # Using line of best fit
        # self.cable_diameter = 36.958 * np.exp(0.004 * cable_current)
     
    def compute_cable_length(self):
        """
        Calculates the total distance an export cable must travel.
        """

        added_length = 1.0 + self._design.get("percent_added_length", 0.0)
        self.length = round(
            (
                self.free_cable_length
                + (self._distance_to_landfall - self.touchdown / 1000)
                + self._distance_to_interconnection
            )
            * added_length,
            10,
        )
        
    def compute_oss_electrical_components(self):
        """"Computes number of offshore substation electrical components."""
        
        self.num_switchgear = self.num_cables * 2
        
        # dependent on plant capacity
        self.num_transformers = int
        self.num_compensation = int


    def initialize_cables(self):

        self.cable = extract_library_specs(
            "cables", self._export_design["cables"]
        )
        
    

    @property
    def detailed_output(self):
        """Returns detailed output dictionary."""

        return {"example_detailed_output": self.result}

    @property
    def total_cost(self):
        """Returns total cost of subcomponent(s)."""

        num_turbines = 100  # Where applicable
        return self.result * num_turbines

    @property
    def design_result(self):
        """Must match `self.output_config` structure."""

        return {"example_output": self.result}
