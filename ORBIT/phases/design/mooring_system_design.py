"""`MooringSystemDesign` and related functionality."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from ORBIT.phases.design import DesignPhase


class MooringSystemDesign(DesignPhase):
    """Mooring System and Anchor Design."""

    expected_config = {
        "site": {"depth": "float"},
        "turbine": {"turbine_rating": "int | float"},
        "plant": {"num_turbines": "int"},
        "mooring_system_design": {
            "num_lines": "int | float (optional)",
            "anchor_type": "str (optional)",
            "mooring_line_cost_rate": "int | float (optional)",
            "drag_embedment_fixed_length": "int | float (optional)",
        },
    }

    output_config = {"mooring": {"anchor_type": "str", "lines": "int"}}

    def __init__(self, config, **kwargs):
        """
        Creates an instance of MooringSystemDesign.

        Parameters
        ----------
        config : dict
        """

        config = self.initialize_library(config, **kwargs)
        self.config = self.validate_config(config)
        self.num_turbines = self.config["plant"]["num_turbines"]
        self._design = self.config.get("mooring_system_design", {})
        self.num_lines = self._design.get("num_lines", 4)
        self.extract_defaults()
        self._outputs = {}

    def run(self):
        """
        Main run function.
        """

        self.determine_mooring_line()
        self.calculate_breaking_load()
        self.calculate_line_length()
        self.calculate_anchor_cost()

    def determine_mooring_line(self):
        """
        Returns the diameter of the mooring lines based on the turbine rating.
        """

        tr = self.config["turbine"]["turbine_rating"]
        fit = -0.0004 * (tr ** 2) + 0.0132 * tr + 0.0536

        if fit <= 0.09:
            self.line_diam = 0.09
            self.line_cost_rate = 399.0

        elif fit <= 0.12:
            self.line_diam = 0.12
            self.line_cost_rate = 721.0

        else:
            self.line_diam = 0.15
            self.line_cost_rate = 1088.0

    def calculate_breaking_load(self):
        """
        Returns the mooring line breaking load.
        """

        self.breaking_load = (
            419449 * (self.line_diam ** 2) + 93415 * self.line_diam - 3577.9
        )

    def calculate_line_length(self):
        """
        Returns the mooring line length.
        """

        depth = self.config["site"]["depth"]
        fixed = self._design.get("drag_embedment_fixed_length", 0.5)
        self.line_length = (
            0.0002 * (depth ** 2) + 1.264 * depth + 47.776 + fixed
        )

    def calculate_anchor_cost(self):
        """
        Returns the cost of drag embedment anchors.
        """

        self.anchor_cost = self.breaking_load / 9.81 / 20.0 * 2000.0

    def calculate_total_cost(self):
        """
        Returns the total cost of the mooring system.
        """

        return (
            self.num_lines
            * self.num_turbines
            * (self.anchor_cost + self.line_length * self.line_cost_rate)
        )

    @property
    def design_result(self):
        """
        TODO:
        """

        return {
            "num_lines": self.num_lines,
            "line_length": self.line_length,
            "anchor_cost": self.anchor_cost,
            "total_cost": self.calculate_total_cost(),
        }

    @property
    def total_phase_cost(self):
        """Returns total phase cost in $USD."""

        _design = self.config.get("monopile_design", {})
        design_cost = _design.get("design_cost", 0.0)
        material_cost = sum([v for _, v in self.material_cost.items()])

        return design_cost + material_cost

    @property
    def total_phase_time(self):
        """Returns total phase time in hours."""

        _design = self.config.get("monopile_design", {})
        phase_time = _design.get("design_time", 0.0)
        return phase_time

    @property
    def detailed_output(self):
        """Returns detailed phase information."""

        return {}
