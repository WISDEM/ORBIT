"""Mooring System Supply Chain Module."""

import simpy
import pandas as pd
from marmot import process

from ORBIT.phases.install import InstallPhase

from .common import (  # RopeAssemblyLine,; AnchorAssemblyLine,
    Transport,
    DryStorage,
    LaydownArea,
    ChainAssemblyLine,
)
from .components import (  # RopeProduction,; AnchorProduction,
    Component,
    ComponentManufacturing,
    transport_component_to_port,
)

import numpy as np


class MooringSystemSupplyChain(InstallPhase):
    """
    The MooringSystemSupplyChain class is an upstream process that is treated
    as an installation phase. Its purpose is to evaluate and test the impact of
    different production parameters on the full installation of the
    MooringSystem().

    Adapted and informed by "Floating Study" - Jake Nunemaker and Matt Shields.
    """

    phase = "Mooring System Supply Chain"

    expected_config = {
        "port": {
            "laydown_area": "m2",
        },
        "mooring_system": {
            "num_lines": "int",
            "line_cost": "int | float ",
            "system_cost": "int | float ",
        },
    }

    def __init__(self, config, weather=None, **kwargs):
        """Create an instance of MooringSystemSupplyChain."""

        super().__init__(weather, **kwargs)

        config = self.initialize_library(config, **kwargs)
        self.config = self.validate_config(config)

        self.num_turbines = self.config["plant"]["num_turbines"]

        self.mooring_system = self.config["mooring_system"]

        try:
            self.num_lines = self.mooring_system["num_lines"]
        except KeyError:
            self.num_lines = 1

        self.chain_supply = self.config.get("chain_supply", {})
        self.anchor_supply = self.config.get("anchor_supply", {})
        self.rope_supply = self.config.get("rope_supply", {})

        self.setup_simulation(**kwargs)

    def setup_simulation(self, **kwargs):
        """Setup simulation."""
        # Initialize port laydown area
        self.initialize_laydown_area()

        # Initialize Chain storage, production, and delivery
        self.initialize_chain_storage()
        self.initialize_chain_production()
        self.initialize_chain_transport()

        # Initialize Anchor storage, production, and delivery
        self.initialize_anchor_storage()
        self.initialize_anchor_production()
        self.initialize_anchor_transport()

        # Initialize Rope storage, production, and delivery
        self.initialize_rope_storage()
        self.initialize_rope_production()
        self.initialize_rope_transport()

        # At marshalling port
        # self.initialize_chain_assembly()
        # start assembly lines
        # self.start_assembly_lines()

    def initialize_laydown_area(self):
        """Initialize the laydown area at port."""

        area = self.config["port"]["laydown_area"]
        perc = self.config["port"]["assembly_start"]
        self._laydown_cost = self.config["port"]["laydown_cost"] * area
        assert 0 <= perc <= 0.9

        starting_buffer = (
            max(
                [
                    self.config["substructure_delivery"]["space_required"],
                    self.config["turbine_delivery"]["space_required"],
                ]
            )
            + 1
        )

        start = area * perc
        self.laydown = LaydownArea(self.env, area, start, starting_buffer)
        # print(vars(self.laydown))
        self.laydown.start_assembly = simpy.Event(self.env)

        # print("Laydown Vars:", vars(self.laydown))

    def initialize_chain_storage(self):
        """Chain Storage near Production line."""

        # TODO: Make chain storage area constrained instead of integer items.
        # TODO: Check or throw warnings based on area or mass?

        # Option A: Per unit storage
        try:
            storage = self.chain_supply["capacity"]

        except KeyError:
            storage = float("Inf")

        self.chain_storage = DryStorage(self.env, storage)

        # Option B: Per area storage
        # area = self.config["chain_supply"]["laydown_area"]
        # perc = self.config["port"]["assembly_start"]
        # self._laydown_cost = self.config["port"]["laydown_cost"] * area
        # assert 0 <= perc <= 0.9

        # starting_buffer = (
        #    max(
        #        [
        #            self.config["substructure_delivery"]["space_required"],
        #            self.config["turbine_delivery"]["space_required"],
        #        ]
        #    )
        #    + 1
        # )

        # start = area * perc
        # self.chain_storage = LaydownArea(self.env, area, start,
        # starting_buffer)
        # self.chain_storage.start_assembly = simpy.Event(self.env)

    def initialize_chain_transport(self):
        """Initialize the chain transport agent using vessel logic."""

        transport_specs = self.config.get("transport_railcar", None)
        # print(transport_specs)

        name = transport_specs.get("name", "Chain Transport Railcar")

        transit_time = self.chain_supply.get("transit_time", 0)

        transport = Transport(name, transport_specs)
        self.env.register(transport)
        transport.initialize()

        # print("Transport vars: ", vars(transport))
        self.chain_transport = transport

        transport_component_to_port(
            self.chain_transport,
            #sets=len(self.chains),
            sets=len([component for chain_set in self.chains for component in chain_set]),  # regroup after assembly lines
            feed=self.chain_storage,
            target=self.laydown,
            transit_time=transit_time,
            component="Chain",
            #    transit_constraints={},
        )

    def initialize_chain_production(self):
        """Initialize the chain production line and delivery to port."""

        takt = self.chain_supply.get("takt_time", 5.6)
        takt_day_rate = self.chain_supply.get("takt_day_rate", 0)

        reset_trigger = self.chain_supply.get("reset_trigger", 0.0254)
        reset_time = self.chain_supply.get("reset_time", 0.5)

        #import_size = self.chain_supply.get("import_size", 0.127 ) #    set to the current domestic manufacturing limit to simluate international procurement
        import_size = self.chain_supply.get("import_size", 0.220 ) #    set to a high number to include all chain diameters

        chain_makers = int(
            self.chain_supply["assembly_lines"]  # simplifying asumption
        )

        # Get a dataframe of components and make a list of objects w/ attrs
        chains_df = self.mooring_system["chains"]

        try:
            _area = chains_df["area"]

        except KeyError:
            _area = self.chain_supply["space_required"]
            chains_df["area"] = chains_df["length"] * 7.5 * (3.28/90)
        

        domestic_chain = chains_df[chains_df['diameter'] <= import_size]
        domestic_chain = domestic_chain.sort_values(by='diameter')      # automatically sort the chain diameters by size
        
        international_chain = chains_df[chains_df['diameter'] > import_size]


        # organize anchor components into a list of lists based on the number of lines
        self.chains = self.split_into_assembly_lines(chains_df, n=chain_makers)

        '''
        self.itl_chains = [Component(
                row["turbine_id"],
                row["line_id"],
                row["section_id"],
                row["diameter"],
                row["length"],
                row["mass"],
                row["thickness"],
                row["cost_rate"],
                _area,
            )
            for _, row, in international_chain.iterrows()
        ]
        '''

        # print("Internationally sourced chains: ", self.itl_chains)
        # print(f"Number of chains: {len(self.chains)}")
        # print(vars(self.chains[1]))

        for n in range(chain_makers):
            chain_manufacturer = ComponentManufacturing(
                component="Chain",
                num=n + 1,
                area=self.config["chain_supply"]["space_required"],
                sets=self.chains[n],    # include each sublist of components for each chain manufacturer
                takt_time=takt,
                takt_day_rate=takt_day_rate,
                target=self.chain_storage,
                reset=reset_trigger,
                reset_time=reset_time,
            )

            self.env.register(chain_manufacturer)
            chain_manufacturer.start()

    def initialize_rope_storage(self):
        """Initialize the rope storage near production line."""

        # TODO: Make chain storage area constrained instead of integer items.
        # TODO: Check or throw warnings based on area or mass?

        # Option A: Per unit storage
        try:
            storage = self.config["rope_supply"]["capacity"]

        except KeyError:
            storage = float("Inf")

        self.rope_storage = DryStorage(self.env, storage)

    def initialize_rope_production(self):
        """Initialize the rope production line and delivery to port."""

        takt = self.rope_supply.get("takt_time", 182.5)
        takt_day_rate = self.rope_supply.get("takt_day_rate", 0)

        reset_trigger = self.rope_supply.get("reset_trigger", 0.0254)
        reset_time = self.rope_supply.get("reset_time", 0.5)

        rope_makers = int(
            # self.config["substructure_delivery"].get("num_lines", 1)
            self.rope_supply["assembly_lines"]  # simplifying asumption
        )

        # Get a dataframe of components and make a list of objects w/ attrs
        ropes_df = self.mooring_system["ropes"]

        try:
            _area = ropes_df["area"]

        except KeyError:
            _area = self.rope_supply["space_required"]

        self.ropes = [
            Component(
                row["turbine_id"],
                row["line_id"],
                row["section_id"],
                row["diameter"],
                row["length"],
                row["mass"],
                row["thickness"],
                row["cost_rate"],
                _area,
            )
            for _, row, in ropes_df.iterrows()
        ]

        # print(f"Number of ropes: {len(self.ropes)}")
        # print(vars(self.ropes[3]))

        # Loop through number of assembly lines. 1 anchor line won't cut it.
        for n in range(rope_makers):
            rope_manufacturer = ComponentManufacturing(
                component="Ropes",
                num=n + 1,
                area=self.rope_supply["space_required"],
                sets=self.ropes,
                takt_time=takt,
                takt_day_rate=takt_day_rate,
                target=self.rope_storage,
                reset=reset_trigger,
                reset_time=reset_time,
            )

            self.env.register(rope_manufacturer)
            rope_manufacturer.start()

    def initialize_rope_transport(self):
        """Initialize the rope transport agent using vessel logic."""

        transport_specs = self.config.get("transport_railcar", None)

        name = transport_specs.get("name", "Rope Transport Railcar")

        transit_time = self.anchor_supply.get("transit_time", 168)

        transport = Transport(name, transport_specs)
        self.env.register(transport)
        transport.initialize()

        # print("Rope Transport vars: ", vars(transport))
        self.rope_transport = transport

        transport_component_to_port(
            self.rope_transport,
            sets=len(self.ropes),
            feed=self.rope_storage,
            target=self.laydown,
            transit_time=transit_time,
            component="Rope",
            #    transit_constraints={},
        )

    def initialize_anchor_storage(self):
        """Initialize the anchor storage near production line."""

        # TODO: Make chain storage area constrained instead of integer items.
        # TODO: Check or throw warnings based on area or mass?

        # Option A: Per unit storage
        try:
            storage = self.config["anchor_supply"]["capacity"]

        except KeyError:
            storage = float("Inf")

        self.anchor_storage = DryStorage(self.env, storage)

    def initialize_anchor_production(self):
        """Initialize the anchor production line and delivery to port."""

        takt = self.anchor_supply.get("takt_time", 182.5)
        takt_day_rate = self.anchor_supply.get("takt_day_rate", 0)

        reset_trigger = self.anchor_supply.get("reset_trigger", 0.3048)
        reset_time = self.anchor_supply.get("reset_time", 0.5)

        anchor_bays = int(
            # self.config["substructure_delivery"].get("num_lines", 1)
            self.anchor_supply["assembly_lines"]  # simplifying asumption
        )

        # Get a dataframe of components and make a list of objects w/ attrs
        anchors_df = self.mooring_system["anchors"]

        # print(anchors_df)
        try:
            _area = anchors_df["area"]

        except KeyError:
            anchors_df["area"] = (10 + anchors_df["diameter"] / 1e3) * (
                10 + anchors_df["length"]
            )
    

        # organize anchor components into a list of lists based on the number of lines
        self.anchors = self.split_into_assembly_lines(anchors_df, n=anchor_bays)

        
        # print(f"Number of anchors: {len(self.anchors)}")
        # print(vars(self.anchors[5]))
        '''
        # TODO: Finish the split logic
        if anchor_bays > 1:
            k, m = divmod(len(self.anchors), anchor_bays)
            anchor_set = [
                self.anchors[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)]
                for i in range(anchor_bays)
            ]
        else:
            anchor_set = self.anchors
        '''
        #print("Anchor sets: ", type(anchor_set))

        #self.anchor_sets = []

        # Loop through number of assembly lines. 1 anchor line won't cut it.
        for n in range(anchor_bays):
            anchor_manufacturer = ComponentManufacturing(
                component="Anchors",
                num=n + 1,
                area=self.anchor_supply["space_required"],
                sets=self.anchors[n],    # include each sublist of components for each anchor manufacturer
                takt_time=takt,
                takt_day_rate=takt_day_rate,
                target=self.anchor_storage,
                reset=reset_trigger,
                reset_time=reset_time,
            )

            self.env.register(anchor_manufacturer)
            anchor_manufacturer.start()

    def initialize_anchor_transport(self):
        """Initialize the anchor transport agent using vessel logic."""

        transport_specs = self.config.get("transport_vessel", None)
        # print(transport_specs)

        name = transport_specs.get("name", "Anchor Transport Vessel")

        transit_time = self.anchor_supply.get("transit_time", 0)

        transport = Transport(name, transport_specs)
        self.env.register(transport)
        transport.initialize()

        # print("Anchor Transport vars: ", vars(transport))
        self.anchor_transport = transport

        transport_component_to_port(
            self.anchor_transport,
            #sets=len(self.anchors),
            sets=len([component for anchor_set in self.anchors for component in anchor_set]),   # regroup after assembly lines
            feed=self.anchor_storage,
            target=self.laydown,
            transit_time=transit_time,
            component="Anchor",
            #    transit_constraints={},
        )

    def initialize_chain_assembly(self):
        """Initialize the production of chain.

        self.config["chain_supply"]["takt_time"]
        self.config["chain_supply"]["chain_storage]

        """

        try:
            storage = self.config["chain_supply"]["chain_storage"]

        except KeyError:
            storage = float("Inf")

        self.chain_storage = DryStorage(self.env, storage)

        try:
            time = self.config["chain_supply"]["takt_time"]

        except KeyError:
            time = 0

        try:
            lines = self.config["chain_suppl"]["chain_assembly_lines"]

        except KeyError:
            lines = 1

        day_rate = 0  #
        to_assemble = self.num_lines * self.num_turbines

        self.chain_assembly_lines = []
        for i in range(int(lines)):
            c = ChainAssemblyLine(
                to_assemble,
                self.laydown,
                time,
                self.chain_storage,
                i + 1,
                day_rate,
            )
            self.env.register(c)
            self.chain_assembly_lines.append(c)


    def split_into_assembly_lines(self, df, n=1, strategy=1):
        '''Function that should divide up the components contained in 'df' into different 'bins',
        where each bin gets manufactured by a different assembly line
        
        Strategy 1 = the same number of components get sent to each assembly line, regardless of size
        Strategy 2 = the components are divided up between the assembly lines in as equal sets of 
            bin sizes as they can.
            Ex: [2, 2, 3, 3, 3, 4, 4] -> [2, 2, 4, 4]; [3, 3, 3]
        Strategy 3 = the components are divided up based on the midpoint (diameter value), which uses
            the linspace function: linspace(lowest value, highest value, n_assembly_lines + 1)
            Ex: [1, 2, 2, 2, 2, 4, 5] -> [1, 2, 2, 2, 2]; [4, 5]
        '''

        component_list = []

        if strategy == 1:

            total_rows = len(df)
            rows_per_set = total_rows // n

            for d in range(n):

                start_idx = d * rows_per_set
                # For the last set, include any remainder
                if d == n - 1:
                    end_idx = total_rows
                else:
                    end_idx = (d + 1) * rows_per_set
                subset = df.iloc[start_idx:end_idx]

                component_set = [
                    Component(
                        row["turbine_id"],
                        row["line_id"],
                        row["section_id"],
                        row["diameter"],
                        row["length"],
                        row["mass"],
                        row["thickness"],
                        row["cost_rate"],
                        row["area"],
                    )
                    for _, row in subset.iterrows()
                ]
                component_list.append(component_set)
        
        elif strategy == 2 or strategy == 3:

            if strategy == 2:
                #### Set up lists of bins to sort different diameters to different assembly lines ####
                unique_diameters = np.round(anchors_df['diameter'], 3).value_counts().index.values
                unique_bins = anchors_df['diameter'].value_counts().values
                sorted_indices = np.argsort(unique_diameters)
                sorted_diameters = unique_diameters[sorted_indices]
                sorted_bins = unique_bins[sorted_indices]

                # -- Strategy to split list of diameters into as equal of sets as you can get with discrete numbers to send to each chain maker
                n = int(anchor_bays)
                cumsum_bins = np.cumsum(sorted_bins)
                total = cumsum_bins[-1]
                split_points = [total * i / n for i in range(1, n)]
                split_indices = [np.abs(cumsum_bins - sp).argmin() for sp in split_points]
                split_diameters = sorted_diameters[split_indices]
                split_diameters = np.insert(split_diameters, 0, 0)
                split_diameters = np.insert(split_diameters, len(split_diameters), sorted_diameters[-1])
            
            # -- Strategy to split list of diameters into sets of equally spaced diameters, regardless of how many chains are contained in each set
            if strategy == 3:
                split_diameters = np.linspace(sorted_diameters[0], sorted_diameters[-1], n + 1)

            for d in range(len(split_diameters)-1):
                component_set = [
                    Component(
                        row["turbine_id"],
                        row["line_id"],
                        row["section_id"],
                        row["diameter"],
                        row["length"],
                        row["mass"],
                        row["thickness"],
                        row["cost_rate"],
                        row["area"],
                    )
                    for _, row in df[
                        (df["diameter"] > split_diameters[d]) &
                        (df["diameter"] <= split_diameters[d+1])
                    ].iterrows()
                ]
                component_list.append(component_set)
        
        return component_list

    @process
    def start_assembly_lines(self):
        """Start assembly line process."""

        yield self.laydown.start_assembly
        self.assembly_start = self.env.now
        self.env._submit_log(
            {"message": "Assembly processes started"}, level="DEBUG"
        )

        # Chain Assembly Line(s)
        for c_line in self.chain_assembly_lines:
            c_line.start()

        # for crane in self.turbine_assembly_lines:
        #    crane.start()

    @property
    def detailed_output(self):
        """Return detailed outputs."""

        return {
            "operational_delays": 0,
        }

        # #    def operational_delay(self, name):
        # """"""

        # actions = [a for a in self.env.actions if a["agent"] == name]
        # delay = sum(a["duration"] for a in actions if "Delay" in a["action"])

        # return delay

    @property
    def system_capex(self):
        """Returns total procurement cost of the substructures."""

        return (
            0  # self.num_turbines * self.config["substructure"]["unit_cost"]
        )

    @property
    def total_cost(self):
        """Return total cost."""
        return 0
