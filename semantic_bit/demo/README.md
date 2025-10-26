# Semantic Bit Theory v2.0 - Visual Testing Interface

Interactive web interface for testing and visualizing semantic pattern detection.

## Quick Start

### 1. Install Dependencies

**From the semantic_bit directory:**

```bash
# Install semantic_bit package (if not already installed)
pip install -e .

# Install demo dependencies
pip install -r demo/requirements.txt

# Install system graphviz (required for graph visualization)
# macOS:
brew install graphviz

# Ubuntu/Debian:
sudo apt-get install graphviz

# Windows:
# Download from https://graphviz.org/download/
```

### 2. Run the Demo

```bash
# From semantic_bit directory:
python -m demo.gradio_app

# Or directly:
python demo/gradio_app.py
```

The interface will open in your browser at `http://localhost:7860`

## Features

### 📝 Text Processing
- Input natural language text
- Process with flexible pattern detection
- View structured JSON output

### 🎨 Pattern Visualization
- Color-coded semantic elements:
  - 🔵 **Blue**: Points (nouns, entities)
  - 🟢 **Green**: Lines (verbs, relationships)
- Pattern type labels for each sentence
- Original text preservation

### 🔗 Enrichment Testing
- Test asset mapping (URLs to Points)
- Test function mapping (executables to Lines)
- See enriched JSON with embedded resources

### 📊 Graph Visualization ⭐
- **Live graph rendering** from DOT format
- Visual representation of semantic relationships
- Interactive zoom/pan (in supported formats)
- Download graph as SVG/PNG

## Usage Examples

### Basic Text Processing

```
Input: "The cat is sitting on the mat."

Output:
- Type: triple
- Visual: [Point: The cat] → [Line: is sitting on] → [Point: the mat]
- Graph: Directed graph with nodes and edges
```

### Question Detection

```
Input: "What is a cactus?"

Output:
- Type: line-point
- Visual: [Line: What is] → [Point: a cactus]
- Graph: Interrogative structure
```

### With Enrichment

```
Input: "The cactus grows in desert."

Assets:
[{"url": "https://wiki.org/cactus", "label": "cactus"}]

Output:
- Point "cactus" linked to URL
- Graph nodes show enriched data
```

## Interface Tabs

1. **🎨 Patterns** - Color-coded visualization of detected patterns
2. **📄 JSON** - Formatted Semantic Bit JSON output
3. **💻 DOT Code** - Raw Graphviz DOT format
4. **📊 Graph** - Rendered graph visualization (MAIN FEATURE)
5. **📈 Stats** - Statistics about patterns detected

## Keyboard Shortcuts

- `Ctrl/Cmd + Enter` - Process text
- `Ctrl/Cmd + K` - Clear inputs
- `Ctrl/Cmd + E` - Load example

## Tips

- **Graph quality**: Larger text = more complex graphs
- **Performance**: Keep input under 10,000 characters for best performance
- **Assets/Functions**: Use valid JSON format for enrichments
- **Graph export**: Right-click on graph to save image

## Troubleshooting

### Graphviz not found

```
Error: "Graphviz executable not found"
```

**Solution**: Install system graphviz (see installation instructions above)

### Port already in use

```
Error: "Port 7860 already in use"
```

**Solution**:
```bash
python demo/gradio_app.py --server-port 7861
```

### Graph rendering fails

**Check**:
1. System graphviz installed? Run `dot -V`
2. Python graphviz package installed? Run `pip list | grep graphviz`

## Development

### Adding Examples

Edit `gradio_app.py`, section `EXAMPLE_TEXTS`:

```python
EXAMPLE_TEXTS = [
    "Your example text here",
    # Add more examples
]
```

### Customizing Colors

Edit `utils.py`, section `COLORS`:

```python
COLORS = {
    'point': '#e3f2fd',  # Light blue
    'line': '#e8f5e9',   # Light green
    # Add custom colors
}
```

## For Production Use

This demo is for **internal testing only**. For production:
1. Use the semantic_bit package as a pip dependency
2. Build custom Django/React frontend
3. Import components as needed

---

**Version**: 2.0.0
**Status**: Development/Testing Tool
**License**: Same as semantic_bit package
