import pandas as pd

from collections import OrderedDict
import datetime


class TimeSeries(object):
    """An object representing timestamp-value pairs."""

    def __init__(self, iterable=None):
        """Initialize a new `TimeSeries`.

        :iterable: - A iterable of key-value-pairs to be added to the series
            initially.
        """
        if iterable is None:
            iterable = []
        self._data = OrderedDict(iterable)

    def append(self, value, timestamp=None):
        """Append the given value to this timeseries.

        :timestamp: - The timestamp this value corresponds to. If None
            (default) the current time is used.

        Returns the timestamp which was used.
        """
        if timestamp is None:
            timestamp = datetime.datetime.now()

        self._data[timestamp] = value

        return timestamp

    def __getitem__(self, timestamp):
        return self._data[timestamp]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def to_series(self):
        """Returns this series as a `pandas.Series`"""
        index, data = zip(*self._data.items())
        index = pd.DatetimeIndex(index)
        return pd.Series(data, index)


class FixedLengthTimeSeries(TimeSeries):
    """An object representing a fixed number of timestamp-value pairs."""

    length = None

    def __init__(self, length, iterable=None):
        """Initialize a new `FixedLengthTimeSeries`.

        :length: - An integer representing the maximum number of pairs stored.
        :iterable: - A iterable of key-value-pairs to be added to the series
            initially.
        """
        TimeSeries.__init__(self, iterable=iterable)

        self.length = length

    def append(self, value, timestamp=None):
        """Append the given value to this timeseries.

        :timestamp: - The timestamp this value corresponds to. If None
            (default) the current time is used.

        Returns the timestamp which was used.
        """
        timestamp = TimeSeries.append(self, value, timestamp=timestamp)

        if len(self) > self.length:
            self._data.popitem(last=False)

        return timestamp


class FixedHorizonTimeSeries(TimeSeries):
    """An object representing timestamp-value pairs over a fixed duration."""

    horizon = None

    _data = None

    def __init__(self, horizon, iterable=None):
        """Initialize a new `FixedHorizonTimeSeries`.

        :horizon: - A `datetime.timedelta` representing the longest duration
            represented by this series.
        :iterable: - A iterable of key-value-pairs to be added to the series
            initially.
        """
        TimeSeries.__init__(self, iterable=iterable)

        if type(horizon) != datetime.timedelta:
            raise ValueError('`horizon` must be of type `datetime.timedelta`!')
        self.horizon = horizon

    def append(self, value, timestamp=None):
        """Append the given value to this timeseries.

        :timestamp: - The timestamp this value corresponds to. If None
            (default) the current time is used.

        Returns the timestamp which was used.
        """
        timestamp = TimeSeries.append(self, value, timestamp=timestamp)

        count = 0
        for time in iter(self._data):
            if timestamp - time > self.horizon:
                count += 1
            else:
                break

        for i in range(count):
            self._data.popitem(last=False)

        return timestamp
