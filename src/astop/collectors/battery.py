"""Battery collector."""

from __future__ import annotations

from dataclasses import dataclass

import psutil


@dataclass
class BatteryData:
    percent: float = -1  # -1 means no battery
    secs_left: int = -1
    plugged: bool = False


class BatteryCollector:
    def collect(self) -> BatteryData:
        bat = psutil.sensors_battery()
        if bat is None:
            return BatteryData()
        return BatteryData(
            percent=bat.percent,
            secs_left=bat.secsleft if bat.secsleft != psutil.POWER_TIME_UNLIMITED else -1,
            plugged=bat.power_plugged,
        )
