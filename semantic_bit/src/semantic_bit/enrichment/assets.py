"""Asset mapping for Semantic Bit Theory v2.0

Maps external resources (URLs, images, documents) to Points in semantic structures.
"""

from __future__ import annotations

from typing import Dict, List, Any

from .matching import exact_word_match


def map_assets_to_points(
    sb_json: Dict[str, Any],
    assets: List[Dict[str, str]]
) -> Dict[str, Any]:
    """Map named assets to Points with matching content.

    Uses token-based exact word matching with Unicode normalization.
    Returns all matching assets as arrays.

    Args:
        sb_json: Semantic Bit JSON structure (v2.0 format)
        assets: List of {"url": str, "label": str} dictionaries

    Returns:
        Enhanced SB JSON with asset references added to matching Points

    Matching Strategy:
    - Token-based: Extract words from both Point content and asset labels
    - Normalize using Unicode NFKC + casefold() for case-insensitivity
    - Exact word match: "cactus" in "The cactus plant" ✓
    - Not substring: "cat" does NOT match "catch" ✓
    - Multiple matches: Return all matching assets as an array

    Example:
        >>> sb_json = {
        ...     "version": "2.0",
        ...     "sentences": [{
        ...         "type": "triple",
        ...         "point1": {"content": "The cactus"},
        ...         "line1": {"content": "grows in"},
        ...         "point2": {"content": "desert"},
        ...         "original_text": "The cactus grows in desert."
        ...     }]
        ... }
        >>> assets = [
        ...     {"url": "https://wiki.org/cactus", "label": "cactus"},
        ...     {"url": "https://wiki.org/desert", "label": "desert"}
        ... ]
        >>> result = map_assets_to_points(sb_json, assets)
        >>> result["sentences"][0]["point1"]["assets"]
        [{"url": "https://wiki.org/cactus", "label": "cactus"}]
    """
    if not sb_json or "sentences" not in sb_json:
        return sb_json

    if not assets:
        return sb_json

    # Process each sentence
    for sentence in sb_json.get("sentences", []):
        sentence_type = sentence.get("type")

        # Identify point fields based on pattern type
        point_fields = _get_point_fields(sentence_type)

        # Map assets to each point field
        for field_name in point_fields:
            if field_name in sentence:
                _enrich_point_with_assets(sentence[field_name], assets)

    return sb_json


def _get_point_fields(sentence_type: str) -> List[str]:
    """Get the names of Point fields for a given sentence type."""
    point_field_map = {
        "point": ["content"],
        "line": [],  # No points in line-only
        "point-point": ["point1", "point2"],
        "point-line": ["point"],
        "line-point": ["point"],
        "triple": ["point1", "point2"],
    }
    return point_field_map.get(sentence_type, [])


def _enrich_point_with_assets(point: Dict[str, Any], assets: List[Dict[str, str]]) -> None:
    """Add matching assets to a Point object (modifies in place).

    Args:
        point: Point object (must have "content" key)
        assets: List of asset dictionaries
    """
    if not isinstance(point, dict) or "content" not in point:
        return

    content = point["content"]
    if not isinstance(content, str):
        return

    # Find all matching assets
    matches = []
    for asset in assets:
        label = asset.get("label", "")
        if label and exact_word_match(content, label):
            matches.append({
                "url": asset.get("url", ""),
                "label": label
            })

    # Only add assets field if there are matches
    if matches:
        point["assets"] = matches
