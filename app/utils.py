import inspect, logging, re, unicodedata
import pytz
import tzlocal
import dateparser
from datetime import datetime, timedelta, time, date
from pprint import pformat
log = logging.getLogger(__name__)

class colors:
    BLUE = '\033[94m'
    GRN = '\033[92m'
    YLLW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[37m'
    ENDC = '\033[0m'
    HEADER = '\033[95m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

abc = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r',\
    's','t','u','v','w','x','y','z']

def pct_diff(a,b): return ((b-a)/a)*100

##### Datetime #################################################################

def to_ts(dt):
    return int(dt.timestamp())

def dt_to_ms(dt):
    return int(dt.timestamp()*1000)

def utc_date():
    """current date in UTC timezone"""
    return datetime.utcnow().replace(tzinfo=pytz.utc).date()

def utc_dtdate():
    """current date as datetime obj at T:00:00:00:00 in UTC timezone"""
    return datetime.combine(utc_date(), time()).replace(tzinfo=pytz.utc)

def utc_datetime():
    """tz-aware UTC datetime object"""
    return datetime.utcnow().replace(tzinfo=pytz.utc)

def duration(_timedelta, units='total_seconds'):
    if units == 'total_seconds':
        return int(_timedelta.total_seconds())
    elif units == 'hours':
        return round(_timedelta.total_seconds()/3600,1)

def to_local(dt):
    """Show time in local tz.
    """
    zone = tzinfo=tzlocal.get_localzone()
    return dt.astimezone(zone)

def to_dt(val):
    """Convert timestamp or ISOstring to datetime obj
    """
    if val is None:
        return None
    elif type(val) == int:
        # Timestamp
        return datetime.utcfromtimestamp(val).replace(tzinfo=pytz.utc)
    elif type(val) == float:
        # Timestamp
        return datetime.utcfromtimestamp(val).replace(tzinfo=pytz.utc)
    elif type(val) == str:
        # Timestamp
        if re.match(r'^[0-9]*$', val):
            return datetime.utcfromtimestamp(float(val)).replace(tzinfo=pytz.utc)
        # ISO formatted datetime str?
        else:
            try:
                return dateparser.parse(val).replace(tzinfo=pytz.utc)
            except Exception as e:
                raise
    raise Exception("to_dt(): invalid type '%s'" % type(val))

#----------------------------------------------------------------------
def to_relative_str(_delta):
    diff_ms = abs(_delta.total_seconds() * 1000)
    min_ms = 1000 * 60
    hour_ms = 1000 * 3600
    day_ms = hour_ms * 24
    week_ms = day_ms * 7
    month_ms = day_ms * 30
    year_ms = day_ms * 365

    if diff_ms >= year_ms:
        # Year(s) span
        nYears = int(diff_ms/year_ms)
        return "{} year{}".format(nYears, 's' if nYears > 1 else '')

    if diff_ms >= month_ms:
        # Month(s) span
        nMonths = int(diff_ms/month_ms)
        return "{} month{}".format(nMonths, 's' if nMonths > 1 else '')

    if diff_ms >= week_ms:
        # Week(s) span
        nWeeks = int(diff_ms/week_ms)
        return "{} week{}".format(nWeeks, 's' if nWeeks > 1 else '')

    if diff_ms >= day_ms:
        # Day(s) span
        nDays = int(diff_ms/day_ms)
        return "{} day{}".format(nDays, 's' if nDays > 1 else '')

    if diff_ms >= hour_ms:
        # Hour(s) span
        nHours = int(diff_ms/hour_ms)
        return "{} hour{}".format(nHours, 's' if nHours > 1 else '')

    if diff_ms >= min_ms:
        # Minute(s) span
        nMin = int(diff_ms/min_ms)
        return "{} min".format(nMin)

    # Second(s) span
    nSec = int(diff_ms/1000)
    return "{} sec{}".format(nSec, 's' if nSec > 1 else '')

#------------------------------------------------------------------------------
def strtoms(date_str):
    """Convert UTC date to milliseconds
    If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours
    ago UTC"
    See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/
    :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours
    ago UTC", "now UTC"
    :type date_str: str
    """
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    d = dateparser.parse(date_str)
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)
    return int((d - epoch).total_seconds() * 1000.0)

#------------------------------------------------------------------------------
def strtodt(date_str):
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    d = dateparser.parse(date_str)
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)
    return d

##### Datatypes ################################################################

import numpy

#------------------------------------------------------------------------------
def numpy_to_py(adict):
    """Convert dict containing numpy.int64 values to python int's
    """
    for k in adict:
        if type(adict[k]) == numpy.int64:
            adict[k] = int(adict[k])
        elif type(adict[k]) == numpy.float64:
            adict[k] = float(adict[k])
    return adict
#------------------------------------------------------------------------------
def to_int(val):
    if val is None:
        return 0
    elif type(val) is int:
        return val
    elif type(val) == str:
        if is_number(val):
            return int(float(val))
        else:
            return None
    elif type(val) == numpy.int64:
        return int(val)
    else:
        return int(val)
#------------------------------------------------------------------------------
def is_number(s):
    """ """
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False
#------------------------------------------------------------------------------
def to_float(val, dec=None):
    """ """
    if val is None:
        return 0.0
    elif type(val) is float:
        return val
    elif not is_number(val):
        return None
    return round(float(val),dec) if dec else float(val)
