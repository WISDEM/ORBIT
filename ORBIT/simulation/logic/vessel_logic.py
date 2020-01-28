"""This module contains common simulation logic related to vessels."""

__author__ = ["Jake Nunemaker", "Rob Hammond"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from ORBIT.vessels import tasks
from ORBIT.simulation.exceptions import ItemNotFound

from .port_logic import get_list_of_items_from_port


def shuttle_items_to_queue(
    env, vessel, port, queue, distance, items, **kwargs
):
    """
    Shuttles a list of items from port to queue.

    Parameters
    ----------
    env : Environemt
    vessel : Vessel
    port : Port
    queue : simpy.Resource
        Queue object to shuttle to.
    distance : int | float
        Distance between port and site (km).
    items : list
        List of components stored as tuples to shuttle.
        - ('key', 'value')
    """

    transit_time = vessel.transit_time(distance)

    transit = {
        "agent": vessel.name,
        "location": "At Sea",
        "type": "Operations",
        "action": "Transit",
        "duration": transit_time,
        **vessel.transit_limits,
    }

    while True:

        if vessel.at_port:
            env.logger.debug(
                "{} is at port.".format(vessel.name),
                extra={
                    "agent": vessel.name,
                    "time": env.now,
                    "type": "Status",
                },
            )

            if not port.items:
                env.logger.debug(
                    "No items at port. Shutting down.",
                    extra={
                        "agent": vessel.name,
                        "time": env.now,
                        "type": "Status",
                    },
                )
                break

            # Get list of items
            try:
                yield env.process(
                    get_list_of_items_from_port(
                        env, vessel, items, port, **kwargs
                    )
                )

            except ItemNotFound:
                # If no items are at port and vessel.storage.items is empty,
                # the job is done
                if not vessel.storage.items:
                    env.logger.debug(
                        "Item not found. Shutting down.",
                        extra={
                            "agent": vessel.name,
                            "time": env.now,
                            "type": "Status",
                        },
                    )
                    break

            # Transit to site
            vessel.update_trip_data()
            vessel.at_port = False
            yield env.process(env.task_handler(transit))
            vessel.at_site = True

        if vessel.at_site:
            env.logger.debug(
                "{} is at site.".format(vessel.name),
                extra={
                    "agent": vessel.name,
                    "time": env.now,
                    "type": "Status",
                },
            )

            # Join queue to be active feeder at site
            with queue.request() as req:
                queue_start = env.now
                yield req

                queue_time = env.now - queue_start
                if queue_time > 0:
                    env.logger.info(
                        "",
                        extra={
                            "agent": vessel.name,
                            "time": env.now,
                            "type": "Delay",
                            "action": "Queue",
                            "duration": queue_time,
                            "location": "Site",
                        },
                    )

                queue.vessel = vessel
                active_start = env.now
                queue.activate.succeed()

                # Released by WTIV when objects are depleted
                vessel.release = env.event()
                yield vessel.release
                active_time = env.now - active_start
                env.logger.info(
                    "",
                    extra={
                        "agent": vessel.name,
                        "time": env.now,
                        "type": "Operations",
                        "action": "ActiveFeeder",
                        "duration": active_time,
                        "location": "Site",
                    },
                )

                queue.vessel = None
                queue.activate = env.event()

            # Transit back to port
            vessel.at_site = False
            yield env.process(env.task_handler(transit))
            vessel.at_port = True
