""""""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from marmot import process

from ORBIT.core import Cargo
from ORBIT.core._defaults import process_times as pt
from ORBIT.phases.install.monopile_install.common import (
    bolt_transition_piece,
    cure_transition_piece_grout,
    pump_transition_piece_grout,
)


class Topside(Cargo):
    """"""

    def __init__(self, weight=None, deck_space=None, **kwargs):
        """
        Creates an instance of `Topside`.
        """

        self.weight = weight
        self.deck_space = deck_space

    @staticmethod
    def fasten(**kwargs):
        """Returns time required to fasten a topside at port."""

        key = "topside_fasten_time"
        time = kwargs.get(key, pt[key])

        return "Fasten Topside", time

    @staticmethod
    def release(**kwargs):
        """Returns time required to release topside from fastenings."""

        key = "topside_release_time"
        time = kwargs.get(key, pt[key])

        return "Release Topside", time


class Jacket(Cargo):
    # TODO:
    pass


@process
def lift_topside(vessel, constraints={}, **kwargs):
    """
    TODO:
    Calculates time required to lift topside at site.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.

    Returns
    -------
    topside_lift_time : float
        Time required to lift topside (h).
    """

    lift_height = 5  # small lift just to clear the deck
    crane_rate = vessel.crane.crane_rate(**kwargs)
    lift_time = lift_height / crane_rate

    yield vessel.task("Lift Topside", lift_time, constraints=constraints)


@process
def attach_topside(vessel, constraints={}, **kwargs):
    """
    Returns time required to attach topside at site.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    topside_attach_time : int | float
        Time required to attach topside.

    Returns
    -------
    topside_attach_time : float
        Time required to attach topside (h).
    """

    _ = vessel.crane

    key = "topside_attach_time"
    attach_time = kwargs.get(key, pt[key])

    yield vessel.task("Attach Topside", attach_time, constraints=constraints)


@process
def install_topside(vessel, topside, **kwargs):
    """
    TODO:
    Substation topside installation process.
    Subprocesses:
    - Crane reequip
    - Lift topside
    - Attach topside to substructure
    - Pump grout
    - Cure grout

    Parameters
    ----------
    env : Environment
    vessel : Vessel
    topsdie : dict
    """

    connection = kwargs.get("topside_connection_type", "bolted")
    reequip_time = vessel.crane.reequip(**kwargs)
    site_depth = kwargs.get("site_depth", None)
    extension = kwargs.get("extension", site_depth + 10)
    jackdown_time = vessel.jacksys.jacking_time(extension, site_depth)

    yield vessel.task(
        "Crane Reequip",
        reequip_time,
        constraints=vessel.transit_limits,
        **kwargs,
    )
    yield lift_topside(vessel, constraints=vessel.operational_limits)
    yield attach_topside(vessel, constraints=vessel.operational_limits)

    if connection is "bolted":
        yield bolt_transition_piece(
            vessel, constraints=vessel.operational_limits, **kwargs
        )

    elif connection is "grouted":

        yield pump_transition_piece_grout(
            vessel, constraints=vessel.operational_limits, **kwargs
        )
        yield cure_transition_piece_grout(
            vessel, constraints=vessel.transit_limits
        )

    else:
        raise Exception(
            f"Transition piece connection type '{connection}'"
            "not recognized. Must be 'bolted' or 'grouted'."
        )

    yield vessel.task(
        "Jackdown", jackdown_time, constraints=vessel.transit_limits, **kwargs
    )
