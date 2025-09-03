#!/usr/bin/env python3
"""
Extract embedded textual metadata from PNG files (tEXt, zTXt, iTXt).

Pure-stdlib; no external dependencies. Writes one .txt per image containing
all discovered key/value text entries.

Usage:
  python tools/png_textdump.py sbt_*.png --outdir text_metadata
"""
from __future__ import annotations

import argparse
import struct
import zlib
from pathlib import Path
from typing import Dict, List, Tuple


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
    return ctype, chunk, end + 4  # skip CRC


def parse_png_text(buf: bytes) -> List[Tuple[str, str]]:
    if not buf.startswith(PNG_SIG):
        raise ValueError("Not a PNG file (bad signature)")
    mv = memoryview(buf)
    offset = len(PNG_SIG)
    out: List[Tuple[str, str]] = []
    while offset < len(mv):
        ctype, chunk, offset = read_chunk(mv, offset)
        if ctype == "IEND":
            break
        if ctype == "tEXt":
            # key\0text (Latin-1)
            try:
                key, text = chunk.split(b"\x00", 1)
                out.append((key.decode("latin-1"), text.decode("latin-1", errors="replace")))
            except Exception:
                pass
        elif ctype == "zTXt":
            # key\0compression_method compressed_text
            try:
                key, rest = chunk.split(b"\x00", 1)
                comp_method = rest[0]
                comp_data = rest[1:]
                if comp_method == 0:
                    text = zlib.decompress(comp_data).decode("latin-1", errors="replace")
                    out.append((key.decode("latin-1"), text))
            except Exception:
                pass
        elif ctype == "iTXt":
            # key\0comp_flag\0comp_method\0lang\0translated_key\0text (UTF-8)
            try:
                parts = chunk.split(b"\x00", 5)
                if len(parts) == 6:
                    key, comp_flag_b, comp_method_b, lang, trans_key, text = parts
                    comp_flag = comp_flag_b[:1] if comp_flag_b else b"\x00"
                    if comp_flag == b"\x01":
                        # compressed UTF-8 text
                        text = zlib.decompress(text)
                    out.append((key.decode("utf-8", errors="replace"), text.decode("utf-8", errors="replace")))
            except Exception:
                pass
        # else: ignore
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Dump PNG textual metadata")
    ap.add_argument("images", nargs="+", help="Image files or globs")
    ap.add_argument("--outdir", default="text_metadata", help="Output directory (default: text_metadata)")
    args = ap.parse_args()

    from glob import glob

    files: List[Path] = []
    for pat in args.images:
        m = [Path(p) for p in glob(pat)]
        if not m:
            p = Path(pat)
            if p.exists():
                m = [p]
        files.extend(m)
    files = list(dict.fromkeys(files))
    if not files:
        print("No images matched.")
        return 2

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    any_found = False
    for f in files:
        try:
            data = Path(f).read_bytes()
            kvs = parse_png_text(data)
        except Exception as e:
            print(f"[FAIL] {f}: {e}")
            continue

        if not kvs:
            print(f"[OK] {f}: no embedded text chunks found")
            out_path = outdir / (Path(f).stem + ".txt")
            out_path.write_text("", encoding="utf-8")
            continue

        any_found = True
        out_path = outdir / (Path(f).stem + ".txt")
        with out_path.open("w", encoding="utf-8") as w:
            for k, v in kvs:
                w.write(f"[{k}]\n{v}\n\n")
        print(f"[OK] {f}: wrote {out_path} ({len(kvs)} entries)")

    return 0 if any_found else 0


if __name__ == "__main__":
    raise SystemExit(main())

