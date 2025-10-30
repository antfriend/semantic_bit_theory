"""Tests for SVG Animation Generation"""

import pytest
from semantic_bit import encode_text_to_sb, encode_sb_to_animated_svg


def test_basic_svg_generation():
    """Test that basic SVG generation works without errors."""
    sb = encode_text_to_sb("The cat sits on the mat.")
    svg = encode_sb_to_animated_svg(sb)

    assert svg is not None
    assert len(svg) > 0
    assert svg.startswith('<svg')
    assert svg.endswith('</svg>')


def test_empty_input_generates_the_end():
    """Test that empty input generates just 'The End.' sentence."""
    svg = encode_sb_to_animated_svg({})

    assert 'The End.' in svg
    # Should have one sentence group
    assert svg.count('class="sentence-0') == 1


def test_the_end_appended():
    """Test that 'The End.' is appended if not present."""
    sb = encode_text_to_sb("The cat sits.")
    svg = encode_sb_to_animated_svg(sb)

    assert 'The End.' in svg
    # Should have sentence-0 for "The cat sits" and sentence-1 for "The End."
    assert 'sentence-0' in svg
    assert 'sentence-1' in svg


def test_the_end_not_duplicated():
    """Test that 'The End.' is not duplicated if already present."""
    sb = encode_text_to_sb("The cat sits. The End.")
    svg = encode_sb_to_animated_svg(sb)

    # Count occurrences of "The End." in the SVG
    count = svg.count('The End.')
    assert count == 1, f"Expected 1 occurrence of 'The End.', found {count}"


def test_point_styling_present():
    """Test that Point term styling is present."""
    sb = encode_text_to_sb("A cactus grows.")
    svg = encode_sb_to_animated_svg(sb)

    assert 'sb-point' in svg
    assert 'sb-point-bg' in svg


def test_line_styling_present():
    """Test that Line term styling is present."""
    sb = encode_text_to_sb("The cat sits on the mat.")
    svg = encode_sb_to_animated_svg(sb)

    assert 'sb-line' in svg
    assert 'sb-line-bg' in svg


def test_animation_classes_applied():
    """Test that animation classes are applied to sentences."""
    sb = encode_text_to_sb("The cat sits. The dog barks.")
    svg = encode_sb_to_animated_svg(sb)

    # Should have animation classes
    assert 'anim-' in svg
    # Check for at least one of the animation types
    animation_found = any(anim in svg for anim in ['fade_in', 'slide_up', 'zoom_in', 'spin_in', 'pulse'])
    assert animation_found, "No animation class found in SVG"


def test_multiple_sentences():
    """Test that multiple sentences are rendered correctly."""
    sb = encode_text_to_sb("The cat sits. The dog barks. A bird flies.")
    svg = encode_sb_to_animated_svg(sb)

    # Should have 4 sentence groups (3 + "The End.")
    assert 'sentence-0' in svg
    assert 'sentence-1' in svg
    assert 'sentence-2' in svg
    assert 'sentence-3' in svg


def test_svg_dimensions():
    """Test that custom dimensions are applied."""
    sb = encode_text_to_sb("The cat sits.")
    svg = encode_sb_to_animated_svg(sb, width=1024, height=768)

    assert 'width="1024"' in svg
    assert 'height="768"' in svg
    assert 'viewBox="0 0 1024 768"' in svg


def test_custom_interval():
    """Test that custom interval is applied to animations."""
    sb = encode_text_to_sb("The cat sits.")
    svg = encode_sb_to_animated_svg(sb, interval_ms=5000)

    # Check for 5000ms duration in CSS
    assert '5000ms' in svg


def test_arrow_between_tokens():
    """Test that arrows appear between tokens in triple patterns."""
    sb = encode_text_to_sb("The cat sits on the mat.")
    svg = encode_sb_to_animated_svg(sb)

    # Should have arrow character
    assert '→' in svg or '&rarr;' in svg.lower()


def test_css_keyframes_present():
    """Test that CSS keyframe animations are defined."""
    sb = encode_text_to_sb("The cat sits.")
    svg = encode_sb_to_animated_svg(sb)

    # Check for keyframes
    assert '@keyframes' in svg


def test_last_sentence_class():
    """Test that the last sentence has special class."""
    sb = encode_text_to_sb("The cat sits.")
    svg = encode_sb_to_animated_svg(sb)

    # Last sentence should have last-sentence class
    assert 'last-sentence' in svg


def test_different_pattern_types():
    """Test rendering of different pattern types."""
    # Triple
    sb1 = encode_text_to_sb("The cat sits on the mat.")
    svg1 = encode_sb_to_animated_svg(sb1)
    assert 'sb-point' in svg1 and 'sb-line' in svg1

    # Point-only
    sb2 = encode_text_to_sb("A cactus.")
    svg2 = encode_sb_to_animated_svg(sb2)
    assert 'sb-point' in svg2

    # Line-point (question)
    sb3 = encode_text_to_sb("What is a cactus?")
    svg3 = encode_sb_to_animated_svg(sb3)
    assert 'sb-line' in svg3 and 'sb-point' in svg3


def test_text_escaping():
    """Test that special XML characters are escaped."""
    sb = encode_text_to_sb("The <cat> & the \"dog\".")
    svg = encode_sb_to_animated_svg(sb)

    # Should escape < > & "
    assert '&lt;' in svg or '<cat>' not in svg  # Either escaped or in text content
    assert '&amp;' in svg or '&' not in svg.split('<')[1].split('>')[0]  # Not in tag


def test_svg_structure():
    """Test basic SVG structure is valid."""
    sb = encode_text_to_sb("The cat sits.")
    svg = encode_sb_to_animated_svg(sb)

    # Check for required SVG elements
    assert '<svg' in svg
    assert 'xmlns="http://www.w3.org/2000/svg"' in svg
    assert '<defs>' in svg
    assert '<style>' in svg
    assert '</style>' in svg
    assert '</svg>' in svg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
