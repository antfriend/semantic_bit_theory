# Project Alignment Proposal — semantic_bit_theory

Date: 2025-11-02
Owner: Maintainers of semantic_bit_theory

## Summary

This proposal aligns package metadata, CLI behavior, documentation, and tooling with the current codebase and repository rules. It resolves drift between v1 and v2 APIs, standardizes the Python baseline, and reduces duplication that risks regressions.

## Goals

- Single, clear Python version baseline consistent with repo rules
- Consistent v2 API usage across CLI and library with v1 back-compat
- Accurate, current packaging metadata for PyPI
- Remove duplicated logic that can diverge over time
- Ensure docs reflect the actual repository contents and usage
- Establish minimal quality gates (format/lint/type hooks and optional CI)

## Proposed Changes

1) Standardize Python Version
- Adopt Python 3.12 as the project baseline (matches CURSORRULES.md).
- Update `semantic_bit/pyproject.toml`:
  - `requires-python = ">=3.12"`
  - Classifiers include `Programming Language :: Python :: 3.12` (optionally 3.10–3.13 if tested).
- Update conflicting mentions:
  - `semantic_bit/AGENTS.md` references 3.13 “hard requirements” and a “Assume 3.10” guardrail. Replace with a single baseline statement consistent with 3.12, or explicitly list the tested range.

2) Version and Metadata Alignment
- Bump package version in `semantic_bit/pyproject.toml` from `1.0.0` to `2.0.0` to reflect current API (`__version__ = "2.0.0"`).
- Update description and keywords to reflect SBT features:
  - Description: “Encode text into Semantic Bit patterns and generate Graphviz DOT/SVG; optional enrichments.”
  - Keywords: add `nlp`, `graphs`, `graphviz`, `semantic`, `knowledge-graph`.
- Verify `project.urls` point to the canonical repository.

3) CLI → v2 Unification (Back-compat preserved)
- In `semantic_bit/src/semantic_bit/cli.py`, import:
  - `encode_text_to_sb` from `semantic_bit.core` (v2 encoder)
  - `decode_sb_to_dot` from `semantic_bit.graph` (v2 decoder supports v1 JSON)
- Keep legacy “bare analyze” behavior for backward compatibility.
- Optional: add a `--legacy` switch to force v1 paths if needed (not required initially).

4) Remove Logic Duplication Around DOT Escaping/Decode
- Single source of truth for DOT escaping and decoding in `semantic_bit/graph.py`.
- Update any legacy codepaths in `semantic_bit/semantic.py` to call into `graph.py` or clearly mark as deprecated; avoid duplicate `escape_dot_string` implementations.

5) Documentation Corrections and Consistency
- `semantic_bit/README.md`: remove the stray leading “git ” prefix/BOM and ensure header begins `# semantic-bit Package`.
- AGENTS expectations vs. reality:
  - Either add minimal `CHANGELOG.md`, `CONTRIBUTING.md`, `CITATION.cff` under `semantic_bit/` OR
  - Adjust `semantic_bit/AGENTS.md` “Directory Layout” to reflect current files.
- Virtual environment guidance: consistently use a single venv pattern (project-root `venv/`) across README files.

6) Packaging Extras and Dev Tooling
- Extras in `semantic_bit/pyproject.toml`:
  - `dev = ["pytest>=7", "pytest-cov", "ruff", "black", "mypy", "pre-commit", "build", "twine"]`
  - `app = ["gradio", "graphviz"]` (optional extras for the demo app)
- Add `.pre-commit-config.yaml` with hooks for black, ruff, and mypy (mypy optional if stubs not ready).
- Add minimal `mypy` and `ruff` settings (either in `pyproject.toml` or separate config files).

7) Optional CI (GitHub Actions)
- A simple workflow to run lint and tests on Python 3.12 (and optionally 3.10, 3.11, 3.13 if supported).
- Scope: `pytest`, `ruff`, `black --check` (and `mypy` if enabled).

## Impact Assessment

- Users of the CLI: No breaking changes; v2 decoder accepts v1 JSON. Behavior becomes more consistent with library default.
- Packagers: Version bump and metadata changes reflect actual API; no runtime dependency changes.
- Contributors: Clearer Python version baseline and tooling hooks improve consistency.

## Migration & Compatibility

- v1 JSON inputs (strings for point/line fields) continue to render via `graph.decode_sb_to_dot`.
- Legacy `semantic_bit.semantic` remains for now; mark decode helpers as deprecated and internally delegate to `semantic_bit.graph` to avoid drift.
- If Python 3.10/3.11 must remain supported, keep `requires-python = ">=3.10"` and add CI for each version; otherwise, align docs to 3.12 only.

## Implementation Plan

1. Decide Python baseline (recommended: 3.12 per CURSORRULES.md).
2. Update `semantic_bit/pyproject.toml`:
   - Version 2.0.0, description, keywords, Python requires, classifiers, extras.
3. Switch CLI to v2 imports (core encoder, graph decoder).
4. De-duplicate DOT helpers: keep implementations in `semantic_bit/graph.py`; have legacy code call into it or mark deprecated.
5. Fix `semantic_bit/README.md` header/BOM; unify venv guidance.
6. Add missing doc stubs or adjust `semantic_bit/AGENTS.md` directory layout claims.
7. Add `.pre-commit-config.yaml` and minimal lint/type configs; update contributor docs.
8. (Optional) Add CI workflow for lint + tests.

## Acceptance Criteria

- pyproject reports version 2.0.0, with accurate description, keywords, and chosen Python baseline.
- CLI uses v2 encode/decode and passes existing tests.
- There is only one DOT escape/decoder implementation in active use (graph.py).
- README header corrected and single venv pattern documented across files.
- AGENTS directory layout matches actual files (either stubs added or text updated).
- Pre-commit runs black/ruff (and optionally mypy) locally.
- (Optional) CI green on chosen Python matrix.

## Open Questions

- Baseline Python version: lock to 3.12 (recommended) or keep a wider range (3.10–3.13) with CI coverage?
- Canonical repository URLs in pyproject: confirm final owner/organization.
- Should legacy `semantic_bit.semantic` be formally deprecated in docs now, or in a later minor release?

## Notes

This proposal intentionally focuses on alignment and quality-of-life fixes without changing the public v2 JSON shape. Feature work (e.g., richer distance metrics, CLI flags) can follow once these foundations are stable.

