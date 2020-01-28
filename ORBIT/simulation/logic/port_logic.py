"""This module contains common simulation logic related to ports."""

__author__ = ["Jake Nunemaker", "Rob Hammond"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from types import SimpleNamespace

from ORBIT.vessels import tasks
from ORBIT.simulation.exceptions import FastenTimeNotFound, VesselCapacityError


def vessel_fasten_time(item, **kwargs):
    """
    Retrieves the amount of time it takes to fasten an item to a vessel.

    Parameters
    ----------
    item : dict
        Dictionary with key 'type' to indicate what is being fastened.

    Returns
    -------
    fasten_time : int or float
        The amount of time it takes to fasten an item to the vessel.

    Raises
    ------
    Exception
        [description]
    """

    if item["type"] == "Blade":
        fasten_time = tasks.fasten_turbine_blade(**kwargs)

    elif item["type"] == "Nacelle":
        fasten_time = tasks.fasten_nacelle(**kwargs)

    elif item["type"] == "Tower Section":
        fasten_time = tasks.fasten_tower_section(**kwargs)

    elif item["type"] == "Monopile":
        fasten_time = tasks.fasten_monopile(**kwargs)

    elif item["type"] == "Transition Piece":
        fasten_time = tasks.fasten_transition_piece(**kwargs)

    elif item["type"] == "Scour Protection":
        fasten_time = tasks.load_rocks(**kwargs)

    elif item["type"] == "Topside":
        fasten_time = tasks.fasten_topside(**kwargs)

    elif item["type"] == "Carousel":
        lift_time = tasks.lift_carousel(**kwargs)
        fasten_time = tasks.fasten_carousel(**kwargs)
        fasten_time += lift_time

    else:
        raise FastenTimeNotFound(item["type"])

    return fasten_time
