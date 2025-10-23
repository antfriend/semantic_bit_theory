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
# From this directory (semantic_bit/)
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

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
# Build the package
pip install build twine
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

For complete project information, installation instructions, and usage examples, see the [main project README](../README.md).
