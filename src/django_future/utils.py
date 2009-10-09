"""Utils for django_future."""

import datetime

_TIMEDELTA_SUFFIXES = {'m': 'minutes',
                       'h': 'hours',
                       'd': 'days',
                       'w': 'weeks'}

def parse_timedelta(s):
    n, suffix = int(s[:-1]), s[-1]
    key = _TIMEDELTA_SUFFIXES[suffix]
    kwargs = {key: n}
    return datetime.timedelta(**kwargs)
