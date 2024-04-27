import argparse
import datetime
from datetime import datetime, timedelta
import csp
from csp.adapters.parquet import ParquetReader
from csp_mta import gtfs_realtime_pb2

import pytz
ET = pytz.timezone('America/New_York')

@csp.node
def raw_bytes_to_gtfs_message(raw: csp.ts[str]) -> csp.ts[object]:
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(raw.encode("latin-1"))
    return feed


def get_stop_time_at_station(entity, stop_id, direction):
    """
    Helper Python function to get the stop time at a station
    Same as e_01 helper except that this one is directional
    """
    if entity.HasField("trip_update"):
        stop_time_updates = entity.trip_update.stop_time_update
        for update in stop_time_updates:
            # could be N or S
            if update.stop_id == stop_id + direction:
                return update.arrival.time
    return None

@csp.node
def wait_time(feed_msgs: csp.ts[object], stop_id: str) -> csp.Outputs(
    uptown_wait=csp.ts[timedelta], downtown_wait=csp.ts[timedelta]
):
    """
    Posted wait time in both directions from the stop - not really "true" wait time since we don't check
    if the trains actually arrived when they said they would.
    """
    n_min, s_min = timedelta.max, timedelta.max
    print("start")
    for entity in feed_msgs.entity:
        for direction in ("N", "S"):
            t = get_stop_time_at_station(entity, stop_id, direction)
            if t is not None:
                # Some careful notes on timing in csp...
                # The stop time that we load from file is in Eastern time since that's what the MTA reports it as
                # But csp.now() and the engine time (which is recorded in our parquet files) uses UTC!
                # Thus, be very careful about comparing them, making sure to localize first
                stop_time = ET.localize(datetime.fromtimestamp(t))
                current_time = pytz.timezone('UTC').localize(csp.now())
                wait = stop_time - current_time
                print(wait)
                if wait >= timedelta(0):
                    if direction == "N":
                        n_min = min(n_min, wait)
                    else:
                        s_min = min(s_min, wait)
            
    print("done")
    if n_min != timedelta.max and s_min != timedelta.max:
        return csp.output(uptown_wait=n_min, downtown_wait=s_min)

@csp.graph
def train_wait_func(filename: str, stop_id: str) -> csp.Outputs(
    mean=csp.ts[float], std=csp.ts[float]
):
    raw_bytes = ParquetReader(
        filename_or_list=filename, time_column="time"
    ).subscribe_all(typ=str, field_map="msg")
    gtfs = raw_bytes_to_gtfs_message(raw_bytes)
    print("1")
    wait_times = wait_time(gtfs, stop_id)

    bidirectional_wait_times = csp.flatten(
        [
            csp.apply(wait_times.uptown_wait, lambda x: x.total_seconds(), float),
            csp.apply(wait_times.downtown_wait, lambda x: x.total_seconds(), float),
        ]
    )

    trigger = csp.timer(timedelta(hours=1), True)
    avg_wait_time = csp.stats.mean(
        bidirectional_wait_times,
        interval=timedelta(hours=1),
        min_window=None,
        trigger=trigger,
    )
    std_wait_time = csp.stats.stddev(
        bidirectional_wait_times,
        interval=timedelta(hours=1),
        min_window=None,
        trigger=trigger,
    )

    return csp.output(mean=avg_wait_time, std=std_wait_time)


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
        choices=["N", "S"],
        default="NULL",
        required=True,
        help="North (N)/South (S)"
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

    start = datetime(2024, 4, 21, 19)
    start = ET.localize(start)
    end = datetime(2024, 4, 22, 6)
    end = ET.localize(end)

    res = csp.run(
        train_wait_func, # main function
        args.filename,
        args.stop_id,
        starttime=start,
        endtime=end,
    )