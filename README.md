# astop

Terminal-based Apple Silicon system monitor. Like nvitop/btop, but for Mac.

## Install

```bash
pip install astop
```

## Usage

```bash
astop              # basic mode
sudo astop         # enhanced mode (power, thermal, GPU utilization)
astop --no-sudo    # force basic mode
astop --refresh 2  # 2-second refresh interval
```

## Keybindings

- `q` - Quit
- `p` - Pause/Resume
- `r` - Force refresh
