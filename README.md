# semantic-bit

Convert natural language text into semantic graphs using Semantic Bit Theory (SBT).

## Overview

semantic-bit is a Python package that implements Semantic Bit Theory to transform natural language into structured semantic representations. It converts text into Point-Line-Point triples (subject-relationship-object) and generates Graphviz DOT graphs for visualization.

### Key Features

- **Semantic Encoding**: Transform text into Point-Line-Point semantic triples  
- **Graph Generation**: Convert semantic triples to Graphviz DOT format
- **Lightweight**: Zero external dependencies, pure Python implementation
- **CLI Pipeline**: Seamless text → JSON → graph workflows
- **Backward Compatible**: Preserves original text analysis functionality

### Quick Example

```bash
# Encode text to semantic triples
semantic-bit encode "The cat is sitting on the mat."

# Generate a graph
echo "The scientist studies quantum mechanics." | semantic-bit encode | semantic-bit decode
```

## Installation

### For End Users

```bash
pip install semantic-bit
```

The semantic-bit package has **zero runtime dependencies** - it uses only Python's standard library!

### For Development

To work on the semantic_bit_theory project (including diagram generation and testing):

```bash
git clone https://github.com/your-repo/semantic_bit_theory.git
cd semantic_bit_theory

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Install the package in editable mode
pip install -e ./semantic_bit
```

**Development dependencies include:**
- `matplotlib` & `numpy` - For generating visualization diagrams
- `pytest` - For running the test suite
- `build` & `twine` - For packaging and publishing

## Quick Start

### Python API
```python
from semantic_bit import encode_text_to_sb, decode_sb_to_dot

# Encode text to semantic triples
text = "The cat is sitting on the mat."
semantic_bits = encode_text_to_sb(text)
print(semantic_bits)
# {"sentences": [{"point1": "The cat", "line1": "is sitting on", "point2": "the mat"}]}

# Generate DOT graph
dot_graph = decode_sb_to_dot(semantic_bits)
print(dot_graph)
# digraph SBGraph { p1 [label="The cat"]; p2 [label="the mat"]; p1 -> p2 [label="is sitting on"]; }
```

### Command Line Interface
```bash
# Encode text to semantic JSON
semantic-bit encode "The cat is sitting on the mat."
semantic-bit encode --file input.txt --out output.json

# Decode JSON to DOT graph  
semantic-bit decode --file output.json --out graph.dot

# Pipeline operations
semantic-bit encode --file input.txt | semantic-bit decode --name "MyGraph"
```

## Documentation

### 📖 [Examples and Usage Patterns](docs/examples.md)
Comprehensive examples covering file processing, pipeline operations, visualization, and integration with other tools. Includes sample files and common usage patterns.

### 🧪 [Testing Guide](docs/testing.md)  
Complete testing documentation with 62+ tests covering all functionality. Includes test execution instructions, organization details, and troubleshooting guidance.

### 🔬 [Theoretical Framework](docs/theory.md)
Deep dive into Semantic Bit Theory concepts, taxonomic principles, and philosophical foundations. Covers the dual axes framework and applications in knowledge graphs, narrative analytics, and affective computing.

### 📋 [Technical Specification](docs/semantic_bit_analysis.md)
Detailed technical analysis of the implementation including architecture, algorithms, and JSON schema specifications.

## Project Structure

```
semantic_bit_theory/
├── README.md                          # This file - main project documentation
├── requirements.txt                   # Development dependencies (matplotlib, numpy, pytest, build, twine)
├── generate_enhancement_diagrams.py   # Visualization diagram generator
├── semantic_bit/                      # Python package directory
│   ├── requirements.txt               # Package-specific dependencies
│   ├── pyproject.toml                 # Package configuration and metadata
│   ├── src/semantic_bit/              # Source code
│   ├── tests/                         # Test suite (62+ tests)
│   └── README.md                      # Package-specific documentation
├── docs/                              # Documentation
│   ├── examples.md                    # Usage examples and patterns
│   ├── testing.md                     # Testing guide
│   ├── theory.md                      # Conceptual framework
│   └── semantic_bit_analysis.md       # Technical specification
├── examples/                          # Sample files and demonstrations
└── images/                            # Conceptual diagrams and visualizations
```

## Contributing

We welcome contributions! Please see our testing guide for information about running tests and our examples documentation for usage patterns.

1. Fork the repository
2. Clone and set up your development environment:
   ```bash
   git clone https://github.com/your-username/semantic_bit_theory.git
   cd semantic_bit_theory
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -e ./semantic_bit
   ```
3. Create a feature branch (`git checkout -b feature/amazing-feature`)
4. Make your changes and add tests
5. Run the test suite (`pytest semantic_bit/tests/`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

MIT License - see the LICENSE file for details.
