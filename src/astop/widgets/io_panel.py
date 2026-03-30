"""Net/Disk I/O panel with responsive braille graph, btop style."""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

from astop.collectors.network import NetworkData
from astop.collectors.disk import DiskData
from astop.utils import human_rate
from astop.widgets.graph import build_graph


class IOPanel(Static):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dl_history: list[float] = []
        self._ul_history: list[float] = []

    def update_data(self, net: NetworkData, disk: DiskData):
        self._dl_history.append(net.bytes_recv_rate)
        self._ul_history.append(net.bytes_sent_rate)
        if len(self._dl_history) > 200:
            self._dl_history = self._dl_history[-200:]
            self._ul_history = self._ul_history[-200:]

        w = self.size.width
        if w < 10:
            w = 40
        graph_w = max(4, int(w * 0.35))

        info_lines = []
        for label, val, style in [
            ("\u25b2 ", net.bytes_sent_rate, "green"),
            ("\u25bc ", net.bytes_recv_rate, "cyan"),
            ("R ", disk.read_rate, "rgb(100,200,100)"),
            ("W ", disk.write_rate, "rgb(220,180,80)"),
        ]:
            line = Text(no_wrap=True, overflow="crop")
            line.append(label, style=style)
            line.append(f"{human_rate(val):>12}", style=style)
            info_lines.append(line)

        graph_lines, _, _ = build_graph(self._dl_history, graph_w, len(info_lines), base_color="cyan", fixed_scale=False)

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
