"""Disk I/O collector with rate calculation."""

from __future__ import annotations

import time
from dataclasses import dataclass

import psutil


@dataclass
class DiskData:
    read_rate: float = 0.0
    write_rate: float = 0.0
    read_total: int = 0
    write_total: int = 0


class DiskCollector:
    def __init__(self):
        self._prev = psutil.disk_io_counters()
        self._prev_time = time.monotonic()

    def collect(self) -> DiskData:
        now = time.monotonic()
        counters = psutil.disk_io_counters()
        dt = now - self._prev_time
        if dt <= 0:
            dt = 1.0

        data = DiskData(
            read_rate=(counters.read_bytes - self._prev.read_bytes) / dt,
            write_rate=(counters.write_bytes - self._prev.write_bytes) / dt,
            read_total=counters.read_bytes,
            write_total=counters.write_bytes,
        )
        self._prev = counters
        self._prev_time = now
        return data
