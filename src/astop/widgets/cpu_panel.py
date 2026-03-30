"""CPU panel: responsive braille graph + cores, btop style."""

from __future__ import annotations

import os
import time

import psutil
from rich.text import Text

from astop.collectors.cpu import CpuData
from astop.collectors.soc_info import SoCInfo
from astop.widgets.base_panel import BaseMetricPanel


class CpuPanel(BaseMetricPanel):
    INITIAL_COLS = 3
    INITIAL_BAR_W = 10
    MIN_BAR_W = 4
    GRAPH_W_FRACTION = 0.3
    AXIS_COLOR = "rgb(50,70,50)"

    def __init__(self, soc_info: SoCInfo, **kwargs):
        super().__init__(**kwargs)
        self.soc_info = soc_info

    @staticmethod
    def _color(pct: float) -> str:
        if pct > 90:
            return "red"
        if pct > 70:
            return "yellow"
        if pct > 40:
            return "green"
        return "rgb(80,160,80)"

    def update_data(self, data: CpuData):
        self._append_history(data.overall)
        w = self._get_width()
        cores = data.per_core
        n = len(cores)

        num_cols, bar_w, col_size, graph_w, right_w, overall_bar_w = self._compute_sizing(w, n)

        right_lines = []

        # Overall CPU bar
        oc = self._color(data.overall)
        overall = Text(no_wrap=True, overflow="crop")
        overall.append("CPU ", style="bold white")
        overall.append_text(self._bar(data.overall, overall_bar_w))
        overall.append(f" {data.overall:>5.1f}%", style="bold " + oc)
        uptime = time.time() - psutil.boot_time()
        d, rem = divmod(int(uptime), 86400)
        h, rem = divmod(rem, 3600)
        m = rem // 60
        try:
            load = os.getloadavg()
            overall.append(f"  up {d}d{h:02d}:{m:02d} LAV {load[0]:.1f} {load[1]:.1f} {load[2]:.1f}", style="dim")
        except OSError:
            overall.append(f"  up {d}d{h:02d}:{m:02d}", style="dim")
        right_lines.append(overall)

        # Cores
        core_data = [(i, cores[i]) for i in range(n)]
        right_lines.extend(self._build_core_lines(core_data, num_cols, col_size, bar_w, "C"))

        self._render_panel(right_lines, w, graph_w)
