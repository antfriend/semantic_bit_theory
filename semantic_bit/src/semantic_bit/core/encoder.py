"""Main encoding function for Semantic Bit Theory v2.0

Converts natural language text into flexible semantic patterns.
"""

from __future__ import annotations

from typing import Dict, Any

from .tokenization import segment_sentences, tokenize_sentence
from .pattern_detection import detect_pattern
from .data_structures import SemanticBitDocument


def encode_text_to_sb(text: str) -> Dict[str, Any]:
    """Encode natural language text into Semantic Bit JSON v2.0.

    Implements flexible pattern detection supporting 6 pattern types:
    - Point only: Static concept, entity, state
    - Line only: Dynamic action, relationship, process
    - Point-Point: Apposition or identity relationship
    - Point-Line: Subject with action
    - Line-Point: Action to object (common in questions)
    - Triple: Classic Point₁ → Line → Point₂

    Processing Pipeline:
    1. Sentence Segmentation: Split text at punctuation boundaries
    2. Lexical Analysis: Tokenize while preserving surface forms
    3. Pattern Detection: Rule-based classification into 6 types
    4. Ambiguous Handling: Default to Point when structure is unclear

    Args:
        text: Input natural language text

    Returns:
        Dictionary with "version" and "sentences" keys.
        Version is "2.0". Sentences contain flexible patterns.

    Example:
        >>> result = encode_text_to_sb("The cat is sitting on the mat.")
        >>> result["version"]
        "2.0"
        >>> result["sentences"][0]["type"]
        "triple"
        >>> result["sentences"][0]["point1"]["content"]
        "The cat"

    Example (Question):
        >>> result = encode_text_to_sb("What is a cactus?")
        >>> result["sentences"][0]["type"]
        "line-point"
        >>> result["sentences"][0]["line"]["content"]
        "What is"

    Example (Single concept):
        >>> result = encode_text_to_sb("A cactus.")
        >>> result["sentences"][0]["type"]
        "point"
    """
    if not text or not text.strip():
        return {"version": "2.0", "sentences": []}

    document = SemanticBitDocument(sentences=[], version="2.0")

    # Phase 1: Sentence Segmentation
    sentences = segment_sentences(text)

    for sentence in sentences:
        # Phase 2: Lexical Analysis
        tokens = tokenize_sentence(sentence)
        if not tokens:
            continue

        # Phase 3: Pattern Detection
        pattern = detect_pattern(tokens, sentence)
        if pattern:
            document.add_sentence(pattern)

    return document.to_dict()
