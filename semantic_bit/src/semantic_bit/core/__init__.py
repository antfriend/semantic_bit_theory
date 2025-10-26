"""Core semantic processing components for Semantic Bit Theory v2.0

This module contains the fundamental data structures and processing logic
for encoding natural language into semantic bit patterns.
"""

from .data_structures import (
    Token,
    # v2.0 structures
    SBContent,
    SBSentenceBase,
    SBSentence,
    SBPoint,
    SBLine,
    SBPointPoint,
    SBPointLine,
    SBLinePoint,
    SBTriple,
    SemanticBitDocument,
    PatternType,
)

from .tokenization import (
    segment_sentences,
    tokenize_sentence,
)

from .validation import (
    validate_text_for_encoding,
    validate_text_for_encoding_strict,
    ValidationLevel,
)

from .schema import (
    SEMANTIC_BIT_JSON_SCHEMA,
    SEMANTIC_BIT_JSON_SCHEMA_V2,
)

from .pattern_detection import (
    detect_pattern,
)

from .encoder import (
    encode_text_to_sb,
)

__all__ = [
    # Token
    "Token",
    # v2.0 Data Structures
    "SBContent",
    "SBSentenceBase",
    "SBSentence",
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
    # Schemas
    "SEMANTIC_BIT_JSON_SCHEMA",
    "SEMANTIC_BIT_JSON_SCHEMA_V2",
    # Pattern Detection
    "detect_pattern",
    # Encoder
    "encode_text_to_sb",
]
