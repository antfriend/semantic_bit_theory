# Semantic Bit Theory

Convert natural language text into semantic graphs using Semantic Bit Theory (SBT).

## Overview

This repository contains the `semantic-bit` Python package that implements Semantic Bit Theory to transform natural language into structured semantic representations. It converts text into Point-Line-Point triples (subject-relationship-object) and generates Graphviz DOT graphs and animated SVG slideshows.

**Key Features:**
- 🧠 Semantic encoding: text → Point-Line-Point triples
- 📊 Graph generation: Graphviz DOT format
- 🎬 Animated SVG slideshows
- 🖥️ Interactive Gradio web UI
- ⚡ Zero runtime dependencies (pure Python)
- 🔧 CLI pipeline support

## 🚀 Quick Start

**Want to try it immediately?** Launch the Gradio web interface:

```bash
# From the project root (semantic_bit_theory/)
./start_gradio.sh              # macOS/Linux
start_gradio.bat               # Windows

# Opens at: http://localhost:7860
```

**For detailed usage instructions**, see the **[semantic_bit package README](semantic_bit/README.md)** which includes:
- Complete installation guide
- Python API examples
- CLI usage patterns
- Gradio web UI setup
- Troubleshooting tips

## Installation

### End Users (pip)

```bash
pip install semantic-bit
```

### Contributors (Development)

```bash
git clone https://github.com/your-username/semantic_bit_theory.git
cd semantic_bit_theory

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Install package in editable mode
pip install -e ./semantic_bit
```

**Development dependencies:** matplotlib, numpy, pytest, build, twine

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

## Related Repositories

- Semantic Bit GPU Server: https://github.com/jblacketter/semantic_bit_gpu_server
  - Standalone FastAPI microservice for Stable Diffusion 1.5 image generation on RTX 4070 SUPER (WSL2), with model warm-loading and request queuing.

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
