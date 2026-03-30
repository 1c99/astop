"""Shared braille graph builder with gradient colors like btop."""

from __future__ import annotations

from rich.text import Text


def _gradient_color(row: int, total_rows: int) -> str:
    """Color by row position: bottom=green, middle=orange, top=red."""
    if total_rows <= 1:
        return "rgb(0,180,0)"
    pct = (total_rows - 1 - row) / (total_rows - 1)  # 0=bottom, 1=top
    if pct < 0.5:
        # Bottom half: green to orange
        ratio = pct * 2
        r = int(ratio * 220)
        g = int(160 - ratio * 40)
        return f"rgb({r},{g},0)"
    else:
        # Top half: orange to red
        ratio = (pct - 0.5) * 2
        r = int(220 + ratio * 35)
        g = int(120 - ratio * 120)
        return f"rgb({min(255, r)},{max(0, g)},0)"


def build_graph(
    history: list[float],
    width: int,
    height: int,
    base_color: str | None = None,
    fixed_scale: bool = True,
) -> list[Text]:
    """Build a braille waveform graph with gradient or single color.

    If base_color is None, uses gradient (green->yellow->red).
    If base_color is set, uses that color uniformly.
    """
    char_cols = width
    char_rows = height
    total_dots_h = char_rows * 4

    data = history[-(char_cols * 2):]
    while len(data) < char_cols * 2:
        data.insert(0, 0.0)

    data_max = max(data) if data else 0
    data_min = min(v for v in data if v >= 0) if data else 0

    if fixed_scale:
        # Center the wave: use range around the data with padding
        if data_max > 0:
            data_range = data_max - data_min
            padding = max(data_range * 0.5, data_max * 0.3, 3.0)
            min_val = max(0, data_min - padding)
            max_val = data_max + padding
            max_val = min(max_val, 100.0)
        else:
            min_val = 0
            max_val = 100.0
    else:
        min_val = 0
        max_val = max(data_max * 1.2, 5.0) if data_max > 0 else 100.0

    # Pre-compute which dots are active per column
    val_range = max_val - min_val if max_val > min_val else 1.0
    dot_heights: list[int] = []
    for di in range(len(data)):
        val = data[di]
        normalized = (val - min_val) / val_range
        normalized = max(0.0, min(1.0, normalized))
        dot_h = int(normalized * total_dots_h)
        if val > min_val and dot_h == 0:
            dot_h = 1
        dot_heights.append(dot_h)

    rows: list[Text] = []
    for row in range(char_rows):
        line = Text()
        if base_color:
            row_color = base_color
        else:
            row_color = _gradient_color(row, char_rows)
        empty_color = "rgb(25,35,25)" if not base_color else "rgb(25,35,35)"

        for col in range(char_cols):
            char_val = 0x2800
            has_dots = False
            for sub_col in range(2):
                di = col * 2 + sub_col
                if di >= len(dot_heights):
                    continue
                dh = dot_heights[di]
                for dot_row in range(4):
                    y = (char_rows - 1 - row) * 4 + (3 - dot_row)
                    if y < dh:
                        has_dots = True
                        if sub_col == 0:
                            char_val |= [0x01, 0x02, 0x04, 0x40][dot_row]
                        else:
                            char_val |= [0x08, 0x10, 0x20, 0x80][dot_row]

            line.append(chr(char_val), style=row_color if has_dots else empty_color)
        rows.append(line)

    return rows, max_val, min_val
