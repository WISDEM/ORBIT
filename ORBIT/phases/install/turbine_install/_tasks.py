"""
Jake Nunemaker
National Renewable Energy Lab
01/26/2020

A reconstruction of turbine related tasks using Marmot.
"""


from ORBIT.vessels.tasks import defaults

from marmot import process


@process
def lift_nacelle(vessel, constraints={}, **kwargs):
    """
    Calculates time required to lift nacelle to hub height.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    hub_height : int | float
        Hub height above MSL (m).

    Yields
    ------
    lift_time : float
        Time required to lift nacelle to hub height (h).
    """

    hub_height = kwargs.get("hub_height", None)
    crane_rate = vessel.crane.crane_rate(**kwargs)
    lift_time = hub_height / crane_rate

    yield vessel.task("Lift Nacelle", lift_time, constraints=constraints)


@process
def attach_nacelle(vessel, constraints={}, **kwargs):
    """
    Returns time required to attach nacelle to tower.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    nacelle_attach_time : int | float
        Time required to attach nacelle.

    Returns
    -------
    nacelle_attach_time : float
        Time required to attach nacelle (h).
    """

    crane = vessel.crane
    key = "nacelle_attach_time"
    attach_time = kwargs.get(key, defaults[key])

    yield vessel.task("Attach Nacelle", attach_time, constraints=constraints)


@process
def fasten_nacelle(vessel, constraints={}, **kwargs):
    """
    Returns time required to fasten a nacelle at port.

    Parameters
    ----------
    nacelle_fasten_time : int | float
        Time required to fasten a nacelle.

    Returns
    -------
    nacelle_fasten_time : float
        Time required to fasten nacelle (h).
    """

    key = "nacelle_fasten_time"
    fasten_time = kwargs.get(key, defaults[key])

    yield vessel.task("Fasten Nacelle", fasten_time, constraints={})


@process
def release_nacelle(vessel, contraints={}, **kwargs):
    """
    Returns time required to release nacelle from fastenings.

    Parameters
    ----------
    nacelle_release_time : int | float
        Time required to release nacelle.

    Returns
    -------
    nacelle_release_time : float
        Time required to release nacelle (h).
    """

    key = "nacelle_release_time"
    release_time = kwargs.get(key, defaults[key])

    yield vessel.task("Release Nacelle", release_time, constraints={})


@process
def lift_turbine_blade(vessel, constraints={}, **kwargs):
    """
    Calculates time required to lift turbine blade to hub height.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    hub_height : int | float
        Hub height above MSL (m).

    Returns
    -------
    blade_lift_time : float
        Time required to lift blade to hub height (h).
    """

    hub_height = kwargs.get("hub_height", None)
    crane_rate = vessel.crane.crane_rate(**kwargs)
    lift_time = hub_height / crane_rate

    yield vessel.task("Lift Blade", lift_time, constraints=constraints)


@process
def attach_turbine_blade(vessel, constraints={}, **kwargs):
    """
    Returns time required to attach turbine blade to hub.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    blade_attach_time : int | float
        Time required to attach turbine blade.

    Returns
    -------
    blade_attach_time : float
        Time required to attach turbine blade (h).
    """

    crane = vessel.crane
    key = "blade_attach_time"
    attach_time = kwargs.get(key, defaults[key])

    yield vessel.task("Attach Blade", attach_time, constraints=constraints)


@process
def fasten_turbine_blade(vessel, constraints={}, **kwargs):
    """
    Returns time required to fasten a blade at port.

    Parameters
    ----------
    blade_fasten_time : int | float
        Time required to fasten a blade at port.

    Returns
    -------
    blade_fasten_time : float
        Time required to fasten blade (h).
    """

    key = "blade_fasten_time"
    fasten_time = kwargs.get(key, defaults[key])

    yield vessel.task("Fasten Blade", fasten_time, constraints=constraints)


@process
def release_turbine_blade(vessel, constraints={}, **kwargs):
    """
    Returns time required to release turbine blade from fastening.

    Parameters
    ----------
    blade_release_time : int | float
        Time required to release turbine blade.

    Returns
    -------
    blade_release_time : float
        Time required to release turbine blade (h).
    """

    key = "blade_release_time"
    release_time = kwargs.get(key, defaults[key])

    yield vessel.task("Release Blade", release_time, constraints=constraints)


@process
def lift_tower_section(vessel, height, constraints={}, **kwargs):
    """
    Calculates time required to lift tower section at site.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    height : int | float
        Height above MSL (m) required for lift.

    Returns
    -------
    section_lift_time : float
        Time required to lift tower section (h).
    """

    crane_rate = vessel.crane.crane_rate(**kwargs)
    lift_time = height / crane_rate

    yield vessel.task("Lift Tower Section", lift_time, constraints=constraints)


@process
def attach_tower_section(vessel, constraints={}, **kwargs):
    """
    Returns time required to attach tower section at site.

    Parameters
    ----------
    vessel : Vessel
        Vessel to perform action.
    section_attach_time : int | float
        Time required to attach tower section (h).

    Returns
    -------
    section_attach_time : float
        Time required to attach tower section (h).
    """

    crane = vessel.crane
    key = "tower_section_attach_time"
    attach_time = kwargs.get(key, defaults[key])

    yield vessel.task("Attach Tower Section", attach_time, constraints=constraints)


@process
def fasten_tower_section(vessel, constraints={}, **kwargs):
    """
    Returns time required to fasten a tower section at port.

    Parameters
    ----------
    section_fasten_time : int | float
        Time required to fasten a tower section (h).

    Returns
    -------
    section_fasten_time : float
        Time required to fasten tower section (h).
    """

    key = "tower_section_fasten_time"
    fasten_time = kwargs.get(key, defaults[key])

    yield vessel.task("Fasten Tower Section", fasten_time, constraints=constraints)


@process
def release_tower_section(vessel, constraints={}, **kwargs):
    """
    Returns time required to release tower section from fastenings.

    Parameters
    ----------
    tower_section_release_time : int | float
        Time required to release tower section (h).

    Returns
    -------
    section_release_time : float
        Time required to release tower section (h).
    """

    key = "tower_section_release_time"
    release_time = kwargs.get(key, defaults[key])

    yield vessel.task("Release Tower Section", release_time, constraints=constraints)
