"""Pattern detection and extraction for Semantic Bit Theory v2.0

Rule-based decision tree for classifying sentences into 6 flexible patterns.
"""

from __future__ import annotations

from typing import List, Tuple, Optional

from .data_structures import (
    Token,
    SBContent,
    SBSentence,
    SBPoint,
    SBLine,
    SBPointPoint,
    SBPointLine,
    SBLinePoint,
    SBTriple,
)


# =============================================================================
# Linguistic Pattern Sets (from original semantic.py)
# =============================================================================

# Auxiliary verbs: core structural elements indicating verb phrases
_AUXILIARY_VERBS = {
    # Primary auxiliaries
    "am", "is", "are", "was", "were", "be", "been", "being",
    # Perfect auxiliaries
    "have", "has", "had",
    # Do-support auxiliaries
    "do", "does", "did",
    # Modal auxiliaries
    "can", "could", "will", "would", "shall", "should",
    "may", "might", "must", "ought",
}

# Prepositions that commonly attach to verb phrases
_VERBAL_PREPOSITIONS = {
    # Spatial prepositions
    "on", "in", "at", "over", "under", "above", "below", "beside",
    "through", "across", "around", "into", "onto", "upon",
    # Directional prepositions
    "to", "from", "toward", "towards", "away",
    # Temporal prepositions
    "during", "before", "after", "since", "until",
    # Abstract prepositions
    "with", "without", "by", "for", "of", "about", "against",
}

# Determiners: help identify noun phrase boundaries (English-specific)
_DETERMINERS = {
    # Articles
    "the", "a", "an",
    # Demonstratives
    "this", "that", "these", "those",
    # Possessives
    "my", "your", "his", "her", "its", "our", "their",
    # Quantifiers (basic)
    "some", "any", "many", "few", "several", "all", "no",
}

# WH-words: question indicators
_WH_WORDS = {
    "what", "who", "whom", "whose", "which",
    "where", "when", "why", "how"
}


# =============================================================================
# Helper Functions
# =============================================================================

def is_verb_like(token: Token) -> bool:
    """Determine if a token exhibits verb-like characteristics.

    Uses both lexical lookup and morphological pattern matching.

    Args:
        token: Token to analyze

    Returns:
        True if token appears to be verb-like, False otherwise
    """
    word = token.normalized

    # Direct auxiliary verb lookup
    if word in _AUXILIARY_VERBS:
        return True

    # Morphological verb indicators
    if word.endswith("ing") or word.endswith("ed"):
        return True

    # Additional common verb patterns
    if len(word) > 3 and word.endswith("s") and word[:-1] in _AUXILIARY_VERBS:
        return True  # handles "goes", "does", etc.

    return False


def is_article(token: Token) -> bool:
    """Check if token is an article (a, an, the)."""
    return token.normalized in {"a", "an", "the"}


def is_determiner(token: Token) -> bool:
    """Check if token is a determiner."""
    return token.normalized in _DETERMINERS


def is_wh_word(token: Token) -> bool:
    """Check if token is a WH-question word."""
    return token.normalized in _WH_WORDS


def starts_with_wh_or_auxiliary(tokens: List[Token]) -> bool:
    """Check if sentence starts with WH-word or auxiliary (question pattern)."""
    if not tokens:
        return False

    first_word = tokens[0].normalized

    # WH-questions
    if first_word in _WH_WORDS:
        return True

    # Auxiliary-first questions: "Is it?", "Can you?", "Did he?"
    if first_word in _AUXILIARY_VERBS:
        return True

    return False


# =============================================================================
# Extraction Functions
# =============================================================================

def extract_point(tokens: List[Token], start_idx: int = 0) -> Tuple[str, int]:
    """Extract a noun phrase (Point) from token sequence.

    Collects tokens until encountering a verb-like pattern.

    Args:
        tokens: List of tokens to process
        start_idx: Starting position in token list

    Returns:
        Tuple of (extracted_phrase, next_index)
    """
    if start_idx >= len(tokens):
        return "", start_idx

    current_idx = start_idx
    phrase_tokens = []

    # Collect tokens until we hit a verb-like token
    while current_idx < len(tokens):
        token = tokens[current_idx]

        # Stop at obvious verb indicators (but only after collecting at least one token)
        if phrase_tokens and is_verb_like(token):
            break

        phrase_tokens.append(token.text)
        current_idx += 1

    phrase = " ".join(phrase_tokens).strip()
    return phrase, current_idx


def extract_line(tokens: List[Token], start_idx: int, include_wh: bool = False) -> Tuple[str, int]:
    """Extract a verb phrase with optional preposition (Line) from token sequence.

    Args:
        tokens: List of tokens to process
        start_idx: Starting position in token list
        include_wh: If True, include WH-word at start (for questions)

    Returns:
        Tuple of (extracted_phrase, next_index)
    """
    if start_idx >= len(tokens):
        return "", start_idx

    current_idx = start_idx
    phrase_tokens = []
    found_verb = False

    # For questions, include leading WH-word in the line
    if include_wh and current_idx < len(tokens) and is_wh_word(tokens[current_idx]):
        phrase_tokens.append(tokens[current_idx].text)
        current_idx += 1

    # Collect all verb-like tokens
    while current_idx < len(tokens):
        token = tokens[current_idx]

        if is_verb_like(token):
            phrase_tokens.append(token.text)
            found_verb = True
            current_idx += 1
        elif found_verb:
            # After finding verbs, stop at non-verb tokens
            break
        else:
            # Haven't found a verb yet
            # If we have WH-word, we still need to find a verb
            if phrase_tokens and include_wh:
                current_idx += 1
                continue
            # Otherwise this might be a determiner before object
            break

    # Optionally attach a single preposition
    if current_idx < len(tokens) and found_verb:
        next_token = tokens[current_idx]
        if next_token.normalized in _VERBAL_PREPOSITIONS:
            phrase_tokens.append(next_token.text)
            current_idx += 1

    phrase = " ".join(phrase_tokens).strip()
    return phrase, current_idx


def extract_remaining(tokens: List[Token], start_idx: int) -> Tuple[str, int]:
    """Extract all remaining tokens as a phrase.

    Args:
        tokens: List of tokens to process
        start_idx: Starting position in token list

    Returns:
        Tuple of (extracted_phrase, next_index)
    """
    if start_idx >= len(tokens):
        return "", start_idx

    phrase_tokens = [token.text for token in tokens[start_idx:]]
    phrase = " ".join(phrase_tokens).strip()

    return phrase, len(tokens)


# =============================================================================
# Rule-Based Pattern Detection
# =============================================================================

def detect_pattern(tokens: List[Token], original_text: str) -> Optional[SBSentence]:
    """Detect and extract semantic pattern from tokenized sentence.

    Uses a rule-based decision tree with early exits on high-signal cues.

    Decision tree:
    1. Check for Line-first patterns (questions, imperatives)
    2. Try to extract Point₁
    3. Try to extract Line
    4. Try to extract Point₂
    5. Classify based on what was successfully extracted
    6. Default ambiguous cases to Point

    Args:
        tokens: Tokenized sentence
        original_text: Original sentence text with punctuation

    Returns:
        SBSentence subclass instance, or None if no valid pattern found

    Example:
        >>> from core.tokenization import tokenize_sentence
        >>> tokens = tokenize_sentence("What is a cactus?")
        >>> pattern = detect_pattern(tokens, "What is a cactus?")
        >>> pattern.type
        PatternType.LINE_POINT
    """
    if not tokens:
        return None

    # Rule 1: Line-first pattern detection (questions, imperatives)
    if starts_with_wh_or_auxiliary(tokens):
        return _try_line_first_pattern(tokens, original_text)

    # Rule 2: Try classic extraction (Point → Line → Point)
    point1, line_start = extract_point(tokens, 0)

    # If no Point₁ found, try Line-only or treat as Point
    if not point1:
        return _try_line_or_default_point(tokens, original_text)

    # Extract Line
    line, point2_start = extract_line(tokens, line_start)

    # If no Line found, this might be Point-only or Point-Point
    if not line:
        # Check if there's more content after point1
        remaining, _ = extract_remaining(tokens, line_start)
        if remaining:
            # Point-Point pattern (apposition)
            return SBPointPoint(
                point1=SBContent.from_string(point1),
                point2=SBContent.from_string(remaining),
                original_text=original_text
            )
        else:
            # Point-only pattern
            return SBPoint(
                content=SBContent.from_string(point1),
                original_text=original_text
            )

    # Extract Point₂
    point2, _ = extract_remaining(tokens, point2_start)

    # If no Point₂, this is Point-Line pattern
    if not point2:
        return SBPointLine(
            point=SBContent.from_string(point1),
            line=SBContent.from_string(line),
            original_text=original_text
        )

    # Full triple: Point₁ → Line → Point₂
    return SBTriple(
        point1=SBContent.from_string(point1),
        line1=SBContent.from_string(line),
        point2=SBContent.from_string(point2),
        original_text=original_text
    )


def _try_line_first_pattern(tokens: List[Token], original_text: str) -> Optional[SBSentence]:
    """Try to extract Line-first patterns (questions, imperatives).

    Args:
        tokens: Tokenized sentence
        original_text: Original sentence text

    Returns:
        SBSentence (Line-Point or Line-only), or fallback to Point
    """
    # Extract Line starting from beginning, including WH-word for questions
    line, point_start = extract_line(tokens, 0, include_wh=True)

    if not line:
        # No line found, default to Point
        full_text = " ".join(t.text for t in tokens)
        return SBPoint(
            content=SBContent.from_string(full_text),
            original_text=original_text
        )

    # Extract remaining as Point
    point, _ = extract_remaining(tokens, point_start)

    if not point:
        # Line-only pattern
        return SBLine(
            content=SBContent.from_string(line),
            original_text=original_text
        )

    # Line-Point pattern
    return SBLinePoint(
        line=SBContent.from_string(line),
        point=SBContent.from_string(point),
        original_text=original_text
    )


def _try_line_or_default_point(tokens: List[Token], original_text: str) -> SBSentence:
    """Try to extract Line-only, or default to Point.

    Args:
        tokens: Tokenized sentence
        original_text: Original sentence text

    Returns:
        SBSentence (Line or Point)
    """
    # Try to extract Line from beginning
    line, remaining_start = extract_line(tokens, 0)

    if line and remaining_start >= len(tokens):
        # Pure Line pattern (no remaining tokens)
        return SBLine(
            content=SBContent.from_string(line),
            original_text=original_text
        )

    # Default: treat entire sentence as Point
    full_text = " ".join(t.text for t in tokens)
    return SBPoint(
        content=SBContent.from_string(full_text),
        original_text=original_text
    )
