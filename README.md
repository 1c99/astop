<p align="center">
  <h1 align="center">astop</h1>
  <p align="center">
    Terminal-based system monitor for Apple Silicon Macs
    <br />
    <i>Like btop, but built for M-series chips.</i>
  </p>
</p>

<p align="center">
  <a href="https://pypi.org/project/astop/"><img src="https://img.shields.io/pypi/v/astop?color=blue" alt="PyPI"></a>
  <a href="https://pypi.org/project/astop/"><img src="https://img.shields.io/pypi/pyversions/astop" alt="Python"></a>
  <a href="https://github.com/1c99/astop/blob/main/LICENSE"><img src="https://img.shields.io/github/license/1c99/astop" alt="License"></a>
</p>

<!-- Screenshot placeholder — replace with actual screenshot -->
<!-- <p align="center"><img src="assets/screenshot.png" width="800" /></p> -->

---

## Why astop?

Existing Apple Silicon monitors (asitop, macmon, mxtop) **hardcode chip names and cluster layouts**, causing crashes on newer chips. astop discovers your SoC topology at runtime via `sysctl` — no hardcoded chip tables, no breakage on M4/M5/future chips.

| Feature | astop | asitop | mxtop |
|---|---|---|---|
| Works on all M-series | Yes | Partial | No |
| Dynamic SoC discovery | Yes | No | No |
| GPU/ANE monitoring | Yes | Yes | Yes |
| Per-core CPU bars | Yes | No | No |
| Braille waveform graphs | Yes | No | No |
| No sudo required | Yes (degraded) | No | No |

## Install

```bash
pip install astop
```

Requires Python 3.11+ and macOS (Apple Silicon).

## Usage

```bash
astop              # basic mode — CPU, memory, disk, network, processes
sudo astop         # enhanced mode — adds GPU, ANE, power, thermals
astop --no-sudo    # force basic mode even with sudo available
astop --refresh 2  # custom refresh interval (default: 1s)
```

### Panels

| Panel | Basic Mode | Sudo Mode |
|---|---|---|
| **CPU** — per-core bars + braille graph | Yes | Yes |
| **GPU** — utilization, frequency, power | — | Yes |
| **ANE** — Neural Engine utilization | — | Yes |
| **Memory** — usage, active, wired, compressed | Yes | Yes |
| **Network / Disk** — I/O rates + graph | Yes | Yes |
| **Battery** — charge, watts, time remaining | Yes | Yes + power breakdown |
| **Processes** — sortable top-N table | Yes | Yes |

## Keybindings

| Key | Action |
|---|---|
| `q` | Quit |
| `p` | Pause / Resume |
| `r` | Force refresh |
| `s` | Cycle process sort (CPU / Mem / PID / Name) |
| `v` | Reverse sort order |

## How it works

astop uses `hw.nperflevels` and `hw.perflevel{i}.*` sysctl keys to dynamically discover CPU cluster topology at startup — no chip name lookup tables. GPU, ANE, and power data come from `powermetrics` (requires sudo). Everything else uses `psutil`.

Data collection runs in parallel via `asyncio` + thread executors, so the TUI never blocks.

## License

MIT
