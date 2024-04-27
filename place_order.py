import argparse
import csp
import pandas as pd
from filelock import FileLock

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

    # df = pd.DataFrame({
    #     "order_number": [1,2,3,4,5],
    #     "sell": [100, 200, 300, 400, 500],
    #     "buy": [100, 200, 300, 400, 500]
    # })
    shared_file = "shared.csv"
    train_num = 5
    with FileLock(f"{shared_file}.lock"):
        ori_df = pd.read_csv(shared_file)
        # select first 5 rows that is not being read
        df = ori_df[ori_df['read'] == 0].head(5)
        # update the read to 1
        ori_df.loc[df.index, 'read'] = 1
        ori_df.to_csv(shared_file)

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


    

    
    
    

    






    



