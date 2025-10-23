# Semantic Bit Theory – Analysis and Implementation Plan

## Overview

Goal: Implement a lightweight Python encoder/decoder for “Semantic Bit Theory” that:
- Encodes English text into simple Point/Line triples per sentence.
- Decodes that structure into a Graphviz DOT graph.
- Ships with a console app for quick testing (encode/decode) while preserving the existing analyze command.

This initial version uses deterministic heuristics (no external NLP dependencies) to keep the package small and easy to run anywhere.

## Data Model

We represent each sentence as one primary triple:
- point1: leading noun phrase (subject-like)
- line1: verb phrase (verb/auxiliary and an optional preposition)
- point2: trailing noun phrase (object/complement-like)

Top-level JSON shape:

{
  "sentences": [
    {"point1": "The cat", "line1": "is sitting on", "point2": "the matt"}
  ]
}

## Encoding Heuristic

Module: `semantic_bit.semantic.encode_text_to_sb(text)`

Steps per sentence:
1) Split text into sentences by `.`, `!`, `?` boundaries.
2) Tokenize words using a simple regex and preserve original surface forms.
3) Extract phrases in order:
   - point1: collect initial noun phrase until a verb-like token.
   - line1: collect auxiliary/verb tokens and at most one trailing preposition (e.g., “is sitting on”).
   - point2: collect the remaining noun phrase.

Verb detection:
- A fixed set of common auxiliaries (is/are/was/were, have/has/had, do/does/did, modals).
- Basic morphology rule: tokens ending in `-ing` or `-ed` count as verb-like.

Preposition handling:
- If a preposition follows the verb phrase, include it in `line1` (e.g., “sit on”).

Notes:
- If a sentence doesn’t match the expected shape, it’s skipped for this first pass.
- Heuristics are intentionally conservative to avoid overfitting or heavy dependencies.

## Decoding to DOT

Module: `semantic_bit.semantic.decode_sb_to_dot(sb, graph_name="SBGraph")`

Algorithm:
- Create directed nodes for each unique point label (deduplicated by text).
- Create edges from `point1` to `point2` with the `line1` as edge label.
- Output a single DOT graph combining all sentences.

Example output:

digraph SBGraph {
  p1 [label="The cat"];
  p2 [label="the matt"];
  p1 -> p2 [label="is sitting on"];
}

## CLI Usage

Entry: `semantic-bit` (unchanged). Subcommands:

- Analyze (backwards-compatible default):
  - `semantic-bit analyze "Hello world"`
  - `semantic-bit -f input.txt`

- Encode text to Semantic Bit JSON:
  - `semantic-bit encode "The cat is sitting on the matt."`
  - `semantic-bit encode -f input.txt -o out.json`

- Decode Semantic Bit JSON to DOT:
  - `semantic-bit decode -f out.json -o graph.dot`
  - `semantic-bit encode "A bird flew over the tree." | semantic-bit decode --name MyGraph > graph.dot`

All commands support stdout if `-o/--out` is omitted. JSON pretty-print uses `--indent`.

## Limitations and Future Work

- Grammar coverage: The current heuristics handle simple clauses. Complex or compound sentences may not yield a triple.
- POS accuracy: Without a full tagger, some verbs or nouns may be misclassified. We avoid external NLP deps for now.
- Multi-verb/multi-object: Only the primary (first) verb-object relation is extracted per sentence in this version.
- “Executable Line” entities: Future versions can attach function names or event handlers to `line1` values and provide an execution engine/sandbox. Proposed shape:
  - `{ point1, line1: { label: "is sitting on", action: "do_sit_on" }, point2 }`
  - CLI could add `run` to execute actions when available.

## Testing Notes

- The existing `analyzer` tests remain unchanged.
- Manual smoke tests:
  - Encode: `semantic-bit encode "The cat is sitting on the matt."`
  - Decode: `semantic-bit encode "The cat is sitting on the matt." | semantic-bit decode`

## Implementation Files

- `semantic_bit/src/semantic_bit/semantic.py`
  - `encode_text_to_sb(text) -> dict`
  - `decode_sb_to_dot(sb_dict, graph_name) -> str`

- `semantic_bit/src/semantic_bit/cli.py`
  - New subcommands: `encode`, `decode`; default `analyze` path preserved.

- `semantic_bit/src/semantic_bit/__init__.py`
  - Exposes `encode_text_to_sb` and `decode_sb_to_dot` for library use.

