"""CPU metrics collector using psutil."""

from __future__ import annotations

from dataclasses import dataclass, field

import psutil

from astop.collectors.soc_info import SoCInfo


@dataclass
class CpuData:
    per_core: list[float] = field(default_factory=list)
    overall: float = 0.0
    cluster_averages: dict[str, float] = field(default_factory=dict)


class CpuCollector:
    def __init__(self, soc_info: SoCInfo):
        self.soc_info = soc_info
        # Prime the first call (returns 0s)
        psutil.cpu_percent(percpu=True)

    def collect(self) -> CpuData:
        per_core = psutil.cpu_percent(percpu=True)
        overall = psutil.cpu_percent()

        cluster_averages: dict[str, float] = {}
        for cluster in self.soc_info.clusters:
            start = cluster.start_index
            end = start + cluster.core_count
            cores = per_core[start:end]
            if cores:
                cluster_averages[cluster.name] = sum(cores) / len(cores)

        return CpuData(
            per_core=per_core,
            overall=overall,
            cluster_averages=cluster_averages,
        )
