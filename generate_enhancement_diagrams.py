#!/usr/bin/env python3
"""
Generate visual diagrams for Semantic Bit Theory Enhancement Plan
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Set up nice styling
plt.style.use('seaborn-v0_8-darkgrid')
colors = {
    'point': '#4CAF50',  # Green
    'line': '#2196F3',   # Blue
    'triple': '#FF9800', # Orange
    'bg': '#f5f5f5'
}

def create_pattern_comparison():
    """Create diagram comparing rigid vs flexible patterns"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # LEFT SIDE: Current Rigid Pattern
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    ax1.set_title('CURRENT: Rigid Triple Pattern', fontsize=16, fontweight='bold', pad=20)

    # Draw rigid pattern
    point1_box = FancyBboxPatch((0.5, 6), 2.5, 1.5, boxstyle="round,pad=0.1",
                                 edgecolor='black', facecolor=colors['point'], linewidth=2)
    ax1.add_patch(point1_box)
    ax1.text(1.75, 6.75, 'The cat\n(Point₁)', ha='center', va='center',
             fontsize=11, fontweight='bold')

    line_box = FancyBboxPatch((3.5, 6), 3, 1.5, boxstyle="round,pad=0.1",
                               edgecolor='black', facecolor=colors['line'], linewidth=2)
    ax1.add_patch(line_box)
    ax1.text(5, 6.75, 'is sitting on\n(Line)', ha='center', va='center',
             fontsize=11, fontweight='bold', color='white')

    point2_box = FancyBboxPatch((7, 6), 2.5, 1.5, boxstyle="round,pad=0.1",
                                 edgecolor='black', facecolor=colors['point'], linewidth=2)
    ax1.add_patch(point2_box)
    ax1.text(8.25, 6.75, 'the mat\n(Point₂)', ha='center', va='center',
             fontsize=11, fontweight='bold')

    # Arrows
    arrow1 = FancyArrowPatch((3.1, 6.75), (3.4, 6.75), arrowstyle='->',
                             mutation_scale=20, linewidth=2, color='black')
    arrow2 = FancyArrowPatch((6.6, 6.75), (6.9, 6.75), arrowstyle='->',
                             mutation_scale=20, linewidth=2, color='black')
    ax1.add_patch(arrow1)
    ax1.add_patch(arrow2)

    # Add constraint label
    ax1.text(5, 4, 'REQUIREMENT: All three components must exist',
             ha='center', fontsize=12, style='italic',
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

    ax1.text(5, 2.5, '❌ Rejects: "A cactus."\n❌ Rejects: "What is?"\n❌ Rejects: "The dog barks."',
             ha='center', fontsize=10, color='red')

    # RIGHT SIDE: Enhanced Flexible Patterns
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    ax2.set_title('ENHANCED: Flexible Patterns', fontsize=16, fontweight='bold', pad=20)

    # Pattern 1: Point only
    y_pos = 8.5
    p1 = FancyBboxPatch((1, y_pos), 2, 0.8, boxstyle="round,pad=0.05",
                         edgecolor='black', facecolor=colors['point'], linewidth=2)
    ax2.add_patch(p1)
    ax2.text(2, y_pos + 0.4, 'A cactus', ha='center', va='center', fontsize=9, fontweight='bold')
    ax2.text(5, y_pos + 0.4, '← Point only (static concept)', ha='left', va='center', fontsize=9)

    # Pattern 2: Line only
    y_pos = 7.3
    l1 = FancyBboxPatch((1, y_pos), 2, 0.8, boxstyle="round,pad=0.05",
                         edgecolor='black', facecolor=colors['line'], linewidth=2)
    ax2.add_patch(l1)
    ax2.text(2, y_pos + 0.4, 'What is?', ha='center', va='center', fontsize=9,
             fontweight='bold', color='white')
    ax2.text(5, y_pos + 0.4, '← Line only (pure action/question)', ha='left', va='center', fontsize=9)

    # Pattern 3: Line → Point
    y_pos = 6.1
    l2 = FancyBboxPatch((1, y_pos), 1.5, 0.8, boxstyle="round,pad=0.05",
                         edgecolor='black', facecolor=colors['line'], linewidth=2)
    ax2.add_patch(l2)
    ax2.text(1.75, y_pos + 0.4, 'What is', ha='center', va='center', fontsize=9,
             fontweight='bold', color='white')

    p2 = FancyBboxPatch((3, y_pos), 1.5, 0.8, boxstyle="round,pad=0.05",
                         edgecolor='black', facecolor=colors['point'], linewidth=2)
    ax2.add_patch(p2)
    ax2.text(3.75, y_pos + 0.4, 'a cactus', ha='center', va='center', fontsize=9, fontweight='bold')

    arrow3 = FancyArrowPatch((2.6, y_pos + 0.4), (2.9, y_pos + 0.4), arrowstyle='->',
                             mutation_scale=15, linewidth=2, color='black')
    ax2.add_patch(arrow3)
    ax2.text(5, y_pos + 0.4, '← Line-Point pattern', ha='left', va='center', fontsize=9)

    # Pattern 4: Point → Line
    y_pos = 4.9
    p3 = FancyBboxPatch((1, y_pos), 1.5, 0.8, boxstyle="round,pad=0.05",
                         edgecolor='black', facecolor=colors['point'], linewidth=2)
    ax2.add_patch(p3)
    ax2.text(1.75, y_pos + 0.4, 'The dog', ha='center', va='center', fontsize=9, fontweight='bold')

    l3 = FancyBboxPatch((3, y_pos), 1.5, 0.8, boxstyle="round,pad=0.05",
                         edgecolor='black', facecolor=colors['line'], linewidth=2)
    ax2.add_patch(l3)
    ax2.text(3.75, y_pos + 0.4, 'barks', ha='center', va='center', fontsize=9,
             fontweight='bold', color='white')

    arrow4 = FancyArrowPatch((2.6, y_pos + 0.4), (2.9, y_pos + 0.4), arrowstyle='->',
                             mutation_scale=15, linewidth=2, color='black')
    ax2.add_patch(arrow4)
    ax2.text(5, y_pos + 0.4, '← Point-Line pattern', ha='left', va='center', fontsize=9)

    # Pattern 5: Classic triple
    y_pos = 3.7
    p4 = FancyBboxPatch((0.5, y_pos), 1.2, 0.8, boxstyle="round,pad=0.05",
                         edgecolor='black', facecolor=colors['point'], linewidth=2)
    ax2.add_patch(p4)
    ax2.text(1.1, y_pos + 0.4, 'cat', ha='center', va='center', fontsize=9, fontweight='bold')

    l4 = FancyBboxPatch((2.1, y_pos), 1.5, 0.8, boxstyle="round,pad=0.05",
                         edgecolor='black', facecolor=colors['line'], linewidth=2)
    ax2.add_patch(l4)
    ax2.text(2.85, y_pos + 0.4, 'sits on', ha='center', va='center', fontsize=8,
             fontweight='bold', color='white')

    p5 = FancyBboxPatch((4, y_pos), 1.2, 0.8, boxstyle="round,pad=0.05",
                         edgecolor='black', facecolor=colors['point'], linewidth=2)
    ax2.add_patch(p5)
    ax2.text(4.6, y_pos + 0.4, 'mat', ha='center', va='center', fontsize=9, fontweight='bold')

    arrow5 = FancyArrowPatch((1.8, y_pos + 0.4), (2.0, y_pos + 0.4), arrowstyle='->',
                             mutation_scale=12, linewidth=1.5, color='black')
    arrow6 = FancyArrowPatch((3.7, y_pos + 0.4), (3.9, y_pos + 0.4), arrowstyle='->',
                             mutation_scale=12, linewidth=1.5, color='black')
    ax2.add_patch(arrow5)
    ax2.add_patch(arrow6)
    ax2.text(5, y_pos + 0.4, '← Classic triple (still supported)', ha='left', va='center', fontsize=9)

    ax2.text(5, 1.5, '✓ Accepts all patterns\n✓ Adapts to semantic structure\n✓ Preserves meaning',
             ha='center', fontsize=10, color='green', fontweight='bold')

    plt.tight_layout()
    plt.savefig('docs/images/pattern_comparison.png', dpi=300, bbox_inches='tight',
                facecolor='white')
    print("✓ Created: docs/images/pattern_comparison.png")


def create_validation_flow():
    """Create diagram showing validation and processing flow"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    ax.set_title('Enhanced SB Processing Pipeline with Validation',
                 fontsize=16, fontweight='bold', pad=20)

    # Stage 1: Input
    y = 11
    input_box = FancyBboxPatch((3, y), 4, 0.8, boxstyle="round,pad=0.1",
                                edgecolor='black', facecolor='#E3F2FD', linewidth=2)
    ax.add_patch(input_box)
    ax.text(5, y + 0.4, 'Input Text', ha='center', va='center', fontsize=12, fontweight='bold')

    # Arrow down
    ax.annotate('', xy=(5, y - 0.1), xytext=(5, y + 0.05),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))

    # Stage 2: Validation
    y = 9.5
    val_box = FancyBboxPatch((2, y), 6, 1.2, boxstyle="round,pad=0.1",
                              edgecolor='black', facecolor='#FFF9C4', linewidth=2)
    ax.add_patch(val_box)
    ax.text(5, y + 0.8, 'VALIDATION PHASE', ha='center', va='center',
            fontsize=11, fontweight='bold')
    ax.text(5, y + 0.3, '✓ JSON serializable?\n✓ Under character limit?\n✓ Valid sentences?',
            ha='center', va='center', fontsize=9)

    # Branch: Fail
    fail_box = FancyBboxPatch((8.5, y + 0.2), 1.3, 0.8, boxstyle="round,pad=0.05",
                               edgecolor='red', facecolor='#FFCDD2', linewidth=2)
    ax.add_patch(fail_box)
    ax.text(9.15, y + 0.6, 'FAIL', ha='center', va='center', fontsize=10,
            fontweight='bold', color='red')
    ax.annotate('', xy=(8.4, y + 0.6), xytext=(8, y + 0.6),
                arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    ax.text(9.15, y - 0.3, 'Return\nError', ha='center', va='center', fontsize=8)

    # Arrow down (pass)
    ax.annotate('PASS', xy=(5, y - 0.2), xytext=(5, y + 0.05),
                arrowprops=dict(arrowstyle='->', lw=2, color='green'),
                fontsize=10, fontweight='bold', ha='center')

    # Stage 3: Encoding
    y = 7.5
    enc_box = FancyBboxPatch((1.5, y), 7, 1.5, boxstyle="round,pad=0.1",
                              edgecolor='black', facecolor='#E1F5FE', linewidth=2)
    ax.add_patch(enc_box)
    ax.text(5, y + 1.1, 'ENCODING PHASE (Flexible)', ha='center', va='center',
            fontsize=11, fontweight='bold')
    ax.text(5, y + 0.5, '• Preserve original_text\n• Detect articles (a/an/the)\n• Support Point-only, Line-only, Triples\n• Default ambiguous → Point',
            ha='center', va='center', fontsize=8.5)

    ax.annotate('', xy=(5, y - 0.2), xytext=(5, y + 0.05),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))

    # Stage 4: Enrichment
    y = 5
    enrich_box = FancyBboxPatch((1.5, y), 7, 1.8, boxstyle="round,pad=0.1",
                                 edgecolor='black', facecolor='#F3E5F5', linewidth=2)
    ax.add_patch(enrich_box)
    ax.text(5, y + 1.4, 'ENRICHMENT PHASE (Optional)', ha='center', va='center',
            fontsize=11, fontweight='bold')

    # Sub-boxes
    asset_box = FancyBboxPatch((1.8, y + 0.5), 3, 0.7, boxstyle="round,pad=0.05",
                                edgecolor='#9C27B0', facecolor='#E1BEE7', linewidth=1.5)
    ax.add_patch(asset_box)
    ax.text(3.3, y + 0.85, 'map_assets_to_points()', ha='center', va='center',
            fontsize=8, fontweight='bold')

    func_box = FancyBboxPatch((5.2, y + 0.5), 3, 0.7, boxstyle="round,pad=0.05",
                               edgecolor='#9C27B0', facecolor='#E1BEE7', linewidth=1.5)
    ax.add_patch(func_box)
    ax.text(6.7, y + 0.85, 'map_functions_to_lines()', ha='center', va='center',
            fontsize=8, fontweight='bold')

    ax.text(5, y + 0.15, 'Add URLs & labels to Points  |  Add function refs to Lines',
            ha='center', va='center', fontsize=8, style='italic')

    ax.annotate('', xy=(5, y - 0.2), xytext=(5, y + 0.05),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))

    # Stage 5: Output
    y = 2.5
    output_box = FancyBboxPatch((1.5, y), 7, 2, boxstyle="round,pad=0.1",
                                 edgecolor='black', facecolor='#C8E6C9', linewidth=3)
    ax.add_patch(output_box)
    ax.text(5, y + 1.5, 'OUTPUT: Rich SB JSON', ha='center', va='center',
            fontsize=12, fontweight='bold', color='#1B5E20')
    ax.text(5, y + 0.7, '✓ Original text preserved\n✓ Flexible semantic patterns\n✓ Linked to external resources\n✓ Executable function mappings',
            ha='center', va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig('docs/images/validation_flow.png', dpi=300, bbox_inches='tight',
                facecolor='white')
    print("✓ Created: docs/images/validation_flow.png")


def create_asset_function_mapping():
    """Create diagram showing asset and function mapping"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # LEFT: Asset Mapping
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    ax1.set_title('Asset Mapping to Points', fontsize=14, fontweight='bold', pad=20)

    # Point boxes
    y = 8
    point1 = FancyBboxPatch((1, y), 2, 0.8, boxstyle="round,pad=0.05",
                             edgecolor='black', facecolor=colors['point'], linewidth=2)
    ax1.add_patch(point1)
    ax1.text(2, y + 0.4, 'The cactus', ha='center', va='center', fontsize=10, fontweight='bold')

    point2 = FancyBboxPatch((6, y), 2, 0.8, boxstyle="round,pad=0.05",
                             edgecolor='black', facecolor=colors['point'], linewidth=2)
    ax1.add_patch(point2)
    ax1.text(7, y + 0.4, 'desert', ha='center', va='center', fontsize=10, fontweight='bold')

    # Asset boxes
    y = 5.5
    asset1 = FancyBboxPatch((0.5, y), 3, 1.2, boxstyle="round,pad=0.05",
                             edgecolor='#FF6F00', facecolor='#FFE0B2', linewidth=2)
    ax1.add_patch(asset1)
    ax1.text(2, y + 0.8, 'Asset: "cactus"', ha='center', va='center',
             fontsize=9, fontweight='bold')
    ax1.text(2, y + 0.4, 'URL: wiki.org/cactus', ha='center', va='center', fontsize=8)
    ax1.text(2, y + 0.05, 'Label: "cactus"', ha='center', va='center', fontsize=8)

    asset2 = FancyBboxPatch((5.5, y), 3, 1.2, boxstyle="round,pad=0.05",
                             edgecolor='#FF6F00', facecolor='#FFE0B2', linewidth=2)
    ax1.add_patch(asset2)
    ax1.text(7, y + 0.8, 'Asset: "desert"', ha='center', va='center',
             fontsize=9, fontweight='bold')
    ax1.text(7, y + 0.4, 'URL: wiki.org/desert', ha='center', va='center', fontsize=8)
    ax1.text(7, y + 0.05, 'Label: "desert"', ha='center', va='center', fontsize=8)

    # Matching arrows
    ax1.annotate('', xy=(2, y + 1.3), xytext=(2, 7.9),
                 arrowprops=dict(arrowstyle='<->', lw=2, color='#FF6F00'))
    ax1.text(2.5, 7, 'Match!', fontsize=9, color='#FF6F00', fontweight='bold')

    ax1.annotate('', xy=(7, y + 1.3), xytext=(7, 7.9),
                 arrowprops=dict(arrowstyle='<->', lw=2, color='#FF6F00'))
    ax1.text(7.5, 7, 'Match!', fontsize=9, color='#FF6F00', fontweight='bold')

    # Result
    y = 2.5
    result1 = FancyBboxPatch((1, y), 7, 1.8, boxstyle="round,pad=0.1",
                              edgecolor='green', facecolor='#C8E6C9', linewidth=2)
    ax1.add_patch(result1)
    ax1.text(4.5, y + 1.3, 'Enhanced Point (with asset)', ha='center', va='center',
             fontsize=10, fontweight='bold')
    ax1.text(4.5, y + 0.6, '{\n  "content": "The cactus",\n  "asset": {"url": "...", "label": "cactus"}\n}',
             ha='center', va='center', fontsize=8, family='monospace')

    ax1.text(5, 1, 'Use Case: Link entities to knowledge bases', ha='center', fontsize=9,
             style='italic', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))

    # RIGHT: Function Mapping
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    ax2.set_title('Function Mapping to Lines', fontsize=14, fontweight='bold', pad=20)

    # Line box
    y = 8
    line1 = FancyBboxPatch((2.5, y), 2.5, 0.8, boxstyle="round,pad=0.05",
                            edgecolor='black', facecolor=colors['line'], linewidth=2)
    ax2.add_patch(line1)
    ax2.text(3.75, y + 0.4, 'calculates', ha='center', va='center',
             fontsize=10, fontweight='bold', color='white')

    # Function box
    y = 5.5
    func1 = FancyBboxPatch((1.5, y), 5, 1.5, boxstyle="round,pad=0.05",
                            edgecolor='#1976D2', facecolor='#BBDEFB', linewidth=2)
    ax2.add_patch(func1)
    ax2.text(4, y + 1.1, 'Named Function', ha='center', va='center',
             fontsize=9, fontweight='bold')
    ax2.text(4, y + 0.7, 'Name: calculate_distance', ha='center', va='center',
             fontsize=8, family='monospace')
    ax2.text(4, y + 0.3, 'Description: "calculates distance"', ha='center', va='center',
             fontsize=8)

    # Matching arrow
    ax2.annotate('', xy=(3.75, y + 1.6), xytext=(3.75, 7.9),
                 arrowprops=dict(arrowstyle='<->', lw=2, color='#1976D2'))
    ax2.text(4.5, 7, 'Semantic\nMatch!', fontsize=9, color='#1976D2', fontweight='bold')

    # Result
    y = 2.5
    result2 = FancyBboxPatch((0.5, y), 8, 2.2, boxstyle="round,pad=0.1",
                              edgecolor='green', facecolor='#C8E6C9', linewidth=2)
    ax2.add_patch(result2)
    ax2.text(4.5, y + 1.7, 'Enhanced Line (with function)', ha='center', va='center',
             fontsize=10, fontweight='bold')
    ax2.text(4.5, y + 0.8, '{\n  "content": "calculates",\n  "function": {\n    "name": "calculate_distance",\n    "description": "calculates distance"\n  }\n}',
             ha='center', va='center', fontsize=8, family='monospace')

    ax2.text(5, 0.8, 'Use Case: Map natural language to executable code',
             ha='center', fontsize=9, style='italic',
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))

    plt.tight_layout()
    plt.savefig('docs/images/asset_function_mapping.png', dpi=300, bbox_inches='tight',
                facecolor='white')
    print("✓ Created: docs/images/asset_function_mapping.png")


def create_article_detection():
    """Create diagram showing article detection for Point boundaries"""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('Article Detection: Finding Point Boundaries',
                 fontsize=16, fontweight='bold', pad=20)

    # Sentence example
    sentence = "The cat is sitting on the mat"
    words = ["The", "cat", "is", "sitting", "on", "the", "mat"]

    # Draw sentence
    y = 8.5
    ax.text(5, y + 0.5, f'Sentence: "{sentence}"', ha='center', va='center',
            fontsize=14, fontweight='bold', bbox=dict(boxstyle='round',
            facecolor='#E3F2FD', edgecolor='black', linewidth=2))

    # Draw tokens with annotations
    y = 6.5
    x_positions = [0.5, 1.5, 2.8, 3.8, 5, 6, 7.2]

    for i, (word, x) in enumerate(zip(words, x_positions)):
        # Determine color
        is_article = word.lower() in ['a', 'an', 'the']
        is_verb = word.lower() in ['is', 'sitting']
        is_prep = word.lower() in ['on']

        if is_article:
            color = '#FFF9C4'  # Yellow for articles
            edge = '#F57F17'
            edge_width = 3
        elif is_verb or is_prep:
            color = colors['line']
            edge = 'black'
            edge_width = 2
        else:
            color = colors['point']
            edge = 'black'
            edge_width = 2

        # Token box
        box = FancyBboxPatch((x, y), 0.8, 0.6, boxstyle="round,pad=0.05",
                              edgecolor=edge, facecolor=color, linewidth=edge_width)
        ax.add_patch(box)

        text_color = 'white' if (is_verb or is_prep) and not is_article else 'black'
        ax.text(x + 0.4, y + 0.3, word, ha='center', va='center',
                fontsize=10, fontweight='bold', color=text_color)

        # Add annotation for articles
        if is_article:
            ax.annotate('', xy=(x + 0.4, y + 0.7), xytext=(x + 0.4, y + 1.2),
                        arrowprops=dict(arrowstyle='->', lw=2, color='#F57F17'))
            ax.text(x + 0.4, y + 1.4, 'Article!\n→ Next word\nis Point',
                    ha='center', va='center', fontsize=7, fontweight='bold',
                    color='#F57F17')

    # Show segmentation
    y = 4.5
    ax.text(5, y + 0.5, 'Detected Segmentation:', ha='center', va='center',
            fontsize=12, fontweight='bold')

    # Point 1
    y = 3.5
    p1_box = FancyBboxPatch((1, y), 2, 0.8, boxstyle="round,pad=0.05",
                             edgecolor='black', facecolor=colors['point'], linewidth=2)
    ax.add_patch(p1_box)
    ax.text(2, y + 0.4, 'The cat', ha='center', va='center', fontsize=11, fontweight='bold')
    ax.text(2, y - 0.4, 'Point₁', ha='center', va='center', fontsize=9, style='italic')

    # Line
    l1_box = FancyBboxPatch((3.5, y), 2.5, 0.8, boxstyle="round,pad=0.05",
                             edgecolor='black', facecolor=colors['line'], linewidth=2)
    ax.add_patch(l1_box)
    ax.text(4.75, y + 0.4, 'is sitting on', ha='center', va='center',
            fontsize=10, fontweight='bold', color='white')
    ax.text(4.75, y - 0.4, 'Line', ha='center', va='center', fontsize=9, style='italic')

    # Point 2
    p2_box = FancyBboxPatch((6.5, y), 2, 0.8, boxstyle="round,pad=0.05",
                             edgecolor='black', facecolor=colors['point'], linewidth=2)
    ax.add_patch(p2_box)
    ax.text(7.5, y + 0.4, 'the mat', ha='center', va='center', fontsize=11, fontweight='bold')
    ax.text(7.5, y - 0.4, 'Point₂', ha='center', va='center', fontsize=9, style='italic')

    # Arrows
    arrow1 = FancyArrowPatch((3.1, y + 0.4), (3.4, y + 0.4), arrowstyle='->',
                             mutation_scale=15, linewidth=2, color='black')
    arrow2 = FancyArrowPatch((6.1, y + 0.4), (6.4, y + 0.4), arrowstyle='->',
                             mutation_scale=15, linewidth=2, color='black')
    ax.add_patch(arrow1)
    ax.add_patch(arrow2)

    # Rule box
    y = 1
    rule_box = FancyBboxPatch((1.5, y), 7, 1.2, boxstyle="round,pad=0.1",
                               edgecolor='#1565C0', facecolor='#E3F2FD', linewidth=2)
    ax.add_patch(rule_box)
    ax.text(5, y + 0.8, 'RULE: Articles Signal Point Boundaries', ha='center', va='center',
            fontsize=11, fontweight='bold', color='#1565C0')
    ax.text(5, y + 0.3, 'When "a", "an", or "the" precedes a word → that word is part of a Point (noun phrase)',
            ha='center', va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig('docs/images/article_detection.png', dpi=300, bbox_inches='tight',
                facecolor='white')
    print("✓ Created: docs/images/article_detection.png")


if __name__ == '__main__':
    import os
    os.makedirs('docs/images', exist_ok=True)

    print("Generating enhancement diagrams...\n")
    create_pattern_comparison()
    create_validation_flow()
    create_asset_function_mapping()
    create_article_detection()
    print("\n✅ All diagrams generated successfully!")
