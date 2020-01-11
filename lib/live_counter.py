"""
Created by Joscha Vack on 1/11/2020.
"""

from time import time


class LiveCounter:
    def __init__(self, parent):
        self._parent = parent
        self._isLive = False
        self._stream_start = 0
        self._live_time = 0

    def update(self):
        live = True  # self._parent.IsLive()
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
        return self._isLive

    @property
    def seconds_live(self):
        return int(self._live_time)

    @property
    def minutes_live(self):
        return int(self._live_time // 60)

    @property
    def hours_live(self):
        return int(self.minutes_live // 24)
