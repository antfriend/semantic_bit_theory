# Semantic Bit Theory — Analysis and Implementation Plan

## Overview

Semantic Bit Theory (SBT) reduces natural language to two primitives: Points (entities/concepts) and Lines (relationships/actions). This document describes a lightweight, dependency‑free Python implementation that encodes text into simple triples and decodes them into Graphviz DOT for visualization.

## Data Model

The fundamental semantic unit is a Triple: (Point1, Line, Point2), representing a directed relationship between two entities.

Example:

```json
{
  "sentences": [
    { "point1": "The cat", "line1": "is sitting on", "point2": "the mat" }
  ]
}
```

Where:
- `point1`: Subject entity or concept
- `line1`: Relationship, action, or semantic connector
- `point2`: Object entity or target concept

JSON Schema (informal):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "sentences": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["point1", "line1", "point2"],
        "properties": {
          "point1": { "type": "string", "minLength": 1 },
          "line1": { "type": "string", "minLength": 1 },
          "point2": { "type": "string", "minLength": 1 }
        },
        "additionalProperties": true
      }
    }
  },
  "required": ["sentences"],
  "additionalProperties": false
}
```

Constraints & behavior:
- Sentence splitting: boundaries at `.`, `!`, `?` followed by whitespace or end of text.
- Phrase reconstruction: phrases are rebuilt by joining tokens with single spaces (spacing may be normalized; punctuation inside phrases is not preserved).
- Casing: original token casing is preserved per token; surrounding whitespace may differ.
- Skipped sentences: if a sentence does not yield all of `point1`, `line1`, and `point2`, it is omitted.

## Encoding Heuristic

Module: `semantic_bit.semantic.encode_text_to_sb(text)`

Per sentence:
- Tokenize words via regex (`\b[\w']+\b`).
- Extract point1 (leading noun phrase) until a verb‑like token.
- Extract line1 (verb phrase) including auxiliaries and at most one trailing preposition (e.g., “is sitting on”).
- Extract point2 (remaining noun phrase). If any part is missing, skip the sentence.

Verb signal:
- Common auxiliaries (is/are/was/were, have/has/had, do/does/did, modals).
- Morphology heuristic: words ending in `-ing` or `-ed`.

## Decoding to DOT

Module: `semantic_bit.semantic.decode_sb_to_dot(sb, graph_name="SBGraph")`

- Deduplicate identical point labels to single nodes (p1, p2, …) with preserved labels.
- Create directed edges from `point1` to `point2` labeled with `line1`.
- Emit standards‑compliant Graphviz DOT.

Example DOT:

```
digraph SBGraph {
  p1 [label="The cat"];
  p2 [label="the mat"];
  p1 -> p2 [label="is sitting on"];
}
```

## CLI Usage

Base command: `semantic-bit`

Analyze (back‑compat default):
- `semantic-bit analyze "Hello world"`
- `semantic-bit -f input.txt`

Encode:
- `semantic-bit encode "The cat is sitting on the mat."`
- `semantic-bit encode -f input.txt -o semantics.json`

Decode:
- `semantic-bit decode -f semantics.json -o graph.dot`
- `semantic-bit encode "Birds fly south." | semantic-bit decode --name Migration > migration.dot`

## Limitations and Future Work

Linguistic coverage:
- Targets simple S–V–O clauses; compound sentences, subordination, passive voice, and non‑declaratives may be skipped.

Accuracy trade‑offs:
- Prioritizes precision via conservative rules; recall may be reduced without external NLP dependencies.

Executable Lines (future):
- Extend `line1` to support `{ label, action, parameters, preconditions }` and create a sandboxed execution engine.

Knowledge and graph extensions:
- Optional linking to external KBs; ontology alignment; graph querying/analytics.

## Quality Assurance

Regression:
- Existing `analyzer` functionality remains intact; CLI analyze behavior preserved.

Proposed tests (to add):
- Simple sentences encode to expected triples.
- Sentences without clear verbs are skipped.
- Encode → Decode round‑trip produces valid DOT.
- CLI: back‑compat analyze path; encode/decode file and stdin/stdout flows.

Manual checks:
- `semantic-bit encode "The cat is sitting on the mat."`
- `echo "Birds fly south for winter." | semantic-bit encode | semantic-bit decode`

## Implementation Files

- `semantic_bit/src/semantic_bit/semantic.py`: `encode_text_to_sb`, `decode_sb_to_dot`.
- `semantic_bit/src/semantic_bit/cli.py`: subcommands `analyze`, `encode`, `decode` with back‑compat.
- `semantic_bit/src/semantic_bit/__init__.py`: exports new APIs.

## Deployment

- Dependencies: Python standard library only.
- Compatibility: Python 3.9+ (per `pyproject.toml`).
- Distribution: PyPI‑compatible wheel/sdist.
