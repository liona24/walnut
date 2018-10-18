import threading
from time import sleep


class BaseTrader(object):

    thread = None
    storage = None
    symbol = None
    eval_interval = None
    callback = None

    _stop_event = None

    def __init__(self, symbol, storage, eval_interval, callback,
                 name=None, daemon=None):

        self.symbol = symbol
        self.storage = storage
        self.eval_interval = eval_interval
        self.callback = callback

        self._stop_event = threading.Event()

        self.thread = threading.Thread(target=self._trade,
                                       name=name,
                                       daemon=daemon)

    def _get_signal(self, timeseries):
        """Return the trading signal given the series of prices.

        :timeseries: - A ``pd.Series`` of prices.

        Returns:
            An ``Order`` as defined by the schema.
        """
        raise NotImplementedError

    def _evaluate(self):
        with self.storage(self.symbol) as data:
            series = data.to_series()

        signal = self._get_signal(series)
        if signal:
            self.callback(signal)

    def _trade(self):
        while True:
            if self._stop_event.is_set():
                break

            self._evaluate()

            sleep(self.eval_interval)

    def start(self):
        self._stop_event.clear()
        self.thread.start()

    def request_end(self):
        self._stop_event.set()

    def force_eval(self):
        self._evaluate()
