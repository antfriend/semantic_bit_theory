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
