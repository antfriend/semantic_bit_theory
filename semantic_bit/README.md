# semantic-bit

Generate lightweight JSON metadata for short text snippets (up to 5000 characters).

## Installation

```bash
pip install semantic-bit
```

## Python usage

```python
from semantic_bit import analyze_text, analyze_text_as_json

payload = analyze_text("Hello semantic world!")
print(payload)
# {'character_count': 23, 'trimmed_character_count': 23, ...}

json_payload = analyze_text_as_json("Hello semantic world!")
print(json_payload)
```

## Command line interface

```bash
semantic-bit "Your content here"

# Or from a file
semantic-bit --file path/to/document.txt
```

The CLI returns a JSON object describing the text. Use `--no-indent` to emit a compact payload.

## Developing

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`.

## Publishing to PyPI

1. Ensure the version in `pyproject.toml` is bumped appropriately.
2. Build the package (install build backend first: `pip install build twine`):
   ```bash
   python -m build
   ```
3. Upload to PyPI (replace `pypi` with `testpypi` for a dry run):
   ```bash
   python -m twine upload dist/*
   ```

To install the package from TestPyPI for validation:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple semantic-bit
```

## License

MIT
