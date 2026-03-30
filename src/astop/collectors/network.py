"""Network I/O collector with rate calculation."""

from __future__ import annotations

import time
from dataclasses import dataclass

import psutil


@dataclass
class NetworkData:
    bytes_sent_rate: float = 0.0
    bytes_recv_rate: float = 0.0
    bytes_sent_total: int = 0
    bytes_recv_total: int = 0


class NetworkCollector:
    def __init__(self):
        self._prev = psutil.net_io_counters()
        self._prev_time = time.monotonic()

    def collect(self) -> NetworkData:
        now = time.monotonic()
        counters = psutil.net_io_counters()
        dt = now - self._prev_time
        if dt <= 0:
            dt = 1.0

        data = NetworkData(
            bytes_sent_rate=(counters.bytes_sent - self._prev.bytes_sent) / dt,
            bytes_recv_rate=(counters.bytes_recv - self._prev.bytes_recv) / dt,
            bytes_sent_total=counters.bytes_sent,
            bytes_recv_total=counters.bytes_recv,
        )
        self._prev = counters
        self._prev_time = now
        return data
