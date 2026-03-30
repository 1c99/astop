"""Memory panel with responsive braille graph, btop style."""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

from astop.collectors.memory import MemoryData
from astop.utils import human_bytes
from astop.widgets.graph import build_graph


def _mem_bar(pct, width):
    filled = int(pct / 100 * width)
    filled = max(0, min(width, filled))
    color = "red" if pct > 80 else "yellow" if pct > 60 else "green"
    t = Text()
    t.append("\u2501" * filled, style=color)
    t.append("\u2500" * (width - filled), style="rgb(40,40,40)")
    return t


class MemoryPanel(Static):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._history: list[float] = []

    def update_data(self, data: MemoryData):
        self._history.append(data.percent)
        if len(self._history) > 200:
            self._history = self._history[-200:]

        w = self.size.width
        if w < 10:
            w = 40
        graph_w = max(4, int(w * 0.35))
        right_w = w - graph_w - 1

        info_lines = []
        t1 = Text(no_wrap=True, overflow="crop")
        t1.append("Total:  ", style="dim")
        t1.append(f"{human_bytes(data.total):>10}", style="white")
        info_lines.append(t1)

        t2 = Text(no_wrap=True, overflow="crop")
        t2.append("Used:   ", style="dim")
        t2.append(f"{human_bytes(data.used):>10}", style="white")
        info_lines.append(t2)

        t3 = Text(no_wrap=True, overflow="crop")
        pc = "red" if data.percent > 80 else "yellow" if data.percent > 60 else "green"
        mem_bar_w = max(5, right_w - 8)
        t3.append(f"  {data.percent:.0f}%  ", style=pc)
        t3.append_text(_mem_bar(data.percent, mem_bar_w))
        info_lines.append(t3)

        t4 = Text(no_wrap=True, overflow="crop")
        t4.append("Active: ", style="dim")
        t4.append(f"{human_bytes(data.active):>10}", style="rgb(100,200,100)")
        info_lines.append(t4)

        t5 = Text(no_wrap=True, overflow="crop")
        t5.append("Wired:  ", style="dim")
        t5.append(f"{human_bytes(data.wired):>10}", style="rgb(200,100,100)")
        info_lines.append(t5)

        t6 = Text(no_wrap=True, overflow="crop")
        t6.append("Avail:  ", style="dim")
        t6.append(f"{human_bytes(data.available):>10}", style="rgb(100,100,200)")
        info_lines.append(t6)

        graph_lines, _, _ = build_graph(self._history, graph_w, len(info_lines))

        t = Text(no_wrap=True, overflow="crop")
        for i in range(len(info_lines)):
            row = Text(no_wrap=True, overflow="crop")
            if i < len(graph_lines):
                row.append_text(graph_lines[i])
            else:
                row.append(" " * graph_w)
            row.append("\u2502", style="dim rgb(50,50,50)")
            row.append_text(info_lines[i])
            pad = w - len(row.plain)
            if pad > 0:
                row.append(" " * pad)
            t.append_text(row)
            if i < len(info_lines) - 1:
                t.append("\n")

        self.update(t)
