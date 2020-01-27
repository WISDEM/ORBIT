"""This module contains common simulation logic related to vessels."""

__author__ = ["Jake Nunemaker", "Rob Hammond"]
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from marmot import process

from ORBIT.core._defaults import process_times as pt
from ORBIT.core.exceptions import ItemNotFound


@process
def get_item_from_storage(
    vessel, item, action_vessel=None, release=False, **kwargs
):
    """
    Generic item retrieval process.
    Subprocesses:
    - release 'item'

    Parameters
    ----------
    item : str
        Hook to find 'item' in 'vessel.storage' with attr {'type': 'item'}.
    vessel : Vessel
        Vessel to pick monopile from.
    action_vessel : Vessel (optional)
        If defined, the logging statement uses this vessel.
    release : bool (optional)
        If True, triggers vessel.release.succeed() when vessel.storage is empty.
        Used for WTIV + Feeder strategy to signal when feeders can leave.
    """

    if action_vessel is None:
        action_vessel = vessel

    try:
        item = vessel.storage.get_item(item)

    except ItemNotFound as e:
        vessel.submit_debug_log(message="Item not found")
        raise e

    action, time = item.release()
    yield vessel.task(action, time, constraints=vessel.transit_limits)

    if release and vessel.storage.any_remaining(item) is False:
        vessel.release.succeed()

    return item


@process
def prep_for_site_operations(vessel, survey_required=False, **kwargs):
    """
    Performs preperation process at site.

    Parameters
    ----------
    vessel : Vessel
    depth : int | float
        Site depth (m).
    extension : int | float
        Jack-up extension length (m).

    Yields
    ------
    task_list : list
        List of tasks included in preperation process.
    """

    site_depth = kwargs.get("site_depth", None)
    extension = kwargs.get("extension", site_depth + 10)

    position_time = pt["site_position_time"]
    jackup_time = vessel.jacksys.jacking_time(extension, site_depth)

    yield vessel.task(
        "PositionOnsite", position_time, constraints=vessel.transit_limits
    )
    yield vessel.task("Jackup", jackup_time, constraints=vessel.transit_limits)

    if survey_required:
        survey_time = tasks.rov_survey(**kwargs)
        yield vessel.task(
            "RovSurvey", survey_time, constraints=vessel.transit_limits
        )


# TODO:
# def shuttle_items_to_queue(
#     env, vessel, port, queue, distance, items, **kwargs
# ):
#     """
#     Shuttles a list of items from port to queue.

#     Parameters
#     ----------
#     env : Environemt
#     vessel : Vessel
#     port : Port
#     queue : simpy.Resource
#         Queue object to shuttle to.
#     distance : int | float
#         Distance between port and site (km).
#     items : list
#         List of components stored as tuples to shuttle.
#         - ('key', 'value')
#     """

#     transit_time = vessel.transit_time(distance)

#     transit = {
#         "agent": vessel.name,
#         "location": "At Sea",
#         "type": "Operations",
#         "action": "Transit",
#         "duration": transit_time,
#         **vessel.transit_limits,
#     }

#     while True:

#         if vessel.at_port:
#             env.logger.debug(
#                 "{} is at port.".format(vessel.name),
#                 extra={
#                     "agent": vessel.name,
#                     "time": env.now,
#                     "type": "Status",
#                 },
#             )

#             if not port.items:
#                 env.logger.debug(
#                     "No items at port. Shutting down.",
#                     extra={
#                         "agent": vessel.name,
#                         "time": env.now,
#                         "type": "Status",
#                     },
#                 )
#                 break

#             # Get list of items
#             try:
#                 yield env.process(
#                     get_list_of_items_from_port(
#                         env, vessel, items, port, **kwargs
#                     )
#                 )

#             except ItemNotFound:
#                 # If no items are at port and vessel.storage.items is empty,
#                 # the job is done
#                 if not vessel.storage.items:
#                     env.logger.debug(
#                         "Item not found. Shutting down.",
#                         extra={
#                             "agent": vessel.name,
#                             "time": env.now,
#                             "type": "Status",
#                         },
#                     )
#                     break

#             # Transit to site
#             vessel.update_trip_data()
#             vessel.at_port = False
#             yield env.process(env.task_handler(transit))
#             vessel.at_site = True

#         if vessel.at_site:
#             env.logger.debug(
#                 "{} is at site.".format(vessel.name),
#                 extra={
#                     "agent": vessel.name,
#                     "time": env.now,
#                     "type": "Status",
#                 },
#             )

#             # Join queue to be active feeder at site
#             with queue.request() as req:
#                 queue_start = env.now
#                 yield req

#                 queue_time = env.now - queue_start
#                 if queue_time > 0:
#                     env.logger.info(
#                         "",
#                         extra={
#                             "agent": vessel.name,
#                             "time": env.now,
#                             "type": "Delay",
#                             "action": "Queue",
#                             "duration": queue_time,
#                             "location": "Site",
#                         },
#                     )

#                 queue.vessel = vessel
#                 active_start = env.now
#                 queue.activate.succeed()

#                 # Released by WTIV when objects are depleted
#                 vessel.release = env.event()
#                 yield vessel.release
#                 active_time = env.now - active_start
#                 env.logger.info(
#                     "",
#                     extra={
#                         "agent": vessel.name,
#                         "time": env.now,
#                         "type": "Operations",
#                         "action": "ActiveFeeder",
#                         "duration": active_time,
#                         "location": "Site",
#                     },
#                 )

#                 queue.vessel = None
#                 queue.activate = env.event()

#             # Transit back to port
#             vessel.at_site = False
#             yield env.process(env.task_handler(transit))
#             vessel.at_port = True


@process
def get_list_of_items_from_port(vessel, port, items, **kwargs):
    """
    Retrieves multiples of 'items' from port until full.

    Parameters
    ----------
    TODO:
    items : list
        List of tuples representing items to get from port.
        - ('key': 'value')
    port : Port
        Port object to get items from.
    """

    with port.crane.request() as req:
        # Join queue to be active vessel at port
        queue_start = vessel.env.now
        yield req
        queue_time = vessel.env.now - queue_start
        if queue_time > 0:
            vessel.submit_action_log("Queue", queue_time)

        while True and port.items:
            buffer = []
            for i in items:
                item = port.get_item(i)
                buffer.append(item)

            # Calculate deck space and weight of one complete turbine
            total_deck_space = sum([item.deck_space for item in buffer])
            proposed_deck_space = (
                vessel.storage.current_deck_space + total_deck_space
            )

            total_weight = sum([item.weight for item in buffer])
            proposed_weight = (
                vessel.storage.current_cargo_weight + total_weight
            )

            if proposed_deck_space > vessel.storage.max_deck_space:
                vessel.submit_debug_log(message="Full")

                for item in buffer:
                    port.put(item)

                if vessel.storage.current_cargo_weight > 0:
                    break

                else:
                    raise VesselCapacityError(vessel, items)

            elif proposed_weight > vessel.storage.max_cargo_weight:
                vessel.submit_debug_log(message="Full")

                for item in buffer:
                    port.put(item)

                if vessel.storage.current_cargo_weight > 0:
                    break

                else:
                    raise VesselCapacityError(vessel, items)

            else:
                for item in buffer:
                    action, time = item.fasten()
                    yield vessel.task(
                        action, time, constraints=vessel.transit_limits
                    )
                    vessel.storage.put_item(item)

                    # if item["type"] == "Carousel":
                    #     vessel.carousel = SimpleNamespace(**item)

                    # vessel.submit_debug_log(message=f"{item['type']} Retrieved")
