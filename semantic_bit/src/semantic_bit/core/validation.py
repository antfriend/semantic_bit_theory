"""Pre-encoding validation for Semantic Bit Theory v2.0

Validates input text before processing to ensure encoding will succeed.
"""

from __future__ import annotations

from enum import Enum
from typing import Tuple, Optional

from .tokenization import segment_sentences


# =============================================================================
# Enums
# =============================================================================

class ValidationLevel(str, Enum):
    """Validation thoroughness levels"""
    MINIMAL = "minimal"          # Just length check
    MODERATE = "moderate"        # Length + segmentation + basic structure
    COMPREHENSIVE = "comprehensive"  # All checks + pattern extractability


# =============================================================================
# Validation Functions
# =============================================================================

def validate_text_for_encoding(
    text: str,
    max_chars: int = 10000,
    level: ValidationLevel = ValidationLevel.MODERATE
) -> Tuple[bool, Optional[str]]:
    """Validate that text can be successfully encoded to SB JSON.

    Args:
        text: Input text to validate
        max_chars: Maximum character limit (default 10,000, configurable)
        level: Validation thoroughness level

    Returns:
        Tuple of (is_valid, error_message). If valid, error_message is None.

    Validation checks by level:
    - MINIMAL: Length only
    - MODERATE: Length + sentence segmentation + at least one sentence
    - COMPREHENSIVE: All moderate checks + predict pattern extractability

    Note: Python strings are inherently JSON-safe, no serialization check needed.

    Example:
        >>> is_valid, error = validate_text_for_encoding("The cat sits.")
        >>> assert is_valid and error is None

        >>> is_valid, error = validate_text_for_encoding("x" * 20000)
        >>> assert not is_valid
        >>> print(error)
        "Text exceeds maximum length of 10000 characters (got 20000)"
    """
    # Check 1: Text is not None or empty
    if not text:
        return False, "Text is empty or None"

    # Check 2: Length limit (all levels)
    if len(text) > max_chars:
        return False, f"Text exceeds maximum length of {max_chars} characters (got {len(text)})"

    # Minimal level: only length check
    if level == ValidationLevel.MINIMAL:
        return True, None

    # Check 3: Sentence segmentation (moderate and comprehensive)
    sentences = segment_sentences(text)
    if not sentences:
        return False, "Text does not contain any valid sentences (no sentence-ending punctuation found)"

    # Check 4: At least one non-empty sentence after stripping
    non_empty_sentences = [s for s in sentences if s.strip()]
    if not non_empty_sentences:
        return False, "Text does not contain any non-empty sentences after segmentation"

    # Moderate level: length + segmentation
    if level == ValidationLevel.MODERATE:
        return True, None

    # Check 5: Comprehensive - predict at least one extractable pattern
    # This is a heuristic check - we look for basic structure indicators
    if level == ValidationLevel.COMPREHENSIVE:
        # At least one sentence should have multiple words (potential for pattern)
        has_multi_word_sentence = any(len(s.split()) > 1 for s in non_empty_sentences)
        if not has_multi_word_sentence:
            return False, "Text does not appear to contain extractable semantic patterns (all sentences are single words)"

    return True, None


def validate_text_for_encoding_strict(
    text: str,
    max_chars: int = 10000
) -> Tuple[bool, Optional[str]]:
    """Strict validation using COMPREHENSIVE level.

    Convenience wrapper for comprehensive validation.

    Args:
        text: Input text to validate
        max_chars: Maximum character limit

    Returns:
        Tuple of (is_valid, error_message)
    """
    return validate_text_for_encoding(text, max_chars, ValidationLevel.COMPREHENSIVE)
