"""Power & battery panel in btop style."""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

from astop.collectors.battery import BatteryData
from astop.collectors.powermetrics import PowerData
from astop.utils import human_duration


def _bat_bar(pct: float, width: int = 15) -> Text:
    filled = int(pct / 100 * width)
    filled = max(0, min(width, filled))
    color = "green" if pct > 50 else "yellow" if pct > 20 else "red"
    t = Text()
    t.append("\u2503", style="dim rgb(60,60,60)")
    t.append("\u2501" * filled, style=color)
    t.append("\u2500" * (width - filled), style="rgb(40,40,40)")
    t.append("\u2503", style="dim rgb(60,60,60)")
    return t


class PowerPanel(Static):
    def update_data(self, power: PowerData | None, battery: BatteryData | None):
        t = Text(no_wrap=True, overflow="crop")
        if power:
            t.append(f"CPU  {power.cpu_power_w:>5.1f} W\n", style="cyan")
            t.append(f"GPU  {power.gpu_power_w:>5.1f} W\n", style="magenta")
            t.append(f"Pkg  {power.package_power_w:>5.1f} W\n", style="bold yellow")
        if battery and battery.percent >= 0:
            color = "green" if battery.percent > 50 else "yellow" if battery.percent > 20 else "red"
            icon = "\u26a1" if battery.plugged else "\U0001f50b"
            t.append(f"{icon} {battery.percent:.0f}%  ", style=color)
            t.append_text(_bat_bar(battery.percent))
            if battery.secs_left > 0:
                t.append(f"\n     {human_duration(battery.secs_left)} left", style="dim")
            elif battery.plugged:
                t.append(f"\n     Charging", style="green")
        self.update(t)
