#!/usr/bin/env python3
"""
Render an SVG overlay from a Semantic Annotation JSON.

Usage:
  python tools/render_overlay.py annotations/sbt_23.json overlays/sbt_23.overlay.svg [--legend overlays/legend.json]

No external dependencies required.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


DEFAULT_COLORS = {
    "noun": "#2b6cb0",
    "verb": "#ed8936",
    "object": "#63b3ed",
    "predicate": "#f6ad55",
    "particle": "#4a5568",
    "wave": "#38a169",
    "person": "#805ad5",
    "feeling": "#d53f8c",
}


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def color_for(el: Dict[str, Any], colors: Dict[str, str]) -> str:
    axes = el.get("axes") or {}
    # Prioritize temporal (particle/wave) for visual grouping, fallback to lexical/logical
    for key in ("temporal", "lexical", "logical", "human"):
        val = axes.get(key)
        if isinstance(val, str) and val in colors:
            return colors[val]
    return "#333333"


def svg_header(w: int, h: int) -> str:
    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'>
  <defs>
    <marker id='arrow' viewBox='0 0 10 10' refX='10' refY='5' markerWidth='6' markerHeight='6' orient='auto-start-reverse'>
      <path d='M 0 0 L 10 5 L 0 10 z' fill='#4a5568' />
    </marker>
    <marker id='bar' viewBox='0 0 10 10' refX='5' refY='5' markerWidth='6' markerHeight='6' orient='auto'>
      <path d='M 4 0 L 6 0 L 6 10 L 4 10 z' fill='#e53e3e' />
    </marker>
  </defs>
"""


def render_node(el: Dict[str, Any], colors: Dict[str, str]) -> str:
    x = el.get("x", 0)
    y = el.get("y", 0)
    w = el.get("w", 120)
    h = el.get("h", 44)
    label = el.get("label", el.get("id", ""))
    fill = color_for(el, colors)
    rx = 6 if (el.get("axes", {}).get("logical") == "predicate") else 2
    return (
        f"<g id='{el.get('id')}' class='node'>\n"
        f"  <rect x='{x}' y='{y}' width='{w}' height='{h}' rx='{rx}' ry='{rx}' fill='{fill}' fill-opacity='0.15' stroke='{fill}' stroke-width='2'/>\n"
        f"  <text x='{x + w/2}' y='{y + h/2}' dominant-baseline='middle' text-anchor='middle' fill='#1a202c' font-family='Inter, Arial, sans-serif' font-size='12'>{label}</text>\n"
        f"</g>\n"
    )


def render_event(el: Dict[str, Any], colors: Dict[str, str]) -> str:
    cx = el.get("x", 0)
    cy = el.get("y", 0)
    r = el.get("r", 6)
    label = el.get("label", el.get("id", ""))
    fill = color_for(el, colors)
    return (
        f"<g id='{el.get('id')}' class='event'>\n"
        f"  <circle cx='{cx}' cy='{cy}' r='{r}' fill='{fill}' />\n"
        f"  <text x='{cx + r + 6}' y='{cy}' dominant-baseline='middle' fill='#1a202c' font-family='Inter, Arial, sans-serif' font-size='12'>{label}</text>\n"
        f"</g>\n"
    )


def render_band(el: Dict[str, Any], colors: Dict[str, str]) -> str:
    x = el.get("x", 0)
    y = el.get("y", 0)
    w = el.get("w", 200)
    h = el.get("h", 20)
    label = el.get("label", el.get("id", ""))
    fill = color_for(el, colors)
    return (
        f"<g id='{el.get('id')}' class='band'>\n"
        f"  <rect x='{x}' y='{y}' width='{w}' height='{h}' fill='{fill}' fill-opacity='0.12' stroke='{fill}' stroke-dasharray='4 3'/>\n"
        f"  <text x='{x + 6}' y='{y + h/2}' dominant-baseline='middle' fill='#1a202c' font-family='Inter, Arial, sans-serif' font-size='12'>{label}</text>\n"
        f"</g>\n"
    )


def render_link(el: Dict[str, Any], lookup: Dict[str, Dict[str, Any]]) -> str:
    src = lookup.get(el.get("from"))
    dst = lookup.get(el.get("to"))
    if not src or not dst:
        return ""

    # Approximate anchor points at element centers
    def center(e: Dict[str, Any]):
        if e.get("type") == "event":
            return e.get("x", 0), e.get("y", 0)
        x = e.get("x", 0) + (e.get("w", 0) / 2)
        y = e.get("y", 0) + (e.get("h", 0) / 2)
        return x, y

    x1, y1 = center(src)
    x2, y2 = center(dst)
    rel = el.get("relation", "updates_state")
    marker = "url(#arrow)" if rel == "updates_state" else ("url(#bar)" if rel == "terminates_state" else "url(#arrow)")
    stroke = "#4a5568" if rel == "updates_state" else ("#e53e3e" if rel == "terminates_state" else "#3182ce")

    return (
        f"<g class='link {rel}'>\n"
        f"  <line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{stroke}' stroke-width='2' marker-end='{marker}' />\n"
        f"</g>\n"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("annotation", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--legend", type=Path, default=None)
    args = ap.parse_args()

    ann = load_json(args.annotation)
    colors = DEFAULT_COLORS.copy()
    if args.legend and args.legend.exists():
        legend = load_json(args.legend)
        colors.update(legend.get("colors", {}))

    canvas = ann.get("canvas", {})
    width = int(canvas.get("width", 1200))
    height = int(canvas.get("height", 800))
    elements = ann.get("elements", [])

    # Build lookup
    lookup = {e.get("id"): e for e in elements}

    parts = [svg_header(width, height)]

    # Render bands first (background), then nodes/events, then links
    for e in elements:
        if e.get("type") == "band":
            parts.append(render_band(e, colors))
    for e in elements:
        if e.get("type") == "node":
            parts.append(render_node(e, colors))
        elif e.get("type") == "event":
            parts.append(render_event(e, colors))
    for e in elements:
        if e.get("type") == "link":
            parts.append(render_link(e, lookup))

    parts.append("</svg>\n")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(parts), encoding="utf-8")
    print(f"Wrote overlay: {args.output}")


if __name__ == "__main__":
    main()

