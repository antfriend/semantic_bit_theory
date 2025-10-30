# semantic-bit Package

This directory contains the Python package implementation of semantic-bit.

## Package Structure

```
semantic_bit/
├── src/semantic_bit/     # Source code
│   ├── __init__.py       # Package exports and API
│   ├── semantic.py       # Core SBT implementation  
│   ├── cli.py           # Command line interface
│   └── analyzer.py      # Legacy text analysis
├── tests/               # Test suite (62+ tests)
├── pyproject.toml       # Package configuration
└── pytest.ini          # Test configuration
```

## Development

This package is part of the larger semantic_bit_theory project.

**📖 For complete documentation, see the [project README](../README.md)**

### Quick Development Setup

```bash
# From the project root (semantic_bit_theory/)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all development dependencies
pip install -r requirements.txt

# Install this package in editable mode
pip install -e ./semantic_bit

# Run tests
pytest semantic_bit/tests/
```

**Note:** The core `semantic-bit` package has **zero runtime dependencies**. Development dependencies (matplotlib, numpy, pytest) are only needed for working on the repository, not for using the published package.

### Testing

```bash
# Run all tests
pytest

# Run specific test categories  
pytest tests/test_semantic.py::TestEncoding -v
```

**📖 For detailed testing instructions, see [Testing Guide](../docs/testing.md)**

### Gradio Visual Testing App

An interactive web interface for testing pattern detection, visualization, and SVG animation generation.

#### Setup

```bash
# From the project root (semantic_bit_theory/)

# 1. Create virtual environment with Python 3.13 or 3.12
#    (Python 3.14 has compatibility issues with some dependencies)
python3.13 -m venv venv

# 2. Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install Gradio and dependencies
pip install gradio graphviz

# 4. Install semantic_bit package in editable mode
pip install -e ./semantic_bit
```

#### Running the App

```bash
# From the project root
./venv/bin/python semantic_bit/demo/gradio_app.py

# Or from the semantic_bit/ directory
cd semantic_bit
../venv/bin/python -m demo.gradio_app
```

The app will open at: **http://localhost:7860**

#### Features

- **Interactive text processing**: Enter text and see semantic patterns extracted
- **Graph visualization**: Visual representation of semantic relationships
- **Pattern inspection**: Color-coded pattern display
- **JSON output**: View the raw Semantic Bit JSON structure
- **Enrichments**: Link assets and functions to patterns (optional)
- **SVG Animation** *(NEW)*: Generate animated SVG slideshows from text

#### System Requirements

- **macOS**: Requires system Graphviz for graph rendering
  ```bash
  brew install graphviz
  ```

- **Linux**: Install via package manager
  ```bash
  sudo apt-get install graphviz  # Debian/Ubuntu
  sudo yum install graphviz      # Red Hat/CentOS
  ```

## Package Development

### Building and Publishing

```bash
# Install build tools (or use pip install -r requirements.txt from project root)
pip install build twine

# Build the package (from the semantic_bit/ directory)
python3.10 -m build

# Upload to PyPI
python3.10 -m twine upload dist/*
```

**Note:** A `.pypirc` file in your home directory is recommended for PyPI authentication. See the [Twine documentation](https://twine.readthedocs.io/) for details.

For complete project information, installation instructions, and usage examples, see the [main project README](../README.md).
