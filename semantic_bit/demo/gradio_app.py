"""Gradio-based Visual Testing Interface for Semantic Bit Theory v2.0

Interactive web interface for testing flexible pattern detection, enrichment,
and graph visualization.

Usage:
    python -m demo.gradio_app
    # or
    python demo/gradio_app.py

Opens at: http://localhost:7860
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import gradio as gr
import json
import graphviz
import tempfile
import time
from pathlib import Path

from src.semantic_bit import (
    encode_text_to_sb,
    decode_sb_to_dot,
    map_assets_to_points,
    map_functions_to_lines,
    validate_text_for_encoding,
    ValidationLevel,
)

from utils import format_all_patterns, generate_stats


# =============================================================================
# Example Data
# =============================================================================

EXAMPLE_TEXTS = [
    "The cat is sitting on the mat.",
    "What is a cactus?",
    "The dog barks. A cactus grows. The scientist studies quantum mechanics.",
    "The system calculates distance to the target.",
    "My friend, a talented artist, creates beautiful paintings.",
]

EXAMPLE_ASSETS = json.dumps([
    {"url": "https://en.wikipedia.org/wiki/Cat", "label": "cat"},
    {"url": "https://en.wikipedia.org/wiki/Mat", "label": "mat"},
    {"url": "https://en.wikipedia.org/wiki/Cactus", "label": "cactus"},
    {"url": "https://en.wikipedia.org/wiki/Dog", "label": "dog"},
    {"url": "https://en.wikipedia.org/wiki/Scientist", "label": "scientist"},
    {"url": "https://en.wikipedia.org/wiki/Quantum_mechanics", "label": "quantum mechanics"},
], indent=2)

EXAMPLE_FUNCTIONS = json.dumps([
    {"name": "calculate_distance", "description": "calculates distance"},
    {"name": "study_subject", "description": "studies"},
    {"name": "create_art", "description": "creates"},
    {"name": "sit_action", "description": "sitting"},
], indent=2)


# =============================================================================
# Processing Functions
# =============================================================================

def process_text(
    text: str,
    assets_json: str,
    functions_json: str,
    apply_enrichments: bool,
    max_chars: int,
    validation_level: str
) -> tuple:
    """Process input text and return all visualization outputs.

    Returns:
        Tuple of (patterns_html, json_output, dot_code, graph_image, graph_download, stats_html, validation_msg)
    """
    # Validate input
    if not text.strip():
        empty_msg = "⚠️ Please enter some text to process."
        return empty_msg, {}, "", None, None, "", empty_msg

    # Pre-encoding validation
    level_map = {
        "Minimal": ValidationLevel.MINIMAL,
        "Moderate": ValidationLevel.MODERATE,
        "Comprehensive": ValidationLevel.COMPREHENSIVE,
    }
    is_valid, error = validate_text_for_encoding(
        text,
        max_chars=max_chars,
        level=level_map[validation_level]
    )

    if not is_valid:
        error_msg = f"❌ Validation failed: {error}"
        return error_msg, {}, "", None, None, "", error_msg

    validation_msg = f"✅ Validation passed ({validation_level} level)"

    try:
        start_time = time.time()
        timing = {}

        # Encode text to Semantic Bit JSON
        encode_start = time.time()
        result = encode_text_to_sb(text)
        timing['encoding'] = (time.time() - encode_start) * 1000  # ms

        # Apply enrichments if requested
        enrichment_start = time.time()
        if apply_enrichments:
            # Parse assets
            if assets_json.strip():
                try:
                    assets = json.loads(assets_json)
                    result = map_assets_to_points(result, assets)
                except json.JSONDecodeError as e:
                    validation_msg += f"\n⚠️ Assets JSON error: {str(e)}"

            # Parse functions
            if functions_json.strip():
                try:
                    functions = json.loads(functions_json)
                    result = map_functions_to_lines(result, functions)
                except json.JSONDecodeError as e:
                    validation_msg += f"\n⚠️ Functions JSON error: {str(e)}"
        timing['enrichment'] = (time.time() - enrichment_start) * 1000  # ms

        # Generate visualizations
        viz_start = time.time()
        patterns_html = format_all_patterns(result)
        json_output = result  # Gradio will auto-format
        dot_code = decode_sb_to_dot(result)

        graph_start = time.time()
        graph_image = render_graph_to_image(dot_code)
        timing['graph_rendering'] = (time.time() - graph_start) * 1000  # ms

        timing['visualization'] = (time.time() - viz_start) * 1000  # ms
        timing['total'] = (time.time() - start_time) * 1000  # ms

        stats_html = generate_stats(result, timing)

        return patterns_html, json_output, dot_code, graph_image, graph_image, stats_html, validation_msg

    except Exception as e:
        error_msg = f"❌ Error processing text: {str(e)}"
        return error_msg, {}, "", None, None, "", error_msg


def render_graph_to_image(dot_code: str) -> str:
    """Render DOT code to SVG image file.

    Args:
        dot_code: Graphviz DOT format string

    Returns:
        Path to generated SVG file, or None if rendering failed
    """
    if not dot_code or dot_code.strip() == "":
        return None

    try:
        # Create graph from DOT source
        graph = graphviz.Source(dot_code)

        # Render to temporary SVG file
        temp_dir = Path(tempfile.gettempdir()) / "semantic_bit_graphs"
        temp_dir.mkdir(exist_ok=True)

        output_path = temp_dir / f"graph_{id(dot_code)}"

        # Render as SVG (best quality for web display)
        graph.render(
            filename=str(output_path),
            format='svg',
            cleanup=True,
            engine='dot'
        )

        svg_path = str(output_path) + '.svg'

        if Path(svg_path).exists():
            return svg_path
        else:
            return None

    except Exception as e:
        print(f"Graph rendering error: {e}")
        return None


def load_example(example_index: int) -> tuple:
    """Load an example text.

    Args:
        example_index: Index into EXAMPLE_TEXTS (0-based)

    Returns:
        Tuple of (text, assets, functions, enrichments_enabled)
    """
    if 0 <= example_index < len(EXAMPLE_TEXTS):
        return (
            EXAMPLE_TEXTS[example_index],
            EXAMPLE_ASSETS,
            EXAMPLE_FUNCTIONS,
            True
        )
    return "", "", "", False


# =============================================================================
# Gradio Interface
# =============================================================================

def create_interface():
    """Create and configure the Gradio interface."""

    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    .output-image {
        max-height: 800px !important;
        object-fit: contain;
    }
    """

    with gr.Blocks(
        title="Semantic Bit Theory v2.0 - Visual Tester",
        css=custom_css,
        theme=gr.themes.Soft()
    ) as demo:

        gr.Markdown("""
        # 🎨 Semantic Bit Theory v2.0 - Visual Testing Interface

        Interactive tool for testing flexible semantic pattern detection, enrichment, and graph visualization.

        **Quick Start**: Enter text below or click an example, then press **Process Text**.
        """)

        with gr.Row():
            # Left column: Inputs
            with gr.Column(scale=1):
                gr.Markdown("### 📝 Input")

                text_input = gr.Textbox(
                    label="Input Text",
                    lines=10,
                    placeholder="Enter natural language text here...\n\nExample:\nThe cat is sitting on the mat.\nWhat is a cactus?",
                    info="Enter one or more sentences to analyze"
                )

                with gr.Accordion("⚙️ Settings", open=False):
                    apply_enrichments = gr.Checkbox(
                        label="Apply Enrichments",
                        value=False,
                        info="Link assets and functions to patterns"
                    )

                    max_chars = gr.Slider(
                        minimum=100,
                        maximum=50000,
                        value=10000,
                        step=100,
                        label="Max Characters",
                        info="Maximum input length for validation"
                    )

                    validation_level = gr.Dropdown(
                        choices=["Minimal", "Moderate", "Comprehensive"],
                        value="Moderate",
                        label="Validation Level",
                        info="How strictly to validate input"
                    )

                with gr.Accordion("🔗 Enrichments (Optional)", open=False):
                    assets_input = gr.Code(
                        label="Assets JSON - Format: [{\"url\": \"...\", \"label\": \"...\"}]",
                        language="json",
                        lines=8,
                        value=EXAMPLE_ASSETS
                    )

                    functions_input = gr.Code(
                        label="Functions JSON - Format: [{\"name\": \"...\", \"description\": \"...\"}]",
                        language="json",
                        lines=8,
                        value=EXAMPLE_FUNCTIONS
                    )

                with gr.Row():
                    process_btn = gr.Button(
                        "🚀 Process Text",
                        variant="primary",
                        size="lg"
                    )
                    clear_btn = gr.Button(
                        "🗑️ Clear",
                        variant="secondary"
                    )

                validation_status = gr.Textbox(
                    label="Validation Status",
                    interactive=False,
                    lines=2
                )

            # Right column: Outputs
            with gr.Column(scale=2):
                gr.Markdown("### 📊 Output")

                with gr.Tabs():
                    # Tab 1: Graph Visualization (PRIORITY)
                    with gr.Tab("📊 Graph Visualization"):
                        gr.Markdown("""
                        **Visual representation of semantic relationships**

                        - 🔵 Blue nodes = Points (entities, concepts)
                        - 🟢 Green edges = Lines (relationships, actions)
                        - Arrows show directionality
                        """)

                        graph_output = gr.Image(
                            label="Semantic Graph",
                            type="filepath",
                            elem_classes=["output-image"]
                        )

                        graph_download = gr.File(
                            label="📥 Download Graph (SVG)",
                            visible=True
                        )

                        gr.Markdown("💡 **Tip**: You can also right-click the image to save")

                    # Tab 2: Patterns (Color-coded)
                    with gr.Tab("🎨 Patterns"):
                        gr.Markdown("**Color-coded semantic patterns**")

                        patterns_output = gr.HTML(
                            label="Pattern Visualization"
                        )

                    # Tab 3: JSON Output
                    with gr.Tab("📄 JSON"):
                        gr.Markdown("**Structured Semantic Bit JSON output**")

                        json_output = gr.JSON(
                            label="Semantic Bit JSON v2.0"
                        )

                    # Tab 4: DOT Code
                    with gr.Tab("💻 DOT Code"):
                        gr.Markdown("""
                        **Raw Graphviz DOT format**

                        Copy this code to use with:
                        - Graphviz command-line tools
                        - Online DOT viewers
                        - Other graph visualization tools
                        """)

                        dot_output = gr.Code(
                            label="DOT Graph Code",
                            lines=15
                        )

                    # Tab 5: Statistics
                    with gr.Tab("📈 Stats"):
                        gr.Markdown("**Pattern detection statistics**")

                        stats_output = gr.HTML(
                            label="Statistics"
                        )

        # Examples section
        gr.Markdown("### 💡 Examples")

        gr.Examples(
            examples=[
                [text, EXAMPLE_ASSETS, EXAMPLE_FUNCTIONS, True]
                for text in EXAMPLE_TEXTS
            ],
            inputs=[text_input, assets_input, functions_input, apply_enrichments],
            label="Click an example to load it"
        )

        gr.Markdown("""
        ---

        ### 📖 Pattern Types

        | Type | Description | Example |
        |------|-------------|---------|
        | 🔵🟢🔵 **triple** | Point → Line → Point | "The cat sits on the mat" |
        | 🟢🔵 **line-point** | Line → Point | "What is a cactus?" |
        | 🔵🟢 **point-line** | Point → Line | "The dog barks" |
        | 🔵🔵 **point-point** | Point ≡ Point | "My friend, an artist" |
        | 🔵 **point** | Single concept | "A cactus." |
        | 🟢 **line** | Pure action | "Running." |

        ### ℹ️ About

        **Version**: 2.0.0 | **For**: Internal testing and development | **License**: Same as semantic_bit package

        [Documentation](https://github.com/your-repo/semantic-bit-theory) | [Report Issues](https://github.com/your-repo/semantic-bit-theory/issues)
        """)

        # Event handlers
        process_btn.click(
            fn=process_text,
            inputs=[
                text_input,
                assets_input,
                functions_input,
                apply_enrichments,
                max_chars,
                validation_level
            ],
            outputs=[
                patterns_output,
                json_output,
                dot_output,
                graph_output,
                graph_download,
                stats_output,
                validation_status
            ]
        )

        clear_btn.click(
            fn=lambda: ("", EXAMPLE_ASSETS, EXAMPLE_FUNCTIONS, False, "", {}, "", None, None, "", ""),
            inputs=[],
            outputs=[
                text_input,
                assets_input,
                functions_input,
                apply_enrichments,
                patterns_output,
                json_output,
                dot_output,
                graph_output,
                graph_download,
                stats_output,
                validation_status
            ]
        )

    return demo


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    print("🚀 Starting Semantic Bit Theory v2.0 Visual Testing Interface...")
    print("📊 Graph visualization is the priority feature!")
    print()

    # Check if graphviz is installed
    try:
        import graphviz
        # Test if system graphviz is available
        graphviz.Source("digraph { a -> b }").render(format='svg', cleanup=True)
        print("✅ Graphviz is properly installed")
    except Exception as e:
        print("⚠️  WARNING: Graphviz may not be properly installed")
        print(f"   Error: {e}")
        print("   Install with: brew install graphviz (macOS) or apt-get install graphviz (Linux)")
        print()

    demo = create_interface()

    demo.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=False,  # Set to True for temporary public link
        show_error=True
    )
