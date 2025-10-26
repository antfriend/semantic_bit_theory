"""Graph synthesis for Semantic Bit Theory v2.0

Converts semantic patterns into Graphviz DOT format for visualization.
"""

from __future__ import annotations

from typing import Dict, List, Any


def escape_dot_string(text: str) -> str:
    """Escape special characters for DOT format compliance.

    Ensures that node labels and edge labels are properly escaped
    to prevent DOT syntax errors.

    Args:
        text: Raw text to escape

    Returns:
        DOT-safe escaped string
    """
    if not text:
        return ""

    # Escape quotes and backslashes for DOT format
    escaped = text.replace('\\', '\\\\')  # Escape backslashes first
    escaped = escaped.replace('"', '\\"')  # Then escape quotes
    escaped = escaped.replace('\n', '\\n')  # Handle newlines
    escaped = escaped.replace('\t', '\\t')  # Handle tabs

    return escaped


def _extract_content(field: Any) -> str:
    """Extract content string from a field (handles both v2.0 objects and legacy strings).

    Args:
        field: Point or Line field (can be string for v1.0 or dict for v2.0)

    Returns:
        Content string
    """
    if isinstance(field, dict):
        return field.get("content", "")
    elif isinstance(field, str):
        return field
    return ""


def decode_sb_to_dot(sb: Dict[str, Any], graph_name: str = "SBGraph") -> str:
    """Transform Semantic Bit patterns into Graphviz DOT format.

    Supports both v1.0 (legacy string format) and v2.0 (flexible patterns).

    For v2.0 flexible patterns:
    - Triple: Full graph Point₁ → Line → Point₂
    - Point-Line: Point → Line (no second point)
    - Line-Point: Line → Point (no first point)
    - Point-Point: Point₁ ↔ Point₂ (bidirectional edge, no line label)
    - Point only: Single isolated node
    - Line only: Not visualized (no nodes)

    Implements:
    - Node Consolidation: Deduplicate identical point labels
    - Edge Construction: Create directed relationships
    - Output Generation: Produce standards-compliant DOT

    Args:
        sb: Semantic Bit document dictionary with "sentences" key
        graph_name: Name for the generated graph (default: "SBGraph")

    Returns:
        Complete DOT format string ready for Graphviz processing

    Example (v2.0):
        >>> sb = {
        ...     "version": "2.0",
        ...     "sentences": [{
        ...         "type": "triple",
        ...         "point1": {"content": "The cat"},
        ...         "line1": {"content": "sits on"},
        ...         "point2": {"content": "the mat"},
        ...         "original_text": "The cat sits on the mat."
        ...     }]
        ... }
        >>> dot = decode_sb_to_dot(sb)
        >>> "The cat" in dot
        True
    """
    if not sb or "sentences" not in sb:
        return f'digraph {graph_name} {{\n}}'

    dot_lines = [f'digraph {graph_name} {{']

    # Node consolidation: track unique point labels
    node_registry: Dict[str, str] = {}
    node_counter = 1

    def get_or_create_node_id(point_label: str) -> str:
        """Get existing node ID or create new one for a point label."""
        nonlocal node_counter

        if point_label not in node_registry:
            # Create new node with systematic ID
            node_id = f"p{node_counter}"
            node_counter += 1
            node_registry[point_label] = node_id

            # Add node definition to DOT output
            safe_label = escape_dot_string(point_label)
            dot_lines.append(f'  {node_id} [label="{safe_label}"];')

        return node_registry[point_label]

    # Edge construction: process all semantic patterns
    for sentence in sb.get("sentences", []):
        pattern_type = sentence.get("type", "triple")  # Default to triple for v1.0

        if pattern_type == "triple":
            _add_triple_to_graph(sentence, get_or_create_node_id, dot_lines)

        elif pattern_type == "point-line":
            _add_point_line_to_graph(sentence, get_or_create_node_id, dot_lines)

        elif pattern_type == "line-point":
            _add_line_point_to_graph(sentence, get_or_create_node_id, dot_lines)

        elif pattern_type == "point-point":
            _add_point_point_to_graph(sentence, get_or_create_node_id, dot_lines)

        elif pattern_type == "point":
            _add_point_to_graph(sentence, get_or_create_node_id, dot_lines)

        # Line-only patterns have no visualization (no nodes)

    dot_lines.append('}')
    return '\n'.join(dot_lines)


def _add_triple_to_graph(
    sentence: Dict[str, Any],
    get_node_id: Any,
    dot_lines: List[str]
) -> None:
    """Add Triple pattern to graph: Point₁ → Line → Point₂"""
    point1 = _extract_content(sentence.get("point1", "")).strip()
    line1 = _extract_content(sentence.get("line1", "")).strip()
    point2 = _extract_content(sentence.get("point2", "")).strip()

    # Skip incomplete triples
    if not (point1 and line1 and point2):
        return

    # Get or create node IDs for both points
    node1_id = get_node_id(point1)
    node2_id = get_node_id(point2)

    # Create directed edge with semantic label
    safe_edge_label = escape_dot_string(line1)
    dot_lines.append(f'  {node1_id} -> {node2_id} [label="{safe_edge_label}"];')


def _add_point_line_to_graph(
    sentence: Dict[str, Any],
    get_node_id: Any,
    dot_lines: List[str]
) -> None:
    """Add Point-Line pattern to graph: Point → [Line]"""
    point = _extract_content(sentence.get("point", "")).strip()
    line = _extract_content(sentence.get("line", "")).strip()

    if not (point and line):
        return

    # Create node
    node_id = get_node_id(point)

    # Show line as a label on a self-loop or annotation
    # For now, we'll create a self-loop with the line as label
    safe_line_label = escape_dot_string(line)
    dot_lines.append(f'  {node_id} -> {node_id} [label="{safe_line_label}"];')


def _add_line_point_to_graph(
    sentence: Dict[str, Any],
    get_node_id: Any,
    dot_lines: List[str]
) -> None:
    """Add Line-Point pattern to graph: [Line] → Point"""
    line = _extract_content(sentence.get("line", "")).strip()
    point = _extract_content(sentence.get("point", "")).strip()

    if not (line and point):
        return

    # Create node
    node_id = get_node_id(point)

    # Show line as a label on a self-loop
    safe_line_label = escape_dot_string(line)
    dot_lines.append(f'  {node_id} -> {node_id} [label="{safe_line_label}"];')


def _add_point_point_to_graph(
    sentence: Dict[str, Any],
    get_node_id: Any,
    dot_lines: List[str]
) -> None:
    """Add Point-Point pattern to graph: Point₁ ↔ Point₂"""
    point1 = _extract_content(sentence.get("point1", "")).strip()
    point2 = _extract_content(sentence.get("point2", "")).strip()

    if not (point1 and point2):
        return

    # Get or create node IDs
    node1_id = get_node_id(point1)
    node2_id = get_node_id(point2)

    # Create bidirectional edge (apposition/identity)
    # Use dir=both for bidirectional arrow
    dot_lines.append(f'  {node1_id} -> {node2_id} [dir=both, label="≡"];')


def _add_point_to_graph(
    sentence: Dict[str, Any],
    get_node_id: Any,
    dot_lines: List[str]
) -> None:
    """Add Point-only pattern to graph: isolated node"""
    content = _extract_content(sentence.get("content", "")).strip()

    if not content:
        return

    # Just create the node (no edges)
    get_node_id(content)
