"""Core analysis utilities for the semantic_bit package."""

from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any, Dict, List

MAX_INPUT_LENGTH = 5000
_TOKEN_PATTERN = re.compile(r"\b[\w']+\b")

def analyze_text(text: str) -> Dict[str, Any]:
    """Calculate simple statistics for the given text.

    Raises:
        TypeError: If *text* is not a string.
        ValueError: If *text* exceeds MAX_INPUT_LENGTH characters.
    """

    if not isinstance(text, str):  # Explicit type validation to guard API misuse.
        raise TypeError("text must be a string")

    length = len(text)
    if length > MAX_INPUT_LENGTH:
        raise ValueError(
            f"text exceeds maximum length of {MAX_INPUT_LENGTH} characters"
        )

    stripped = text.strip()
    tokens = _TOKEN_PATTERN.findall(text.lower())
    frequency = Counter(tokens)

    most_common: List[Dict[str, Any]] = [
        {"token": token, "count": count}
        for token, count in frequency.most_common(5)
    ]

    return {
        "character_count": length,
        "trimmed_character_count": len(stripped),
        "word_count": len(tokens),
        "unique_word_count": len(frequency),
        "most_common_tokens": most_common,
        "line_count": text.count("\n") + (1 if text else 0),
        "is_empty": length == 0,
    }

def analyze_text_as_json(text: str) -> str:
    """Return the analysis results as a JSON string."""

    result = analyze_text(text)
    return json.dumps(result, ensure_ascii=False)
