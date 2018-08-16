from jsonschema import validate
from dateutil import parser

import os
import datetime
import json
from threading import RLock
from collections import defaultdict

from walnut.timeseries import FixedHorizonTimeSeries
from walnut.storage import Storage

_dir = os.path.dirname(__file__)


class Engine(object):
    """The main application wrapper.

    All methods on this object are thread-safe.
    """

    schema_file = os.path.join(_dir, 'schema_definitions.json')

    traders = None
    horizon = None
    storage = None
    schema_definitions = None

    __lock = None

    def __init__(self, horizon, new_trader):
        """Initialize a new application.

        :horizon: - The time horizon to store tick data for. This has to be
            either a `datetime.timedelta` or a dictionary containing the kvargs
            to initialize one.
        :new_trader: - A callable (symbol: str, storage: Storage) -> BaseTrader
            which returns a new trader for the given symbol
        """
        self.traders = {}
        self.new_trader = new_trader

        if type(horizon) == datetime.timedelta:
            self.horizon = horizon
        else:
            self.horizon = datetime.timedelta(**horizon)

        def storage_obj_creator():
            return FixedHorizonTimeSeries(self.horizon)

        self.storage = Storage(storage_obj_creator)

        with open(self.schema_file, 'r') as f:
            self.schema_definitions = json.load(f)

        self.__lock = RLock()

    def tick(self, tick_data):
        """Handles a `tick` event.

        The tick events are persisted into memory. Eventually they are
        processed by the trading engine (if it is running).

        :tick_data: - The data representing the tick event. It should follow
            the schema definitions for 'tick'
        """

        validate(tick_data, self.schema_definitions['tick'])

        with self.storage(tick_data['symbol']) as data:
            timestamp = None
            if 'timestamp' in tick_data:
                timestamp = parser.parse(tick_data['timestamp'])

            data.append(float(tick_data['price']), timestamp=timestamp)

    def stop(self, symbol):
        """Stops trading on the specified symbol.

        Raises ValueError if no trader is active for the given symbol.
        """
        with self.__lock:
            if symbol not in self.traders:
                raise ValueError('Trader for the specified symbol (%s) not started.' % symbol)  # noqa E501

            self.traders.pop(symbol).request_end()

    def start(self, symbol):
        """Starts trading on the specified symbol.

        Trades are reported to the given callback in the format specified by
        the schema. Raises ValueError if a trader for the given symbol is
        already active.
        The trader evaluates all data every `eval_interval` seconds or if the
        application is in time travel mode, every `eval_interval` ticks.
        """
        with self.__lock:
            if symbol in self.traders:
                raise ValueError('Trader for the specified symbol (%s) already running' % symbol)  # noqa E501

            trader = self.new_trader(symbol, self.storage)
            self.traders[symbol] = trader
            trader.run()


class TestEngine(Engine):
    """The main application wrapper extended to a time travel mode for testing.
    """

    def __init__(self, horizon, new_trader):
        Engine.__init__(self, horizon, new_trader)

    def tick_many(self, tick_iter, eval_every, skip=0):
        """Emulate a collection of ticks and evaluate every `eval_every` ticks.

        Arguments:
            tick_iter {iterable} -- An iterator over a collection of tick_data
            eval_every {int} -- Evaluation interval in number of ticks

        Keyword Arguments:
            skip {int} -- Optional: Skips a number of ticks before evaluating.
                (default: {0})
        """
        tick_counts = defaultdict(lambda: -skip)
        traders = {}
        for tick_data in tick_iter:
            self.tick(tick_data)

            symbol = tick_data['symbol']
            tick_counts[symbol] += 1
            tc = tick_counts[symbol]
            if tc >= 0 and tc % eval_every == 0:
                tick_counts[symbol] = 0

                if symbol not in traders:
                    # note that this is kinda hacky:
                    # we abuse the fact that the eval interval is not used
                    # outside of the running mode
                    traders[symbol] = self.new_trader(symbol, self.storage)

                traders[symbol].force_eval()
