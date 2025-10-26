"""Tokenization and sentence segmentation for Semantic Bit Theory

Extracted from semantic.py for better code organization in v2.0.
"""

from __future__ import annotations

import re
from typing import List

from .data_structures import Token


# =============================================================================
# Patterns
# =============================================================================

# Tokenization pattern: words including contractions and possessives
_WORD_PATTERN = re.compile(r"\b[\w']+\b")

# Sentence boundary pattern: split on .!? followed by whitespace or end of text
_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


# =============================================================================
# Sentence Segmentation
# =============================================================================

def segment_sentences(text: str) -> List[str]:
    """Split text into discrete sentences at punctuation boundaries.

    Uses sentence-ending punctuation (.!?) followed by whitespace or end-of-text
    as segmentation boundaries. Preserves sentence-level semantic scope.

    Args:
        text: Input text to segment

    Returns:
        List of sentence strings, stripped of leading/trailing whitespace

    Example:
        >>> segment_sentences("Hello world. How are you?")
        ["Hello world.", "How are you?"]
    """
    if not text or not text.strip():
        return []

    # Split on sentence boundaries and filter empty results
    sentences = _SENTENCE_BOUNDARY.split(text.strip())
    return [sentence.strip() for sentence in sentences if sentence.strip()]


# =============================================================================
# Lexical Analysis
# =============================================================================

def tokenize_sentence(sentence: str) -> List[Token]:
    """Convert a sentence into a sequence of tokens.

    Uses regex pattern matching to extract words while preserving:
    - Contractions (don't, won't, etc.)
    - Possessives (cat's, children's, etc.)
    - Original surface form casing

    Args:
        sentence: Input sentence to tokenize

    Returns:
        List of Token objects with text and normalized forms

    Example:
        >>> tokens = tokenize_sentence("The cat's meowing")
        >>> [(t.text, t.normalized) for t in tokens]
        [("The", "the"), ("cat's", "cat's"), ("meowing", "meowing")]
    """
    if not sentence or not sentence.strip():
        return []

    tokens = []
    for match in _WORD_PATTERN.finditer(sentence):
        word = match.group(0)
        tokens.append(Token(text=word, normalized=word.lower()))

    return tokens
