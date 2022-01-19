"""Common processes and cargo types for Monopile installations."""

__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from marmot import process
from ORBIT.core import Cargo
from ORBIT.core.logic import jackdown_if_required


class Monopile(Cargo):
    """Monopile Cargo"""

    def __init__(
        self, length=None, diameter=None, mass=None, deck_space=None, **kwargs
    ):
        """
        Creates an instance of `Monopile`.
        """

        self.length = length
        self.diameter = diameter
        self.mass = mass
        self.deck_space = deck_space

    @staticmethod
    def fasten(**kwargs):
        """Returns time required to fasten a monopile at port."""

        process = kwargs.get("processes")["fasten_mono"]
        return process["name"], process["duration"]

    @staticmethod
    def release(**kwargs):
        """Returns time required to release tmonopile from fastenings."""

        process = kwargs.get("processes")["release_mono"]
        return process["name"], process["duration"]


class TransitionPiece(Cargo):
    """Transition Piece Cargo"""

    def __init__(self, mass=None, deck_space=None, **kwargs):
        """
        Creates an instance of `TransitionPiece`.
        """

        self.mass = mass
        self.deck_space = deck_space

    @staticmethod
    def fasten(**kwargs):
        """Returns time required to fasten a transition piece at port."""

        process = kwargs.get("processes")["fasten_tp"]
        return process["name"], process["duration"]

    @staticmethod
    def release(**kwargs):
        """Returns time required to release transition piece from fastenings."""

        process = kwargs.get("processes")["release_tp"]
        return process["name"], process["duration"]


@process
def upend_monopile(vessel, length, **kwargs):
    """
    Calculates time required to upend monopile to vertical position.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    length : int | float
        Overall length of monopile (m).

    Yields
    ------
    vessel.task representing time to "Upend Monopile".
    """

    process = kwargs.get("processes")["upend_mono"]

    if process["duration"] == "dynamic":
        crane_rate = vessel.crane.crane_rate(**kwargs)
        upend_time = length / crane_rate

    else:
        upend_time = process["duration"]

    yield vessel.task_wrapper(
        process["name"],
        upend_time,
        constraints=process["constraints"],
        **kwargs,
    )


@process
def lower_monopile(vessel, **kwargs):
    """
    Calculates time required to lower monopile to seafloor.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    site_depth : int | float
        Seafloor depth at site (m).

    Yields
    ------
    vessel.task representing time to "Lower Monopile".
    """

    process = kwargs.get("processes")["lower_mono"]

    if process["duration"] == "dynamic":
        depth = kwargs.get("site_depth", None)
        rate = vessel.crane.crane_rate(**kwargs)
        height = (
            depth + 10
        ) / rate  # Assumed 10m deck height added to site depth
        lower_time = height / rate

    else:
        lower_time = process["duration"]

    yield vessel.task_wrapper(
        process["name"],
        lower_time,
        constraints=process["constraints"],
        **kwargs,
    )


@process
def drive_monopile(vessel, **kwargs):
    """
    Calculates time required to drive monopile into seafloor.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    mono_embed_len : int | float
        Monopile embedment length below seafloor (m).
    mono_drive_rate : int | float
        Driving rate (m/hr).

    Yields
    ------
    vessel.task representing time to "Drive Monopile".
    """

    _ = vessel.crane
    process = kwargs.get("processes")["drive_mono"]

    if process["duration"] == "dynamic":
        mono_embed_len = process["mono_embed_len"]
        mono_drive_rate = process["mono_drive_rate"]
        drive_time = mono_embed_len / mono_drive_rate

    else:
        drive_time = process["duration"]

    yield vessel.task_wrapper(
        process["name"],
        drive_time,
        constraints=process["constraints"],
        **kwargs,
    )


@process
def lower_transition_piece(vessel, **kwargs):
    """
    Calculates time required to lower a transition piece onto monopile.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.

    Yields
    ------
    vessel.task representing time to "Lower Transition Piece".
    """

    process = kwargs.get("processes")["lower_tp"]
    yield vessel.task_wrapper(**process)


@process
def bolt_transition_piece(vessel, **kwargs):
    """
    Returns time required to bolt transition piece to monopile.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    tp_bolt_time : int | float
        Time required to attach transition piece.

    Yields
    ------
    vessel.task representing time to "Bolt TP".
    """

    process = kwargs.get("processes")["bolt_tp"]
    yield vessel.task_wrapper(**process)


@process
def pump_transition_piece_grout(vessel, **kwargs):
    """
    Returns time required to pump grout at the transition piece interface.

    Parameters
    ----------
    grout_pump_time : int | float
        Time required to pump grout at the interface.

    Yields
    ------
    vessel.task representing time to "Pump TP Grout".
    """

    process = kwargs.get("processes")["pump_grout"]
    yield vessel.task_wrapper(**process)


@process
def cure_transition_piece_grout(vessel, **kwargs):
    """
    Returns time required for the transition piece grout to cure.

    Parameters
    ----------
    grout_cure_time : int | float
        Time required for the grout to cure.

    Yields
    ------
    vessel.task representing time to "Cure TP Grout".
    """

    process = kwargs.get("processes")["cure_grout"]
    yield vessel.task_wrapper(
        **process
    )  # TODO: Does kwargs need to be passed here still?


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

    yield lower_monopile(vessel, **kwargs)
    yield vessel.task_wrapper(
        "Crane Reequip",
        reequip_time,
        constraints=vessel.transit_limits,
        **kwargs,
    )
    yield drive_monopile(vessel, **kwargs)


@process
def install_transition_piece(vessel, tp, **kwargs):
    """
    Process logic for installing a transition piece on a monopile at site.

    Subprocesses:

    - Reequip crane, ``vessel.crane.reequip()``
    - Lower transition piece, ``tasks.lower_transition_piece()``
    - Install connection, see below.
    - Jackdown, ``vessel.jacksys.jacking_time()`` (if a jackup vessel)

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
    reequip = kwargs.get("processes")["crane_reequip"]

    yield vessel.task_wrapper(**reequip)
    yield lower_transition_piece(vessel, **kwargs)

    if connection == "bolted":
        yield bolt_transition_piece(vessel, **kwargs)

    elif connection == "grouted":
        yield pump_transition_piece_grout(vessel, **kwargs)
        yield cure_transition_piece_grout(vessel)

    else:
        raise Exception(
            f"Transition piece connection type '{connection}'"
            "not recognized. Must be 'bolted' or 'grouted'."
        )

    yield jackdown_if_required(vessel, **kwargs)
