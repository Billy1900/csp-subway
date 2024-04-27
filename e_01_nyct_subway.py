import argparse
from datetime import datetime, timedelta
from typing import List, Tuple
import pandas as pd
import math
from filelock import FileLock
import os

import csp

from csp_mta import (
    GTFS_DIRECTION,
    LINE_TO_ENDPOINT,
    STOP_INFO_DF,
    GTFSRealtimeInputAdapter,
    nyct_subway_pb2,
)

shared_file = "shared.csv"


def get_stop_time_at_station(entity, stop_id, dir):
    """
    Helper Python function to get the stop time at a station
    """
    if entity.HasField("trip_update"):
        stop_time_updates = entity.trip_update.stop_time_update
        for update in stop_time_updates:
            # could be N or S
            if (
                stop_id in update.stop_id
                and datetime.fromtimestamp(update.arrival.time) >= datetime.now()
                and update.stop_id == f"{stop_id}{dir}"
            ):
                return update.arrival.time
    return None


@csp.node
def filter_trains_headed_for_stop(
    gtfs_msgs: csp.ts[object], stop_id: str, dir: str,
) -> csp.ts[object]:
    """
    Filters the GTFS messages to only include trains that are currently headed for a stop with a given stop_id, found in stops.txt
    Any train that has either passed the stop or does not stop at said stop will be ignored
    """
    relevant_entities = []
    for entity in gtfs_msgs.entity:
        if get_stop_time_at_station(entity, stop_id, dir):
            relevant_entities.append(entity)

    return relevant_entities


@csp.node
def next_N_trains_at_stop(
    gtfs_msgs: csp.ts[object], stop_id: str, N: int, dir: str
) -> csp.ts[object]:
    """
    Returns the TripUpdate objects of the next N trains approaching the stop
    """
    gtfs_msgs.sort(key=lambda entity: get_stop_time_at_station(entity, stop_id, dir))
    return gtfs_msgs[:N]


def get_terminus(entity):
    return entity.trip_update.stop_time_update[-1].stop_id

tracker = {}
ticks = [0]
def entities_to_departure_board_str(entities, stop_id, dir, tracker, ticks):
    """
    Helper function to pretty-print train info
    """
    df = pd.DataFrame(columns = ["order_number", "sell", "buy", "read"])
    dep_str = f'\n At station {STOP_INFO_DF.loc[stop_id, "stop_name"]}\n\n'
    i = 0
    for entity in entities:
        route = entity.trip_update.trip.route_id
        
        direction = GTFS_DIRECTION[
            entity.trip_update.trip.Extensions[
                nyct_subway_pb2.nyct_trip_descriptor
            ].direction
        ]
        i += 1
        terminus = get_terminus(entity)
        arrival = datetime.fromtimestamp(get_stop_time_at_station(entity, stop_id, dir))
        delta = arrival - datetime.now()

        if entity.trip_update.trip.trip_id in tracker:
            tracker[entity.trip_update.trip.trip_id]["current"] = round(delta.total_seconds())
            tracker[entity.trip_update.trip.trip_id]["mult"] = (tracker[entity.trip_update.trip.trip_id]["origin"]-tracker[entity.trip_update.trip.trip_id]["current"])/ticks[0]
        else:
            tracker[entity.trip_update.trip.trip_id] = {}
            tracker[entity.trip_update.trip.trip_id]["origin"] = round(delta.total_seconds())
            tracker[entity.trip_update.trip.trip_id]["current"] = round(delta.total_seconds())
            tracker[entity.trip_update.trip.trip_id]["mult"] = 1            

        if (tracker[entity.trip_update.trip.trip_id]["mult"] > 1):
            ev = tracker[entity.trip_update.trip.trip_id]["current"]/(((tracker[entity.trip_update.trip.trip_id]["mult"]-1)/8)+1)
        else:
            ev =  tracker[entity.trip_update.trip.trip_id]["current"]/(((tracker[entity.trip_update.trip.trip_id]["mult"]-1)/4)+1)

        spread = ev * (0.2 * (math.e ** (-0.7*ticks[0]/100)) + 0.1) 

        buy = ev + spread/2
        sell = ev - spread/2


        dep_str += f'{i}. {direction} {route} train to {STOP_INFO_DF.loc[terminus, "stop_name"]} ({terminus}) in {round(delta.total_seconds())} seconds\n'
        dep_str += f'Market: [Sell: {sell}, Buy: {buy}]\n\n'

        df.loc[i-1] = [i, ev, ev, 0] # 0: not being read; 1: being read

    if os.path.exists(shared_file):
        with FileLock(f"{shared_file}.lock"):
            ori_df = pd.read_csv(shared_file)
            ori_df: pd.DataFrame = ori_df.append(df, ignore_index=True)  # append the new data
            ori_df.to_csv(shared_file, index=False)
    else:
        with FileLock(f"{shared_file}.lock"):
            df.to_csv(shared_file, index=False)

    print(tracker)
    ticks[0] += 10
    return dep_str


@csp.graph
def departure_board(platforms: List[Tuple[str, str]], N: int, dir: str):
    """s
    csp graph which ticks out the next N trains approaching the provided stations on each given line
    """
    for service in platforms:
        stop_id, line = service
        line_data = GTFSRealtimeInputAdapter(line, False)
        trains_headed_for_station = filter_trains_headed_for_stop(line_data, stop_id, dir)
        next_N_trains = next_N_trains_at_stop(trains_headed_for_station, stop_id, N, dir)
        dep_str = csp.apply(
            next_N_trains,
            lambda x, key_=stop_id: entities_to_departure_board_str(x, key_, dir, tracker, ticks),
            str,
        )
        csp.print("Departure Board", dep_str)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Print a realtime departure board at a set of stations."
    )
    parser.add_argument(
        "platforms", nargs="+", help="stop_id:service pair: see stops.txt for stop_id"
    )
    parser.add_argument(
        "--show_graph",
        action="store_true",
        default=False,
        help="Boolean flag indicating if the graph should be shown",
    )
    parser.add_argument(
        "--run_graph",
        action="store_true",
        default=True,
        help="Boolean flag indicating if the graph should be run",
    )
    parser.add_argument(
        "--num_trains",
        type=int,
        default=5,
        help="Number of trains for each line to show on the departure board",
    )

    args = parser.parse_args()
    platforms = args.platforms
    show_graph = args.show_graph
    run_graph = args.run_graph
    num_trains = args.num_trains

    # Process input data
    platforms_to_subscribe_to = []
    for platform in args.platforms:
        stop_id, train_line = tuple(platform.split(":"))

        # process which line to track
        found = False
        for line in LINE_TO_ENDPOINT.keys():
            if train_line in line:
                train_line = line
                found = True
                break
        if not found:
            raise ValueError(f"Did not recognize service {train_line}")

        # process stop_id
        if stop_id not in STOP_INFO_DF.index:
            raise ValueError(
                f"Did not recognize stop_id {stop_id}: see stops.txt for valid stop_ids"
            )

        platforms_to_subscribe_to.append((stop_id, train_line))

    if show_graph:
        csp.show_graph(
            departure_board,
            platforms_to_subscribe_to,
            num_trains,
            graph_filename="departure_board.png",
        )
    if run_graph:
        csp.run(
            departure_board,
            platforms_to_subscribe_to,
            1,
            dir,
            starttime=datetime.utcnow(),
            endtime=timedelta(seconds=5),
            realtime=True,
        )
