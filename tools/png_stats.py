#!/usr/bin/env python3
"""
Minimal PNG inspector (no external deps).

Reports: width, height, bit depth, color type, interlace, and
computes an average color for RGB/RGBA 8-bit non-interlaced PNGs.
Optional outputs:
- --hist: RGB histograms (per-channel) with N bins (default 16)
- --ascii: grayscale ASCII preview with target width (default 80)

Usage:
  python tools/png_stats.py path/to/image.png [--hist [--bins 16]] [--ascii [--width 80]]
"""
from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path
from typing import Tuple, List


PNG_SIG = b"\x89PNG\r\n\x1a\n"


def read_chunk(data: memoryview, offset: int) -> Tuple[str, bytes, int]:
    if offset + 8 > len(data):
        raise ValueError("truncated PNG chunk header")
    length = struct.unpack_from(">I", data, offset)[0]
    ctype = bytes(data[offset + 4 : offset + 8]).decode("ascii")
    start = offset + 8
    end = start + length
    if end + 4 > len(data):
        raise ValueError("truncated PNG chunk data")
    chunk = bytes(data[start:end])
    # skip CRC (next 4 bytes)
    return ctype, chunk, end + 4


def parse_png_header(buf: bytes):
    mv = memoryview(buf)
    if not buf.startswith(PNG_SIG):
        raise ValueError("Not a PNG file (bad signature)")
    offset = len(PNG_SIG)
    width = height = bit_depth = color_type = comp = flt = interlace = None
    idat_parts: list[bytes] = []
    plte: bytes | None = None

    while offset < len(mv):
        ctype, chunk, offset = read_chunk(mv, offset)
        if ctype == "IHDR":
            width, height, bit_depth, color_type, comp, flt, interlace = struct.unpack(
                ">IIBBBBB", chunk
            )
        elif ctype == "PLTE":
            plte = chunk
        elif ctype == "IDAT":
            idat_parts.append(chunk)
        elif ctype == "IEND":
            break
        # ignore ancillary chunks

    if width is None:
        raise ValueError("IHDR not found")
    return {
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "compression": comp,
        "filter": flt,
        "interlace": interlace,
        "idat": b"".join(idat_parts),
        "plte": plte,
    }


def bytes_per_pixel(bit_depth: int, color_type: int) -> int:
    # Only for 8-bit depth
    if bit_depth != 8:
        return 0
    if color_type == 2:  # RGB
        return 3
    if color_type == 6:  # RGBA
        return 4
    if color_type == 0:  # grayscale
        return 1
    if color_type == 4:  # grayscale+alpha
        return 2
    if color_type == 3:  # indexed
        return 1
    return 0


def paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def unfilter_scanlines(raw: bytes, w: int, h: int, bpp: int) -> bytes:
    row_size = w * bpp
    out = bytearray(h * row_size)
    i = 0  # index into raw
    o = 0  # index into out
    prev_row = bytearray(row_size)
    for _ in range(h):
        ftype = raw[i]
        i += 1
        row = bytearray(raw[i : i + row_size])
        i += row_size
        if ftype == 0:  # None
            pass
        elif ftype == 1:  # Sub
            for x in range(row_size):
                left = row[x - bpp] if x >= bpp else 0
                row[x] = (row[x] + left) & 0xFF
        elif ftype == 2:  # Up
            for x in range(row_size):
                up = prev_row[x]
                row[x] = (row[x] + up) & 0xFF
        elif ftype == 3:  # Average
            for x in range(row_size):
                left = row[x - bpp] if x >= bpp else 0
                up = prev_row[x]
                row[x] = (row[x] + ((left + up) // 2)) & 0xFF
        elif ftype == 4:  # Paeth
            for x in range(row_size):
                a = row[x - bpp] if x >= bpp else 0
                b = prev_row[x]
                c = prev_row[x - bpp] if x >= bpp else 0
                row[x] = (row[x] + paeth(a, b, c)) & 0xFF
        else:
            raise ValueError(f"Unsupported PNG filter type: {ftype}")
        out[o : o + row_size] = row
        prev_row[:] = row
        o += row_size
    return bytes(out)


def avg_color(info: dict) -> tuple[int, int, int] | None:
    w = info["width"]
    h = info["height"]
    bit_depth = info["bit_depth"]
    ct = info["color_type"]
    interlace = info["interlace"]
    if bit_depth != 8 or interlace != 0 or ct not in (2, 6):
        return None
    bpp = bytes_per_pixel(bit_depth, ct)
    raw = zlib.decompress(info["idat"])  # includes filter bytes per row
    # Unfilter into pixel bytes
    pixels = unfilter_scanlines(raw, w, h, bpp)

    # Sampling stride to keep work bounded (~1e6 samples)
    max_samples = 1_000_000
    stride = max(1, int((w * h) / max_samples))

    r_sum = g_sum = b_sum = a_sum = 0
    count = 0
    if ct == 2:  # RGB
        for idx in range(0, w * h, stride):
            p = idx * 3
            r, g, b = pixels[p], pixels[p + 1], pixels[p + 2]
            r_sum += r
            g_sum += g
            b_sum += b
            count += 1
        if count == 0:
            return (0, 0, 0)
        return (r_sum // count, g_sum // count, b_sum // count)
    else:  # RGBA
        for idx in range(0, w * h, stride):
            p = idx * 4
            r, g, b, a = pixels[p], pixels[p + 1], pixels[p + 2], pixels[p + 3]
            r_sum += r * a
            g_sum += g * a
            b_sum += b * a
            a_sum += a
            count += 1
        if a_sum == 0 or count == 0:
            return (0, 0, 0)
        return (r_sum // a_sum, g_sum // a_sum, b_sum // a_sum)


def decode_pixels(info: dict) -> Tuple[bytes, int]:
    """Return (pixel_bytes, bytes_per_pixel) for supported PNGs or (b"", 0)."""
    w = info["width"]
    h = info["height"]
    bit_depth = info["bit_depth"]
    ct = info["color_type"]
    interlace = info["interlace"]
    if bit_depth != 8 or interlace != 0 or ct not in (2, 6):
        return b"", 0
    bpp = bytes_per_pixel(bit_depth, ct)
    raw = zlib.decompress(info["idat"])  # includes filter bytes per row
    pixels = unfilter_scanlines(raw, w, h, bpp)
    return pixels, bpp


def compute_histogram(pixels: bytes, bpp: int, bins: int, w: int, h: int) -> Tuple[List[int], List[int], List[int]]:
    """Compute per-channel histograms. bins should divide 256 evenly (e.g., 16, 32, 64)."""
    if bins <= 0 or 256 % bins != 0:
        bins = 16
    step = 256 // bins
    r_hist = [0] * bins
    g_hist = [0] * bins
    b_hist = [0] * bins
    if bpp == 3:
        for idx in range(w * h):
            p = idx * 3
            r = pixels[p]
            g = pixels[p + 1]
            b = pixels[p + 2]
            r_hist[r // step] += 1
            g_hist[g // step] += 1
            b_hist[b // step] += 1
    elif bpp == 4:
        for idx in range(w * h):
            p = idx * 4
            r = pixels[p]
            g = pixels[p + 1]
            b = pixels[p + 2]
            # ignore alpha for histogram bins
            r_hist[r // step] += 1
            g_hist[g // step] += 1
            b_hist[b // step] += 1
    return r_hist, g_hist, b_hist


def print_histogram(r_hist: List[int], g_hist: List[int], b_hist: List[int], bins: int) -> None:
    def render_line(name: str, hist: List[int]) -> None:
        maxv = max(hist) or 1
        barlen = 40
        line = []
        for v in hist:
            n = int(v / maxv * barlen)
            line.append("#" * n + " " * (barlen - n))
        # Show bins as compact blocks separated by | to save space
        blocks = "|".join(seg[:10] for seg in line)  # limit each block preview
        print(f"  {name}: {blocks}")

    print("Histogram (relative bars):")
    render_line("R", r_hist)
    render_line("G", g_hist)
    render_line("B", b_hist)


ASCII_GRAD = " .:-=+*#%@"


def print_ascii_preview(pixels: bytes, bpp: int, w: int, h: int, target_width: int) -> None:
    if target_width <= 0:
        target_width = 80
    # account for character aspect ratio; characters are ~2x taller than wide
    scale_x = w / target_width
    target_height = max(1, int(h / (scale_x * 2)))
    step_x = max(1, int(w / target_width))
    step_y = max(1, int(h / target_height))
    def lum_at(x: int, y: int) -> int:
        idx = (y * w + x)
        if bpp == 3:
            p = idx * 3
            r, g, b = pixels[p], pixels[p + 1], pixels[p + 2]
        else:
            p = idx * 4
            r, g, b = pixels[p], pixels[p + 1], pixels[p + 2]
        # Rec. 601 luma approximation
        return int(0.299 * r + 0.587 * g + 0.114 * b)
    levels = len(ASCII_GRAD) - 1
    for y in range(0, h, step_y):
        row_chars = []
        for x in range(0, w, step_x):
            L = lum_at(x, y)
            row_chars.append(ASCII_GRAD[int(L / 255 * levels)])
        print("".join(row_chars))


def color_type_name(ct: int) -> str:
    return {
        0: "grayscale",
        2: "rgb",
        3: "indexed",
        4: "grayscale+alpha",
        6: "rgba",
    }.get(ct, f"unknown({ct})")


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Minimal PNG inspector")
    ap.add_argument("image", type=Path)
    ap.add_argument("--hist", action="store_true", help="print RGB histograms")
    ap.add_argument("--bins", type=int, default=16, help="histogram bins (divisor of 256)")
    ap.add_argument("--ascii", action="store_true", help="print ASCII grayscale preview")
    ap.add_argument("--width", type=int, default=80, help="ASCII preview width")
    args = ap.parse_args()

    data = args.image.read_bytes()
    info = parse_png_header(data)
    w = info["width"]
    h = info["height"]
    bit_depth = info["bit_depth"]
    ct = info["color_type"]
    interlace = info["interlace"]
    print(f"File: {args.image}")
    print(f"  size: {w}x{h}")
    print(f"  bit depth: {bit_depth}")
    print(f"  color type: {ct} ({color_type_name(ct)})")
    print(f"  interlace: {interlace}")
    avg = avg_color(info)
    if avg is None:
        print("  average: (unsupported for this PNG type)")
    else:
        r, g, b = avg
        print(f"  average: rgb({r},{g},{b})  hex: #{r:02x}{g:02x}{b:02x}")

    if args.hist or args.ascii:
        pixels, bpp = decode_pixels(info)
        if not pixels or bpp not in (3, 4):
            print("\n(Decode unsupported for histogram/ASCII on this PNG)")
        else:
            if args.hist:
                r_hist, g_hist, b_hist = compute_histogram(pixels, bpp, args.bins, w, h)
                print_histogram(r_hist, g_hist, b_hist, args.bins)
            if args.ascii:
                print("\nASCII preview:")
                print_ascii_preview(pixels, bpp, w, h, args.width)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
