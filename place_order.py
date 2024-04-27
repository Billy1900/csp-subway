import argparse
import csp
import pandas as pd

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
        "platforms", nargs="+", help="stop_id:service pair: see stops.txt for stop_id"
    )
    parser.add_argument(
        "--order_number",
        type=int,
        default="NULL",
        required=True,
        help="buy/sell"
    )
    parser.add_argument(
        "--order_type",
        type=str,
        default=None,
        required=True,
        choices=["B", "S"],
        help="buy/sell",
    )
    parser.add_argument(
        "--qty",
        type=float,
        default=None,
        required=True,
        help="quantity you buy/sell",
    )
    args = parser.parse_args()

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

    df = pd.DataFrame({
        "order_number": [1,2,3,4,5],
        "sell": [100, 200, timedelta(seconds=10), 400, 500],
        "buy": [1000, 200, timedelta(seconds=10), 400, 500],
        "trip_id": [1, 1, 1, 1, 1]
    })

    
    order_type = args.order_type
    order_num = args.order_number
    quantity = args.qty
    price = 0
    if order_type == 'S':
        price = df.loc[df['order_number'] == order_num, 'sell'].iloc[0]
        sign = '-'
    else:
        price = df.loc[df['order_number'] == order_num, 'buy'].iloc[0]
        sign = "+"
    trip_id = total = df.loc[df['order_number'] == order_num, 'trip_id'].iloc[0]
    total = price
    if order_type == 'S':
        total *= -1
    print(f"spent: {total}, contracts: {sign}{quantity}")
    


    csp.run(
        departure_board,
        [(stop_id, line)],
        5,
        "S",
        {"transaction": order_type, "trip_id": trip_id, "qty": quantity, "price": price},
        starttime=datetime.utcnow(),
        endtime=timedelta(minutes=100),
        realtime=True,
         )


    
    
    

    






    



