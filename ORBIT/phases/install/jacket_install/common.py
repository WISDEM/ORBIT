__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2021, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from marmot import false, process

from ORBIT.core import Cargo
from ORBIT.core.defaults import process_times as pt


class Jacket(Cargo):
    """Jacket Cargo"""

    def __init__(
        self,
        height=None,
        mass=None,
        deck_space=None,
        foundation_type="piles",
        **kwargs,
    ):
        """Creats an instance of `Jacket`."""

        self.height = height
        self.mass = mass
        self.deck_space = deck_space
        self.num_legs = kwargs.get("num_legs", 4)
        self.foundation_type = foundation_type

    @staticmethod
    def fasten(**kwargs):
        """Returns time requred to fasten a jacket at port."""

        key = "jacket_fasten_time"
        time = kwargs.get(key, pt[key])

        return "Fasten Jacket", time

    @staticmethod
    def release(**kwargs):
        """Returns time required to release jacket from fastenings."""

        key = "jacket_release_time"
        time = kwargs.get(key, pt[key])

        return "Release Jacket", time


@process
def install_piles(vessel, jacket, **kwargs):
    """
    Process logic for installing piles at site.

    Parameters
    ----------
    vessel : Vessel
    jacket : dict
    """

    drive_time = kwargs.get("drive_piles_time", 6)
    for i in range(jacket.num_legs):
        yield vessel.task_wrapper(
            "Position Pile",
            6,
            constraints={**vessel.operational_limits},
            **kwargs,
        )

        yield vessel.task_wrapper(
            "Drive Pile",
            drive_time,
            constraints={**vessel.operational_limits, "night": false()},
            suspendable=True,
            **kwargs,
        )

        if i < (jacket.num_legs - 1):
            yield vessel.task_wrapper(
                "Move to Next Leg",
                4,
                constraints=vessel.transit_limits,
                suspendable=True,
                **kwargs,
            )


@process
def install_suction_buckets(vessel, jacket, **kwargs):
    """
    Process logic for installing suction buckets at site.

    Parameters
    ----------
    vessel : Vessel
    jacket : dict
    """

    suction_bucket_install_time = kwargs.get("suction_bucket_install_time", 24)
    for i in range(jacket.num_legs):
        yield vessel.task_wrapper(
            "Install Suction Bucket",
            suction_bucket_install_time,
            constraints={**vessel.operational_limits},
            **kwargs,
        )

        if i < (jacket.num_legs - 1):
            yield vessel.task_wrapper(
                "Move to Next Leg",
                4,
                constraints=vessel.transit_limits,
                suspendable=True,
                **kwargs,
            )


@process
def install_jacket(vessel, jacket, **kwargs):
    """
    Process logic for installing a jacket at site.

    Parameters
    ----------
    vessel : Vessel
    jacket : dict
    """

    if jacket.foundation_type == "piles":
        yield install_piles(vessel, jacket, **kwargs)

    elif jacket.foundation_type == "suction":
        yield install_suction_buckets(vessel, jacket, **kwargs)

    else:
        return ValueError(
            "Input 'jacket.foundation_type' must be 'piles' or 'suction'."
        )

    yield vessel.task_wrapper(
        "Lift Jacket", 4, constraints=vessel.operational_limits, **kwargs
    )

    yield vessel.task_wrapper(
        "Lower and Position Jacket",
        8,
        constraints=vessel.operational_limits,
        **kwargs,
    )

    yield vessel.task_wrapper(
        "Grout Jacket", 8, constraints=vessel.transit_limits, **kwargs
    )
