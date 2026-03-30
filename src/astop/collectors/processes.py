"""Process list collector."""

from __future__ import annotations

from dataclasses import dataclass

import psutil


@dataclass
class ProcessInfo:
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    status: str
    username: str


class ProcessCollector:
    def __init__(self):
        # Prime cpu_percent for all processes
        for p in psutil.process_iter(["cpu_percent"]):
            pass

    def collect(self, limit: int = 30) -> list[ProcessInfo]:
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status", "username"]):
            try:
                info = p.info
                procs.append(ProcessInfo(
                    pid=info["pid"],
                    name=info["name"] or "?",
                    cpu_percent=info["cpu_percent"] or 0.0,
                    memory_percent=info["memory_percent"] or 0.0,
                    status=info["status"] or "?",
                    username=info["username"] or "?",
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        procs.sort(key=lambda p: p.cpu_percent, reverse=True)
        return procs[:limit]
