"""One-shot Apple Silicon SoC topology discovery.

Dynamically discovers CPU clusters, core counts, GPU cores — no hardcoded chip names.
This is what prevents the crashes that asitop/macmon have on newer chips.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ClusterInfo:
    name: str
    core_count: int
    start_index: int  # index of first core in psutil's per-core array


@dataclass(frozen=True)
class SoCInfo:
    chip_name: str
    clusters: list[ClusterInfo] = field(default_factory=list)
    total_cores: int = 0
    gpu_cores: int = 0
    metal_version: str = ""
    total_memory: int = 0


def _sysctl(key: str) -> str:
    try:
        r = subprocess.run(
            ["sysctl", "-n", key], capture_output=True, text=True, timeout=5
        )
        return r.stdout.strip()
    except Exception:
        return ""


def _sysctl_int(key: str) -> int:
    v = _sysctl(key)
    try:
        return int(v)
    except ValueError:
        return 0


def _get_gpu_info() -> tuple[int, str]:
    """Parse system_profiler for GPU core count and Metal version."""
    try:
        r = subprocess.run(
            ["system_profiler", "SPDisplaysDataType"],
            capture_output=True, text=True, timeout=10,
        )
        cores = 0
        metal = ""
        for line in r.stdout.splitlines():
            line = line.strip()
            if "Total Number of Cores" in line:
                parts = line.split(":")
                if len(parts) == 2:
                    try:
                        cores = int(parts[1].strip())
                    except ValueError:
                        pass
            if "Metal" in line and ":" in line:
                metal = line.split(":")[-1].strip()
        return cores, metal
    except Exception:
        return 0, ""


def discover() -> SoCInfo:
    """Discover the SoC topology dynamically."""
    chip_name = _sysctl("machdep.cpu.brand_string") or "Apple Silicon"
    total_memory = _sysctl_int("hw.memsize")

    # Discover performance levels (clusters)
    nperflevels = _sysctl_int("hw.nperflevels")
    if nperflevels == 0:
        nperflevels = 2  # fallback

    clusters: list[ClusterInfo] = []
    core_offset = 0
    for i in range(nperflevels):
        name = _sysctl(f"hw.perflevel{i}.name") or f"Cluster {i}"
        core_count = _sysctl_int(f"hw.perflevel{i}.physicalcpu")
        if core_count == 0:
            core_count = _sysctl_int(f"hw.perflevel{i}.logicalcpu")
        clusters.append(ClusterInfo(name=name, core_count=core_count, start_index=core_offset))
        core_offset += core_count

    total_cores = sum(c.core_count for c in clusters)
    if total_cores == 0:
        total_cores = _sysctl_int("hw.ncpu")

    gpu_cores, metal_version = _get_gpu_info()

    return SoCInfo(
        chip_name=chip_name,
        clusters=clusters,
        total_cores=total_cores,
        gpu_cores=gpu_cores,
        metal_version=metal_version,
        total_memory=total_memory,
    )
