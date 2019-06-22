import logging
import time
from datetime import datetime

class Timer():
    start_dt = None
    stop_dt = None
    counting = False
    _id = None

    def start(self):

        self.counting = True

        if not self.start_dt:
            self.start_dt = datetime.now()

    def stop(self, to_str=True):

        if self.counting == True:
            self.stop_dt = datetime.now()
            self.counting = False

        if to_str:
            return self.clock(stop=False)

    def restart(self):

        self.start_dt = datetime.now()
        self.stop_dt = None
        self.start()

    def __repr__(self):
        '''Return str duration in sec'''

        return self.clock(stop=False)

    def clock(self, t='s', stop=True):
        '''Return str duration in sec w/ stop option'''

        if self.counting and stop:
            self.stop()
            diff = self.stop_dt - self.start_dt
        elif self.counting and not stop:
            diff = datetime.now() - self.start_dt
        elif not self.counting:
            diff = self.stop_dt - self.start_dt

        if t == 's':
            return round(diff.seconds + diff.microseconds/1000, 1)
        elif t == 'ms':
            return diff.seconds*1000 + diff.microseconds/1000
            #return int(diff.microseconds/100)

    def __init__(self, start=True):

        self._id = int(time.time())

        if start:

            self.start()
