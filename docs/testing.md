# Testing Guide

The semantic-bit project includes a comprehensive test suite with 62+ tests covering all functionality. This guide explains how to run tests, what they cover, and how they're organized.

## Quick Start

```bash
# Navigate to the semantic_bit directory
cd semantic_bit

# Run all tests
pytest

# Run with verbose output
pytest -v
```

**Important**: Tests must be run from the `semantic_bit/` directory where `pytest.ini` is located, not from the project root.

## Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output and details
pytest -v

# Run specific test file
pytest tests/test_semantic.py
pytest tests/test_cli.py
pytest tests/test_analyzer.py

# Run with coverage (if coverage is installed)
pytest --cov=semantic_bit
```

## Test Coverage by Module

### Core Semantic Processing (`tests/test_semantic.py`)
Tests the heart of Semantic Bit Theory implementation:
- **Sentence segmentation** - Text splitting at punctuation boundaries
- **Lexical analysis and tokenization** - Word extraction preserving contractions
- **Verb detection and morphological analysis** - Auxiliary verb recognition
- **Phrase extraction** - Point₁, Line, Point₂ syntactic role assignment
- **Encoding pipeline** - Complete text-to-semantic-triples conversion
- **Data structures** - SBTriple, SemanticBitDocument validation
- **DOT graph generation** - Graph synthesis and special character escaping
- **Integration tests** - End-to-end workflows and edge cases

### CLI Interface (`tests/test_cli.py`)
Tests command-line functionality and user interaction:
- **Argument parsing** - Subcommand routing and parameter handling
- **Backward compatibility** - Legacy usage pattern support
- **File I/O operations** - Reading from files, writing output
- **Error handling** - User-friendly error messages and exit codes
- **Pipeline operations** - Encode → decode chaining
- **JSON formatting** - Pretty-printing and compact output options
- **Help system** - Usage information and documentation
- **Edge cases** - Empty input, Unicode text, very long input

### Legacy Analysis (`tests/test_analyzer.py`)
Tests original text analysis functionality:
- **Text statistics** - Character counts, word counts, metadata
- **Input validation** - Length limits and type checking
- **Backward compatibility** - Ensuring existing functionality preserved

## Test Organization

Tests are organized into logical classes within each module for better organization and targeted testing:

### Semantic Processing Classes
- `TestSentenceSegmentation` - Text splitting at boundaries
- `TestTokenization` - Word extraction and normalization
- `TestVerbDetection` - Linguistic pattern matching
- `TestPhraseExtraction` - Syntactic role assignment
- `TestDataStructures` - Semantic triple validation
- `TestEncoding` - End-to-end text processing
- `TestDOTGeneration` - Graph synthesis pipeline
- `TestIntegration` - Complete workflows

### CLI Testing Classes
- `TestArgumentParsing` - Command processing and routing
- `TestFileOperations` - File I/O handling
- `TestErrorHandling` - Exception management
- `TestBackwardCompatibility` - Legacy support
- `TestPipelineOperations` - Multi-step workflows
- `TestJSONFormatting` - Output formatting
- `TestHelpSystem` - Documentation display
- `TestEdgeCases` - Boundary conditions

## Running Specific Test Categories

You can run targeted subsets of tests to focus on specific functionality:

```bash
# Test only semantic processing
pytest tests/test_semantic.py::TestEncoding -v

# Test only CLI functionality  
pytest tests/test_cli.py::TestArgumentParsing -v

# Test integration workflows
pytest tests/test_semantic.py::TestIntegration -v

# Test error handling
pytest tests/test_cli.py::TestErrorHandling -v

# Test backward compatibility
pytest tests/test_cli.py::TestBackwardCompatibility -v

# Test data structures
pytest tests/test_semantic.py::TestDataStructures -v
```

## Test Configuration

The project uses `pytest.ini` for configuration:

```ini
[pytest]
pythonpath = src
```

This configuration:
- Sets the Python path to include the `src` directory
- Enables direct imports from the semantic_bit module
- Allows tests to be run from the semantic_bit directory

## Expected Results

All tests should pass consistently:

```
============================== test session starts ==============================
platform darwin -- Python 3.10.18, pytest-8.3.2, pluggy-1.6.0
rootdir: /path/to/semantic_bit_theory/semantic_bit
configfile: pytest.ini
collecting ... collected 62 items

tests/test_analyzer.py::test_analyze_basic_counts_words_and_characters PASSED [  1%]
tests/test_analyzer.py::test_analyze_text_respects_length_limit PASSED       [  3%]
...
tests/test_semantic.py::TestIntegration::test_handles_edge_cases_gracefully PASSED [100%]

============================== 62 passed in 0.14s ==============================
```

## Troubleshooting Test Issues

If tests fail, check these common issues:

### 1. Wrong Working Directory
**Error**: `ERROR: file or directory not found: tests/test_semantic.py::TestEncoding`

**Solution**: Make sure you're in the `semantic_bit/` directory:
```bash
cd semantic_bit
pytest tests/test_semantic.py::TestEncoding -v
```

### 2. Virtual Environment Not Activated
**Error**: Import errors or missing dependencies

**Solution**: Activate your virtual environment:
```bash
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\Activate.ps1  # Windows PowerShell
```

### 3. Dependencies Not Installed
**Error**: `ModuleNotFoundError` for pytest or semantic_bit

**Solution**: Install the package in development mode:
```bash
pip install -e .[dev]
```

### 4. Permission Issues
**Error**: Permission denied when reading/writing files

**Solution**: Check file permissions in the test directory:
```bash
ls -la tests/
chmod 644 tests/*.py  # if needed
```

### 5. Source Code Modifications
**Error**: Tests fail unexpectedly after working on code

**Solution**: Verify source files haven't been corrupted:
```bash
git status  # check for unexpected changes
git diff    # review any modifications
```

## Running Tests in Different Environments

### Development Environment
```bash
# Full test suite with verbose output
pytest -v

# With coverage reporting
pytest --cov=semantic_bit --cov-report=html
```

### Continuous Integration
```bash
# Fast test run for CI
pytest --tb=short

# Generate JUnit XML for CI systems
pytest --junitxml=test-results.xml
```

### Performance Testing
```bash
# Run with timing information
pytest --durations=10

# Run with benchmark plugin (if installed)
pytest --benchmark-only
```

## Test Development Guidelines

When adding new tests:

1. **Follow naming conventions**: `test_function_name` or `TestClassName`
2. **Use descriptive test names**: Clearly indicate what is being tested
3. **Organize into logical classes**: Group related tests together
4. **Test both success and failure cases**: Include error conditions
5. **Use appropriate assertions**: Be specific about expected outcomes
6. **Mock external dependencies**: Isolate units under test
7. **Document complex test scenarios**: Add comments for intricate logic

## Integration with Development Workflow

### Pre-commit Testing
```bash
# Run quick smoke tests before committing
pytest tests/test_semantic.py::TestEncoding

# Run all tests before pushing
pytest
```

### Feature Development
```bash
# Test specific functionality while developing
pytest tests/test_semantic.py -k "tokenize" -v

# Watch for file changes (with pytest-watch)
ptw -- tests/test_semantic.py
```

This comprehensive test suite ensures the reliability and correctness of the Semantic Bit Theory implementation across all functionality areas.