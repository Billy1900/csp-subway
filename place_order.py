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

    df = pd.DataFrame({
        "order_number": [1,2,3,4,5],
        "sell": [100, 200, 300, 400, 500],
        "buy": [100, 200, 300, 400, 500]
    })

    order_type = args.order_type
    order_num = args.order_number
    quantity = args.qty
    if order_type == "S":
        total = df.loc[df['order_number'] == order_num, 'sell'].iloc[0] * quantity
        sign = "-"
    else:
        total = df.loc[df['order_number'] == order_num, 'buy'].iloc[0] * -quantity
        sign = "+"
    print(f"spent: {total}, contracts: {sign}{quantity}")



    
    
    

    






    



