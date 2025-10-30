"""Semantic Bit Theory v2.0 - Natural Language to Graph Conversion

This package implements Semantic Bit Theory (SBT), providing lightweight,
dependency-free conversion of natural language into semantic graphs.

Core functionality:
- encode_text_to_sb(): Convert text to flexible semantic patterns (v2.0)
- decode_sb_to_dot(): Transform patterns into Graphviz DOT format
- map_assets_to_points(): Link external resources to Points
- map_functions_to_lines(): Link executable functions to Lines

Data structures (v2.0):
- SBPoint, SBLine, SBPointPoint, SBPointLine, SBLinePoint, SBTriple
- SemanticBitDocument: Collection of flexible patterns
- Token: Lexical token with surface and normalized forms

Legacy analysis:
- analyze_text(): Text statistics and metadata

Example (v2.0):
    >>> import semantic_bit
    >>> result = semantic_bit.encode_text_to_sb("The cat is sitting on the mat.")
    >>> print(result["version"])
    "2.0"
    >>> print(result["sentences"][0]["type"])
    "triple"

    >>> dot_graph = semantic_bit.decode_sb_to_dot(result)
    >>> print(dot_graph)
    digraph SBGraph {
      p1 [label="The cat"];
      p2 [label="the mat"];
      p1 -> p2 [label="is sitting on"];
    }
"""

# Legacy analyzer functionality
from .analyzer import analyze_text, analyze_text_as_json, MAX_INPUT_LENGTH

# Core v2.0 functionality
from .core import (
    # Main encoding function
    encode_text_to_sb,
    # Data structures
    Token,
    SBContent,
    SBPoint,
    SBLine,
    SBPointPoint,
    SBPointLine,
    SBLinePoint,
    SBTriple,
    SemanticBitDocument,
    PatternType,
    # Tokenization
    segment_sentences,
    tokenize_sentence,
    # Validation
    validate_text_for_encoding,
    validate_text_for_encoding_strict,
    ValidationLevel,
    # Schema
    SEMANTIC_BIT_JSON_SCHEMA,
    SEMANTIC_BIT_JSON_SCHEMA_V2,
)

# Graph generation
from .graph import decode_sb_to_dot

# Enrichment
from .enrichment import (
    map_assets_to_points,
    map_functions_to_lines,
)

# SVG Animation
from .svg_animation import (
    encode_sb_to_animated_svg,
)

__all__ = [
    # Legacy API
    "analyze_text",
    "analyze_text_as_json",
    "MAX_INPUT_LENGTH",

    # Core v2.0 API
    "encode_text_to_sb",
    "decode_sb_to_dot",

    # Enrichment API
    "map_assets_to_points",
    "map_functions_to_lines",

    # SVG Animation API
    "encode_sb_to_animated_svg",

    # Data structures
    "Token",
    "SBContent",
    "SBPoint",
    "SBLine",
    "SBPointPoint",
    "SBPointLine",
    "SBLinePoint",
    "SBTriple",
    "SemanticBitDocument",
    "PatternType",

    # Tokenization
    "segment_sentences",
    "tokenize_sentence",

    # Validation
    "validate_text_for_encoding",
    "validate_text_for_encoding_strict",
    "ValidationLevel",

    # Schema
    "SEMANTIC_BIT_JSON_SCHEMA",
    "SEMANTIC_BIT_JSON_SCHEMA_V2",
]

__version__ = "2.0.0"
