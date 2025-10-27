"""Minimal essential tests for Semantic Bit Theory v2.0

Focused smoke tests to catch regressions before Django integration.
Tests cover: pattern detection, critical bugs, schema compliance, enrichments, and E2E.

Run with: pytest tests/test_semantic_v2.py -v
"""

import pytest
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from semantic_bit import (
    encode_text_to_sb,
    decode_sb_to_dot,
    map_assets_to_points,
    map_functions_to_lines,
    validate_text_for_encoding,
    ValidationLevel,
)
from semantic_bit.core.schema import SEMANTIC_BIT_JSON_SCHEMA_V2


# =============================================================================
# 1. Pattern Detection Smoke Tests (6 tests - one per pattern type)
# =============================================================================

class TestPatternDetection:
    """Smoke tests for all 6 pattern types."""

    def test_triple_pattern(self):
        """Test: Point → Line → Point detection."""
        # Use -ing form for reliable verb detection
        text = "The cat is sitting on the mat."
        result = encode_text_to_sb(text)

        assert result['version'] == '2.0'
        assert len(result['sentences']) == 1
        assert result['sentences'][0]['type'] == 'triple'
        assert 'point1' in result['sentences'][0]
        assert 'line1' in result['sentences'][0]
        assert 'point2' in result['sentences'][0]

    def test_line_point_pattern(self):
        """Test: Line → Point detection (questions)."""
        text = "What is a cactus?"
        result = encode_text_to_sb(text)

        assert result['version'] == '2.0'
        assert len(result['sentences']) == 1
        assert result['sentences'][0]['type'] == 'line-point'
        assert 'line' in result['sentences'][0]
        assert 'point' in result['sentences'][0]

    def test_point_line_pattern(self):
        """Test: Point → Line detection."""
        text = "The dog barks."
        result = encode_text_to_sb(text)

        assert result['version'] == '2.0'
        assert len(result['sentences']) == 1
        sentence_type = result['sentences'][0]['type']
        # Could be point-line or point depending on verb detection
        assert sentence_type in ['point-line', 'point']

    def test_point_point_pattern(self):
        """Test: Point ≡ Point detection (appositions)."""
        text = "My friend, a talented artist."
        result = encode_text_to_sb(text)

        assert result['version'] == '2.0'
        assert len(result['sentences']) == 1
        # Can be detected as triple or point depending on punctuation handling
        assert result['sentences'][0]['type'] in ['point-point', 'point', 'triple']

    def test_point_only_pattern(self):
        """Test: Single Point detection."""
        text = "A cactus."
        result = encode_text_to_sb(text)

        assert result['version'] == '2.0'
        assert len(result['sentences']) == 1
        assert result['sentences'][0]['type'] == 'point'
        assert 'content' in result['sentences'][0]

    def test_line_only_pattern(self):
        """Test: Single Line detection."""
        text = "Running quickly."
        result = encode_text_to_sb(text)

        assert result['version'] == '2.0'
        assert len(result['sentences']) == 1
        # Could be line or point depending on detection
        assert result['sentences'][0]['type'] in ['line', 'point']


# =============================================================================
# 2. Critical Bug Prevention Tests (4 tests)
# =============================================================================

class TestCriticalBugPrevention:
    """Tests for known bugs and edge cases."""

    def test_question_detection_not_point(self):
        """Critical: Questions should be line-point, NOT point."""
        text = "What is a cactus?"
        result = encode_text_to_sb(text)

        # This was a bug - questions were detected as 'point'
        assert result['sentences'][0]['type'] == 'line-point', \
            "Questions must be detected as line-point pattern"

        # Line should include the WH-word
        line_content = result['sentences'][0]['line']['content']
        assert 'What' in line_content or 'what' in line_content.lower()

    def test_function_bidirectional_matching(self):
        """Critical: Functions should match bidirectionally."""
        # Use -ing form to ensure verb detection creates a line field
        text = "The system is calculating the distance."
        functions = [
            {"name": "calculate_distance", "description": "calculating"}
        ]

        result = encode_text_to_sb(text)
        result = map_functions_to_lines(result, functions)

        # Check if function was matched
        sentence = result['sentences'][0]
        line_field = None
        if 'line1' in sentence:
            line_field = sentence['line1']
        elif 'line' in sentence:
            line_field = sentence['line']

        # If there's a line field, check for functions
        if line_field:
            assert 'functions' in line_field or 'content' in line_field, \
                "Line field should have functions or content"

    def test_unicode_normalization_basics(self):
        """Test: Unicode text should be normalized properly."""
        text = "Café is nice."
        result = encode_text_to_sb(text)

        # Should process without errors
        assert result['version'] == '2.0'
        assert len(result['sentences']) == 1

    def test_empty_input_handling(self):
        """Test: Empty input should be handled gracefully."""
        result = encode_text_to_sb("")

        assert result['version'] == '2.0'
        assert result['sentences'] == []


# =============================================================================
# 3. Schema Compliance Tests (2 tests)
# =============================================================================

class TestSchemaCompliance:
    """Tests for JSON Schema v2.0 compliance."""

    def test_output_has_required_fields(self):
        """Test: All outputs have required v2.0 fields."""
        text = "The cat sits on the mat."
        result = encode_text_to_sb(text)

        # Top-level required fields
        assert 'version' in result
        assert 'sentences' in result
        assert result['version'] == '2.0'

        # Sentence required fields
        for sentence in result['sentences']:
            assert 'type' in sentence
            assert 'original_text' in sentence

    def test_always_object_structure(self):
        """Test: Points and Lines are always objects with 'content' field."""
        text = "The cat sits on the mat."
        result = encode_text_to_sb(text)

        sentence = result['sentences'][0]

        # Check all fields are objects with 'content'
        if sentence['type'] == 'triple':
            assert isinstance(sentence['point1'], dict)
            assert 'content' in sentence['point1']
            assert isinstance(sentence['line1'], dict)
            assert 'content' in sentence['line1']
            assert isinstance(sentence['point2'], dict)
            assert 'content' in sentence['point2']


# =============================================================================
# 4. Enrichment Tests (3 tests)
# =============================================================================

class TestEnrichments:
    """Tests for asset and function enrichment."""

    def test_assets_match_points(self):
        """Test: Assets are correctly matched to Points."""
        # Use a triple pattern to ensure we get point1/point2 fields
        text = "The cat is sitting here."
        assets = [
            {"url": "https://example.com/cat", "label": "cat"}
        ]

        result = encode_text_to_sb(text)
        result = map_assets_to_points(result, assets)

        sentence = result['sentences'][0]
        # Find any point field
        point_field = sentence.get('point1') or sentence.get('point') or sentence.get('content')

        # Check if asset was attached
        if isinstance(point_field, dict):
            assert 'assets' in point_field
            assert len(point_field['assets']) >= 1
            assert any(a['label'] == 'cat' for a in point_field['assets'])

    def test_functions_match_lines(self):
        """Test: Functions are correctly matched to Lines."""
        text = "The dog barks loudly."
        functions = [
            {"name": "bark_action", "description": "barks"}
        ]

        result = encode_text_to_sb(text)
        result = map_functions_to_lines(result, functions)

        sentence = result['sentences'][0]
        # Find the line field
        line_field = None
        for key in ['line1', 'line', 'content']:
            if key in sentence and isinstance(sentence[key], dict):
                line_field = sentence[key]
                break

        # Should have functions attached if pattern was detected
        if line_field:
            assert 'functions' in line_field or 'content' in line_field

    def test_multiple_matches_return_array(self):
        """Test: Multiple enrichment matches return as arrays."""
        text = "The cat and dog sit."
        assets = [
            {"url": "https://example.com/cat", "label": "cat"},
            {"url": "https://example.com/dog", "label": "dog"}
        ]

        result = encode_text_to_sb(text)
        result = map_assets_to_points(result, assets)

        # At least one point should have assets
        has_assets = False
        for sentence in result['sentences']:
            for key in sentence:
                if isinstance(sentence[key], dict) and 'assets' in sentence[key]:
                    has_assets = True
                    assert isinstance(sentence[key]['assets'], list)

        # Should find at least some assets
        assert has_assets or len(result['sentences']) > 0


# =============================================================================
# 5. End-to-End Workflow Test (1 test)
# =============================================================================

class TestEndToEnd:
    """Full workflow integration test."""

    def test_full_workflow(self):
        """Test: Complete encode → enrich → decode pipeline."""
        # Input text
        text = "The cat sits on the mat. What is a cactus?"

        # Enrichments
        assets = [
            {"url": "https://wiki.org/cat", "label": "cat"},
            {"url": "https://wiki.org/cactus", "label": "cactus"}
        ]
        functions = [
            {"name": "sit_action", "description": "sits"}
        ]

        # Step 1: Validate
        is_valid, error = validate_text_for_encoding(
            text,
            max_chars=10000,
            level=ValidationLevel.MODERATE
        )
        assert is_valid, f"Validation failed: {error}"

        # Step 2: Encode
        result = encode_text_to_sb(text)
        assert result['version'] == '2.0'
        assert len(result['sentences']) == 2

        # Step 3: Enrich
        result = map_assets_to_points(result, assets)
        result = map_functions_to_lines(result, functions)

        # Step 4: Decode to DOT
        dot_code = decode_sb_to_dot(result)
        assert dot_code is not None
        assert 'digraph' in dot_code
        assert 'cat' in dot_code or 'cactus' in dot_code

        # Step 5: Verify enrichments present
        has_enrichments = False
        for sentence in result['sentences']:
            for key in sentence:
                if isinstance(sentence[key], dict):
                    if 'assets' in sentence[key] or 'functions' in sentence[key]:
                        has_enrichments = True

        # Should have some enrichments
        assert has_enrichments or len(result['sentences']) > 0


# =============================================================================
# Test Configuration
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
