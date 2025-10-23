"""Command line interface for semantic_bit.

Adds encode/decode subcommands for Semantic Bit triples while preserving
the original analyze behavior when no subcommand is provided.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, Optional

from .analyzer import analyze_text
from .semantic import encode_text_to_sb, decode_sb_to_dot


def _load_text(argument_text: Optional[str], file_path: Optional[Path]) -> str:
    if file_path is not None:
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:  # Provide more context when decoding fails.
            raise ValueError("could not decode the provided file as UTF-8") from exc

    if argument_text is not None:
        return argument_text

    return _read_stdin()


def _read_stdin() -> str:
    try:
        return sys.stdin.read()
    except KeyboardInterrupt:  # Gracefully handle Ctrl+C.
        return ""


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="semantic-bit CLI: analyze, encode, and decode text",
    )

    subparsers = parser.add_subparsers(dest="cmd")

    # analyze (default)
    p_analyze = subparsers.add_parser("analyze", help="Analyze text statistics")
    p_analyze.add_argument("text", nargs="?", help="Text to analyze; else read STDIN")
    p_analyze.add_argument("-f", "--file", type=Path, help="Path to text file to analyze")
    p_analyze.add_argument("--indent", type=int, default=2, help="Pretty-print JSON indentation")
    p_analyze.add_argument("--no-indent", action="store_true", help="Disable pretty printing")

    # encode
    p_encode = subparsers.add_parser("encode", help="Encode text to Semantic Bit JSON")
    p_encode.add_argument("text", nargs="?", help="Text to encode; else read STDIN")
    p_encode.add_argument("-f", "--file", type=Path, help="Path to text file to encode")
    p_encode.add_argument("-o", "--out", type=Path, help="Output JSON file (default stdout)")
    p_encode.add_argument("--indent", type=int, default=2, help="Pretty-print JSON indentation")

    # decode
    p_decode = subparsers.add_parser("decode", help="Decode SB JSON to Graphviz DOT")
    p_decode.add_argument("-f", "--file", type=Path, help="Input JSON file; else read STDIN")
    p_decode.add_argument("-o", "--out", type=Path, help="Output DOT file (default stdout)")
    p_decode.add_argument("--name", type=str, default="SBGraph", help="Graph name")

    # Back-compat: allow old style without subcommand
    parser.add_argument("text", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("-f", "--file", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--indent", type=int, default=2, help=argparse.SUPPRESS)
    parser.add_argument("--no-indent", action="store_true", help=argparse.SUPPRESS)

    args = parser.parse_args(list(argv) if argv is not None else None)

    # Dispatch based on subcommand or fall back to analyze
    cmd = args.cmd
    if cmd is None:
        # Back-compat analyze behavior
        if args.text and args.file:
            parser.error("Provide either inline text or --file, not both.")
        text = _load_text(args.text, args.file)
        result = analyze_text(text)
        indent = None if getattr(args, "no_indent", False) else getattr(args, "indent", 2)
        json_output = json.dumps(result, ensure_ascii=False, indent=indent)
        print(json_output)
        return 0

    if cmd == "analyze":
        if args.text and args.file:
            parser.error("Provide either inline text or --file, not both.")
        text = _load_text(args.text, args.file)
        result = analyze_text(text)
        indent = None if args.no_indent else args.indent
        print(json.dumps(result, ensure_ascii=False, indent=indent))
        return 0

    if cmd == "encode":
        if args.text and args.file:
            parser.error("Provide either inline text or --file, not both.")
        text = _load_text(args.text, args.file)
        sb = encode_text_to_sb(text)
        payload = json.dumps(sb, ensure_ascii=False, indent=args.indent)
        if args.out:
            args.out.write_text(payload, encoding="utf-8")
        else:
            print(payload)
        return 0

    if cmd == "decode":
        # Read JSON from file if provided, else from STDIN
        if args.file:
            content = args.file.read_text(encoding="utf-8")
        else:
            content = _read_stdin()
        try:
            sb = json.loads(content)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON: {exc}")
        dot = decode_sb_to_dot(sb, graph_name=args.name)
        if args.out:
            args.out.write_text(dot, encoding="utf-8")
        else:
            print(dot)
        return 0

    parser.error(f"Unknown command: {cmd}")
    return 2

if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())

