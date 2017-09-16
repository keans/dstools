#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
from .utils import pairwise


def daterange(start_ts, end_ts, step_td):
    """
    generator that creates a date range between the
    start date and the end date using the provided step timedelta
    """
    for n in range(
        int(
            (end_ts - start_ts).total_seconds() /
            float(step_td.total_seconds()) + 1
        )
    ):
        yield start_ts + n * step_td


class DateTimeBin(object):
    """
    The DateTimeBin class allows the storage of values based on dates.
    From the start timestamp to the end timestamp a couple of bins are
    created based on the given timedelta step
    """
    def __init__(self, start_ts, end_ts, step_delta):
        self.bins = collections.OrderedDict()
        self._values = set([])
        self.step_delta = step_delta

        # create bins
        for dt_tuple in pairwise(daterange(start_ts, end_ts, step_delta)):
            self.bins[dt_tuple] = collections.Counter()

    @property
    def values(self):
        return self._values

    def start_dates(self):
        for k in list(self.bins.keys()):
            yield k[0]

    def get_spans(self, value):
        """
        returns a list of time spans pairs (bin number, timespan)
        for the given value
        """
        res = []
        tmp = []
        for no, (k, v) in enumerate(self.bins.items()):
            if v.get(value) > 0:
                tmp.append((no, k))
            elif tmp != []:
                res.append(tmp)
                tmp = []

        if tmp != []:
            res.append(tmp)

        return res

    def __len__(self):
        return len(self.bins)

    def __getitem__(self, dt):
        """
        returns the bin that matches the date
        """
        for no, (k, v) in enumerate(self.bins.items()):
            if (dt >= k[0]) and (dt < k[1]):
                return (no, k, v)

        return (-1, None, None)

    def __setitem__(self, dt, value):
        # get the timespan
        no, k, v = self[dt]
        if no == -1:
            raise Exception("unknown bin '%s'" % dt)

        # update the counter for the given value
        v.update([value, ])

        # update value set to keep track of all set values
        self._values.update([value, ])

    def __str__(self):
        tmp = ""
        for k, v in list(self.bins.items()):
            tmp += "%s - %s => %s\n" % (k[0], k[1], v)

        return tmp
