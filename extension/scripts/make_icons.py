"""Draws the LegitCheck toolbar icons (16/32/48/128 px PNG) with the standard library only.

The mark is the same as the web favicon: an ink-green tile with two text lines and one
highlighted line between them, like a flagged phrase in a message.

Run from the repo root:  python extension/scripts/make_icons.py
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "icons"
SIZES = (16, 32, 48, 128)
SUPERSAMPLE = 8

INK = (0x0E, 0x2A, 0x22)
MARKER = (0xFF, 0xDF, 0x9E)
LINE = (0x87, 0x95, 0x91)  # white at 55% over ink

# (x, y, w, h, radius, colour) on the 32-unit grid used by the SVG logo.
SHAPES = (
    (0.0, 0.0, 32.0, 32.0, 8.0, INK),
    (8.0, 9.0, 16.0, 2.5, 1.25, LINE),
    (6.5, 14.2, 19.0, 4.2, 1.4, MARKER),
    (8.0, 21.0, 11.0, 2.5, 1.25, LINE),
)


def inside_rounded_rect(px: float, py: float, x: float, y: float, w: float, h: float, r: float) -> bool:
    if not (x <= px <= x + w and y <= py <= y + h):
        return False
    cx = min(max(px, x + r), x + w - r)
    cy = min(max(py, y + r), y + h - r)
    return (px - cx) ** 2 + (py - cy) ** 2 <= r * r


def render(size: int) -> bytes:
    scale = 32.0 / size
    rows = bytearray()
    for j in range(size):
        rows.append(0)  # PNG filter: none
        for i in range(size):
            acc = [0.0, 0.0, 0.0, 0.0]
            for sj in range(SUPERSAMPLE):
                for si in range(SUPERSAMPLE):
                    px = (i + (si + 0.5) / SUPERSAMPLE) * scale
                    py = (j + (sj + 0.5) / SUPERSAMPLE) * scale
                    colour = None
                    for x, y, w, h, r, c in SHAPES:
                        if inside_rounded_rect(px, py, x, y, w, h, r):
                            colour = c
                    if colour:
                        acc[0] += colour[0]
                        acc[1] += colour[1]
                        acc[2] += colour[2]
                        acc[3] += 1
            n = SUPERSAMPLE * SUPERSAMPLE
            covered = acc[3]
            if covered:
                rows += bytes((round(acc[0] / covered), round(acc[1] / covered), round(acc[2] / covered), round(255 * covered / n)))
            else:
                rows += b"\x00\x00\x00\x00"
    return png(size, size, bytes(rows))


def png(w: int, h: int, raw: bytes) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for size in SIZES:
        (OUT / f"icon-{size}.png").write_bytes(render(size))
        print(f"wrote icons/icon-{size}.png")


if __name__ == "__main__":
    main()
