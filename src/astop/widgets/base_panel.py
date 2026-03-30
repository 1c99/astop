"""Shared base for metric panels (CPU/GPU/ANE) with braille graph + core bars."""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

from astop.widgets.graph import build_graph


class BaseMetricPanel(Static):
    """Base class for panels that show a braille graph alongside per-core bars."""

    INITIAL_COLS: int = 3
    INITIAL_BAR_W: int = 10
    MIN_BAR_W: int = 4
    GRAPH_W_FRACTION: float = 0.3
    AXIS_COLOR: str = "rgb(50,70,50)"
    GRAPH_BASE_COLOR: str | None = None
    MIN_WIDTH: int = 20
    DEFAULT_WIDTH: int = 80

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._history: list[float] = []

    def _append_history(self, value: float):
        self._history.append(value)
        if len(self._history) > 300:
            self._history = self._history[-300:]

    @staticmethod
    def _color(pct: float) -> str:
        raise NotImplementedError

    def _bar(self, pct: float, width: int) -> Text:
        filled = int(pct / 100 * width)
        filled = max(0, min(width, filled))
        c = self._color(pct)
        t = Text()
        t.append("\u2501" * filled, style=c)
        t.append("\u2500" * (width - filled), style="rgb(40,40,40)")
        return t

    def _get_width(self) -> int:
        w = self.size.width
        return w if w >= self.MIN_WIDTH else self.DEFAULT_WIDTH

    def _compute_sizing(self, w: int, n_cores: int):
        num_cols = self.INITIAL_COLS
        bar_w = self.INITIAL_BAR_W
        core_col_w = 9 + bar_w
        core_area_w = num_cols * core_col_w
        while core_area_w > w * 0.7 and (num_cols > 1 or bar_w > self.MIN_BAR_W):
            if bar_w > self.MIN_BAR_W:
                bar_w -= 1
            else:
                num_cols -= 1
                bar_w = self.INITIAL_BAR_W
            core_col_w = 9 + bar_w
            core_area_w = num_cols * core_col_w

        col_size = (n_cores + num_cols - 1) // num_cols
        graph_w = max(6, int(w * self.GRAPH_W_FRACTION))
        right_w = w - graph_w - 4  # 3 axis + 1 separator
        bar_w = max(self.MIN_BAR_W, (right_w // num_cols) - 9)
        overall_bar_w = max(self.MIN_BAR_W + 4, right_w - 15)
        return num_cols, bar_w, col_size, graph_w, right_w, overall_bar_w

    def _build_core_lines(
        self,
        cores: list[tuple[int, float]],
        num_cols: int,
        col_size: int,
        bar_w: int,
        prefix: str,
        spacing: str = "  ",
    ) -> list[Text]:
        lines: list[Text] = []
        n = len(cores)
        for row in range(col_size):
            line = Text(no_wrap=True, overflow="crop")
            for col in range(num_cols):
                i = col * col_size + row
                if i < n:
                    idx, pct = cores[i]
                    c = self._color(pct)
                    t_idx = f"{prefix}{idx:<2}" if idx < 10 else f"{prefix}{idx}"
                    line.append(t_idx, style=c)
                    line.append_text(self._bar(pct, bar_w))
                    line.append(f"{pct:>4.0f}%", style=c)
                    if col < num_cols - 1:
                        line.append(spacing)
            lines.append(line)
        return lines

    def _render_panel(self, right_lines: list[Text], w: int, graph_w: int):
        graph_lines, graph_max, graph_min = build_graph(
            self._history, graph_w, len(right_lines),
            base_color=self.GRAPH_BASE_COLOR,
        )
        t = Text(no_wrap=True, overflow="crop")
        for i in range(len(right_lines)):
            row = Text(no_wrap=True, overflow="crop")
            if i == 0:
                row.append(f"{graph_max:>3.0f}", style=f"dim {self.AXIS_COLOR}")
            elif i == len(right_lines) - 1:
                row.append(f"{graph_min:>3.0f}", style=f"dim {self.AXIS_COLOR}")
            else:
                row.append("   ")
            if i < len(graph_lines):
                row.append_text(graph_lines[i])
            else:
                row.append(" " * graph_w)
            row.append("\u2502", style="dim rgb(60,60,60)")
            row.append_text(right_lines[i])
            pad = w - len(row.plain)
            if pad > 0:
                row.append(" " * pad)
            t.append_text(row)
            if i < len(right_lines) - 1:
                t.append("\n")
        self.update(t)
