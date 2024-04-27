import argparse


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