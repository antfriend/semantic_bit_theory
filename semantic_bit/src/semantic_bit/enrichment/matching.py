"""Token-based matching utilities for asset and function mapping

Uses Unicode normalization and case-folding for robust, language-aware matching.
"""

from __future__ import annotations

import re
import unicodedata
from typing import List, Set


# =============================================================================
# Normalization
# =============================================================================

def normalize_for_matching(text: str) -> str:
    """Normalize text for case/punctuation-insensitive matching.

    Uses Unicode NFKC normalization + casefold for robust matching across
    different character representations and languages.

    Args:
        text: Input text to normalize

    Returns:
        Normalized text suitable for matching

    Example:
        >>> normalize_for_matching("The Cactus!")
        'the cactus'
        >>> normalize_for_matching("café")
        'café'  # NFKC normalized, casefolded
    """
    if not text:
        return ""

    # Unicode NFKC normalization (compatibility decomposition + canonical composition)
    normalized = unicodedata.normalize("NFKC", text)

    # Casefold for case-insensitive comparison (more robust than lower() for non-ASCII)
    normalized = normalized.casefold()

    # Remove punctuation for matching
    # Keep only alphanumeric and whitespace
    normalized = re.sub(r'[^\w\s]', ' ', normalized)

    # Normalize whitespace
    normalized = ' '.join(normalized.split())

    return normalized


def tokenize_for_matching(text: str) -> List[str]:
    """Extract word tokens from text for matching.

    Args:
        text: Input text to tokenize

    Returns:
        List of normalized word tokens

    Example:
        >>> tokenize_for_matching("The cactus plant!")
        ['the', 'cactus', 'plant']
        >>> tokenize_for_matching("real-time processing")
        ['real', 'time', 'processing']
    """
    normalized = normalize_for_matching(text)
    if not normalized:
        return []

    # Split on whitespace to get tokens
    tokens = normalized.split()

    return tokens


def tokens_contain_phrase(content_tokens: List[str], label_tokens: List[str]) -> bool:
    """Check if content tokens contain the label phrase as a contiguous sequence.

    Args:
        content_tokens: Tokens from Point/Line content
        label_tokens: Tokens from asset label or function description

    Returns:
        True if label tokens appear as a contiguous sequence in content tokens

    Example:
        >>> content = ['the', 'cactus', 'plant', 'grows']
        >>> label = ['cactus']
        >>> tokens_contain_phrase(content, label)
        True

        >>> label = ['cactus', 'plant']
        >>> tokens_contain_phrase(content, label)
        True

        >>> label = ['cat']  # Not in content
        >>> tokens_contain_phrase(content, label)
        False

        >>> label = ['plant', 'grows']  # Contiguous
        >>> tokens_contain_phrase(content, label)
        True

        >>> label = ['cactus', 'grows']  # NOT contiguous
        >>> tokens_contain_phrase(content, label)
        False
    """
    if not label_tokens:
        return False

    if not content_tokens:
        return False

    label_len = len(label_tokens)
    content_len = len(content_tokens)

    # Label can't be longer than content
    if label_len > content_len:
        return False

    # Single token match
    if label_len == 1:
        return label_tokens[0] in content_tokens

    # Multi-token phrase match - must be contiguous
    for i in range(content_len - label_len + 1):
        if content_tokens[i:i + label_len] == label_tokens:
            return True

    return False


def exact_word_match(content: str, label: str) -> bool:
    """Check if content contains label as exact word(s), case/punctuation insensitive.

    This is the main matching function used for asset and function mapping.

    Args:
        content: Point or Line content
        label: Asset label or function description

    Returns:
        True if label words appear in content

    Example:
        >>> exact_word_match("The cactus plant", "cactus")
        True
        >>> exact_word_match("The cat", "catch")
        False  # Not a substring match!
        >>> exact_word_match("Real-time processing", "real time")
        True
    """
    content_tokens = tokenize_for_matching(content)
    label_tokens = tokenize_for_matching(label)

    return tokens_contain_phrase(content_tokens, label_tokens)
