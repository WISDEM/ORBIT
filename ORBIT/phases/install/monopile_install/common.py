"""
Jake Nunemaker
National Renewable Energy Lab
01/26/2020

A reconstruction of monopile related tasks using Marmot.
"""


from marmot import process

from ORBIT.core import Cargo
from ORBIT.core._defaults import process_times as pt


class Monopile(Cargo):
    """"""

    def __init__(self, length=None, diameter=None, weight=None, deck_space=None, **kwargs):
        """
        Creates an instance of `Monopile`.
        """

        self.length = length
        self.diameter = diameter
        self.weight = weight
        self.deck_space = deck_space

    @staticmethod
    def fasten(**kwargs):
        """Returns time required to fasten a monopile at port."""

        key = "mono_fasten_time"
        time = kwargs.get(key, pt[key])

        return "Fasten Monopile", time

    @staticmethod
    def release(**kwargs):
        """Returns time required to release tmonopile from fastenings."""

        key = "mono_release_time"
        time = kwargs.get(key, pt[key])

        return "Release Monopile", time


class TransitionPiece(Cargo):
    """"""

    def __init__(self, weight=None, deck_space=None, **kwargs):
        """
        Creates an instance of `TransitionPiece`.
        """

        self.weight = weight
        self.deck_space = deck_space

    @staticmethod
    def fasten(**kwargs):
        """Returns time required to fasten a transition piece at port."""

        key = "tp_fasten_time"
        time = kwargs.get(key, pt[key])

        return "Fasten Transition Piece", time

    @staticmethod
    def release(**kwargs):
        """Returns time required to release transition piece from fastenings."""

        key = "tp_release_time"
        time = kwargs.get(key, pt[key])

        return "Release Transition Piece", time

@process
def upend_monopile(vessel, length, constraints={}, **kwargs):
    """
    TODO:
    Calculates time required to upend monopile to vertical position.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    length : int | float
        Overall length of monopile (m).

    Returns
    -------
    mono_upend_time : float
        Time required to upened monopile (h).
    """

    crane_rate = vessel.crane.crane_rate(**kwargs)
    upend_time = length / crane_rate

    yield vessel.task("Upend Monopile", upend_time, constraints=constraints)


@process
def lower_monopile(vessel, constraints={}, **kwargs):
    """
    TODO:
    Calculates time required to lower monopile to seafloor.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    site_depth : int | float
        Seafloor depth at site (m).

    Returns
    -------
    mono_lower_time : float
        Time required to lower monopile (h).
    """


    depth = kwargs.get("site_depth", None)
    rate = vessel.crane.crane_rate(**kwargs)

    height = (vessel.jacksys.air_gap + vessel.jacksys.leg_pen + depth) / rate
    lower_time = height / rate

    yield vessel.task("Lower Monopile", lower_time, constraints=constraints)


@process
def drive_monopile(vessel, constraints={}, **kwargs):
    """
    TODO:
    Calculates time required to drive monopile into seafloor.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    mono_embed_len : int | float
        Monopile embedment length below seafloor (m).
    mono_drive_rate : int | float
        Driving rate (m/hr).

    Returns
    -------
    drive_time : float
        Time required to drive monopile to 'drive_length' (h).
    """

    mono_embed_len = kwargs.get("mono_embed_len", pt["mono_embed_len"])
    mono_drive_rate = kwargs.get(
        "mono_drive_rate", pt["mono_drive_rate"]
    )

    drive_time = mono_embed_len / mono_drive_rate

    yield vessel.task("Drive Monopile", drive_time, constraints=constraints)


@process
def lower_transition_piece(vessel, constraints={}, **kwargs):
    """
    TODO:
    Calculates time required to lower a transition piece onto monopile.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.

    Returns
    -------
    tp_lower_time : float
        Time required to lower transition piece.
    """

    rate = vessel.crane.crane_rate(**kwargs)
    lower_time = vessel.jacksys.air_gap / rate

    yield vessel.task("Lower TP", lower_time, constraints=constraints)


@process
def bolt_transition_piece(vessel, constraints={}, **kwargs):
    """
    TODO:
    Returns time required to bolt transition piece to monopile.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    tp_bolt_time : int | float
        Time required to attach transition piece.

    Returns
    -------
    tp_bolt_time : float
        Time required to attach transition piece (h).
    """

    key = "tp_bolt_time"
    bolt_time = kwargs.get(key, pt[key])

    yield vessel.task("Bolt TP", bolt_time, constraints=constraints)


@process
def pump_transition_piece_grout(vessel, constraints={}, **kwargs):
    """
    Returns time required to pump grout at the transition piece interface.

    Parameters
    ----------
    grout_pump_time : int | float
        Time required to pump grout at the interface.

    Returns
    -------
    grout_pump_time : float
        Time required to pump grout at the interface (h).
    """

    key = "grout_pump_time"
    pump_time = kwargs.get(key, pt[key])

    yield vessel.task("Pump TP Grout", pump_time, constraints=constraints)


@process
def cure_transition_piece_grout(vessel, constraints={}, **kwargs):
    """
    Returns time required for the transition piece grout to cure.

    Parameters
    ----------
    grout_cure_time : int | float
        Time required for the grout to cure.

    Returns
    -------
    grout_cure_time : float
        Time required for the grout to cure (h).
    """

    key = "grout_cure_time"
    cure_time = kwargs.get(key, pt[key])

    yield vessel.task("Cure TP Grout", cure_time, constraints=constraints)


@process
def install_monopile(vessel, monopile, **kwargs):
    """
    Process logic for installing a monopile at site.

    Subprocesses:

    - Lower monopile, ``tasks.lower_monopile()``
    - Reequip crane, ``vessel.crane.reequip()``
    - Drive monopile, ``tasks.drive_monopile()``

    Parameters
    ----------
    env : Environment
    vessel : Vessel
    monopile : dict
    """

    reequip_time = vessel.crane.reequip(**kwargs)

    yield lower_monopile(vessel, constraints=vessel.operational_limits, **kwargs)
    yield vessel.task("Crane Reequip", reequip_time, constraints=vessel.transit_limits, **kwargs)
    yield drive_monopile(vessel, constraints=vessel.operational_limits, **kwargs)


@process
def install_transition_piece(vessel, tp, **kwargs):
    """
    Process logic for installing a transition piece on a monopile at site.

    Subprocesses:

    - Reequip crane, ``vessel.crane.reequip()``
    - Lower transition piece, ``tasks.lower_transition_piece()``
    - Install connection, see below.
    - Jackdown, ``vessel.jacksys.jacking_time()``

    The transition piece can either be installed with a bolted or a grouted
    connection. By default, ORBIT uses the bolted connection with the following
    task:

    - Bolt transition piece, ``tasks.bolt_transition_piece()``

    ORBIT can also be configured to model a grouted connection by passing in
    `tp_connection_type='grouted'` as a `kwarg`. This process uses the
    following tasks:

    - Pump grout, ``tasks.pump_transition_piece_grout()``
    - Cure grout, ``tasks.cure_transition_piece_grout()``

    Parameters
    ----------
    env : Environment
    vessel : Vessel
    tp : dict
    """

    connection = kwargs.get("tp_connection_type", "bolted")
    reequip_time = vessel.crane.reequip(**kwargs)
    site_depth = kwargs.get("site_depth", None)
    extension = kwargs.get("extension", site_depth + 10)
    jackdown_time = vessel.jacksys.jacking_time(extension, site_depth)

    yield vessel.task("Crane Reequip", reequip_time, constraints=vessel.transit_limits, **kwargs)
    yield lower_transition_piece(vessel, constraints=vessel.operational_limits, **kwargs)
    
    if connection is "bolted":
        yield bolt_transition_piece(vessel, constraints=vessel.operational_limits, **kwargs)

    elif connection is "grouted":

        yield pump_transition_piece_grout(vessel, constraints=vessel.operational_limits, **kwargs)
        yield cure_transition_piece_grout(vessel, constraints=vessel.transit_limits)

    else:
        raise Exception(
            f"Transition piece connection type '{connection}'"
            "not recognized. Must be 'bolted' or 'grouted'."
        )

    yield vessel.task("Jackdown", jackdown_time, constraints=vessel.transit_limits, **kwargs)