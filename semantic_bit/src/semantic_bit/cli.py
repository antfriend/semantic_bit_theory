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
    """Load text from argument, file, or stdin with comprehensive error handling."""
    if file_path is not None:
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"Could not decode file '{file_path}' as UTF-8. Please ensure the file contains valid UTF-8 text.") from exc
        except PermissionError as exc:
            raise ValueError(f"Permission denied reading file: {file_path}") from exc
        except OSError as exc:
            raise ValueError(f"Error reading file '{file_path}': {exc}") from exc

    if argument_text is not None:
        return argument_text

    return _read_stdin()


def _read_stdin() -> str:
    try:
        return sys.stdin.read()
    except KeyboardInterrupt:  # Gracefully handle Ctrl+C.
        return ""


def main(argv: Optional[Iterable[str]] = None) -> int:
    # Convert argv to list for processing
    args_list = list(argv) if argv is not None else None
    
    # Determine if we should use legacy mode
    should_use_legacy = False
    
    if args_list is not None:
        # Explicit argv provided
        if len(args_list) == 0:
            # No arguments - could be stdin input
            should_use_legacy = True
        elif len(args_list) > 0:
            first_arg = args_list[0]
            # If first argument is not a subcommand or help flag, assume legacy
            if first_arg not in ["analyze", "encode", "decode", "-h", "--help"]:
                should_use_legacy = True
    else:
        # Check sys.argv directly
        import sys
        if len(sys.argv) == 1:
            # No arguments - could be stdin input
            should_use_legacy = True
        elif len(sys.argv) > 1:
            first_arg = sys.argv[1]
            if first_arg not in ["analyze", "encode", "decode", "-h", "--help"]:
                should_use_legacy = True
                
    # Apply legacy mode if detected
    if should_use_legacy:
        if args_list is not None:
            args_list = ["analyze"] + args_list
        else:
            import sys
            args_list = ["analyze"] + sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="semantic-bit CLI: analyze, encode, and decode text",
    )

    subparsers = parser.add_subparsers(dest="cmd")

    # analyze (default/legacy mode)
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

    try:
        args = parser.parse_args(args_list)
    except SystemExit as e:
        # Re-raise SystemExit to preserve argparse behavior
        raise e
    except Exception as e:
        import sys
        print(f"Error parsing arguments: {e}", file=sys.stderr)
        return 2

    # Dispatch based on subcommand with comprehensive error handling
    cmd = args.cmd
    if cmd is None:
        parser.error("A subcommand is required. Use 'analyze', 'encode', or 'decode'.")

    try:
        if cmd == "analyze":
            if args.text and args.file:
                parser.error("Provide either inline text or --file, not both.")
            
            text = _load_text(args.text, args.file)
            result = analyze_text(text)
            indent = None if args.no_indent else args.indent
            output = json.dumps(result, ensure_ascii=False, indent=indent)
            print(output)
            return 0

        elif cmd == "encode":
            if args.text and args.file:
                parser.error("Provide either inline text or --file, not both.")
            
            text = _load_text(args.text, args.file)
            sb = encode_text_to_sb(text)
            payload = json.dumps(sb, ensure_ascii=False, indent=args.indent)
            
            if args.out:
                try:
                    args.out.parent.mkdir(parents=True, exist_ok=True)  # Create parent dirs
                    args.out.write_text(payload, encoding="utf-8")
                except OSError as exc:
                    import sys
                    print(f"Error writing to file '{args.out}': {exc}", file=sys.stderr)
                    return 1
            else:
                print(payload)
            return 0

        elif cmd == "decode":
            # Read JSON input
            if args.file:
                try:
                    if not args.file.exists():
                        import sys
                        print(f"Error: File not found: {args.file}", file=sys.stderr)
                        return 1
                    content = args.file.read_text(encoding="utf-8")
                except OSError as exc:
                    import sys
                    print(f"Error reading file '{args.file}': {exc}", file=sys.stderr)
                    return 1
            else:
                content = _read_stdin()
            
            # Parse JSON
            try:
                sb = json.loads(content)
            except json.JSONDecodeError as exc:
                import sys
                print(f"Error: Invalid JSON input: {exc}", file=sys.stderr)
                return 1
            
            # Validate JSON structure
            if not isinstance(sb, dict) or "sentences" not in sb:
                import sys
                print("Error: JSON must contain a 'sentences' key with an array of triples", file=sys.stderr)
                return 1
            
            # Generate DOT output
            try:
                dot = decode_sb_to_dot(sb, graph_name=args.name)
            except Exception as exc:
                import sys
                print(f"Error generating DOT graph: {exc}", file=sys.stderr)
                return 1
            
            # Write output
            if args.out:
                try:
                    args.out.parent.mkdir(parents=True, exist_ok=True)  # Create parent dirs
                    args.out.write_text(dot, encoding="utf-8")
                except OSError as exc:
                    import sys
                    print(f"Error writing to file '{args.out}': {exc}", file=sys.stderr)
                    return 1
            else:
                print(dot)
            return 0

        else:
            parser.error(f"Unknown command: {cmd}")
            return 2
            
    except ValueError as exc:
        # Handle our custom ValueError exceptions from _load_text
        import sys
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        import sys
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130  # Standard exit code for SIGINT
    except Exception as exc:
        import sys
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())

