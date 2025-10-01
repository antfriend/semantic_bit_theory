"""Tests for semantic_bit.analyzer."""

import pytest

from semantic_bit import MAX_INPUT_LENGTH, analyze_text

def test_analyze_basic_counts_words_and_characters():
    text = "Hello world"
    result = analyze_text(text)

    assert result["word_count"] == 2
    assert result["character_count"] == len(text)
    assert result["is_empty"] is False

def test_analyze_text_respects_length_limit():
    with pytest.raises(ValueError):
        analyze_text("a" * (MAX_INPUT_LENGTH + 1))

def test_analyze_text_requires_string_input():
    with pytest.raises(TypeError):
        analyze_text(123)  # type: ignore[arg-type]
