#!/usr/bin/env python3
"""
OCR extractor for PNGs using Tesseract via pytesseract.

Requirements:
  - Tesseract OCR engine installed and on PATH
    Windows (choco):  choco install tesseract
    Windows (scoop):  scoop install tesseract
    macOS (brew):     brew install tesseract
    Linux (Debian):   sudo apt-get install tesseract-ocr

  - Python packages: pillow, pytesseract
    pip install pillow pytesseract

Usage:
  python tools/ocr_extract.py sbt_*.png --outdir text --lang eng --psm 6 --scale 1.5 --preprocess thresh

Notes:
  - Preprocessing can improve results on diagram-style images.
  - Outputs one .txt per image in the output directory.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Iterable, List


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extract text from images with Tesseract OCR")
    p.add_argument(
        "images",
        nargs="+",
        help="Image paths or globs (e.g. sbt_*.png)",
    )
    p.add_argument(
        "--outdir",
        default="text",
        help="Directory to write extracted .txt files (default: text)",
    )
    p.add_argument(
        "--lang",
        default="eng",
        help="Tesseract language (default: eng)",
    )
    p.add_argument(
        "--psm",
        type=int,
        default=6,
        help="Page segmentation mode (default: 6 = Assume a single uniform block of text)",
    )
    p.add_argument(
        "--oem",
        type=int,
        default=3,
        help="OCR Engine Mode (default: 3 = Default, based on what is available)",
    )
    p.add_argument(
        "--scale",
        type=float,
        default=1.0,
        help="Upscale factor before OCR (e.g., 1.5 or 2.0). Can help on small text.",
    )
    p.add_argument(
        "--preprocess",
        choices=["none", "gray", "thresh", "adaptive"],
        default="none",
        help="Optional preprocessing: grayscale or thresholding",
    )
    return p.parse_args()


def expand_paths(patterns: Iterable[str]) -> List[Path]:
    out: List[Path] = []
    from glob import glob

    for pat in patterns:
        matches = [Path(p) for p in glob(pat)]
        if not matches:
            # Treat as literal
            p = Path(pat)
            if p.exists():
                matches = [p]
        out.extend(matches)
    # Unique, keep order
    seen = set()
    uniq: List[Path] = []
    for p in out:
        if p not in seen:
            uniq.append(p)
            seen.add(p)
    return uniq


def load_image(path: Path):
    try:
        from PIL import Image, ImageFilter, ImageOps
    except Exception as e:
        raise SystemExit(
            "Pillow is required. Install with: pip install pillow\n"
            f"Import error: {e}"
        )

    img = Image.open(path)
    return img, ImageFilter, ImageOps


def preprocess_image(img, ImageFilter, ImageOps, *, scale: float, mode: str):
    # Optional upscale for small fonts
    if scale and scale != 1.0:
        w, h = img.size
        img = img.resize((int(w * scale), int(h * scale)), resample=getattr(img, "LANCZOS", 1))

    if mode == "none":
        return img
    if mode == "gray":
        return img.convert("L")
    if mode == "thresh":
        g = img.convert("L")
        # Light median filter to reduce noise
        g = g.filter(ImageFilter.MedianFilter(size=3))
        # Fixed threshold 150 (tweak as needed)
        return g.point(lambda p: 255 if p > 150 else 0).convert("L")
    if mode == "adaptive":
        # Simple approximation: enhance contrast and median-filter
        g = img.convert("L")
        g = ImageOps.autocontrast(g)
        g = g.filter(ImageFilter.MedianFilter(size=3))
        return g
    return img


def ocr_image(img, *, lang: str, psm: int, oem: int) -> str:
    try:
        import pytesseract
    except Exception as e:
        raise SystemExit(
            "pytesseract is required. Install with: pip install pytesseract\n"
            f"Import error: {e}"
        )

    config = f"--oem {oem} --psm {psm}"
    return pytesseract.image_to_string(img, lang=lang, config=config)


def main() -> int:
    args = parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    images = expand_paths(args.images)
    if not images:
        print("No images matched.")
        return 2

    # Check Tesseract availability early and provide a better error if missing
    tesseract_ok = True
    from shutil import which

    if which("tesseract") is None and which("tesseract.exe") is None:
        tesseract_ok = False
        print(
            "Warning: Tesseract binary not found on PATH.\n"
            "Install Tesseract OCR and ensure 'tesseract' is on your PATH.\n"
            "See: https://tesseract-ocr.github.io/tessdoc/Installation.html"
        )

    processed = 0
    for img_path in images:
        try:
            img, ImageFilter, ImageOps = load_image(img_path)
            img = preprocess_image(
                img,
                ImageFilter,
                ImageOps,
                scale=args.scale,
                mode=args.preprocess,
            )
            text = ocr_image(img, lang=args.lang, psm=args.psm, oem=args.oem)
        except SystemExit as e:
            print(e)
            return 2
        except Exception as e:
            print(f"[FAIL] {img_path}: {e}")
            continue

        out_path = outdir / (img_path.stem + ".txt")
        try:
            out_path.write_text(text, encoding="utf-8")
            print(f"[OK] {img_path} -> {out_path}")
            processed += 1
        except Exception as e:
            print(f"[FAIL] write {out_path}: {e}")

    if processed == 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

