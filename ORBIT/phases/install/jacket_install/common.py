__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2021, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from marmot import process

from ORBIT.core import Cargo
from ORBIT.core.defaults import process_times as pt


class Jacket(Cargo):
    """Jacket Cargo"""

    def __init__(self, height=None, mass=None, deck_space=None, **kwargs):
        """Creats an instance of `Jacket`."""

        self.height = height
        self.mass = mass
        self.deck_space = deck_space

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
def install_jacket(vessel, jacket, **kwargs):
    """
    Process logic for installing a jacket at site.

    Parameters
    ----------
    env : Environment
    vessel : Vessel
    jacket : dict
    """

    reequip_time = vessel.crane.reequip(**kwargs)
    # TODO:
    yield vessel.task_wrapper(
        "Lift Jacket", 4, constraints=vessel.transit_limits, **kwargs
    )
    yield vessel.task_wrapper(
        "Lower Jacket", 4, constraints=vessel.transit_limits, **kwargs
    )

    pile_time = kwargs.get("drive_piles_time", 12)
    yield vessel.task_wrapper(
        "Drive Piles", pile_time, constraints=vessel.transit_limits, **kwargs
    )
