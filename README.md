# walnut


This is a simple trading engine. It enables storing of tick events in memory
and running background analysis tasks.

The module exposes two main modules ```Engine``` and ```TestEngine```. The latter is extended by a time travel mode for testing
purposes.

In order to use an engine you are required to create a trader. A basic trader (which provides sample orders) can be created like this:
```python
import walnut.trading as trading

class DummyTrader(trading.BaseTrader):
    def __init__(self, symbol, storage, eval_interval, callback, name=None, daemon=None):
        trading.BaseTrader.__init__(self, symbol, storage, eval_interval, callback, name, daemon)

    def _get_signal(self, timeseries):
        return { 'timestamp': '2018-08-15T12:12:12', 'type': 'short', 'symbol': self.symbol }
```

The `symbol` and `storage` are used by the engine to determine which data to use. Each tick-event-stream is associated with one symbol.
Every `eval_interval` number of seconds this trader wakes and calls `_get_signal(..)` in order to evaluate the latest observed prices. This method may return `None` or an *Order*. The Order should be constructed using the corresponding schema definitions.
If an order was issued, the `callback` will be called with this order as argument.

Optionally you can run this trader as daemon and give it a desirable name.


This trader can then be used in conjunction with a trading engine:
```python
import walnut
import walnut.trading as trading

class DummyTrader(trading.BaseTrader):
    ...

def new_trader(symbol, storage):
    # new trader which evaluates every 5 seconds and simply prints orders
    return DummyTrader(symbol, storage, 5, print)

# new engine which stores tick data for up to 1 hour
engine = walnut.Engine({ 'hours': 1 }, new_trader)

# store tick data for every symbol you wish
engine.tick({ 'price': 1.3, 'symbol': 'TEST' })
# ...
# create and run a new trader for the given symbol
engine.start('TEST')
engine.tick({ 'price': 1.7, 'symbol': 'TEST', 'timestamp': '2018-08-15T12:12:12' })

# request shutdown of the trader for the given symbol.
# Eventually it will shutdown in the next evaluation phase.
engine.stop('TEST')
```
