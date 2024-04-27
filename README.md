# SubExchange

The subway system is a central part of life for many people in New York City. The MTA provides a convenient and wide-spanning public transit network that moves millions of New York residents to and from different areas of the city every day. However, we envision the possibility of making subway riders' daily commutes even more exciting.

## A Market for MTA Arrival Time Contracts

Inspired by new ideas in event prediction markets, we explore the potential for tradeable contracts for MTA subway times. We formulate a tradeable instrument that provides a fascinating new way to get financial exposure to the daily operations of the New York subway system.

SubExchange contracts are defined by three parameters:
1. Train ID
2. Station
3. Creation Time

Contracts tied to a particular train and corresponding station are exercised when the train arrives at that station, and the holder of the contract is paid the elapsed time, in minutes, between the contract's creation time and the time of arrival. 
* We expect that new contracts will be created at a price that reflects how long the predicted arrival time is from the creation (current) time.
* When a user buys a contract, they are betting that the actual arrival time of the train will be later than the predicted arrival time when the contract was originally created.
* Likewise, a user can sell a contract to bet that the train will arrive earlier than the predicted arrival time at the time of creation.

## Not Just Trading: Long-Term Social Benefits

```shell
python place_order.py --order_number 3 --order_type B --qty 10
python real_time.py --filename TEST --direction S 635:456    
```
