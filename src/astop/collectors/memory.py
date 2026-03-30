"""Memory metrics collector."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

import psutil


@dataclass
class MemoryData:
    total: int = 0
    used: int = 0
    available: int = 0
    active: int = 0
    inactive: int = 0
    wired: int = 0
    compressed: int = 0
    percent: float = 0.0
    swap_used: int = 0
    swap_total: int = 0


def _parse_vm_stat() -> int:
    """Get compressed pages from vm_stat (not available via psutil)."""
    try:
        r = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=5)
        page_size = 16384  # Apple Silicon default
        for line in r.stdout.splitlines():
            if "page size of" in line:
                parts = line.split()
                for p in parts:
                    try:
                        page_size = int(p)
                    except ValueError:
                        continue
            if "occupied by compressor" in line:
                parts = line.split(":")
                if len(parts) == 2:
                    count = int(parts[1].strip().rstrip("."))
                    return count * page_size
    except Exception:
        pass
    return 0


class MemoryCollector:
    def collect(self) -> MemoryData:
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        compressed = _parse_vm_stat()

        return MemoryData(
            total=vm.total,
            used=vm.used,
            available=vm.available,
            active=vm.active,
            inactive=vm.inactive,
            wired=vm.wired,
            compressed=compressed,
            percent=vm.percent,
            swap_used=swap.used,
            swap_total=swap.total,
        )
