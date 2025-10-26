"""Utility functions for Semantic Bit Theory visual testing interface

Handles formatting, color-coding, and graph rendering.
"""

import json
from typing import Dict, Any, List, Tuple


# =============================================================================
# Color Scheme
# =============================================================================

COLORS = {
    'point_bg': '#e3f2fd',      # Light blue background
    'point_text': '#1565c0',    # Dark blue text
    'line_bg': '#e8f5e9',       # Light green background
    'line_text': '#2e7d32',     # Dark green text
    'border': '#90caf9',        # Border color
    'meta_text': '#666666',     # Gray for metadata
}

# Pattern type emojis
PATTERN_EMOJIS = {
    'point': '🔵',
    'line': '🟢',
    'point-point': '🔵🔵',
    'point-line': '🔵🟢',
    'line-point': '🟢🔵',
    'triple': '🔵🟢🔵',
}


# =============================================================================
# HTML Formatting
# =============================================================================

def format_pattern_html(sentence: Dict[str, Any]) -> str:
    """Generate color-coded HTML for a single sentence pattern.

    Args:
        sentence: Sentence dictionary from SB JSON

    Returns:
        HTML string with color-coded pattern visualization
    """
    pattern_type = sentence.get('type', 'unknown')
    original_text = sentence.get('original_text', '')
    emoji = PATTERN_EMOJIS.get(pattern_type, '⚪')

    html = f'''
    <div class="sb-sentence">
        <div class="sb-meta">
            <span class="sb-emoji">{emoji}</span>
            <strong>Type:</strong> {pattern_type}
        </div>
        <div class="sb-original">"{original_text}"</div>
        <div class="sb-pattern">
    '''

    # Format based on pattern type
    if pattern_type == 'triple':
        point1 = _extract_content(sentence.get('point1', {}))
        line1 = _extract_content(sentence.get('line1', {}))
        point2 = _extract_content(sentence.get('point2', {}))

        html += f'''
            <span class="sb-point">{point1}</span>
            <span class="sb-arrow">→</span>
            <span class="sb-line">{line1}</span>
            <span class="sb-arrow">→</span>
            <span class="sb-point">{point2}</span>
        '''

    elif pattern_type == 'line-point':
        line = _extract_content(sentence.get('line', {}))
        point = _extract_content(sentence.get('point', {}))

        html += f'''
            <span class="sb-line">{line}</span>
            <span class="sb-arrow">→</span>
            <span class="sb-point">{point}</span>
        '''

    elif pattern_type == 'point-line':
        point = _extract_content(sentence.get('point', {}))
        line = _extract_content(sentence.get('line', {}))

        html += f'''
            <span class="sb-point">{point}</span>
            <span class="sb-arrow">→</span>
            <span class="sb-line">{line}</span>
        '''

    elif pattern_type == 'point-point':
        point1 = _extract_content(sentence.get('point1', {}))
        point2 = _extract_content(sentence.get('point2', {}))

        html += f'''
            <span class="sb-point">{point1}</span>
            <span class="sb-arrow">≡</span>
            <span class="sb-point">{point2}</span>
        '''

    elif pattern_type == 'point':
        content = _extract_content(sentence.get('content', {}))
        html += f'<span class="sb-point">{content}</span>'

    elif pattern_type == 'line':
        content = _extract_content(sentence.get('content', {}))
        html += f'<span class="sb-line">{content}</span>'

    # Show enrichments if present
    enrichments = _get_enrichments(sentence)
    if enrichments:
        html += f'''
        <div class="sb-enrichments">
            {enrichments}
        </div>
        '''

    html += '''
        </div>
    </div>
    '''

    return html


def _extract_content(field: Any) -> str:
    """Extract content string from field (handles both dict and string)."""
    if isinstance(field, dict):
        return field.get('content', '')
    return str(field) if field else ''


def _get_enrichments(sentence: Dict[str, Any]) -> str:
    """Extract and format enrichment information (assets/functions)."""
    enrichments = []

    # Check all possible fields for assets
    for field_name in ['point1', 'point2', 'point', 'content']:
        if field_name in sentence:
            field = sentence[field_name]
            if isinstance(field, dict) and 'assets' in field:
                for asset in field['assets']:
                    label = asset.get('label', 'unknown')
                    url = asset.get('url', '#')
                    enrichments.append(
                        f'🔗 Asset: <a href="{url}" target="_blank">{label}</a>'
                    )

    # Check all possible fields for functions
    for field_name in ['line1', 'line', 'content']:
        if field_name in sentence:
            field = sentence[field_name]
            if isinstance(field, dict) and 'functions' in field:
                for func in field['functions']:
                    name = func.get('name', 'unknown')
                    desc = func.get('description', '')
                    enrichments.append(
                        f'⚡ Function: <code>{name}</code> ({desc})'
                    )

    return '<br>'.join(enrichments) if enrichments else ''


def format_all_patterns(sb_json: Dict[str, Any]) -> str:
    """Generate HTML for all sentences in SB JSON with CSS styling.

    Args:
        sb_json: Complete Semantic Bit JSON output

    Returns:
        Complete HTML with embedded CSS
    """
    css = f'''
    <style>
        .sb-container {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 100%;
        }}
        .sb-sentence {{
            margin: 15px 0;
            padding: 15px;
            border-left: 4px solid {COLORS['border']};
            background: white;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .sb-meta {{
            color: {COLORS['meta_text']};
            font-size: 0.9em;
            margin-bottom: 8px;
        }}
        .sb-emoji {{
            font-size: 1.2em;
            margin-right: 5px;
        }}
        .sb-original {{
            font-style: italic;
            color: #555;
            margin-bottom: 10px;
            padding: 8px;
            background: #f5f5f5;
            border-radius: 3px;
        }}
        .sb-pattern {{
            font-size: 1.1em;
            line-height: 2;
        }}
        .sb-point {{
            background: {COLORS['point_bg']};
            color: {COLORS['point_text']};
            padding: 4px 10px;
            border-radius: 4px;
            font-weight: 500;
            margin: 0 3px;
            display: inline-block;
        }}
        .sb-line {{
            background: {COLORS['line_bg']};
            color: {COLORS['line_text']};
            padding: 4px 10px;
            border-radius: 4px;
            font-weight: 500;
            margin: 0 3px;
            display: inline-block;
        }}
        .sb-arrow {{
            color: #999;
            margin: 0 8px;
            font-weight: bold;
        }}
        .sb-enrichments {{
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px dashed #ddd;
            font-size: 0.9em;
            color: #666;
        }}
        .sb-enrichments a {{
            color: #1976d2;
            text-decoration: none;
        }}
        .sb-enrichments a:hover {{
            text-decoration: underline;
        }}
        .sb-enrichments code {{
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
    </style>
    '''

    sentences = sb_json.get('sentences', [])
    if not sentences:
        return css + '<div class="sb-container"><p>No patterns detected.</p></div>'

    html_parts = [css, '<div class="sb-container">']

    for i, sentence in enumerate(sentences, 1):
        html_parts.append(format_pattern_html(sentence))

    html_parts.append('</div>')

    return '\n'.join(html_parts)


# =============================================================================
# Statistics
# =============================================================================

def generate_stats(sb_json: Dict[str, Any]) -> str:
    """Generate statistics about detected patterns.

    Args:
        sb_json: Complete Semantic Bit JSON output

    Returns:
        HTML formatted statistics
    """
    sentences = sb_json.get('sentences', [])

    if not sentences:
        return '<p>No patterns to analyze.</p>'

    # Count pattern types
    pattern_counts = {}
    total_points = 0
    total_lines = 0
    total_enrichments = 0

    for sentence in sentences:
        pattern_type = sentence.get('type', 'unknown')
        pattern_counts[pattern_type] = pattern_counts.get(pattern_type, 0) + 1

        # Count points and lines
        if pattern_type == 'triple':
            total_points += 2
            total_lines += 1
        elif pattern_type in ['line-point', 'point-line']:
            total_points += 1
            total_lines += 1
        elif pattern_type == 'point-point':
            total_points += 2
        elif pattern_type == 'point':
            total_points += 1
        elif pattern_type == 'line':
            total_lines += 1

        # Count enrichments
        if _has_enrichments(sentence):
            total_enrichments += 1

    # Generate HTML
    html = f'''
    <div style="font-family: sans-serif;">
        <h3>📊 Pattern Statistics</h3>

        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background: #f5f5f5;">
                <th style="padding: 8px; text-align: left;">Metric</th>
                <th style="padding: 8px; text-align: right;">Count</th>
            </tr>
            <tr>
                <td style="padding: 8px;">Total Sentences</td>
                <td style="padding: 8px; text-align: right; font-weight: bold;">{len(sentences)}</td>
            </tr>
            <tr style="background: #fafafa;">
                <td style="padding: 8px;">Total Points (🔵)</td>
                <td style="padding: 8px; text-align: right; font-weight: bold;">{total_points}</td>
            </tr>
            <tr>
                <td style="padding: 8px;">Total Lines (🟢)</td>
                <td style="padding: 8px; text-align: right; font-weight: bold;">{total_lines}</td>
            </tr>
            <tr style="background: #fafafa;">
                <td style="padding: 8px;">Enriched Sentences</td>
                <td style="padding: 8px; text-align: right; font-weight: bold;">{total_enrichments}</td>
            </tr>
        </table>

        <h4 style="margin-top: 20px;">Pattern Type Distribution</h4>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background: #f5f5f5;">
                <th style="padding: 8px; text-align: left;">Pattern Type</th>
                <th style="padding: 8px; text-align: right;">Count</th>
                <th style="padding: 8px; text-align: right;">%</th>
            </tr>
    '''

    for pattern_type, count in sorted(pattern_counts.items(), key=lambda x: -x[1]):
        percentage = (count / len(sentences)) * 100
        emoji = PATTERN_EMOJIS.get(pattern_type, '⚪')
        html += f'''
            <tr>
                <td style="padding: 8px;">{emoji} {pattern_type}</td>
                <td style="padding: 8px; text-align: right;">{count}</td>
                <td style="padding: 8px; text-align: right;">{percentage:.1f}%</td>
            </tr>
        '''

    html += '''
        </table>
    </div>
    '''

    return html


def _has_enrichments(sentence: Dict[str, Any]) -> bool:
    """Check if sentence has any enrichments (assets or functions)."""
    for field_name in ['point1', 'point2', 'point', 'line1', 'line', 'content']:
        if field_name in sentence:
            field = sentence[field_name]
            if isinstance(field, dict):
                if 'assets' in field or 'functions' in field:
                    return True
    return False
