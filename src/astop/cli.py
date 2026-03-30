"""CLI entry point for astop."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


def detect_sudo() -> bool:
    if os.geteuid() == 0:
        return True
    try:
        result = subprocess.run(
            ["sudo", "-n", "true"],
            capture_output=True,
            timeout=2,
        )
        return result.returncode == 0
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(
        prog="astop",
        description="astop - Apple Silicon System Monitor",
    )
    parser.add_argument(
        "--no-sudo", action="store_true",
        help="Disable sudo features (power/thermal/GPU utilization)",
    )
    parser.add_argument(
        "--refresh", type=float, default=1.0,
        help="Refresh interval in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--version", action="version", version="astop 0.1.0",
    )
    args = parser.parse_args()

    sudo_mode = False if args.no_sudo else detect_sudo()

    from astop.app import AstopApp
    app = AstopApp(sudo_mode=sudo_mode, refresh_rate=args.refresh)
    app.run()


if __name__ == "__main__":
    main()
