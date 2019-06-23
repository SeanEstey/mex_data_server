'''app.lib.timer'''
import time, pytz
import dateparser
from datetime import datetime, date, time, timedelta
from app.utils import utc_datetime as now, utc_dtdate as today, to_relative_str

#------------------------------------------------------------------------------
class Timer():
    """Simple timer object which functions in one of 2 modes:
    A) Stopwatch. Counts elapsed time upward.
    B) Timer. Counts remaining time downward until set target. Target can be
    explicitly defined or fixed interval with re-adjusting targets.
    """
    start = None
    expire = None
    name = None
    expire_str = None
    target = None
    words = None
    relative_kw = ['next', 'every']
    quiet = None

    def __repr__(self):
        return str(self.elapsed())
    def __format__(self, format_spec):
        return "{:,}".format(self.elapsed())

    #--------------------------------------------------------------------------
    def reset(self):
        """Restart stopwatch or countdown timer.
        """
        self.start = now()
        if self.expire_str:
            self.set_expiry(self.expire_str)

    #--------------------------------------------------------------------------
    def elapsed(self, unit='ms'):
        """Time since initialization or last reset.
        """
        sec = (now() - self.start).total_seconds()
        if unit == 'ms':
            return round(sec * 1000, 1)
        elif unit == 's':
            return round(sec, 1)

    #--------------------------------------------------------------------------
    def remain(self, unit='ms'):
        """If in timer mode, return time remaining as milliseconds
        integer (unit='ms') or minutes string (unit='str')
        """
        if self.expire is None:
            return None

        if self.expire > now():
            if self.quiet != True:
                print("{}: {}".format(self.name, to_relative_str(self.expire - now())))
        else:
            if self.quiet != True:
                print("{} expired!".format(self.name))

        rem_ms = int((self.expire - now()).total_seconds()*1000)

        if unit == 'ms':
            return rem_ms if rem_ms > 0 else 0
        elif unit == 'str':
            if rem_ms == 0:
                return "expired"
            else:
                return "%s min" % round((rem_ms/1000/3600)*60,1)

    #--------------------------------------------------------------------------
    def set_expiry(self, target):
        """target can be datetime.datetime obj or recognizable
        string.
        """
        if isinstance(target, datetime):
            self.start = now()
            self.expire = target
        elif isinstance(target, str):
            self.start = now()
            self.parse(target)

        if self.quiet != True:
            print("{} expires in {}".format(self.name, to_relative_str(self.expire - now())))

    #--------------------------------------------------------------------------
    def parse(self, target_str):
        """Parse natural language definition of timer expiry.
        """
        self.words = target_str.split(" ")

        # Fixed datetime target
        if len(set(self.words) & set(self.relative_kw)) == 0:
            self.expire = dateparser.parse(target_str)
            return True

        # Relative fixed target (i.e. "next hour change")
        if "next" in self.words:
            if "hour" in self.words:
                self.expire = datetime.combine(today().date(), time(now().time().hour)
                    ).replace(tzinfo=pytz.utc) + timedelta(hours=1)
                return True
            else:
                raise Exception("Cannot parse '%s'" % target_str)
        # Relative interval target (i.e. "every 5 clock minutes utc")
        elif "every" in self.words:
            inc = int(self.words[1])

            # Intervals relative to clock time instead of absolute.
            if self.words[2] == 'clock':
                unit = self.words[3]

                if unit not in ['min', 'minute', 'minutes']:
                    raise Exception("Cannot parse '%'" % target_str)

                solutions = [n for n in range(0,60) if n % inc == 0]
                t_now = now().time()
                gt_min = list(filter(lambda x: (x > t_now.minute), solutions))
                _date = today().date()

                if len(gt_min) == 0:
                    if t_now.hour == 23:
                        _time = time(0, solutions[0])
                        # Catch last day of month error
                        try:
                            _date = date(_date.year, _date.month, _date.day+1)
                        except ValueError as e:
                            _date = date(_date.year, _date.month+1, 1)
                    else:
                        _time = time(t_now.hour+1, solutions[0])
                else:
                    _time = time(t_now.hour, gt_min[0])

                self.expire = datetime.combine(_date, _time
                    ).replace(tzinfo=pytz.utc)
                self.expire_str = target_str
                return True
        else:
            raise Exception("Cannot parse '%s'" % target_str)

    #--------------------------------------------------------------------------
    def __init__(self, name=None, expire=None, quiet=False):
        self.start = now()
        self.quiet = quiet
        if name:
            self.name=name
        if expire:
            self.set_expiry(expire)
