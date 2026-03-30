"""Sudo-enhanced powermetrics collector.

Runs `sudo powermetrics` as a background subprocess, parses plist output.
Gracefully returns None if sudo is not available — never crashes.
"""

from __future__ import annotations

import atexit
import plistlib
import subprocess
import threading
from dataclasses import dataclass, field


@dataclass
class ClusterPower:
    name: str = ""
    power_mw: float = 0.0
    freq_mhz: float = 0.0
    active_pct: float = 0.0


@dataclass
class PowerData:
    cpu_power_w: float = 0.0
    gpu_power_w: float = 0.0
    gpu_active_pct: float = 0.0
    gpu_freq_mhz: float = 0.0
    thermal_pressure: str = "Nominal"
    clusters: list[ClusterPower] = field(default_factory=list)
    package_power_w: float = 0.0
    ane_power_w: float = 0.0
    ane_active_pct: float = 0.0


class PowerMetricsCollector:
    def __init__(self):
        self._latest: PowerData | None = None
        self._lock = threading.Lock()
        self._running = False
        self._proc: subprocess.Popen | None = None
        self._thread: threading.Thread | None = None

    @property
    def latest(self) -> PowerData | None:
        with self._lock:
            return self._latest

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        atexit.register(self.stop)

    def stop(self):
        self._running = False
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=3)
            except Exception:
                try:
                    self._proc.kill()
                except Exception:
                    pass

    def _run(self):
        try:
            self._proc = subprocess.Popen(
                [
                    "sudo", "-n", "powermetrics",
                    "-f", "plist",
                    "-i", "1000",
                    "-s", "cpu_power,gpu_power,thermal,ane_power",
                    "-n", "0",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception:
            return

        buffer = b""
        while self._running and self._proc.poll() is None:
            try:
                chunk = self._proc.stdout.read(4096)
                if not chunk:
                    break
                buffer += chunk
                while b"\x00" in buffer:
                    record, buffer = buffer.split(b"\x00", 1)
                    record = record.strip()
                    if record:
                        self._parse(record)
            except Exception:
                continue

    def _parse(self, data: bytes):
        try:
            d = plistlib.loads(data)
        except Exception:
            return

        clusters = []
        cpu_power = 0.0
        proc = d.get("processor", {})
        for c in proc.get("clusters", []):
            name = c.get("name", "?")
            power = c.get("power", 0)  # milliwatts
            freq = c.get("freq_hz", 0) / 1_000_000
            idle = c.get("idle_residency", 1.0)
            active = max(0, (1.0 - idle)) * 100
            clusters.append(ClusterPower(
                name=name, power_mw=power, freq_mhz=freq, active_pct=active,
            ))
            cpu_power += power

        gpu = d.get("gpu", {})
        gpu_power = gpu.get("power", 0)
        gpu_idle = gpu.get("idle_residency", 1.0)
        gpu_active = max(0, (1.0 - gpu_idle)) * 100
        gpu_freq = gpu.get("freq_hz", 0) / 1_000_000

        thermal = d.get("thermal_pressure", "Nominal")

        # ANE (Neural Engine)
        ane = d.get("ane", {})
        ane_power = ane.get("power", 0)
        ane_idle = ane.get("idle_residency", 1.0)
        ane_active = max(0, (1.0 - ane_idle)) * 100

        package_power = cpu_power + gpu_power + ane_power

        with self._lock:
            self._latest = PowerData(
                cpu_power_w=cpu_power / 1000,
                gpu_power_w=gpu_power / 1000,
                gpu_active_pct=gpu_active,
                gpu_freq_mhz=gpu_freq,
                thermal_pressure=thermal,
                clusters=clusters,
                package_power_w=package_power / 1000,
                ane_power_w=ane_power / 1000,
                ane_active_pct=ane_active,
            )
