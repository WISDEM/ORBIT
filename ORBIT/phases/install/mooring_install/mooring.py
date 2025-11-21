"""Installation strategies for mooring systems."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from marmot import process

from ORBIT.core import Cargo
from ORBIT.core.logic import position_onsite, get_list_of_items_from_port
from ORBIT.core.defaults import process_times as pt
from ORBIT.phases.install import InstallPhase
from ORBIT.core.exceptions import ItemNotFound


class MooringSystemInstallation(InstallPhase):
    """Module to model the installation of mooring systems at sea."""

    phase = "Mooring System Installation"
    capex_category = "Mooring System"

    #:
    expected_config = {
        "mooring_install_vessel": "dict | str",
        "site": {"depth": "m", "distance": "km"},
        "plant": {"num_turbines": "int"},
        "mooring_system_design": {
            "installation_method": "str (optional, default: 'standard')"
        },
    }

    def __init__(self, config, weather=None, **kwargs):
        """
        Creates an instance of `MooringSystemInstallation`.

        Parameters
        ----------
        config : dict
            Simulation specific configuration.
        weather : np.array
            Weather data at site.
        """

        super().__init__(weather, **kwargs)

        config = self.initialize_library(config, **kwargs)
        self.config = self.validate_config(config)

        self.setup_simulation(**kwargs)

    def setup_simulation(self, **kwargs):
        """
        Sets up the required simulation infrastructure:
            - initializes port
            - initializes installation vessel
            - initializes mooring systems at port.
        """

        depth = self.config["site"]["depth"]
        distance = self.config["site"]["distance"]

        self.num_lines = self.config["mooring_system"]["num_lines"]
        self.num_anchors = self.config["mooring_system"].get("num_anchors", self.num_lines)

        self.line_cost = self.config["mooring_system"]["line_cost"]
        self.anchor_cost = self.config["mooring_system"]["anchor_cost"]
        self.system_cost = self.config["mooring_system"]["system_cost"]
        self.design_class = self.config["mooring_system"]["design_class"]
        
        # Get installation method from config, default to 'standard'
        self.installation_method = self.config.get("mooring_system_design", {}).get(
            "installation_method", "standard"
        )

        self.initialize_port()
        self.initialize_installation_vessel()
        self.initialize_components()

        if self.installation_method == 'standard':
            # Install complete mooring systems
            install_mooring_systems(
                self.vessel,
                self.port,
                distance,
                depth,
                self.num_systems,
                **kwargs,
            )

        elif self.installation_method == 'sequential':
            # Install all anchors first, then all mooring lines
            install_all_anchors_then_moorings(
                self.vessel, self.port, distance, depth, 
                self.num_anchors, self.num_lines, **kwargs
            )

    @property
    def system_capex(self):
        """Returns total procurement cost of all mooring systems."""
        return self.system_cost

    def initialize_installation_vessel(self):
        """Initializes the mooring system installation vessel."""

        vessel_specs = self.config.get("mooring_install_vessel", None)
        name = vessel_specs.get("name", "Mooring System Installation Vessel")

        vessel = self.initialize_vessel(name, vessel_specs)
        self.env.register(vessel)

        vessel.initialize()
        vessel.at_port = True
        vessel.at_site = False
        self.vessel = vessel

    def initialize_components(self):
        """Initializes the Cargo components at port."""        
        
        if self.installation_method == 'standard':
            # Standard installation: load complete mooring systems

            self.num_systems = self.config["plant"]["num_turbines"]

            if self.design_class == 'standard':
                # MooringSystemDesign
                system = MooringSystem(**self.config["mooring_system"])
                for _ in range(self.num_systems):
                    self.port.put(system)

            elif self.design_class == 'custom':
                # CustomMooringSystemDesign
                for i in range(self.num_systems):
                    system = MooringSystem(i, **self.config["mooring_system"])
                    self.port.put(system)
        
        elif self.installation_method == 'sequential':
            # Sequential installation: load all anchors, then all mooring lines

            if self.design_class == 'standard':
                # MooringSystemDesign
                raise ValueError("Sequential installation method is not compatible with the standard mooring design. ")
            
            elif self.design_class == 'custom':
                # CustomMooringSystemDesign
                for i in range(self.num_anchors):
                    anchor = Anchor(i, **self.config["mooring_system"])
                    self.port.put(anchor)
                
                for i in range(self.num_lines):
                    mooring = Mooring(i, **self.config["mooring_system"])
                    self.port.put(mooring)
        
        else:
            raise ValueError(
                f"Installation method '{self.installation_method}' not recognized. "
                "Valid options: 'standard', 'sequential'"
            )


    @property
    def detailed_output(self):
        """Detailed outputs of the scour protection installation."""

        outputs = {self.phase: {**self.agent_efficiencies}}

        return outputs


@process
def install_mooring_systems(vessel, port, distance, depth, systems, **kwargs):
    """
    Logic for the Mooring System Installation Vessel.

    Parameters
    ----------
    vessel : Vessel
        Mooring System Installation Vessel
    port : Port
    distance : int | float
        Distance between port and site (km).
    systems : int
        Total systems to install.
    """

    n = 0
    while n < systems:
        if vessel.at_port:
            try:
                # Get mooring systems from port.
                yield get_list_of_items_from_port(
                    vessel,
                    port,
                    ["MooringSystem"],
                    **kwargs,
                )

            except ItemNotFound:
                # If no items are at port and vessel.storage.items is empty,
                # the job is done
                if not vessel.storage.items:
                    vessel.submit_debug_log(
                        message="Item not found. Shutting down."
                    )
                    break

            # Transit to site
            vessel.update_trip_data()
            vessel.at_port = False
            yield vessel.transit(distance)
            vessel.at_site = True

        if vessel.at_site:

            if vessel.storage.items:

                system = yield vessel.get_item_from_storage(
                    "MooringSystem", **kwargs
                )
                for _ in range(system.num_lines):
                    yield position_onsite(vessel, **kwargs)
                    yield perform_mooring_site_survey(vessel, **kwargs)
                    yield install_mooring_anchor(
                        vessel,
                        depth,
                        system.anchor_type,
                        **kwargs,
                    )
                    yield install_mooring_line(vessel, depth, **kwargs)

                n += 1

            else:
                # Transit to port
                vessel.at_site = False
                yield vessel.transit(distance)
                vessel.at_port = True

    vessel.submit_debug_log(message="Mooring systems installation complete!")


@process
def install_all_anchors_then_moorings(vessel, port, distance, depth, nanchors, nmoorings, **kwargs):
    """
    Logic for mooring system installation - to install all anchors first

    Parameters
    ----------
    vessel : Vessel
        Mooring System Installation Vessel
    port : Port
    distance : int | float
        Distance between port and site (km).
    nanchors : int
        Total number of anchors to install.
    """

    n = 0
    while n < nanchors:
        if vessel.at_port:
            try:
                # Get anchors from port.
                yield get_list_of_items_from_port(
                    vessel,
                    port,
                    ["Anchor"],
                    **kwargs,
                )

            except ItemNotFound:
                # If no items are at port and vessel.storage.items is empty,
                # the job is done
                if not vessel.storage.items:
                    vessel.submit_debug_log(
                        message="Item not found. Shutting down."
                    )
                    break

            # Transit to site
            vessel.update_trip_data()
            vessel.at_port = False
            yield vessel.transit(distance)
            vessel.at_site = True

        if vessel.at_site:

            if vessel.storage.items:

                anchor = yield vessel.get_item_from_storage(
                    "Anchor", **kwargs
                )

                yield position_onsite(vessel, **kwargs)
                yield perform_mooring_site_survey(vessel, **kwargs)     # updated to only take 1 hour for 1 inspection of an anchor or mooring line
                yield install_mooring_anchor(
                    vessel,
                    depth,
                    anchor.anchor_type,
                    **kwargs,
                )

                n += 1

            else:
                # Transit to port
                vessel.at_site = False
                yield vessel.transit(distance)
                vessel.at_port = True

    vessel.submit_debug_log(message="Installation of all anchors complete!")


    n = 0
    while n < nmoorings:
        if vessel.at_port:
            try:
                # Get mooring systems from port.
                yield get_list_of_items_from_port(
                    vessel,
                    port,
                    ["Mooring"],
                    **kwargs,
                )

            except ItemNotFound:
                # If no items are at port and vessel.storage.items is empty,
                # the job is done
                if not vessel.storage.items:
                    vessel.submit_debug_log(
                        message="Item not found. Shutting down."
                    )
                    break

            # Transit to site
            vessel.update_trip_data()
            vessel.at_port = False
            yield vessel.transit(distance)
            vessel.at_site = True

        if vessel.at_site:

            if vessel.storage.items:

                mooring = yield vessel.get_item_from_storage(
                    "Mooring", **kwargs
                )

                yield position_onsite(vessel, **kwargs)
                yield perform_mooring_site_survey(vessel, **kwargs)     # updated to only take 1 hour for 1 inspection of an anchor or mooring line
                yield install_mooring_line(vessel, depth, **kwargs)                    

                n += 1

            else:
                # Transit to port
                vessel.at_site = False
                yield vessel.transit(distance)
                vessel.at_port = True

    vessel.submit_debug_log(message="Installation of all mooring lines complete!")


@process
def perform_mooring_site_survey(vessel, **kwargs):
    """
    Calculates time required to perform a mooring system survey.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.

    Yields
    ------
    vessel.task representing time to "Perform Mooring Site Survey".
    """

    key = "mooring_site_survey_time"
    survey_time = kwargs.get(key, pt[key])

    yield vessel.task_wrapper(
        "Perform Mooring Site Survey",
        survey_time,
        constraints=vessel.transit_limits,
        **kwargs,
    )


@process
def install_mooring_anchor(vessel, depth, anchor_type, **kwargs):
    """
    Calculates time required to install a mooring system anchor.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    depth : int | float
        Depth at site (m).
    _type : str
        Anchor type. 'Suction Pile' or 'Drag Embedment'.

    Yields
    ------
    vessel.task representing time to install mooring anchor.
    """

    if anchor_type == "Suction Pile":
        key = "suction_pile_install_time"
        task = "Install Suction Pile Anchor"
        fixed = kwargs.get(key, pt[key])

    elif anchor_type == "Drag Embedment":
        key = "drag_embed_install_time"
        task = "Install Drag Embedment Anchor"
        fixed = kwargs.get(key, pt[key])

    elif anchor_type == "D&G Pile":
        key = "dandg_pile_install_time"
        task = "Install D&G Pile Anchor"
        fixed = kwargs.get(key, pt[key])

    else:
        raise ValueError(
            f"Mooring System Anchor Type: {anchor_type} not recognized.",
        )

    install_time = fixed + 0.005 * depth
    yield vessel.task_wrapper(
        task,
        install_time,
        constraints=vessel.transit_limits,
        **kwargs,
    )


@process
def install_mooring_line(vessel, depth, **kwargs):
    """
    Calculates time required to install a mooring system line.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    depth : int | float
        Depth at site (m).

    Yields
    ------
    vessel.task representing time to install mooring line.
    """

    install_time = 0.005 * depth

    yield vessel.task_wrapper(
        "Install Mooring Line",
        install_time,
        constraints=vessel.transit_limits,
        **kwargs,
    )


class MooringSystem(Cargo):
    """Mooring System Cargo."""

    def __init__(
        self,
        i=None,
        num_lines=None,
        line_mass=None,
        anchor_mass=None,
        anchor_type="Suction Pile",
        **kwargs,
    ):
        """Creates an instance of MooringSystem."""

        # Store design class for use in properties
        self.design_class = kwargs.get('design_class', 'standard')

        if self.design_class == 'standard':
            self.num_lines = num_lines
            self.line_mass = line_mass
            self.anchor_mass = anchor_mass
            self.anchor_type = anchor_type

        elif self.design_class == 'custom':
            # Filter DataFrames for this turbine
            self.chain = kwargs['chains'][kwargs['chains']['turbine_id'] == i]
            self.rope = kwargs['ropes'][kwargs['ropes']['turbine_id'] == i]
            self.anchor = kwargs['anchors'][kwargs['anchors']['turbine_id'] == i]

            # Calculate number of lines for this specific turbine
            self.num_lines = len(self.rope)  # One line per rope
            self.line_mass = self.chain['mass'].sum() + self.rope['mass'].sum()
            self.anchor_mass = self.anchor['mass'].sum()
            
            # Extract anchor type from first anchor's section_id
            first_anchor = self.anchor.iloc[0]
            section_id = first_anchor['section_id'].lower()
            
            if 'suction' in section_id:
                self.anchor_type = 'Suction Pile'
            elif 'dea' in section_id or 'drag' in section_id:
                self.anchor_type = 'Drag Embedment'
            elif 'dandg' in section_id:
                self.anchor_type = 'D&G Pile'
            else:
                raise ValueError(f'Anchor type listed in {section_id} is not supported yet')

        self.deck_space = 0

    @property
    def mass(self):
        """Returns total system mass in t."""

        if self.design_class == 'standard':
            return self.num_lines * (self.line_mass + self.anchor_mass)
        elif self.design_class == 'custom':
            return self.line_mass + self.anchor_mass
        else:
            return self.num_lines * (self.line_mass + self.anchor_mass)

    @staticmethod
    def fasten(**kwargs):
        """Dummy method to work with `get_list_of_items_from_port`."""

        key = "mooring_system_load_time"
        time = kwargs.get(key, pt[key])

        return "Load Mooring System", time

    @staticmethod
    def release(**kwargs):
        """Dummy method to work with `get_list_of_items_from_port`."""

        return "", 0



class Anchor(Cargo):
    """Single Anchor Cargo Component."""

    def __init__(self, i, anchors=None, **kwargs):
        """Creates an instance of MooringSystem."""

        self.anchors = anchors
        anchor = self.anchors.iloc[i]

        anchor_diameter = anchor['diameter']
        anchor_length = anchor['length']
        self.deck_space = (anchor_diameter + 3) * (anchor_length + 3)
    
        # Extract anchor type from section_id
        section_id = anchor['section_id'].lower()
        
        if 'suction' in section_id:
            self.anchor_type = 'Suction Pile'
        elif 'dea' in section_id or 'drag' in section_id:
            self.anchor_type = 'Drag Embedment'
        elif 'dandg' in section_id:
            self.anchor_type = 'D&G Pile'
        else:
            raise ValueError(f'Anchor type in {section_id} is not supported yet')

        self.anchor_mass = anchor['mass']       # [t]
    
    @property
    def mass(self):
        """Returns total system mass in t."""
        return self.anchor_mass

    @staticmethod
    def fasten(**kwargs):
        """Dummy method to work with `get_list_of_items_from_port`."""
        key = "anchor_load_time"
        time = kwargs.get(key, pt["mooring_system_load_time"]/5)
        return "Load Anchor", time

    @staticmethod
    def release(**kwargs):
        """Dummy method to work with `get_list_of_items_from_port`."""
        return "", 0





class Mooring(Cargo):
    """Single Mooring Line Cargo Component."""

    def __init__(self, i, **kwargs):
        """Creates an instance of MooringSystem."""

        # Get all unique (turbine_id, line_id) pairs from the chains dataframe
        unique_pairs = kwargs['chains'][['turbine_id', 'line_id']].drop_duplicates().sort_values(['turbine_id', 'line_id']).reset_index(drop=True)
        
        # Get the i-th pair
        turbine_id = unique_pairs.loc[i, 'turbine_id']
        line_id = unique_pairs.loc[i, 'line_id']
        
        # Filter chains and ropes for this specific turbine and mooring line
        # This gets ALL chain sections for this specific turbine's mooring line
        self.chains = kwargs['chains'][
            (kwargs['chains']['turbine_id'] == turbine_id) & 
            (kwargs['chains']['line_id'] == line_id)
        ]
        self.ropes = kwargs['ropes'][
            (kwargs['ropes']['turbine_id'] == turbine_id) & 
            (kwargs['ropes']['line_id'] == line_id)
        ]

        # Calculate total mass for all chain segments in this line
        self.chain_mass = self.chains['mass'].sum() if len(self.chains) > 0 else 0.0
        self.rope_mass = self.ropes['mass'].sum() if len(self.ropes) > 0 else 0.0

        # Calculate deck space based on total lengths
        chain_total_length = self.chains['length'].sum() if len(self.chains) > 0 else 0.0
        rope_total_length = self.ropes['length'].sum() if len(self.ropes) > 0 else 0.0
        
        self.chain_deck_space = (chain_total_length * 3.28 / 90) * 7.5
        self.rope_deck_space = (6.4 * 4.5) * (rope_total_length / 2020)
        self.deck_space = self.chain_deck_space + self.rope_deck_space
    
    @property
    def mass(self):
        """Returns total system mass in t."""
        return self.chain_mass + self.rope_mass

    @staticmethod
    def fasten(**kwargs):
        """Dummy method to work with `get_list_of_items_from_port`."""
        key = "mooring_line_load_time"
        time = kwargs.get(key, pt["mooring_system_load_time"]/2)
        return "Load Mooring Line", time

    @staticmethod
    def release(**kwargs):
        """Dummy method to work with `get_list_of_items_from_port`."""
        return "", 0



