"""
Created by Joscha Vack on 1/11/2020.
"""

from time import time

from lib.logger import log_call


class LiveCounter(object):
    def __init__(self, parent):
        log_call('LiveCounter.__init__')
        self._parent = parent
        self._isLive = False
        self._stream_start = 0
        self._live_time = 0

    def update(self):
        live = self._parent.IsLive()
        if live:
            if not self._isLive:
                self._isLive = True
                self._stream_start = time()
            else:
                self._live_time = time() - self._stream_start
        else:
            if self._isLive:
                self._isLive = False
                self._stream_start = 0

    @property
    def is_live(self):
        log_call('LiveCounter.is_live.getter')
        return self._isLive

    @property
    def seconds_live(self):
        log_call('LiveCounter.seconds_live.getter')
        return int(self._live_time)

    @property
    def minutes_live(self):
        log_call('LiveCounter.minutes_live.getter')
        return int(self._live_time // 60)

    @property
    def hours_live(self):
        log_call('LiveCounter.hours_live.getter')
        return int(self.minutes_live // 24)
