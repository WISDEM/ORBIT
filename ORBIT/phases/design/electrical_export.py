__author__ = []
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = ""
__email__ = []


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
        # "export_system": {
        #     "cable": {
        #         "linear_density": "t/km",
        #         "sections": [("length, km", "speed, km/h (optional)")],
        #         "number": "int (optional)",
        #     },
        # },
    }

    def __init__(self, config, **kwargs):
        """Creates an instance of `TemplateDesign`."""

        config = self.initialize_library(config, **kwargs)
        self.config = self.validate_config(config)

        self._outputs = {}
        self._export_design = self.config["export_system_design"]
        self.initialize_cables()

    def run(self):
        """Main run function."""

        self.example_computation()

    def example_computation(self):
        """Example computation method."""

        depth = self.config["site"]["depth"]
        var2 = self.config.get("optional_input", "default")

        self.result = var1 + var2
        self._outputs["example_output"] = self.result

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
