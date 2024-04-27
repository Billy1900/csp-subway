import argparse
import csp
import os
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
        "--line",
        type=str,
        default="NULL",
        required=True,
        help="line ID, such as ACE"
    )
    parser.add_argument(
        "--stop_id",
        type=str,
        default=None,
        required=True,
        help="stop_id from data/stops.txt",
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

    stop_id = args.stop_id
    line = args.line

    csp.run(
            departure_board,
            [(stop_id, line)],
            10,
            starttime=datetime.utcnow(),
            endtime=timedelta(minutes=1),
            realtime=True,
        )
    

    






    



