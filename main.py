import argparse
import csp
import os

from csp_mta import (
    GTFS_DIRECTION,
    LINE_TO_ENDPOINT,
    STOP_INFO_DF,
    GTFSRealtimeInputAdapter,
    nyct_subway_pb2,
)

# sample run: csp-subway % python main.py --filename "TEST" --direction "N" --side "buy" --qty 1.0 635:456;  

from datetime import datetime, timedelta
from e_01_nyct_subway import get_stop_time_at_station, filter_trains_headed_for_stop, next_N_trains_at_stop, get_terminus, entities_to_departure_board_str, departure_board;

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--filename",
        type=str,
        default=None,
        required=True,
        help="File which stores the recorded data",
    )
    parser.add_argument(
        "platforms", nargs="+", help="stop_id:service pair: see stops.txt for stop_id"
    )
    parser.add_argument(
        "--direction",
        type=str,
        default="NULL",
        required=True,
        help="direction"
    )
    parser.add_argument(
        "--side",
        type=str,
        default="NULL",
        choices=["buy", "sell"],
        required=True,
        help="buy/sell"
    )
    parser.add_argument(
        "--qty",
        type=float,
        default=None,
        required=True,
        help="qunatity you buy/sell"
    )
    args = parser.parse_args()

    #stop_id = args.stop_id
    #line = args.line

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
    

    csp.run(
            departure_board,
            [(stop_id, line)],
            10,
            starttime=datetime.utcnow(),
            endtime=timedelta(minutes=1),
            realtime=True,
        )
    

    






    



