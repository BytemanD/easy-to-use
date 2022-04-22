import time
import pytz
from datetime import datetime
from datetime import timedelta

YMD_HMS = '%Y-%m-%d %H:%M:%S'
YMD_HMS_Z = '%Y-%m-%d %H:%M:%S %Z'


def parse_timestamp2str(timestamp, date_fmt=None):
    """Parse timestamp to string with DATE_FORMAT

    >>> parse_timestamp2str(0.0, date_fmt=FORMAT_YYYY_MM_DD_HHMMSS)
    '1970-01-01 08:00:00'
    """
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime(date_fmt) if date_fmt else dt.isoformat()


def parse_str2timestamp(datetime_str, date_fmt=None):
    """Parse timestamp to string with DATE_FORMAT
    >>> parse_str2timestamp('1970-01-01 08:00:00')
    0.0
    """
    return time.mktime(time.strptime(datetime_str, date_fmt or YMD_HMS))


parse_ts2str = parse_timestamp2str
parse_str2ts = parse_str2timestamp


def now(tz=None):
    """return type: datetime
    """
    timezone = pytz.timezone(tz) if tz else None
    return datetime.now(tz=timezone)


def now_str(tz=None, date_fmt=YMD_HMS):
    date_now = now(tz=tz)
    return date_now.strftime(date_fmt) if date_fmt else date_now.isoformat()


def utc_now():
    """return type: datetime
    """
    return datetime.utcnow(tz='utc')


def utc_now_str(date_fmt=None):
    return now_str(tz='utc', date_fmt=date_fmt)


def datetime_after(start=None, **kwargs):
    return (start or datetime.now()) + timedelta(**kwargs)


def datetime_before(end=None, **kwargs):
    return (end or datetime.now()) - timedelta(**kwargs)
