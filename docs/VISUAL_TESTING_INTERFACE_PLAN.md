# Visual Testing Interface - Planning Document

**Purpose**: Simple web interface for visually testing Semantic Bit Theory v2.0
**Status**: Planning Phase
**Target Users**: Development team (internal testing only)

---

## Overview

Create a lightweight web interface that allows developers to:
1. Input natural language text
2. See the flexible pattern detection in action
3. Visualize semantic structures with color-coding
4. View graph representations
5. Test asset and function mapping

**Key Constraint**: This is a pip package, so the web interface should be:
- Optional (not required for package use)
- Lightweight and easy to run
- No impact on core package dependencies

---

## Architecture Options

### Option 1: Gradio (⭐ RECOMMENDED)

**What is it**: Python library for building ML/AI demo interfaces

**Pros**:
- ✅ Zero frontend knowledge needed (pure Python)
- ✅ Beautiful, modern UI out-of-the-box
- ✅ Hot reload during development
- ✅ Built-in sharing/deployment options
- ✅ Perfect for internal testing tools
- ✅ Supports all our needs: text input, colored output, graphs, JSON
- ✅ Can package as optional dependency

**Cons**:
- ❌ Adds a dependency (but optional)
- ❌ Less customizable than custom React

**Code Example**:
```python
import gradio as gr
from semantic_bit import encode_text_to_sb, decode_sb_to_dot
import json

def process_text(text, assets_json, functions_json):
    # Encode
    result = encode_text_to_sb(text)

    # Generate graph
    dot = decode_sb_to_dot(result)

    # Return formatted JSON, graph
    return json.dumps(result, indent=2), dot

demo = gr.Interface(
    fn=process_text,
    inputs=[
        gr.Textbox(label="Input Text", lines=5),
        gr.Textbox(label="Assets (JSON)", lines=3),
        gr.Textbox(label="Functions (JSON)", lines=3)
    ],
    outputs=[
        gr.JSON(label="Semantic Bit JSON"),
        gr.Code(label="DOT Graph", language="dot")
    ],
    title="Semantic Bit Theory v2.0 - Visual Tester"
)

demo.launch()
```

**Installation**:
```bash
# As optional dependency
pip install semantic-bit[dev]
# Or standalone
pip install gradio
```

---

### Option 2: Streamlit

**What is it**: Python library for data apps

**Pros**:
- ✅ Pure Python (no frontend needed)
- ✅ Great for data visualization
- ✅ Simple and fast to build
- ✅ Interactive widgets

**Cons**:
- ❌ More opinionated than Gradio
- ❌ Re-runs entire script on interaction (can be slow)
- ❌ Less suitable for ML/demo use cases

**Not recommended** for this use case - Gradio is better fit.

---

### Option 3: Flask + Vanilla JS/HTML

**What is it**: Custom Python backend with simple frontend

**Pros**:
- ✅ Full control over UI/UX
- ✅ No build process needed (vanilla JS)
- ✅ Python-based backend (familiar)
- ✅ Can serve static Graphviz visualizations

**Cons**:
- ❌ More code to write and maintain
- ❌ Need to handle frontend styling manually
- ❌ More work for color-coding and interactivity

**Use Case**: If you want complete customization

**Structure**:
```
semantic_bit_demo/
├── app.py              # Flask server
├── static/
│   ├── style.css
│   └── app.js          # Vanilla JS
└── templates/
    └── index.html      # Simple form + visualization
```

---

### Option 4: Simple React App (Separate Repo)

**What is it**: Standalone React app that imports the Python package via API

**Pros**:
- ✅ Modern, component-based UI
- ✅ Great for future Django integration
- ✅ Reusable components
- ✅ Professional look and feel

**Cons**:
- ❌ Requires build process (npm, webpack)
- ❌ Need a Python API server (Flask/FastAPI)
- ❌ More complex setup
- ❌ Overkill for internal testing

**Use Case**: For the future Django/React production app

---

## Recommendation: Gradio

**Why Gradio is perfect for this**:

1. **Fast to build**: 50-100 lines of Python, no frontend code
2. **Beautiful UI**: Modern, responsive, professional-looking
3. **All features we need**: Text input, JSON display, code highlighting, file upload
4. **Optional dependency**: Won't bloat the core package
5. **Easy to run**: `python demo.py` or `gradio run demo.py`
6. **Shareable**: Can generate temporary public links for team demos
7. **Python-native**: Team already knows Python

---

## Proposed Features (Gradio Implementation)

### Phase 1: Basic Text Processing

**UI Elements**:
- Text area: "Input Text" (multiline)
- Button: "Process"
- JSON viewer: "Semantic Bit JSON Output" (formatted, colored)
- Code viewer: "DOT Graph" (syntax highlighted)

**Functionality**:
```python
Input: "The cat is sitting on the mat. What is a cactus?"
↓
Process with encode_text_to_sb()
↓
Display JSON with pattern types highlighted
Display DOT graph code
```

### Phase 2: Pattern Visualization

**UI Elements**:
- Same as Phase 1, plus:
- HTML output: "Color-Coded Patterns" (sentences with colored segments)

**Color Coding**:
- 🔵 **Blue**: Points (nouns, entities)
- 🟢 **Green**: Lines (verbs, relationships)
- 🟡 **Yellow**: Pattern type labels

**Example**:
```
Sentence: "The cat is sitting on the mat."
Pattern: triple

[🔵 The cat] [🟢 is sitting on] [🔵 the mat]
Type: triple
```

### Phase 3: Enrichment Testing

**UI Elements**:
- Text area: "Assets (JSON)" - paste asset mappings
- Text area: "Functions (JSON)" - paste function mappings
- Checkbox: "Apply enrichments"

**Functionality**:
```python
# User provides assets
assets = [
    {"url": "https://wiki.org/cat", "label": "cat"},
    {"url": "https://wiki.org/mat", "label": "mat"}
]

# Show enriched JSON with assets embedded
```

### Phase 4: Graph Visualization

**UI Elements**:
- Image output: "Graph Visualization" (rendered SVG/PNG)

**Implementation Options**:
1. **Server-side rendering**: Use `graphviz` Python package to render DOT → image
2. **Client-side**: Use `viz.js` to render DOT in browser (Gradio supports custom components)

**Example**:
```python
import graphviz

def render_graph(dot_code):
    graph = graphviz.Source(dot_code)
    graph.render('output', format='svg', cleanup=True)
    return 'output.svg'
```

### Phase 5 (Optional): Validation Testing

**UI Elements**:
- Number input: "Max characters" (default 10,000)
- Dropdown: "Validation level" (minimal, moderate, comprehensive)
- Status indicator: ✅ Valid / ❌ Invalid

---

## Proposed File Structure

### Option A: Inside semantic_bit package (as optional demo)

```
semantic_bit/
├── src/semantic_bit/        # Core package
│   ├── core/
│   ├── enrichment/
│   └── ...
├── demo/                     # ✨ New: Demo interface
│   ├── __init__.py
│   ├── gradio_app.py        # Main Gradio interface
│   ├── utils.py             # Formatting, color-coding helpers
│   └── requirements.txt     # gradio, graphviz (optional deps)
└── README.md
```

**Running**:
```bash
# Install with demo dependencies
pip install -e ".[demo]"

# Run demo
python -m semantic_bit.demo.gradio_app
# or
gradio run demo/gradio_app.py
```

### Option B: Separate demo repository

```
semantic_bit_demo/           # Separate repo
├── app.py                   # Gradio app
├── requirements.txt         # semantic-bit, gradio, graphviz
├── README.md
└── examples/                # Sample inputs
    ├── simple.txt
    ├── complex.txt
    └── assets.json
```

**Pros**: Keeps demo code separate from core package
**Cons**: Extra repo to maintain

---

## UI Mockup (Gradio)

### Layout Design

```
┌─────────────────────────────────────────────────────────────┐
│ Semantic Bit Theory v2.0 - Visual Testing Interface        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Input Tab                                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Input Text:                                                 │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ The cat is sitting on the mat.                      │   │
│ │ What is a cactus?                                   │   │
│ │                                                     │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                             │
│ Assets (JSON - optional):                                  │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ [{"url": "...", "label": "cat"}]                   │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                             │
│ Functions (JSON - optional):                               │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ [{"name": "sits", "description": "sitting"}]       │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                             │
│              [Process Text] [Clear] [Load Example]         │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Output Tabs                                                 │
├─────────────────────────────────────────────────────────────┤
│ [Patterns] [JSON] [Graph Code] [Graph Visual] [Stats]      │
│                                                             │
│ ┌─ Patterns Tab ──────────────────────────────────────┐   │
│ │                                                       │   │
│ │ Sentence 1: "The cat is sitting on the mat."         │   │
│ │ Type: triple                                          │   │
│ │                                                       │   │
│ │ [Point] The cat → [Line] is sitting on → [Point] the mat │
│ │  🔵           🟢                   🔵            │   │
│ │                                                       │   │
│ │ ─────────────────────────────────────────────────    │   │
│ │                                                       │   │
│ │ Sentence 2: "What is a cactus?"                       │   │
│ │ Type: line-point                                      │   │
│ │                                                       │   │
│ │ [Line] What is → [Point] a cactus                     │   │
│ │  🟢           🔵                                 │   │
│ │                                                       │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Graph Visual Tab                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    ┌─────────┐                             │
│                    │ The cat │                             │
│                    └────┬────┘                             │
│                         │ is sitting on                    │
│                         ↓                                   │
│                    ┌─────────┐                             │
│                    │ the mat │                             │
│                    └─────────┘                             │
│                                                             │
│                    ┌──────────┐                            │
│           What is  │ a cactus │                            │
│              ───→  └──────────┘                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Step 1: Basic Gradio App (1-2 hours)

Create `demo/gradio_app.py`:

```python
import gradio as gr
from semantic_bit import encode_text_to_sb, decode_sb_to_dot
import json

def process_text(text):
    """Process text and return formatted results."""
    if not text.strip():
        return "Please enter some text", ""

    # Encode
    result = encode_text_to_sb(text)

    # Generate DOT
    dot = decode_sb_to_dot(result)

    # Format JSON
    json_output = json.dumps(result, indent=2)

    return json_output, dot

# Create interface
with gr.Blocks(title="Semantic Bit Theory v2.0") as demo:
    gr.Markdown("# Semantic Bit Theory v2.0 - Visual Tester")

    with gr.Row():
        with gr.Column():
            text_input = gr.Textbox(
                label="Input Text",
                lines=10,
                placeholder="Enter natural language text here..."
            )
            process_btn = gr.Button("Process Text", variant="primary")

        with gr.Column():
            json_output = gr.JSON(label="Semantic Bit JSON")
            dot_output = gr.Code(label="DOT Graph", language="dot")

    process_btn.click(
        fn=process_text,
        inputs=[text_input],
        outputs=[json_output, dot_output]
    )

if __name__ == "__main__":
    demo.launch()
```

**Test**:
```bash
python demo/gradio_app.py
# Opens browser at http://localhost:7860
```

### Step 2: Add Color-Coded Patterns (2-3 hours)

Create pattern visualization with HTML/CSS:

```python
def format_patterns(sb_json):
    """Generate color-coded HTML for pattern visualization."""
    html_parts = []

    for sentence in sb_json.get("sentences", []):
        pattern_type = sentence.get("type")
        original = sentence.get("original_text", "")

        html = f"<div class='sentence'>"
        html += f"<div class='meta'>Type: <strong>{pattern_type}</strong></div>"

        # Color code based on pattern
        if pattern_type == "triple":
            point1 = sentence["point1"]["content"]
            line1 = sentence["line1"]["content"]
            point2 = sentence["point2"]["content"]
            html += (
                f"<span class='point'>{point1}</span> "
                f"<span class='line'>{line1}</span> "
                f"<span class='point'>{point2}</span>"
            )
        elif pattern_type == "line-point":
            line = sentence["line"]["content"]
            point = sentence["point"]["content"]
            html += (
                f"<span class='line'>{line}</span> "
                f"<span class='point'>{point}</span>"
            )
        # ... handle other patterns

        html += "</div>"
        html_parts.append(html)

    # Add CSS
    css = """
    <style>
        .sentence { margin: 10px 0; padding: 10px; border-left: 3px solid #ccc; }
        .meta { color: #666; font-size: 0.9em; margin-bottom: 5px; }
        .point { background: #e3f2fd; color: #1976d2; padding: 2px 6px; border-radius: 3px; }
        .line { background: #e8f5e9; color: #388e3c; padding: 2px 6px; border-radius: 3px; }
    </style>
    """

    return css + "".join(html_parts)
```

### Step 3: Add Graph Visualization (2-3 hours)

Use `graphviz` Python package to render images:

```python
import graphviz
import tempfile

def render_graph_image(dot_code):
    """Render DOT code to SVG image."""
    try:
        graph = graphviz.Source(dot_code)
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            graph.render(f.name, format='svg', cleanup=True)
            return f.name + '.svg'
    except Exception as e:
        return None
```

Add to Gradio:
```python
graph_image = gr.Image(label="Graph Visualization", type="filepath")
```

### Step 4: Add Enrichment UI (1-2 hours)

Add asset/function inputs:

```python
with gr.Accordion("Enrichments (Optional)", open=False):
    assets_input = gr.Code(
        label="Assets JSON",
        language="json",
        value='[{"url": "https://example.com", "label": "example"}]'
    )
    functions_input = gr.Code(
        label="Functions JSON",
        language="json",
        value='[{"name": "func_name", "description": "description"}]'
    )
```

### Step 5: Add Examples (30 min)

```python
examples = gr.Examples(
    examples=[
        ["The cat is sitting on the mat."],
        ["What is a cactus?"],
        ["The dog barks. A cactus grows."],
    ],
    inputs=[text_input]
)
```

---

## Dependencies

### Core (Already Have)
- ✅ `semantic-bit` (our package)

### Demo-Specific (New)
- `gradio` - Web interface framework
- `graphviz` - Graph rendering (optional, for visual graphs)

### Installation Strategy

**Option A**: Optional dependency group in `pyproject.toml`:
```toml
[project.optional-dependencies]
demo = [
    "gradio>=4.0.0",
    "graphviz>=0.20.0"
]
```

**Install**:
```bash
pip install semantic-bit[demo]
```

**Option B**: Separate `requirements.txt` in demo folder:
```
semantic-bit>=2.0.0
gradio>=4.0.0
graphviz>=0.20.0
```

---

## Timeline Estimate

| Task | Time | Complexity |
|------|------|------------|
| Step 1: Basic Gradio app | 1-2 hours | Low |
| Step 2: Color-coded patterns | 2-3 hours | Medium |
| Step 3: Graph visualization | 2-3 hours | Medium |
| Step 4: Enrichment UI | 1-2 hours | Low |
| Step 5: Polish + examples | 1 hour | Low |
| **Total** | **7-11 hours** | **Low-Medium** |

---

## Future Enhancements (Not in Initial Scope)

### For Production Django/React App

When building the full application, you can extract reusable components:

**React Component Library**:
```
semantic-bit-react/
├── src/
│   ├── components/
│   │   ├── PatternVisualizer.tsx    # Color-coded patterns
│   │   ├── SBJsonViewer.tsx         # Formatted JSON display
│   │   ├── GraphViewer.tsx          # Interactive graph
│   │   └── TextInput.tsx            # Input with validation
│   └── hooks/
│       └── useSemantic Bit.ts        # API integration
```

**Django Integration**:
```python
# views.py
from semantic_bit import encode_text_to_sb
from django.http import JsonResponse

def process_text_api(request):
    text = request.POST.get('text')
    result = encode_text_to_sb(text)
    return JsonResponse(result)
```

---

## Recommendation Summary

### For Immediate Testing (Now)

✅ **Build**: Gradio-based demo (Steps 1-5)
- Fast to implement (7-11 hours)
- Beautiful UI out-of-the-box
- No frontend expertise needed
- Perfect for internal testing

### For Future Production (Later)

🔮 **Plan**: Custom React components + Django API
- Reusable component library
- Full control over UX
- Production-ready
- Can import semantic-bit as pip package

---

## Next Steps

1. **Decide**: Gradio demo vs. custom solution
2. **Set up**: Add demo dependencies to project
3. **Implement**: Follow steps 1-5 above
4. **Test**: Use for validating v2.0 behavior
5. **Iterate**: Add features based on testing needs

---

## Questions to Answer

Before starting implementation:

1. **Preference**: Gradio (recommended) vs. Flask+vanilla JS vs. wait for React?
2. **Location**: Inside `semantic_bit/demo/` or separate repo?
3. **Scope**: Just basic (Steps 1-2) or full featured (Steps 1-5)?
4. **Graph rendering**: Server-side (graphviz) or client-side (viz.js)?
5. **Deployment**: Local only or also support remote sharing (Gradio has built-in sharing)?

---

*Document Status: Ready for review and decision-making*
*Recommended: Start with Gradio basic app (Steps 1-2), iterate based on feedback*
