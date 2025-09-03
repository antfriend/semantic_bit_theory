#!/usr/bin/env python3
"""
Validate Semantic Bit JSON instances with jsonschema if available,
and provide a friendly fallback validator otherwise.

Usage:
  python tools/validate.py [files_or_globs...]

If no args are given, validates:
  - examples/*.json
  - examples/invalid/*.json
"""
from __future__ import annotations

import json
import re
import sys
from glob import glob
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "semantic-bit.schema.json"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def try_jsonschema() -> Tuple[bool, Any]:
    try:
        import jsonschema  # type: ignore
        return True, jsonschema
    except Exception:
        return False, None


ALLOWED = {
    "lexical": {"noun", "verb"},
    "logical": {"object", "predicate"},
    "temporal": {"particle", "wave"},
    "human": {"person", "feeling", None},
}


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")


def fallback_validate(instance: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if not isinstance(instance, dict):
        return ["Root must be an object"]

    # story_id
    if not isinstance(instance.get("story_id"), str) or not instance["story_id"].strip():
        errors.append("story_id must be a non-empty string")

    # bits
    bits = instance.get("bits")
    if not isinstance(bits, list) or not bits:
        errors.append("bits must be a non-empty array")
        return errors

    for i, bit in enumerate(bits):
        loc = f"bits[{i}]"
        if not isinstance(bit, dict):
            errors.append(f"{loc} must be an object")
            continue
        if not isinstance(bit.get("bit_id"), str) or not bit["bit_id"].strip():
            errors.append(f"{loc}.bit_id must be a non-empty string")

        axes = bit.get("axes")
        if not isinstance(axes, dict):
            errors.append(f"{loc}.axes must be an object with required fields")
        else:
            for key in ("lexical", "logical", "temporal", "human"):
                if key not in axes:
                    errors.append(f"{loc}.axes.{key} is required")
            # Check enums
            if "lexical" in axes and axes["lexical"] not in ALLOWED["lexical"]:
                errors.append(f"{loc}.axes.lexical must be one of {sorted(ALLOWED['lexical'])}")
            if "logical" in axes and axes["logical"] not in ALLOWED["logical"]:
                errors.append(f"{loc}.axes.logical must be one of {sorted(ALLOWED['logical'])}")
            if "temporal" in axes and axes["temporal"] not in ALLOWED["temporal"]:
                errors.append(f"{loc}.axes.temporal must be one of {sorted(ALLOWED['temporal'])}")
            if "human" in axes and axes["human"] not in ALLOWED["human"]:
                errors.append(f"{loc}.axes.human must be one of {sorted(v for v in ALLOWED['human'] if v is not None)} or null")

        payload = bit.get("payload")
        if not isinstance(payload, dict):
            errors.append(f"{loc}.payload must be an object")
        else:
            # Optional format checks
            interval = payload.get("interval")
            if interval is not None:
                if not isinstance(interval, dict):
                    errors.append(f"{loc}.payload.interval must be an object")
                else:
                    start = interval.get("start")
                    if not isinstance(start, str) or not DATE_RE.match(start):
                        errors.append(f"{loc}.payload.interval.start must be YYYY-MM-DD")
                    end = interval.get("end")
                    if end is not None and (not isinstance(end, str) or not DATE_RE.match(end)):
                        errors.append(f"{loc}.payload.interval.end must be YYYY-MM-DD or null")

            time = payload.get("time")
            if time is not None and (not isinstance(time, str) or not DATETIME_RE.match(time)):
                errors.append(f"{loc}.payload.time must be RFC3339 UTC like YYYY-MM-DDTHH:MM:SSZ")

            intensity = payload.get("intensity")
            if intensity is not None:
                if not (isinstance(intensity, (int, float)) and 0 <= intensity <= 1):
                    errors.append(f"{loc}.payload.intensity must be a number in [0,1]")

    return errors


def main(argv: List[str]) -> int:
    patterns = argv[1:] or ["examples/*.json", "examples/invalid/*.json"]
    files: List[str] = []
    for p in patterns:
        files.extend(glob(p))
    files = sorted(set(files))
    if not files:
        print("No files matched.")
        return 2

    has_js, js = try_jsonschema()
    schema = None
    if has_js:
        try:
            schema = load_json(SCHEMA_PATH)
        except Exception as e:
            print(f"Failed to load schema: {SCHEMA_PATH}: {e}")
            return 2

    total_errors = 0
    for f in files:
        path = Path(f)
        try:
            data = load_json(path)
        except Exception as e:
            print(f"[ERROR] {f}: failed to parse JSON: {e}")
            total_errors += 1
            continue

        if has_js and schema is not None:
            try:
                js.validate(instance=data, schema=schema)  # type: ignore
                print(f"[OK]    {f}")
            except Exception as e:  # jsonschema.ValidationError or SchemaError
                # Try to extract nice path info if present
                msg = str(e)
                path_info = getattr(e, 'path', None)
                if path_info:
                    msg = f"at $.{'/'.join(map(str, path_info))}: {e.message}"
                print(f"[FAIL]  {f}: {msg}")
                total_errors += 1
        else:
            errs = fallback_validate(data)
            if not errs:
                print(f"[OK]    {f} (fallback)")
            else:
                print(f"[FAIL]  {f}")
                for err in errs:
                    print(f"        - {err}")
                total_errors += 1

    if total_errors:
        print(f"\n{total_errors} file(s) failed validation.")
        return 1
    else:
        print("\nAll files valid.")
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
