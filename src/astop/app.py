"""Main astop Textual application."""

from __future__ import annotations

import asyncio

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.widgets import Footer

from astop.collectors.soc_info import discover
from astop.collectors.cpu import CpuCollector
from astop.collectors.memory import MemoryCollector
from astop.collectors.battery import BatteryCollector
from astop.collectors.network import NetworkCollector
from astop.collectors.disk import DiskCollector
from astop.collectors.processes import ProcessCollector
from astop.collectors.powermetrics import PowerMetricsCollector

from astop.widgets.cpu_panel import CpuPanel
from astop.widgets.memory_panel import MemoryPanel
from astop.widgets.gpu_panel import GpuPanel
from astop.widgets.power_panel import PowerPanel
from astop.widgets.io_panel import IOPanel
from astop.widgets.ane_panel import AnePanel
from astop.widgets.process_table import ProcessTable


class AstopApp(App):
    CSS_PATH = "styles/app.tcss"
    TITLE = "astop"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("p", "toggle_pause", "Pause"),
        Binding("r", "force_refresh", "Refresh"),
        Binding("s", "sort_proc", "Sort"),
        Binding("v", "reverse_sort", "Reverse"),
    ]

    def __init__(self, sudo_mode: bool = False, refresh_rate: float = 1.0):
        super().__init__()
        self.sudo_mode = sudo_mode
        self.refresh_rate = refresh_rate
        self.paused = False

        self.soc_info = discover()
        self.cpu_collector = CpuCollector(self.soc_info)
        self.memory_collector = MemoryCollector()
        self.battery_collector = BatteryCollector()
        self.network_collector = NetworkCollector()
        self.disk_collector = DiskCollector()
        self.process_collector = ProcessCollector()
        self.power_collector = PowerMetricsCollector() if self.sudo_mode else None

    def compose(self) -> ComposeResult:
        with Vertical(id="main-vertical"):
            cpu = CpuPanel(self.soc_info, id="cpu-panel")
            cpu.border_title = f"cpu \u2500 {self.soc_info.chip_name}"
            yield cpu

            gpu = GpuPanel(self.soc_info, self.sudo_mode, id="gpu-panel")
            gpu.border_title = f"gpu \u2500 {self.soc_info.gpu_cores} cores \u2500 {self.soc_info.metal_version}"
            yield gpu

            ane = AnePanel(id="ane-panel")
            ane.border_title = "ane \u2500 Neural Engine"
            yield ane

            with Horizontal(id="bottom-row"):
                with Vertical(id="left-stack"):
                    mem = MemoryPanel(id="mem-panel")
                    mem.border_title = "mem"
                    yield mem

                    io = IOPanel(id="io-panel")
                    io.border_title = "net / disk"
                    yield io

                    pwr = PowerPanel(id="pwr-panel")
                    pwr.border_title = "battery"
                    yield pwr

                proc_scroll = VerticalScroll(id="proc-scroll")
                proc_scroll.border_title = "proc"
                with proc_scroll:
                    yield ProcessTable(id="process-table")

        yield Footer()

    def on_mount(self):
        if self.power_collector:
            self.power_collector.start()
        self.set_interval(self.refresh_rate, self._refresh_data)
        self.call_later(self._refresh_data)

    async def _refresh_data(self):
        if self.paused:
            return

        loop = asyncio.get_event_loop()
        cpu_data, mem_data, bat_data, net_data, disk_data, proc_data = await asyncio.gather(
            loop.run_in_executor(None, self.cpu_collector.collect),
            loop.run_in_executor(None, self.memory_collector.collect),
            loop.run_in_executor(None, self.battery_collector.collect),
            loop.run_in_executor(None, self.network_collector.collect),
            loop.run_in_executor(None, self.disk_collector.collect),
            loop.run_in_executor(None, self.process_collector.collect),
        )
        power_data = self.power_collector.latest if self.power_collector else None

        self.query_one("#cpu-panel", CpuPanel).update_data(cpu_data)
        self.query_one("#mem-panel", MemoryPanel).update_data(mem_data)
        self.query_one("#gpu-panel", GpuPanel).update_data(power_data)
        self.query_one("#ane-panel", AnePanel).update_data(power_data)
        self.query_one("#pwr-panel", PowerPanel).update_data(power_data, bat_data)
        self.query_one("#io-panel", IOPanel).update_data(net_data, disk_data)
        self.query_one("#process-table", ProcessTable).update_data(proc_data)

    def action_toggle_pause(self):
        self.paused = not self.paused
        self.sub_title = "PAUSED" if self.paused else ""

    def action_force_refresh(self):
        self.paused = False
        self.call_later(self._refresh_data)

    def action_sort_proc(self):
        self.query_one("#process-table", ProcessTable).cycle_sort()

    def action_reverse_sort(self):
        self.query_one("#process-table", ProcessTable).toggle_reverse()

    def on_unmount(self):
        if self.power_collector:
            self.power_collector.stop()
