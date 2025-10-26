"""Function mapping for Semantic Bit Theory v2.0

Maps executable functions or API endpoints to Lines in semantic structures.
"""

from __future__ import annotations

from typing import Dict, List, Any

from .matching import exact_word_match


def map_functions_to_lines(
    sb_json: Dict[str, Any],
    functions: List[Dict[str, str]]
) -> Dict[str, Any]:
    """Map named functions to Lines with matching content.

    Uses token-based exact word matching with Unicode normalization.
    Returns all matching functions as arrays.

    Args:
        sb_json: Semantic Bit JSON structure (v2.0 format)
        functions: List of {"name": str, "description": str} dictionaries
                   (name must be valid identifier, no spaces)

    Returns:
        Enhanced SB JSON with function references added to matching Lines

    Matching Strategy (Same as Assets):
    - Token-based: Extract words from both Line content and function descriptions
    - Normalize using Unicode NFKC + casefold() for case-insensitivity
    - Exact word match: "calculates" matches "calculates distance" ✓
    - Not substring: "calc" does NOT match "calculates" ✓
    - Multiple matches: Return all matching functions as an array

    Example:
        >>> sb_json = {
        ...     "version": "2.0",
        ...     "sentences": [{
        ...         "type": "triple",
        ...         "point1": {"content": "The system"},
        ...         "line1": {"content": "calculates"},
        ...         "point2": {"content": "distance"},
        ...         "original_text": "The system calculates distance."
        ...     }]
        ... }
        >>> functions = [{
        ...     "name": "calculate_distance",
        ...     "description": "calculates distance"
        ... }]
        >>> result = map_functions_to_lines(sb_json, functions)
        >>> result["sentences"][0]["line1"]["functions"]
        [{"name": "calculate_distance", "description": "calculates distance"}]
    """
    if not sb_json or "sentences" not in sb_json:
        return sb_json

    if not functions:
        return sb_json

    # Process each sentence
    for sentence in sb_json.get("sentences", []):
        sentence_type = sentence.get("type")

        # Identify line fields based on pattern type
        line_fields = _get_line_fields(sentence_type)

        # Map functions to each line field
        for field_name in line_fields:
            if field_name in sentence:
                _enrich_line_with_functions(sentence[field_name], functions)

    return sb_json


def _get_line_fields(sentence_type: str) -> List[str]:
    """Get the names of Line fields for a given sentence type."""
    line_field_map = {
        "point": [],  # No lines in point-only
        "line": ["content"],
        "point-point": [],  # No lines in point-point
        "point-line": ["line"],
        "line-point": ["line"],
        "triple": ["line1"],
    }
    return line_field_map.get(sentence_type, [])


def _enrich_line_with_functions(line: Dict[str, Any], functions: List[Dict[str, str]]) -> None:
    """Add matching functions to a Line object (modifies in place).

    Args:
        line: Line object (must have "content" key)
        functions: List of function dictionaries
    """
    if not isinstance(line, dict) or "content" not in line:
        return

    content = line["content"]
    if not isinstance(content, str):
        return

    # Find all matching functions
    # For functions, check if Line content is contained in function description
    # e.g., "calculates" should match description "calculates distance"
    matches = []
    for func in functions:
        description = func.get("description", "")
        if description and (exact_word_match(content, description) or exact_word_match(description, content)):
            matches.append({
                "name": func.get("name", ""),
                "description": description
            })

    # Only add functions field if there are matches
    if matches:
        line["functions"] = matches
