"""
Provides the base class and simulation logic for array and export cable
installation simulations.
"""

__author__ = "Rob Hammond"
__copyright__ = "Copyright 2019, National Renewable Energy Laboratory"
__maintainer__ = "Rob Hammond"
__email__ = "robert.hammond@nrel.gov"


from numpy import isclose

from ORBIT.vessels import tasks
from ORBIT.simulation.logic import get_list_of_items_from_port
from ORBIT.simulation.exceptions import InsufficientAmount

# Trech digging pre-installation task


def dig_trench(env, vessel, distance, **kwargs):
    """
    Subprocess to dig the trench for the export cable between landfall
    and the onshore substation.

    Parameters
    ----------
    distance : int or float
        Distance between landfall and onshore substation.
    """

    kwargs = {**vessel._transport_specs, **kwargs}
    dig_time = tasks.dig_trench(distance, **kwargs)

    task = {
        "agent": "Trench Dig Vessel",
        "action": "DigTrench",
        "duration": dig_time,
        "location": "Onshore",
        "type": "Operations",
    }

    yield env.process(env.task_handler(task))


# Basic cable laying processes


def transport(env, vessel, distance, to_port, to_site, **kwargs):
    """
    Subprocess to travel between port and site.

    Parameters
    ----------
    env : simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable laying vessel.
    distance : int or float
        Distance between port and site.
    to_port : bool
        Indicator for travelling to port (True) or to site (False).
    """

    kwargs = {**vessel._transport_specs, **kwargs}
    transit_time = vessel.transit_time(distance)

    task = {
        "agent": vessel.name,
        "action": "Transit",
        "duration": transit_time,
        "location": "At Sea",
        "type": "Operations",
        **vessel.transit_limits,
    }

    if to_port and not to_site:
        vessel.at_site = False
        vessel.storage.deck_space -= 1
    elif to_site and not to_port:
        vessel.at_port = False

    yield env.process(env.task_handler(task))

    if to_port and not to_site:
        vessel.at_port = True
    elif to_site and not to_port:
        vessel.at_site = True


def get_carousel_from_port(env, vessel, port, **kwargs):
    """
    Logic required to load a carousel onto the cable laying vessel at port.

    Parameters
    ----------
    env : simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable laying vessel.
    port : Port
        Port object.
    """

    component_list = [("type", "Carousel")]
    yield env.process(
        get_list_of_items_from_port(
            env, vessel, component_list, port, **kwargs
        )
    )


def position_onsite(env, vessel, **kwargs):
    """
    Processs to position cable laying vessel at turbine substation.

    Parameters
    ----------
    env : simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable laying vessel.
    """

    kwargs = {**vessel._transport_specs, **kwargs}
    position_time = tasks.position_onsite(**kwargs)
    task = {
        "agent": vessel.name,
        "action": "PositionOnsite",
        "duration": position_time,
        "location": "Site",
        "type": "Operations",
        **vessel.transit_limits,
    }
    yield env.process(env.task_handler(task))


def prep_cable(env, vessel, **kwargs):
    """
    Processs to prepare the cable for laying and burial at site.

    Parameters
    ----------
    env : simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable laying vessel.
    """

    prep_time = tasks.prep_cable(**kwargs)
    task = {
        "agent": vessel.name,
        "action": "PrepCable",
        "duration": prep_time,
        "location": "Site",
        "type": "Operations",
        **vessel.transit_limits,
    }
    yield env.process(env.task_handler(task))


def lower_cable(env, vessel, **kwargs):
    """
    Process to lower the cable to the seafloor at site.

    Parameters
    ----------
    env : simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable laying vessel.
    """

    kwargs = {**vessel._transport_specs, **kwargs}
    lower_time = tasks.lower_cable(**kwargs)
    task = {
        "agent": vessel.name,
        "action": "LowerCable",
        "duration": lower_time,
        "location": "Site",
        "type": "Operations",
        **vessel.transit_limits,
    }
    yield env.process(env.task_handler(task))


def pull_in_cable(env, vessel, **kwargs):
    """
    Process to pull cable into substation at site.

    Parameters
    ----------
    env : simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable laying vessel.
    """

    kwargs = {**vessel._transport_specs, **kwargs}
    pull_time = tasks.pull_in_cable(**kwargs)
    task = {
        "agent": vessel.name,
        "action": "PullInCable",
        "duration": pull_time,
        "location": "Site",
        "type": "Operations",
        **vessel.transit_limits,
    }
    yield env.process(env.task_handler(task))


def test_cable(env, vessel, **kwargs):
    """
    Process to test cable at substation to ensure it works.

    Parameters
    ----------
    env : simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable laying vessel.
    """

    kwargs = {**vessel._transport_specs, **kwargs}
    test_time = tasks.test_cable(**kwargs)

    task = {
        "agent": vessel.name,
        "action": "TestCable",
        "duration": test_time,
        "location": "Site",
        "type": "Operations",
        **vessel.transit_limits,
    }

    yield env.process(env.task_handler(task))


def lay_bury_cable_section(
    env, vessel, cable_len_km, cable_mass_tonnes, **kwargs
):
    """
    Process to lay (and bury) cable between substructures.

    Parameters
    ----------
    env : simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable laying vessel.
    cable_len_km : int or float
        Length of cable to be laid.
    simultaneous_lay_bury : bool
        Indicator for whether or not laying and burrying of cable happen
        simultaneously or separately.
    """

    kwargs = {**vessel._transport_specs, **kwargs}
    lay_bury_time = tasks.lay_bury_cable(cable_len_km, **kwargs)
    task = {
        "agent": vessel.name,
        "action": "LayBuryCable",
        "duration": lay_bury_time,
        "location": "Site",
        "type": "Operations",
        **vessel.transit_limits,
    }

    # Check that we are not just getting a float error that is some trivial
    # difference as opposed to a legitimate error
    try:
        _ = vessel.storage.get_item("cable", cable_mass_tonnes)
    except InsufficientAmount:
        try:
            _ = vessel.storage.get_item("cable", round(cable_mass_tonnes, 10))
        except InsufficientAmount:
            if isclose(vessel.storage.current_cargo_weight, cable_mass_tonnes):
                _ = vessel.storage.get_item(
                    "cable", vessel.storage.current_cargo_weight
                )

    yield env.process(env.task_handler(task))


def lay_cable_section(env, vessel, cable_len_km, cable_mass_tonnes, **kwargs):
    """
    Process to lay (and bury) cable between substructures.

    Parameters
    ----------
    env : simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable laying vessel.
    cable_len_km : int or float
        Length of cable to be laid.
    simultaneous_lay_bury : bool
        Indicator for whether or not laying and burrying of cable happen
        simultaneously or separately.
    """

    kwargs = {**vessel._transport_specs, **kwargs}
    lay_time = tasks.lay_cable(cable_len_km, **kwargs)
    task = {
        "agent": vessel.name,
        "action": "LayCable",
        "duration": lay_time,
        "location": "Site",
        "type": "Operations",
        **vessel.transit_limits,
    }

    # Check that we are not just getting a float error that is some trivial
    # difference as opposed to a legitimate error
    try:
        _ = vessel.storage.get_item("cable", cable_mass_tonnes)
    except InsufficientAmount:
        try:
            _ = vessel.storage.get_item("cable", round(cable_mass_tonnes, 10))
        except InsufficientAmount:
            if isclose(vessel.storage.current_cargo_weight, cable_mass_tonnes):
                _ = vessel.storage.get_item(
                    "cable", vessel.storage.current_cargo_weight
                )

    yield env.process(env.task_handler(task))


def bury_cable_section(env, vessel, cable_len_km, **kwargs):
    """
    Process to bury cable section between substructures.

    Parameters
    ----------
    env : simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable burying vessel.
    cable_len_km : int or float
        Length of cable to be laid.
    """

    kwargs = {**vessel._transport_specs, **kwargs}
    bury_time = tasks.bury_cable(cable_len_km, **kwargs)
    task = {
        "agent": vessel.name,
        "action": "BuryCable",
        "duration": bury_time,
        "location": "Site",
        "type": "Operations",
        **vessel.transit_limits,
    }
    yield env.process(env.task_handler(task))


# Cable splicing processes


def raise_cable(env, vessel, **kwargs):
    """
    Process to raise the unspliced cable end from the seafloor.

    Parameters
    ----------
    env : simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable laying vessel.
    """

    kwargs = {**vessel._transport_specs, **kwargs}
    raise_time = tasks.raise_cable(**kwargs)
    task = {
        "agent": vessel.name,
        "action": "RaiseCable",
        "duration": raise_time,
        "location": "Site",
        "type": "Operations",
        **vessel.transit_limits,
    }
    yield env.process(env.task_handler(task))


def splice_cable(env, vessel, **kwargs):
    """
    Process to splice two cable ends together.

    Parameters
    ----------
    env : simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable laying vessel.
    """

    kwargs = {**vessel._transport_specs, **kwargs}
    splice_time = tasks.splice_cable(**kwargs)

    task = {
        "agent": vessel.name,
        "action": "SpliceCable",
        "duration": splice_time,
        "location": "Site",
        "type": "Operations",
        **vessel.transit_limits,
    }

    yield env.process(env.task_handler(task))


# Export cable specific processes


def tow_plow(env, vessel, distance, **kwargs):
    """
    Process to tow the plow to the landfall site from the cable laying vessel.

    Parameters
    ----------
    env : simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable laying vessel.
    distance : int or float
        Distance between landfall and cable laying vessel. This is either
        where the vessel has beached itself or will be anchored while
        doing the onshore part of installation.
    """

    kwargs = {**vessel._transport_specs, **kwargs}
    tow_time = tasks.tow_plow(distance, **kwargs)
    if tow_time > 0:
        task = {
            "agent": vessel.name,
            "action": "TowPlow",
            "duration": tow_time,
            "location": "Landfall",
            "type": "Operations",
            **vessel.transit_limits,
        }
        yield env.process(env.task_handler(task))


def pull_in_winch(env, vessel, distance, **kwargs):
    """
    Subprocess to pull in the winch to the landfall site from the cable
    laying vessel.

    Parameters
    ----------
    env : simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable laying vessel.
    distance : int or float
        Distance between landfall and the onshare substation. This is either
        where the vessel has beached itself or will be anchored while
        doing the onshore part of installation.
    """

    kwargs = {**vessel._transport_specs, **kwargs}
    winch_time = tasks.pull_winch(distance, **kwargs)
    task = {
        "agent": vessel.name,
        "action": "PullWinch",
        "duration": winch_time,
        "location": "Landfall",
        "type": "Operations",
        **vessel.transit_limits,
    }
    yield env.process(env.task_handler(task))


# Grouped processes for simpler logic in the simulation


def connect_cable_section_to_target(env, vessel, **kwargs):
    """
    Subprocess to start or end a cable installation.

    Parameters
    ----------
    env : simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable laying vessel.
    """

    # Prep cable
    yield env.process(prep_cable(env, vessel, **kwargs))

    # Pull in cable to offshore substructure
    yield env.process(pull_in_cable(env, vessel, **kwargs))

    # Test and terminate cable at offshore substructure
    yield env.process(test_cable(env, vessel, **kwargs))


def lay_bury_full_array_cable_section(
    env, vessel, cable_len_km, cable_mass_tonnes, **kwargs
):
    """
    Subprocesses to lay and connect cable between turbines and offshore
    substation.

    Parameters
    ----------
    env : simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable laying vessel.
    cable_len_km : int or float
        Length of cable, in km.
    cable_mass_tonnes : int or float
        Mass of cable, tonnes.
    simultaneous_lay_bury : bool
        Indicator for simultaneous laying and burying of cable
    """

    # Position at site
    yield env.process(position_onsite(env, vessel, **kwargs))

    # Connect cable to turbine
    yield env.process(connect_cable_section_to_target(env, vessel, **kwargs))

    # Lower cable
    yield env.process(lower_cable(env, vessel, **kwargs))

    # Lay and bury cable between offshore substructure
    yield env.process(
        lay_bury_cable_section(
            env, vessel, cable_len_km, cable_mass_tonnes, **kwargs
        )
    )

    # Complete the installation of the cable
    yield env.process(connect_cable_section_to_target(env, vessel, **kwargs))


def splice_cable_process(env, vessel, **kwargs):
    """
    Subprocess for splicing two cable ends together.

    Parameters
    ----------
    env : simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable laying vessel.
    cable_len_km : int or float
        Length (in km) of the cable section to be installed.
    """

    # Position at splice site
    yield env.process(position_onsite(env, vessel, **kwargs))

    # Raise the cable end from the seafloor
    yield env.process(raise_cable(env, vessel, **kwargs))

    # Splice the cable ends
    yield env.process(splice_cable(env, vessel, **kwargs))

    # Lower cable to seafloor
    yield env.process(lower_cable(env, vessel, **kwargs))


def onshore_work(
    env,
    vessel,
    distance_to_beach,
    distance_to_interconnection,
    cable_mass,
    **kwargs,
):
    """
    Processes to connect the export cable between the offshore
    substation and landfall.

    TODO: Allow for splicing in the logic for the case where the onshore
    substation is located very far from landfall.

    Parameters
    ----------
    env : simpy.Environment
        Simulation environment.
    vessel : Vessel
        Cable laying vessel.
    distance_to_beach : int or float
        Distance from lanfall to where the vessel is located (could beach
        itself or remain at sea).
    distance_to_interconnection : int or float
        Distance between the landfall site and the onshore substation, in km.
    cable_mass : int or float
        Mass of cable length to be installed onshore, in tonnes.
    """

    distance_vessel_to_inter = distance_to_beach + distance_to_interconnection

    # Tow plow to landfall
    yield env.process(tow_plow(env, vessel, distance_to_beach, **kwargs))

    # Pull in winch wire
    yield env.process(
        pull_in_winch(env, vessel, distance_vessel_to_inter, **kwargs)
    )

    # Remove the onshore cable length from storage
    _ = vessel.storage.get_item("cable", cable_mass)

    # Connect cable at interconnection
    yield env.process(connect_cable_section_to_target(env, vessel, **kwargs))

    # Lower cable to seafloor
    yield env.process(lower_cable(env, vessel, **kwargs))
