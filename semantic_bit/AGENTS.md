# AGENTS.md — semantic_bit

## Project One-Liner

**semantic_bit**: a Python 3.13 package for “Semantic Bit” primitives—lightweight data structures, transforms, and utilities for composing symbolic/semantic computations.

## North Star Goals

* Provide a clean, well-tested Python API for Semantic Bit operations (encode, compose, transform, visualize).
* Ship on PyPI with semantic versioning and a zero-surprise developer experience.
* Maintain clear boundaries: core library (pure Python as possible), optional extras (viz, CLI), examples (notebooks, demos).

## Target Users

* Python developers and researchers prototyping symbolic/semantic systems.
* Data-curious makers who want legible, composable building blocks.

---

## Directory Layout (authoritative)

```
semantic_bit/
├─ src/semantic_bit/
├─ tests/
├─ pyproject.toml
├─ README.md
├─ CHANGELOG.md
├─ LICENSE
├─ CITATION.cff
├─ CONTRIBUTING.md
└─ AGENTS.md                 # this file
```

---

## Tooling & Environment (hard requirements)

* **Python**: 3.13
* **Formatting/Lint/Type**: `black`, `ruff`, `mypy`
* **Tests**: `pytest`, `pytest-cov`
* **Build/Publish**: `hatch` (preferred) or `build` + `twine`
* **Pre-commit**: enable hooks for black/ruff/mypy
* **Docs** (optional): `mkdocs-material` or `pdoc`
* **Graphviz** (optional): for `viz.py` dot output rendering

### Standard Commands

```bash
# one-time
pip install -e .[dev]
pre-commit install

# dev loop
pytest -q
pytest --cov=semantic_bit_pip --cov-report=term-missing
ruff check .
black .
mypy src

# build & publish
hatch build
hatch publish  # or: python -m build && twine upload dist/*
```

---

## Versioning & Commits

* **SemVer**: MAJOR.MINOR.PATCH
* **Conventional Commits**: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `perf:`
* Keep **CHANGELOG.md** current. Each change includes a brief rationale.

---

## Security & Data Handling

* No PII; examples use synthetic data.
* `io.py` must validate schema; reject unknown fields by default.
* Avoid implicit network calls—library is offline-first.

---

## API Design Principles

* Pure functions where practical; small, composable units.
* Dataclasses or `TypedDict` for structured payloads.
* Total ordering and hashing for “Bit” where sensible.
* Raise precise exceptions (`ValueError`, `TypeError`) with actionable messages.
* Docstrings include: purpose, params, returns, examples.

---

## Agents & Roles

### 1) **Architect Agent**

**Mission**: Keep system shape coherent and future-proof.
**Do**:

* Maintain module boundaries (`bits`, `compose`, `transform`).
* Approve public API surface (`__all__` exports).
* Keep complexity low; prefer data-oriented designs.

**Deliverables**:

* Updated module diagrams (simple ASCII or Graphviz).
* ADR notes in `CONTRIBUTING.md` when decisions affect API.

---

### 2) **Librarian Agent**

**Mission**: Keep docs and examples delightful.
**Do**:

* Expand `README.md` quick-start to runnable examples.
* Ensure examples sync with API (tests should import examples).
* Maintain `CITATION.cff` and badges.

**Deliverables**:

* At least one notebook showing composition + transform pipeline.
* Docs pages for each top-level module.

---

### 3) **Coder Agent**

**Mission**: Implement features with tests first.
**Do**:

* Write tests before or alongside code.
* Keep functions under ~50 lines when feasible.
* Follow style tools (black/ruff/mypy) without exceptions.

**Deliverables**:

* Green CI on PR (lint, type, tests).
* Clear docstrings + minimal examples.

---

### 4) **Reviewer Agent**

**Mission**: Protect quality and API stability.
**Checklist**:

* [ ] Naming coherent and discoverable?
* [ ] Types precise (no `Any` unless justified)?
* [ ] Tests cover edge cases and failure modes?
* [ ] No hidden I/O or global state?
* [ ] Public API documented and versioned?

---

### 5) **Data Engineer Agent** (optional)

**Mission**: Validate schemas and codecs.
**Do**:

* Define JSON/YAML schemas for Bit structures.
* Round-trip tests: encode → decode → equals.

---

### 6) **DevOps Agent**

**Mission**: Reproducible builds, clean releases.
**Do**:

* Ensure `pyproject.toml` is the single source of truth.
* Automate version bumps and changelog generation if desired.
* Verify wheels for py3.10 and sdist.

---

## Rules for AI Assistants (Copilot/Cursor/Codex)

### Global Guardrails

1. **Assume Python 3.10** for all code.
2. Prefer **standard library** first; add deps only when justified.
3. Generate **tests** with each non-trivial function.
4. Keep suggestions **idempotent**; do not introduce stateful singletons.
5. Never write secrets or tokens to files or logs.

### Editing & Context

* Respect the declared **directory layout**.
* When creating new files, place them under the correct module and add imports/exports.
* If unsure, propose a small ADR note in the PR description rather than blocking.

### Style & Quality

* Enforce `black`, `ruff`, `mypy` before presenting code as “done.”
* Prefer small PRs with crisp scope.
* Use **doctest-style examples** in docstrings when possible.

### Testing Expectations

* Minimum target coverage: **85%** for core modules.
* Every bug fix includes a regression test.
* Property-based tests are welcome for composition laws.

---

## Public API (first pass)

* `semantic_bit_pip.bits`

  * `Bit` (dataclass): `id: str`, `value: int | str | bool | float | bytes`, `meta: dict[str, Any]`
  * `as_int`, `as_str`, `as_bool`, `as_float` (converters)
* `semantic_bit_pip.compose`

  * `compose(*bits) -> Bit` (define associativity/commutativity via kwargs)
  * `overlay(a: Bit, b: Bit, *, policy: Literal["left","right","merge"]="merge") -> Bit`
  * `distance(a: Bit, b: Bit) -> float`
* `semantic_bit_pip.transform`

  * `normalize(bit: Bit, *, schema: dict | None = None) -> Bit`
  * `map_values(bit: Bit, fn: Callable[[Any], Any]) -> Bit`
  * `project(bit: Bit, keys: Iterable[str]) -> Bit`
* `semantic_bit_pip.io`

  * `to_json(bit: Bit) -> str`
  * `from_json(text: str) -> Bit`
  * `to_yaml(bit: Bit) -> str` (optional dep: `pyyaml`)
  * `from_yaml(text: str) -> Bit`

> Any additions require updating README + tests.

---

## Acceptance Criteria (for any PR)

* [ ] Code runs on **Python 3.10**.
* [ ] Lint/type/test all pass locally and in CI.
* [ ] Public API changes documented and typed.
* [ ] Examples updated (if behavior visible to users).
* [ ] No breaking changes without a MINOR/MAJOR bump and changelog entry.

---

## Example: Minimal `Bit` and Compose (sketch)

```python
# src/semantic_bit_pip/bits.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Mapping

@dataclass(frozen=True, slots=True)
class Bit:
    id: str
    value: Any
    meta: Mapping[str, Any] = field(default_factory=dict)
```

```python
# src/semantic_bit_pip/compose.py
from __future__ import annotations
from typing import Iterable
from .bits import Bit

def compose(*bits: Bit) -> Bit:
    """Compose bits by stable concatenation of ids and right-biased value.
    Example:
        >>> from semantic_bit_pip.bits import Bit
        >>> compose(Bit("a", 1), Bit("b", 2)).id
        'a+b'
    """
    if not bits:
        raise ValueError("compose() requires at least one Bit")
    cid = "+".join(b.id for b in bits)
    val = bits[-1].value
    meta = {k: v for b in bits for k, v in b.meta.items()}
    return Bit(cid, val, meta)
```

```python
# tests/test_compose.py
from semantic_bit_pip.bits import Bit
from semantic_bit_pip.compose import compose
def test_compose_basic():
    a, b = Bit("a", 1), Bit("b", 2)
    c = compose(a, b)
    assert c.id == "a+b"
    assert c.value == 2
```

---

## Documentation Stubs to Maintain

* **README.md**

  * Install, quick start, API tour, roadmap.
* **CONTRIBUTING.md**

  * Dev setup, test matrix, release process, code of conduct link.
* **CHANGELOG.md**

  * Keep entries human-readable with links to PRs/issues.

---

## Migration Notes (Cursor/Codex)

* If you previously used `.cursorrules`, mirror any still-relevant rules into this **AGENTS.md**.
* Keep this file short and specific; link deeper design notes from `CONTRIBUTING.md` or `/docs`.

---

## Non-Goals

* Heavy deep-learning dependencies.
* Hidden network calls.
* Magical global registries.

---

## Glossary

* **Bit**: smallest semantic unit with an `id`, `value`, and optional `meta`.
* **Compose**: deterministic operation combining Bits into a new Bit.
* **Normalize**: enforce schema/typing invariants on a Bit.

---

## Roadmap (short)

* v0.1.0: Core `Bit`, `compose`, `transform`, JSON I/O, minimal docs.
* v0.2.x: YAML I/O, Graphviz viz, CLI (`sbp`).
* v0.3.x: Laws & property tests; richer distance metrics.

---

**Footnote for AI tools**: Prefer proposing small refactors with tests. When uncertain, add a short “Assumptions” comment at the top of a PR and proceed—don’t stall work.
