# SubExchange

The subway system is a central part of life for many people in New York City. The MTA provides a convenient and wide-spanning public transit network that moves millions of New York residents to and from different areas of the city every day. However, we envision the possibility of making subway riders' daily commutes even more exciting.

## A Market for Subway Time Contracts

Inspired by new ideas in event prediction markets, we explore the potential for tradeable contracts for MTA subway times. We formulate a tradeable instrument that provides a fascinating new way to get financial exposure to the daily operations of the New York subway system.

SubExchange contracts are defined by three parameters:
1. Train ID
2. Station
3. Creation Time

When a user purchases (sells) a contract, betting on the late (early) arrival of a particular train at a particular station, he is debited or credited a dollar for every second to arrival.

* For example, when a user purchases a contract stating a train will arrive in 2:37 minutes, he is debited $157 and becomes slightly more excited at the idea of a delayed train. Likewise, a user that sells a contract stating the train will arrive in 8:43 minutes is credited $43, and is betting that the train will get here sooner.

When the train arrives at the station, the user must close out their position by counteracting the original trade for the price of the realized elapsed time. 

* If the train from the first user's example actually arrives in 2:12 minutes, he must sell his contract for $132, realizing a loss of $25. If the train from the second user's example actually arrives in 6:37, she profits $126 and has a much happier ride to work.

As a market maker, we price these contracts with the expectation that, in the long run, our superior knowledge of MTA delays and transit times will make this a profitable venture.

## Long-Term Social Benefits, Not Just for Traders

As developers with financial backgrounds ourselves, we think it's really exciting to apply ideas of financial markets to a practical aspect of our daily lives and create direct monetary and entertainment value. What excites us even more about this project is in the value it can create beyond just trading and speculative betting.

In any financial market, traders aim to identify and profit off of market inefficiencies, or asset mispricings. Over long periods of time, asset mispricings are continuously arbitraged out, and asset prices approach increasingly fair values representative of available information. 

Drawing inspiration from this behavior of financial markets, we find a very exciting way to create long-term value for subway riders. The subway system is often subject to delays and estimation errors regarding arrival times, which can be quite detrimental to the experience of subway riders. The ability of traders to rectify mispricings in the value of SubExchange contracts contributes to more accurate estimations for subway scheduling. In the long term, increasingly efficient and competitive markets on our time contracts translates to better timing information and scheduling systems for the general public. **In other words, market participants are financially rewarded for contributing to the improvement of public infrastructure!**

## Our Vision: Time Contracts for Many Industries

Our methodology formulates a new class of financial instruments to speculate and trade on the timing of events. Beyond the MTA, we believe in the possibility of markets for time contracts in various different industries. There is vast potential to contribute to efficiency in scheduling and logistical applications in various sectors. 
* For example, time contracts on shipping could allow companies to more accurately inform themselves and their customers as well as trade to hedge against delays. In the long term, market-informed improvements in scheduling and logistical processes will support global trade.

The key innovation of our time contract methodology lies in allowing market participants to "trade time" and profit from helping improve scheduling-intensive processes in many parts of the global economy.

## Extensions

* Allow users to close out contracts before expiration (train arrival)
* Bet on multiple trains simultaneously
* Accomodate more order flow (and adjust spreads accordingly)



```shell
# sample program to retrieve data on all 4/5/6 trains heading south from station 635 (14 St. Union Sq.)
python real_time.py --direction S 635:456  
# sample program to execute by order of third listed market for 10 units, 
python place_order.py --order_number 3 --order_type B --qty 10 635:456
```
