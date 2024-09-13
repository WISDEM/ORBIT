"""Provides information about what class or functionality is provided."""

__author__ = ["Jake Nunemaker"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = ["jake.nunemaker@nrel.gov"]


import math

from ORBIT.phases.design import DesignPhase


class TemplateDesign(DesignPhase):
    """Template Design Phase."""

    expected_config = {
        "required_input": "unit",
        "optional_input": "unit, (optional, default: 'default')",
    }

    output_config = {"example_output": "unit"}

    def __init__(self, config, **kwargs):
        """Creates an instance of `TemplateDesign`."""

        config = self.initialize_library(config, **kwargs)
        self.config = self.validate_config(config)

        self._outputs = {}

    def run(self):
        """Main run function."""

        self.example_computation()

    def example_computation(self):
        """Example computation method."""

        var1 = self.config["required_input"]
        var2 = self.config.get("optional_input", "default")

        self.result = var1 + var2
        self._outputs["example_output"] = self.result

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


# === Annotated Example ===
class SparDesign(DesignPhase):
    """Spar Design Module."""

    # The expected config tells ProjectManager what inputs are required to run
    # the module. If a input is optional (and has a default value), then flag
    # it with the (optional, default: ###) after the unit. This will make it so
    # that ProjectManager doesn't raise a warning if doesn't find the input in
    # a project level config.
    expected_config = {
        "site": {
            "depth": "m",
        },  # For common inputs that will be shared across many modules,
        "plant": {
            "num_turbines": "int",
        },  # look up how the variable is named in existing modules
        "turbine": {
            "turbine_rating": "MW",
        },  # so the user doesn't have to input the same thing twice. For
        # example, avoid adding 'number_turbines' if 'num_turbines' is already
        # used throughout ORBIT Inputs can be grouped into dictionaries like
        # the following:
        "spar_design": {
            # I tend to group module specific cost rates into dictionaries
            # named after the component being considered eg. spar_design,
            # gbf_design, etc.
            "stiffened_column_CR": "$/t (optional, default: 3120)",
            "tapered_column_CR": "$/t (optional, default: 4220)",
            "ballast_material_CR": "$/t (optional, default: 100)",
            "secondary_steel_CR": "$/t (optional, default: 7250)",
            "towing_speed": "km/h (optional, default: 6)",
        },
    }

    # The output config tells ProjectManager which inputs will be produced by
    # the design module. Design modules are ran first in a project, and the
    # results are used as inputs to installation modules. As such, these output
    # names should match the input names of the respective installation module
    output_config = {
        "substructure": {
            # Typically a design phase ouptuts a component design grouped into
            # a dictionary, eg. "substructure" dict to the left.
            "mass": "t",
            "ballasted_mass": "t",
            "unit_cost": "USD",
            "towing_speed": "km/h",
        },
    }

    def __init__(self, config, **kwargs):
        """
        Creates an instance of `SparDesign`.

        Parameters
        ----------
        config : dict
        """
        # These first two lines are required in all modules. They initialize
        # the library
        config = self.initialize_library(config, **kwargs)

        # if it hasn't already been and validate the config against
        # '.expected_config' from above
        self.config = self.validate_config(config)

        # Not required, but I often save module specific outputs to "_design"
        # for later use. If the "spar_design" sub dictionary isn't found, an
        # empty one is returned to work with later methods.
        self._design = self.config.get("spar_design", {})
        self._outputs = {}

    def run(self):
        """
        Required method that ProjectManager will call after initialization.
        Any calculations should be called from here and the outputs should be
        stored.
        """

        substructure = {
            "mass": self.unballasted_mass,
            "ballasted_mass": self.ballasted_mass,
            "unit_cost": self.substructure_cost,
            "towing_speed": self._design.get("towing_speed", 6),
        }

        self._outputs["substructure"] = substructure

    @property
    def stiffened_column_mass(self):
        """
        Calculates the mass of the stiffened column for a single spar in
        tonnes. From original OffshoreBOS model.
        """

        # The following methods are examples of module specific calculations.
        # Note that they can access the input dictionary at `self.config`

        rating = self.config["turbine"]["turbine_rating"]
        depth = self.config["site"]["depth"]

        mass = 535.93 + 17.664 * rating**2 + 0.02328 * depth * math.log(depth)

        return mass

    @property
    def tapered_column_mass(self):
        """
        Calculates the mass of the atpered column for a single spar in tonnes.
        From original OffshoreBOS model.
        """

        rating = self.config["turbine"]["turbine_rating"]

        mass = 125.81 * math.log(rating) + 58.712

        return mass

    @property
    def stiffened_column_cost(self):
        """
        Calculates the cost of the stiffened column for a single spar. From
        original OffshoreBOS model.
        """

        # This is how I typically handle outputs. This will look for the key in
        # self._design, and return default value if it isn't found.
        cr = self._design.get("stiffened_column_CR", 3120)
        return self.stiffened_column_mass * cr

    @property
    def tapered_column_cost(self):
        """
        Calculates the cost of the tapered column for a single spar. From
        original OffshoreBOS model.
        """

        cr = self._design.get("tapered_column_CR", 4220)
        return self.tapered_column_mass * cr

    @property
    def ballast_mass(self):
        """
        Calculates the ballast mass of a single spar. From original OffshoreBOS
        model.
        """

        rating = self.config["turbine"]["turbine_rating"]
        mass = -16.536 * rating**2 + 1261.8 * rating - 1554.6

        return mass

    @property
    def ballast_cost(self):
        """
        Calculates the cost of ballast material for a single spar. From
        original OffshoreBOS model.
        """

        cr = self._design.get("ballast_material_CR", 100)
        return self.ballast_mass * cr

    @property
    def secondary_steel_mass(self):
        """
        Calculates the mass of the required secondary steel for a single
        spar. From original OffshoreBOS model.
        """

        rating = self.config["turbine"]["turbine_rating"]
        depth = self.config["site"]["depth"]

        mass = math.exp(
            3.58
            + 0.196 * (rating**0.5) * math.log(rating)
            + 0.00001 * depth * math.log(depth),
        )

        return mass

    @property
    def secondary_steel_cost(self):
        """
        Calculates the cost of the required secondary steel for a single
        spar. For original OffshoreBOS model.
        """

        cr = self._design.get("secondary_steel_CR", 7250)
        return self.secondary_steel_mass * cr

    @property
    def unballasted_mass(self):
        """Returns the unballasted mass of the spar substructure."""

        return (
            self.stiffened_column_mass
            + self.tapered_column_mass
            + self.secondary_steel_mass
        )

    @property
    def ballasted_mass(self):
        """Returns the ballasted mass of the spar substructure."""

        return self.unballasted_mass + self.ballast_mass

    @property
    def substructure_cost(self):
        """
        Returns the total cost (including ballast) of the
        spar substructure.
        """

        return (
            self.stiffened_column_cost
            + self.tapered_column_cost
            + self.secondary_steel_cost
            + self.ballast_cost
        )

    # === End of module specific calculations ===

    # The following properties are required methods for a DesignPhase

    # .detailed_output returns any relevant detailed outputs from the module
    # in a dictionary.
    @property
    def detailed_output(self):
        """Returns detailed phase information."""

        _outputs = {
            "stiffened_column_mass": self.stiffened_column_mass,
            "stiffened_column_cost": self.stiffened_column_cost,
            "tapered_column_mass": self.tapered_column_mass,
            "tapered_column_cost": self.tapered_column_cost,
            "ballast_mass": self.ballast_mass,
            "ballast_cost": self.ballast_cost,
            "secondary_steel_mass": self.secondary_steel_mass,
            "secondary_steel_cost": self.secondary_steel_cost,
        }

        return _outputs

    # .total_cost returns the total procurement cost for the subsystem for the
    # entire project.
    @property
    def total_cost(self):
        """Returns total phase cost in $USD."""

        num = self.config["plant"]["num_turbines"]
        return num * self.substructure_cost

    # .design_result returns an output dictionary that includes all of the
    # outputs included in `self.output_config`. This property is called by
    # ProjectManager and used to add the results of design phases to the
    # total project configuration.
    @property
    def design_result(self):
        """Returns the result of `self.run()`."""

        if not self._outputs:
            raise Exception("Has `SparDesign` been ran yet?")

        return self._outputs
