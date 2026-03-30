"""Process table with keyboard sorting, btop style."""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

from astop.collectors.processes import ProcessInfo

SORT_KEYS = ["cpu_percent", "memory_percent", "pid", "name"]
SORT_LABELS = {"cpu_percent": "cpu", "memory_percent": "mem", "pid": "pid", "name": "name"}


class ProcessTable(Static):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sort_key = "cpu_percent"
        self.sort_reverse = True
        self._processes: list[ProcessInfo] = []

    def cycle_sort(self):
        idx = SORT_KEYS.index(self.sort_key)
        idx = (idx + 1) % len(SORT_KEYS)
        self.sort_key = SORT_KEYS[idx]
        self.sort_reverse = self.sort_key in ("cpu_percent", "memory_percent", "pid")
        self._do_render()

    def toggle_reverse(self):
        self.sort_reverse = not self.sort_reverse
        self._do_render()

    def update_data(self, processes: list[ProcessInfo]):
        self._processes = processes
        self._do_render()

    def _do_render(self):
        procs = sorted(
            self._processes,
            key=lambda p: getattr(p, self.sort_key),
            reverse=self.sort_reverse,
        )

        t = Text(no_wrap=True, overflow="crop")

        # Sort indicator
        arrow = "\u25bc" if self.sort_reverse else "\u25b2"
        sort_label = SORT_LABELS[self.sort_key]
        t.append(f" sort: {sort_label}{arrow}  ", style="dim")
        t.append("[s]ort [r]everse", style="dim rgb(80,80,80)")
        t.append("\n")

        # Header
        t.append(
            f"{'Pid:':>7} {'Program:':<20} {'User:':<12} {'Mem%':>6} {'Cpu%':>6}",
            style="bold dim white",
        )
        t.append("\n")

        for p in procs:
            if p.cpu_percent > 50:
                style = "bold red"
            elif p.cpu_percent > 20:
                style = "yellow"
            elif p.cpu_percent > 5:
                style = "white"
            else:
                style = "dim white"

            name = p.name[:20]
            user = p.username[:12]

            # Mini CPU bar
            bar_w = 6
            filled = int(p.cpu_percent / 100 * bar_w)
            filled = max(0, min(bar_w, filled))
            bar_c = "red" if p.cpu_percent > 50 else "yellow" if p.cpu_percent > 20 else "green" if p.cpu_percent > 5 else "rgb(50,50,50)"

            t.append(f"{p.pid:>7} ", style=style)
            t.append(f"{name:<20} ", style=style)
            t.append(f"{user:<12} ", style="dim")
            t.append(f"{p.memory_percent:>5.1f} ", style="dim")
            t.append("\u2501" * filled, style=bar_c)
            t.append("\u2500" * (bar_w - filled), style="rgb(40,40,40)")
            t.append(f" {p.cpu_percent:>5.1f}", style=style)
            t.append("\n")

        self.update(t)
