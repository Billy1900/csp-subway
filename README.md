# SubExchange

The subway system is a central part of life for many people in New York City. The MTA provides a convenient and wide-spanning public transit network that moves millions of New York residents to and from different areas of the city every day. However, we envision the possibility of making subway riders' daily commutes even more exciting.

## A Market for MTA Arrival Time Contracts

Inspired by new ideas in event prediction markets, we explore the potential for tradeable contracts for MTA subway times. We formulate a tradeable instrument that provides a fascinating new way to get financial exposure to the daily operations of the New York subway system.

SubExchange contracts are defined by three parameters:
1. Train ID
2. Station
3. Creation Time

When a user purchases (sells) a contract, betting on the late (early) arrival of a particular train at a particular station, he is debited or credited a dollar for every second to arrival.

* i.e.,  when a user purchases a contract stating a train will arrive in 2:37 minutes, he is debited $157 and becomes slightly more excited at the idea of a delayed train. Likewise, a user that sells a contract stating the train will arrive in 8:43 minutes is credited $43, and is betting that the train will get here sooner.

When the train arrives at the station, the user must close out their position by counteracting the original trade for the price of the realized elapsed time. 

* If the train from the first user's example actually arrives in 2:12 minutes, he must sell his contract for $132, realizing a loss of $25. If the train from the second user's example actually arrives in 6:37, she profits $126 and has a much happier ride to work.

As a market maker, we price these contracts with the expectation that, in the long run, our superior knowledge of MTA delays and transit times will make this a profitable venture.

## Not Just Trading: Long-Term Social Benefits

```shell
python place_order.py --order_number 3 --order_type B --qty 10
python real_time.py - --direction S 635:456    
```
