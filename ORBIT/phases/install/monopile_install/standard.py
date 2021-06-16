"""`MonopileInstallation` class and related processes."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


import numpy as np
import simpy
from marmot import le, process

from ORBIT.core import Vessel, DryStorage, AssemblyLine, ComponentDelivery
from ORBIT.core.cargo import Monopile, TransitionPiece
from ORBIT.core.logic import (
    shuttle_items_to_queue,
    prep_for_site_operations,
    get_list_of_items_from_port,
)
from ORBIT.phases.install import InstallPhase
from ORBIT.core.exceptions import ItemNotFound

from .common import (
    Monopile,
    TransitionPiece,
    upend_monopile,
    install_monopile,
    install_transition_piece,
)


class MonopileInstallation(InstallPhase):
    """
    Standard monopile installation module using a Wind Turbine Installation
    Vessel (WTIV). If input `feeder` and `num_feeders` are not supplied, the
    WTIV will perform all transport and installation tasks. If the above inputs
    are defined, feeder barges will transport monopile components from port to
    site.
    """

    phase = "Monopile Installation"

    #:
    expected_config = {
        "wtiv": "dict | str",
        "feeder": "dict | str (optional)",
        "num_feeders": "int (optional)",
        "site": {"depth": "m", "distance": "km"},
        "plant": {"num_turbines": "int"},
        "turbine": {"hub_height": "m"},
        "port": {
            "num_cranes": "int (optional, default: 1)",
            "monthly_rate": "USD/mo (optional)",
            "name": "str (optional)",
        },
        "monopile": {
            "length": "m",
            "diameter": "m",
            "deck_space": "m2",
            "mass": "t",
            "unit_cost": "USD",
        },
        "transition_piece": {
            "deck_space": "m2",
            "mass": "t",
            "unit_cost": "USD",
        },
        "transport_vessel": {
            "day_rate": "$/day (optional, default: 20000)",
            "constaints": "dict (optional)",
        },
        "monopile_supply_chain": {
            "enabled": "(optional, default: False)",
            "component_time": "h (optional, default: 168)",
            "component_lines": "(optional, default: 1)",
            "component_line_rate": "(optional, default: 10)",
            "transit_time": "h (optional, default: 0)",
            "assembly_time": "h (optional, default: 168)",
            "assembly_lines": "(optional, default: 1)",
            "assembly_line_rate": "(optional, default: 10)",
        },
    }

    def __init__(self, config, weather=None, **kwargs):
        """
        Creates an instance of MonopileInstallation.

        Parameters
        ----------
        config : dict
            Simulation specific configuration.
        weather : pd.DataFrame (optional)
            Weather profile at site.
            Expects columns 'max_waveheight' and 'max_windspeed'.
        """

        super().__init__(weather, **kwargs)

        config = self.initialize_library(config, **kwargs)
        self.config = self.validate_config(config)

        port = self.config.get("port", {})
        self.initialize_port(**port)

        self.initialize_supply_chain_infrastructure()
        self.initialize_wtiv()
        self.setup_simulation(**kwargs)

    def initialize_supply_chain_infrastructure(self):
        """"""

        self.num_monopiles = self.config["plant"]["num_turbines"]
        monopile = Monopile(**self.config["monopile"])
        tp = TransitionPiece(**self.config["transition_piece"])
        self.set_mass = monopile.mass + tp.mass
        self.set_deck_space = monopile.deck_space + tp.deck_space

        self.supply_chain = self.config.get("monopile_supply_chain", {})
        if self.supply_chain.get("enabled", False):
            self.initialize_substructure_delivery()
            self.initialize_substructure_assembly()

        else:
            self.storage = DryStorage(self.env, float("inf"))
            self.storage.crane = simpy.Resource(self.env, 1)
            for _ in range(self.num_monopiles):
                self.storage.put(monopile)
                self.storage.put(tp)

    def initialize_substructure_delivery(self):
        """"""

        component_time = self.supply_chain.get("component_time", 168)
        component_lines = self.supply_chain.get("component_lines", 1)
        transit_time = self.supply_chain.get("transit_time", 0)
        assembly_rate = self.supply_chain.get("component_line_rate", 10)
        vessel = self.config.get("transport_vessel", {})
        constr = {k: le(v) for k, v in vessel.get("constraints", {}).items()}

        self.component_delivery = ComponentDelivery(
            component="Monopile",
            num=self.num_monopiles,
            num_parallel=component_lines,
            takt_time=component_time,
            takt_day_rate=assembly_rate,
            transit_time=transit_time,
            transit_constraints=constr,
            transit_day_rate=vessel.get("day_rate", 20000),
        )
        self.env.register(self.component_delivery)
        self.component_delivery.initialize_staging_area()
        self.component_delivery.start()

    def initialize_substructure_assembly(self):
        """"""

        mp = self.config["monopile"]
        tp = self.config["transition_piece"]

        class MonopileAssemblyLine(AssemblyLine):

            component = "Monopile"
            outputs = [Monopile(**mp), TransitionPiece(**tp)]

        assembly_time = self.supply_chain.get("assembly_time", 168)
        assembly_lines = self.supply_chain.get("assembly_lines", 1)
        storage_berths = self.supply_chain.get("storage_berths", 4)
        assembly_rate = self.supply_chain.get("component_line_rate", 10)

        self.storage = DryStorage(self.env, storage_berths)
        self.storage.crane = simpy.Resource(self.env, 1)

        to_assemble = [1] * self.num_monopiles

        self.sub_assembly_lines = []
        for i in range(int(assembly_lines)):
            a = MonopileAssemblyLine(
                assigned=to_assemble,
                pull_from=self.component_delivery.staging_area,
                time=assembly_time,
                target=self.storage,
                day_rate=assembly_rate,
            )

            self.env.register(a)
            a.start()
            self.sub_assembly_lines.append(a)

    @property
    def system_capex(self):
        """Returns procurement cost of the substructures."""

        return (
            self.config["monopile"]["unit_cost"]
            + self.config["transition_piece"]["unit_cost"]
        ) * self.config["plant"]["num_turbines"]

    def setup_simulation(self, **kwargs):
        """
        Sets up simulation infrastructure, routing to specific methods dependent
        on number of feeders.
        """

        if self.config.get("num_feeders", None):
            self.initialize_feeders()
            self.initialize_queue()
            self.setup_simulation_with_feeders(**kwargs)

        else:
            self.feeders = None
            self.setup_simulation_without_feeders(**kwargs)

    def setup_simulation_without_feeders(self, **kwargs):
        """
        Sets up infrastructure for turbine installation without feeder barges.
        """

        site_distance = self.config["site"]["distance"]
        site_depth = self.config["site"]["depth"]
        hub_height = self.config["turbine"]["hub_height"]

        self.sets_per_trip = int(
            min(
                np.floor(self.wtiv.storage.max_cargo_mass / self.set_mass),
                np.floor(
                    self.wtiv.storage.max_deck_space / self.set_deck_space
                ),
            )
        )

        solo_install_monopiles(
            self.wtiv,
            port=self.storage,
            distance=site_distance,
            monopiles=self.num_monopiles,
            site_depth=site_depth,
            hub_height=hub_height,
            per_trip=self.sets_per_trip,
            **kwargs,
        )

    def setup_simulation_with_feeders(self, **kwargs):
        """
        Sets up infrastructure for turbine installation using feeder barges.
        """

        site_distance = self.config["site"]["distance"]
        site_depth = self.config["site"]["depth"]
        component_list = ["Monopile", "TransitionPiece"]

        self.sets_per_trip = int(
            min(
                np.floor(
                    self.feeders[0].storage.max_cargo_mass / self.set_mass
                ),
                np.floor(
                    self.feeders[0].storage.max_deck_space
                    / self.set_deck_space
                ),
            )
        )

        install_monopiles_from_queue(
            self.wtiv,
            queue=self.active_feeder,
            monopiles=self.num_monopiles,
            distance=site_distance,
            site_depth=site_depth,
            **kwargs,
        )

        assignments = [
            self.num_monopiles // len(self.feeders)
            + (1 if x < self.num_monopiles % len(self.feeders) else 0)
            for x in range(len(self.feeders))
        ]

        for assigned, feeder in zip(assignments, self.feeders):
            shuttle_items_to_queue(
                feeder,
                port=self.storage,
                queue=self.active_feeder,
                distance=site_distance,
                items=component_list,
                per_trip=self.sets_per_trip,
                assigned=assigned,
                **kwargs,
            )

    def initialize_wtiv(self):
        """
        Initializes the WTIV simulation object and the onboard vessel storage.
        """

        wtiv_specs = self.config.get("wtiv", None)
        name = wtiv_specs.get("name", "WTIV")

        wtiv = Vessel(name, wtiv_specs)
        self.env.register(wtiv)

        wtiv.initialize()
        wtiv.at_port = True
        wtiv.at_site = False
        self.wtiv = wtiv

    def initialize_feeders(self):
        """
        Initializes feeder barge objects.
        """

        number = self.config.get("num_feeders", None)
        feeder_specs = self.config.get("feeder", None)

        self.feeders = []
        for n in range(number):
            # TODO: Add in option for named feeders.
            name = "Feeder {}".format(n)

            feeder = Vessel(name, feeder_specs)
            self.env.register(feeder)

            feeder.initialize()
            feeder.at_port = True
            feeder.at_site = False
            self.feeders.append(feeder)

    def initialize_queue(self):
        """
        Initializes the queue, modeled as a ``SimPy.Resource`` that feeders
        join at site. This limits the simulation to one active feeder at a time.
        """

        self.active_feeder = simpy.Resource(self.env, capacity=1)
        self.active_feeder.vessel = None
        self.active_feeder.activate = self.env.event()

    @property
    def detailed_output(self):
        """Returns detailed outputs of the monopile installation."""

        if self.feeders:
            transport_vessels = [*self.feeders]

        else:
            transport_vessels = [self.wtiv]

        outputs = {
            self.phase: {
                **self.agent_efficiencies,
                **self.get_max_cargo_mass_utilzations(transport_vessels),
                **self.get_max_deck_space_utilzations(transport_vessels),
            }
        }

        return outputs


@process
def solo_install_monopiles(
    vessel, port, distance, monopiles, per_trip, **kwargs
):
    """
    TODO:
    Logic that a Wind Turbine Installation Vessel (WTIV) uses during a single
    monopile installation process.

    Parameters
    ----------
    vessel : vessels.Vessel
        Vessel object that represents the WTIV.
    port : Port
    distance : int | float
        Distance between port and site (km).
    monopiles : int
        Total monopiles to install.
    per_trip : int
    """

    component_list = ["Monopile", "TransitionPiece"]

    n = 0
    while n < monopiles:
        if vessel.at_port:
            # Get substructures + transition pieces from port
            yield get_list_of_items_from_port(
                vessel, port, component_list * per_trip, **kwargs
            )

            # Transit to site
            vessel.update_trip_data()
            vessel.at_port = False
            yield vessel.transit(distance)
            vessel.at_site = True

        if vessel.at_site:

            if vessel.storage.items:
                # Prep for monopile install
                yield prep_for_site_operations(
                    vessel, survey_required=True, **kwargs
                )

                # Get monopile from internal storage
                monopile = yield vessel.get_item_from_storage(
                    "Monopile", **kwargs
                )

                yield upend_monopile(vessel, monopile.length, **kwargs)
                yield install_monopile(vessel, monopile, **kwargs)

                # Get transition piece from internal storage
                tp = yield vessel.get_item_from_storage(
                    "TransitionPiece", **kwargs
                )

                yield install_transition_piece(vessel, tp, **kwargs)
                vessel.submit_debug_log(progress="Substructure")
                n += 1

            else:
                # Transit to port
                vessel.at_site = False
                yield vessel.transit(distance)
                vessel.at_port = True

    vessel.submit_debug_log(message="Monopile installation complete!")


@process
def install_monopiles_from_queue(wtiv, queue, monopiles, distance, **kwargs):
    """
    Logic that a Wind Turbine Installation Vessel (WTIV) uses to install
    monopiles and transition pieces from queue of feeder barges.

    Parameters
    ----------
    env : simulation.Environment
        SimPy environment that the simulation runs in.
    wtiv : vessels.Vessel
        Vessel object that represents the WTIV.
    queue : simpy.Resource
        Queue object to interact with active feeder barge.
    number : int
        Total monopiles to install.
    distance : int | float
        Distance from site to port (km).
    """

    n = 0
    while n < monopiles:
        if wtiv.at_port:
            # Transit to site
            wtiv.at_port = False
            yield wtiv.transit(distance)
            wtiv.at_site = True

        if wtiv.at_site:

            if queue.vessel:

                # Prep for monopile install
                yield prep_for_site_operations(
                    wtiv, survey_required=True, **kwargs
                )

                # Get monopile
                monopile = yield wtiv.get_item_from_storage(
                    "Monopile", vessel=queue.vessel, **kwargs
                )

                yield upend_monopile(wtiv, monopile.length, **kwargs)
                yield install_monopile(wtiv, monopile, **kwargs)

                # Get transition piece from active feeder
                tp = yield wtiv.get_item_from_storage(
                    "TransitionPiece",
                    vessel=queue.vessel,
                    release=True,
                    **kwargs,
                )

                # Install transition piece
                yield install_transition_piece(wtiv, tp, **kwargs)
                wtiv.submit_debug_log(progress="Substructure")
                n += 1

            else:
                start = wtiv.env.now
                yield queue.activate
                delay_time = wtiv.env.now - start
                wtiv.submit_action_log("Delay", delay_time, location="Site")

    # Transit to port
    wtiv.at_site = False
    yield wtiv.transit(distance)
    wtiv.at_port = True

    wtiv.submit_debug_log(message="Monopile installation complete!")
