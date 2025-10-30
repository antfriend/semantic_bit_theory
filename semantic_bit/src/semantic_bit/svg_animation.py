"""SVG Animation Generation for Semantic Bit Theory v2.0

Generates animated SVG slideshows from Semantic Bit JSON structures.
Displays one sentence at a time with automatic transitions and styled terms.
"""

from __future__ import annotations

from typing import Dict, List, Any, Tuple
import html
import hashlib


# Animation types for Line term mapping
ANIMATION_TYPES = ["fade_in", "slide_up", "zoom_in", "spin_in", "pulse"]


def encode_sb_to_animated_svg(
    sb_json: Dict[str, Any],
    *,
    interval_ms: int = 3000,
    width: int = 800,
    height: int = 600
) -> str:
    """Generate animated SVG slideshow from Semantic Bit JSON.

    Args:
        sb_json: Semantic Bit JSON (v2.0 format)
        interval_ms: Time per sentence in milliseconds (default: 3000)
        width: SVG width in pixels
        height: SVG height in pixels

    Returns:
        Complete SVG string with embedded CSS animations

    Example:
        >>> sb = encode_text_to_sb("The cat sits on the mat.")
        >>> svg = encode_sb_to_animated_svg(sb)
        >>> Path("output.svg").write_text(svg, encoding="utf-8")
    """
    if not sb_json or "sentences" not in sb_json:
        # Empty input - generate just "The End."
        sb_json = {
            "version": "2.0",
            "sentences": [
                {"type": "point", "content": "The End.", "original_text": "The End."}
            ]
        }

    # Ensure "The End." sentence exists
    sb_json = _ensure_the_end(sb_json)

    sentences = sb_json.get("sentences", [])
    num_sentences = len(sentences)

    # Generate CSS styles and animations
    css = _generate_css(num_sentences, interval_ms)

    # Generate sentence groups
    sentence_groups = []
    for idx, sentence in enumerate(sentences):
        group = _render_sentence_group(sentence, idx, num_sentences)
        sentence_groups.append(group)

    # Combine into complete SVG
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <style>
{css}
    </style>
  </defs>
  <rect width="100%" height="100%" fill="#f8f9fa"/>
  <g id="slideshow" transform="translate({width/2}, {height/2})">
{_indent_lines("".join(sentence_groups), 4)}
  </g>
</svg>'''

    return svg


def _ensure_the_end(sb_json: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure the last sentence is 'The End.' - append if not present.

    Args:
        sb_json: Semantic Bit JSON structure

    Returns:
        Modified SB JSON with "The End." as last sentence
    """
    sentences = sb_json.get("sentences", [])

    if not sentences:
        # Empty - add just "The End."
        sb_json["sentences"] = [
            {"type": "point", "content": "The End.", "original_text": "The End."}
        ]
        return sb_json

    last_sentence = sentences[-1]
    last_text = last_sentence.get("original_text", "").strip()

    if last_text != "The End.":
        # Append "The End." sentence
        sentences.append(
            {"type": "point", "content": "The End.", "original_text": "The End."}
        )

    return sb_json


def _extract_tokens(sentence: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Extract display tokens from a sentence.

    Args:
        sentence: Sentence dictionary from SB JSON

    Returns:
        List of (text, type) tuples where type is 'point' or 'line'
        Example: [("The cat", "point"), ("sits on", "line"), ("the mat", "point")]
    """
    sentence_type = sentence.get("type")
    tokens = []

    if sentence_type == "triple":
        point1 = sentence.get("point1", {}).get("content", "")
        line1 = sentence.get("line1", {}).get("content", "")
        point2 = sentence.get("point2", {}).get("content", "")
        if point1:
            tokens.append((point1, "point"))
        if line1:
            tokens.append((line1, "line"))
        if point2:
            tokens.append((point2, "point"))

    elif sentence_type == "point-line":
        point = sentence.get("point", {}).get("content", "")
        line = sentence.get("line", {}).get("content", "")
        if point:
            tokens.append((point, "point"))
        if line:
            tokens.append((line, "line"))

    elif sentence_type == "line-point":
        line = sentence.get("line", {}).get("content", "")
        point = sentence.get("point", {}).get("content", "")
        if line:
            tokens.append((line, "line"))
        if point:
            tokens.append((point, "point"))

    elif sentence_type == "point-point":
        point1 = sentence.get("point1", {}).get("content", "")
        point2 = sentence.get("point2", {}).get("content", "")
        if point1:
            tokens.append((point1, "point"))
        if point2:
            tokens.append((point2, "point"))

    elif sentence_type == "line":
        content = sentence.get("content", "")
        # Handle both string and dict content
        if isinstance(content, dict):
            content = content.get("content", "")
        if content:
            tokens.append((content, "line"))

    elif sentence_type == "point":
        content = sentence.get("content", "")
        # Handle both string and dict content
        if isinstance(content, dict):
            content = content.get("content", "")
        if content:
            tokens.append((content, "point"))

    return tokens


def _pick_animation(sentence: Dict[str, Any]) -> str:
    """Pick an animation type based on the first Line term in the sentence.

    Uses hash of Line content to deterministically select an animation.
    Falls back to 'fade_in' if no Line term exists.

    Args:
        sentence: Sentence dictionary from SB JSON

    Returns:
        Animation type name (e.g., "fade_in", "zoom_in")
    """
    sentence_type = sentence.get("type")
    line_content = None

    # Extract first Line content
    if sentence_type == "triple":
        line_content = sentence.get("line1", {}).get("content", "")
    elif sentence_type == "point-line" or sentence_type == "line-point":
        line_content = sentence.get("line", {}).get("content", "")
    elif sentence_type == "line":
        line_content = sentence.get("content", "")

    # If no line content, use default
    if not line_content:
        return "fade_in"

    # Hash the line content to pick animation
    hash_val = int(hashlib.md5(line_content.encode('utf-8')).hexdigest(), 16)
    idx = hash_val % len(ANIMATION_TYPES)
    return ANIMATION_TYPES[idx]


def _render_sentence_group(
    sentence: Dict[str, Any],
    idx: int,
    total_sentences: int
) -> str:
    """Render a single sentence as an SVG group.

    Args:
        sentence: Sentence dictionary from SB JSON
        idx: Sentence index (0-based)
        total_sentences: Total number of sentences

    Returns:
        SVG <g> element containing styled tokens
    """
    tokens = _extract_tokens(sentence)
    animation = _pick_animation(sentence)

    # Calculate layout
    token_gap = 20  # Gap between tokens
    arrow_width = 30  # Space for arrow

    # Build token elements
    token_elements = []
    current_x = 0

    for token_idx, (text, token_type) in enumerate(tokens):
        # Escape text for XML
        escaped_text = html.escape(text)

        # Estimate text width (rough approximation: 8px per char)
        text_width = len(text) * 8
        bg_width = text_width + 16  # Add padding
        bg_height = 32

        # Render token with background and text
        token_svg = f'''<g class="sb-token sb-{token_type}" transform="translate({current_x}, 0)">
  <rect class="sb-{token_type}-bg" x="{-bg_width/2}" y="-16" width="{bg_width}" height="{bg_height}" rx="4"/>
  <text class="sb-{token_type}" text-anchor="middle" y="5">{escaped_text}</text>
</g>'''
        token_elements.append(token_svg)

        current_x += bg_width/2

        # Add arrow between tokens
        if token_idx < len(tokens) - 1:
            arrow_svg = f'''<text class="sb-arrow" x="{current_x + arrow_width/2}" y="5" text-anchor="middle">→</text>'''
            token_elements.append(arrow_svg)
            current_x += arrow_width + bg_width/2
        else:
            current_x += bg_width/2

    # Center the entire group
    offset_x = -current_x / 2

    # Generate group with animation
    is_last = (idx == total_sentences - 1)
    animation_class = f"sentence-{idx} anim-{animation}"

    if is_last:
        # Last sentence - no loop
        animation_class += " last-sentence"

    group = f'''<g class="{animation_class}" transform="translate({offset_x}, 0)">
{_indent_lines("".join(token_elements), 2)}
</g>'''

    return group


def _generate_css(num_sentences: int, interval_ms: int) -> str:
    """Generate CSS styles and animations for the SVG.

    Args:
        num_sentences: Number of sentences to animate
        interval_ms: Duration per sentence in milliseconds

    Returns:
        CSS string with keyframes and styles
    """
    # Base styles
    css_parts = [
        "/* Base Styles */",
        ".sb-token { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 20px; }",
        ".sb-point { font-weight: bold; fill: #000; }",
        ".sb-point-bg { fill: #fff; stroke: #333; stroke-width: 2; }",
        ".sb-line { font-weight: bold; fill: #0a0; }",
        ".sb-line-bg { fill: #c7f7d4; stroke: #0a0; stroke-width: 2; }",
        ".sb-arrow { font-size: 24px; fill: #666; }",
        "",
        "/* Sentence visibility control */",
        f"[class*='sentence-'] {{ opacity: 0; visibility: hidden; animation-duration: {interval_ms}ms; animation-fill-mode: both; animation-iteration-count: 1; }}",
        f".last-sentence {{ animation-fill-mode: forwards; }}",
        "",
    ]

    # Generate animation keyframes
    css_parts.append("/* Animation Keyframes */")

    keyframes = {
        "fade_in": """@keyframes fadeIn {
  0%, 10% { opacity: 0; visibility: visible; }
  20%, 80% { opacity: 1; visibility: visible; }
  90%, 100% { opacity: 0; visibility: hidden; }
}""",
        "slide_up": """@keyframes slideUp {
  0%, 10% { opacity: 0; transform: translateY(50px); visibility: visible; }
  20%, 80% { opacity: 1; transform: translateY(0); visibility: visible; }
  90%, 100% { opacity: 0; transform: translateY(-50px); visibility: hidden; }
}""",
        "zoom_in": """@keyframes zoomIn {
  0%, 10% { opacity: 0; transform: scale(0.5); visibility: visible; }
  20%, 80% { opacity: 1; transform: scale(1); visibility: visible; }
  90%, 100% { opacity: 0; transform: scale(1.5); visibility: hidden; }
}""",
        "spin_in": """@keyframes spinIn {
  0%, 10% { opacity: 0; transform: rotate(-180deg) scale(0.5); visibility: visible; }
  20%, 80% { opacity: 1; transform: rotate(0deg) scale(1); visibility: visible; }
  90%, 100% { opacity: 0; transform: rotate(180deg) scale(0.5); visibility: hidden; }
}""",
        "pulse": """@keyframes pulse {
  0%, 10% { opacity: 0; transform: scale(0.8); visibility: visible; }
  20%, 40% { opacity: 1; transform: scale(1.1); visibility: visible; }
  50%, 80% { opacity: 1; transform: scale(1); visibility: visible; }
  90%, 100% { opacity: 0; transform: scale(0.8); visibility: hidden; }
}"""
    }

    for anim_name, keyframe in keyframes.items():
        css_parts.append(keyframe)

    css_parts.append("")
    css_parts.append("/* Animation assignments */")

    # Assign animations to sentences with delays
    for idx in range(num_sentences):
        delay = idx * interval_ms
        css_parts.append(f".sentence-{idx} {{ animation-delay: {delay}ms; }}")

    for anim_name in ANIMATION_TYPES:
        css_parts.append(f".anim-{anim_name} {{ animation-name: {_camel_case(anim_name)}; }}")

    return "\n".join(css_parts)


def _camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase.

    Args:
        snake_str: String in snake_case format

    Returns:
        String in camelCase format
    """
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def _indent_lines(text: str, spaces: int) -> str:
    """Indent each line of text by a number of spaces.

    Args:
        text: Multi-line string to indent
        spaces: Number of spaces to indent

    Returns:
        Indented text
    """
    indent = ' ' * spaces
    lines = text.split('\n')
    return '\n'.join(indent + line if line.strip() else line for line in lines)
