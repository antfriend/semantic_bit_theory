"""Command line interface for semantic_bit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, Optional

from .analyzer import analyze_text


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
        description="Generate a semantic summary of up to 5000 characters of text.",
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Text to analyze. If omitted, input is read from STDIN.",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=Path,
        help="Path to a UTF-8 encoded text file to analyze.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Pretty-print JSON output with the provided indentation (default: 2).",
    )
    parser.add_argument(
        "--no-indent",
        action="store_true",
        help="Disable pretty-printing and emit a single-line JSON payload.",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.text and args.file:
        parser.error("Provide either inline text or --file, not both.")

    text = _load_text(args.text, args.file)
    result = analyze_text(text)

    indent = None if args.no_indent else args.indent
    json_output = json.dumps(result, ensure_ascii=False, indent=indent)
    print(json_output)

    return 0

if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
