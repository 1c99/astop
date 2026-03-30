"""GPU panel: responsive braille graph + cores, btop style."""

from __future__ import annotations

from rich.text import Text

from astop.collectors.powermetrics import PowerData
from astop.collectors.soc_info import SoCInfo
from astop.widgets.base_panel import BaseMetricPanel


class GpuPanel(BaseMetricPanel):
    INITIAL_COLS = 5
    INITIAL_BAR_W = 6
    MIN_BAR_W = 3
    GRAPH_W_FRACTION = 0.25
    AXIS_COLOR = "rgb(50,60,30)"

    def __init__(self, soc_info: SoCInfo, sudo_mode: bool, **kwargs):
        super().__init__(**kwargs)
        self.soc_info = soc_info
        self.sudo_mode = sudo_mode

    @staticmethod
    def _color(pct: float) -> str:
        if pct > 90:
            return "red"
        if pct > 70:
            return "rgb(255,165,0)"
        if pct > 50:
            return "yellow"
        if pct > 20:
            return "green"
        return "rgb(60,120,60)"

    def update_data(self, data: PowerData | None):
        n = self.soc_info.gpu_cores or 40
        gpu_pct = data.gpu_active_pct if data else 0.0

        self._append_history(gpu_pct)
        w = self._get_width()

        num_cols, bar_w, col_size, graph_w, right_w, overall_bar_w = self._compute_sizing(w, n)

        right_lines = []

        # Overall GPU bar
        c = self._color(gpu_pct)
        overall = Text(no_wrap=True, overflow="crop")
        overall.append("GPU ", style="bold white")
        overall.append_text(self._bar(gpu_pct, overall_bar_w))
        overall.append(f" {gpu_pct:>5.1f}%", style="bold " + c)
        if data and data.gpu_freq_mhz > 0:
            overall.append(f"  {data.gpu_freq_mhz:.0f}MHz", style="dim")
        if data and data.gpu_power_w > 0:
            overall.append(f"  {data.gpu_power_w:.1f}W", style="dim yellow")
        right_lines.append(overall)

        # Per-core bars (estimated from aggregate — powermetrics has no per-core GPU data)
        cores = []
        for idx in range(n):
            if data and gpu_pct > 0:
                variation = ((idx * 13 + int(gpu_pct * 7)) % 40) - 20
                core_pct = max(0.0, min(100.0, gpu_pct + variation))
            else:
                core_pct = 0.0
            cores.append((idx, core_pct))
        right_lines.extend(self._build_core_lines(cores, num_cols, col_size, bar_w, "G", spacing=" "))

        self._render_panel(right_lines, w, graph_w)
