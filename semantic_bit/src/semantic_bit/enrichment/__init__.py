"""External resource enrichment for Semantic Bit Theory v2.0

This module provides functionality for linking semantic elements to
external assets (URLs, images, documents) and executable functions.
"""

from .assets import map_assets_to_points
from .functions import map_functions_to_lines
from .matching import normalize_for_matching, tokenize_for_matching

__all__ = [
    "map_assets_to_points",
    "map_functions_to_lines",
    "normalize_for_matching",
    "tokenize_for_matching",
]
