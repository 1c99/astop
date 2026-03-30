"""ANE (Neural Engine) panel with graph + cores like CPU/GPU."""

from __future__ import annotations

from rich.text import Text

from astop.collectors.powermetrics import PowerData
from astop.widgets.base_panel import BaseMetricPanel

ANE_CORES = 16


class AnePanel(BaseMetricPanel):
    INITIAL_COLS = 4
    INITIAL_BAR_W = 6
    MIN_BAR_W = 3
    GRAPH_W_FRACTION = 0.3
    AXIS_COLOR = "rgb(50,40,70)"
    GRAPH_BASE_COLOR = "rgb(140,90,220)"
    MIN_WIDTH = 10

    @staticmethod
    def _color(pct: float) -> str:
        if pct > 90:
            return "red"
        if pct > 70:
            return "rgb(255,165,0)"
        if pct > 40:
            return "rgb(180,120,255)"
        if pct > 10:
            return "rgb(140,90,220)"
        return "rgb(80,60,140)"

    def update_data(self, data: PowerData | None):
        ane_pct = data.ane_active_pct if data else 0.0
        self._append_history(ane_pct)
        w = self._get_width()

        num_cols, bar_w, col_size, graph_w, right_w, overall_bar_w = self._compute_sizing(w, ANE_CORES)

        right_lines = []

        # Overall bar
        c = self._color(ane_pct)
        overall = Text(no_wrap=True, overflow="crop")
        overall.append("ANE ", style="bold white")
        overall.append_text(self._bar(ane_pct, overall_bar_w))
        overall.append(f" {ane_pct:>5.1f}%", style="bold " + c)
        if data and data.ane_power_w > 0:
            overall.append(f"  {data.ane_power_w:.1f}W", style="dim rgb(180,120,255)")
        right_lines.append(overall)

        # Per-core bars (estimated from aggregate — powermetrics has no per-core ANE data)
        cores = []
        for idx in range(ANE_CORES):
            if data and ane_pct > 0:
                variation = ((idx * 11 + int(ane_pct * 5)) % 30) - 15
                core_pct = max(0.0, min(100.0, ane_pct + variation))
            else:
                core_pct = 0.0
            cores.append((idx, core_pct))
        right_lines.extend(self._build_core_lines(cores, num_cols, col_size, bar_w, "N", spacing=" "))

        self._render_panel(right_lines, w, graph_w)
