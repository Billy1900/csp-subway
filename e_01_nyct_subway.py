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
ticks = {}
ticker = [0]
last_anticipated_arrival = [datetime.now()]
def entities_to_departure_board_str(entities, stop_id, dir, tracker, ticks, order):
    """
    Helper function to pretty-print train info
    """
    if not order:
        df = pd.DataFrame(columns = ["order_number", "sell", "buy", "trip_id", "read"])
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

            trip_id = entity.trip_update.trip.trip_id
            if trip_id not in ticks:
                ticks[trip_id] = 10
            else:
                ticks[trip_id] += 10

            if trip_id in tracker:
                tracker[trip_id]["current"] = round(delta.total_seconds())
                tracker[trip_id]["mult"] = (tracker[trip_id]["origin"]-tracker[trip_id]["current"])/ticks[trip_id]
            else:
                tracker[trip_id] = {}
                tracker[trip_id]["origin"] = round(delta.total_seconds())
                tracker[trip_id]["current"] = round(delta.total_seconds())
                tracker[trip_id]["mult"] = 1            

            if (tracker[trip_id]["mult"] > 1):
                ev = tracker[trip_id]["current"]/(((tracker[trip_id]["mult"]-1)/8)+1)
            else:
                ev =  tracker[trip_id]["current"]/(((tracker[trip_id]["mult"]-1)/4)+1)

            spread = ev * (0.2 * (math.e ** (-0.7*ticks[trip_id]/100)) + 0.1) 

            buy = ev + spread/2
            sell = ev - spread/2

            dep_str += f'{i}. {direction} {route} train to {STOP_INFO_DF.loc[terminus, "stop_name"]} in {math.floor(delta.total_seconds()/60)}:{(round(delta.total_seconds()%60)):02d} minutes\n'
            dep_str += f'Market: [Sell: {math.floor(sell/60)}:{(round(sell%60)):02d}, Buy: {math.floor(buy/60)}:{(round(buy%60)):02d}]\n\n'

            df.loc[i-1] = [i, sell, buy, trip_id, 0]
        
        if os.path.exists(shared_file):
            with FileLock(f"{shared_file}.lock"):
                ori_df = pd.read_csv(shared_file)
                ori_df = ori_df._append(df, ignore_index=True)  # append the new data
                ori_df.to_csv(shared_file, index=False)
        else:
            with FileLock(f"{shared_file}.lock"):
                df.to_csv(shared_file, index=False)

        return dep_str
    else:
        price = order["price"] 
        tracker_start = datetime.now()
        goal = tracker_start + timedelta(seconds=price-ticker[0])
        goal = goal.replace(microsecond=0)

        found = False
        for entity in entities:
            if entity.trip_update.trip.trip_id == order["trip_id"]:
                found = True
                route = entity.trip_update.trip.route_id
                direction = GTFS_DIRECTION[
                    entity.trip_update.trip.Extensions[
                        nyct_subway_pb2.nyct_trip_descriptor
                    ].direction
                ]
                terminus = get_terminus(entity)
                arrival = datetime.fromtimestamp(get_stop_time_at_station(entity, stop_id, dir))
                last_anticipated_arrival[0] = arrival
                delta = arrival - datetime.now()
                
                dep_str = f' {direction} {route} train to {STOP_INFO_DF.loc[terminus, "stop_name"]} in {math.floor(delta.total_seconds()/60)}:{(round(delta.total_seconds()%60)):02d} minutes\n'
                dep_str += f"Desired arrival time: "
                if order["transaction"] == 'B':
                    dep_str += f"later than {goal}\n"
                else:
                    dep_str += f"before {goal}\n"
                dep_str += f"Current anticipated arrival time: {arrival}\n"
                ticker[0] += 10
                return dep_str
        if not found:
            print(f"Actual arrival time: {last_anticipated_arrival[0]}")
            diff = last_anticipated_arrival[0] - goal
            pnl = diff.total_seconds() * order['qty']
            
            if order["transaction"] == 'S': 
                pnl *= -1 
            print(f'PNL: {pnl}')
            exit(-1)
            





@csp.graph
def departure_board(platforms: List[Tuple[str, str]], N: int, dir: str, print: dict):
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
            lambda x, key_=stop_id: entities_to_departure_board_str(x, key_, dir, tracker, ticks, print),
            str,
        )
        csp.print("", dep_str)



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