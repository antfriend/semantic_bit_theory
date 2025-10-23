"""Semantic Bit encoder/decoder.

This module implements a minimal, heuristic-based interpretation of
"Semantic Bit Theory" as described in the project notes:

- Encode English text into simple Point/Line structures
- Decode those structures to Graphviz DOT

The heuristics are intentionally lightweight (no external NLP deps):
  * Split text into sentences by punctuation (.!?).
  * Within each sentence, collect a leading noun phrase as point1,
    a verb phrase as line1 (aux/verb + optional preposition), and
    a trailing noun phrase as point2.
  * If a sentence does not match this shape, it is skipped.

These choices satisfy the example: "The cat is sitting on the matt." ->
{"point1":"The cat", "line1":"is sitting on", "point2":"the matt"}
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence
import re

# Basic tokenization retaining simple words (with apostrophes)
_WORD_RE = re.compile(r"\b[\w']+\b")

# Common auxiliaries and verb indicators; used to detect the verb phrase
_AUXILIARIES = {
    "am",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "can",
    "could",
    "will",
    "would",
    "shall",
    "should",
    "may",
    "might",
    "must",
}

# Prepositions commonly tied to a verb phrase in simple clauses
_PREPOSITIONS = {
    "on",
    "in",
    "at",
    "to",
    "from",
    "with",
    "by",
    "for",
    "of",
    "over",
    "under",
    "into",
    "onto",
    "about",
    "through",
}

# Simple determiners to help group noun phrases
_DETERMINERS = {"the", "a", "an", "this", "that", "these", "those", "my", "your", "his", "her", "its", "our", "their"}


@dataclass
class SBTriple:
    point1: str
    line1: str
    point2: str

    def to_dict(self) -> Dict[str, str]:
        return {"point1": self.point1, "line1": self.line1, "point2": self.point2}


def _split_sentences(text: str) -> List[str]:
    # Split on ., !, ? followed by space or end, keep simple; remove empties
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _tokens(sentence: str) -> List[Dict[str, str]]:
    return [{"text": m.group(0), "lower": m.group(0).lower()} for m in _WORD_RE.finditer(sentence)]


def _looks_like_verb(word_lower: str) -> bool:
    # Auxiliary or a simple verb morphology heuristic
    if word_lower in _AUXILIARIES:
        return True
    if word_lower.endswith("ing") or word_lower.endswith("ed"):
        return True
    return False


def _collect_phrase(tokens: Sequence[Dict[str, str]], idx: int, *, include_prepositions: bool) -> (str, int):
    if idx >= len(tokens):
        return "", idx

    start = idx

    # If noun phrase: optionally determiners + words until a verb-ish token
    if not include_prepositions:
        # Gather until we hit a clear verb indicator
        seen_word = False
        while idx < len(tokens):
            t = tokens[idx]
            lower = t["lower"]
            # stop at obvious verb start
            if _looks_like_verb(str(lower)) and seen_word:
                break
            seen_word = True
            idx += 1
        phrase = _reconstruct(tokens, start, idx)
        return phrase, idx

    # Verb phrase: must include at least one verb-like token; extend through optional preposition
    saw_verb = False
    while idx < len(tokens):
        lower = tokens[idx]["lower"]
        if _looks_like_verb(lower) or (include_prepositions and (lower in _PREPOSITIONS or lower in _AUXILIARIES)):
            saw_verb = True or saw_verb
            idx += 1
        else:
            # Stop when hitting something that looks like start of the next noun phrase
            if saw_verb:
                break
            # If we haven't seen a verb yet but encounter auxiliaries, keep them
            if lower in _AUXILIARIES:
                idx += 1
            else:
                # Not verb-like; stop to avoid consuming noun phrase
                break
    # If the token immediately after verb(s) is a preposition, include exactly one
    if idx < len(tokens):
        next_lower = tokens[idx]["lower"]
        if next_lower in _PREPOSITIONS:
            idx += 1
    phrase = _reconstruct(tokens, start, idx)
    return phrase, idx


def _reconstruct(tokens: Sequence[Dict[str, str]], start: int, end: int) -> str:
    if start >= end:
        return ""
    return " ".join(t["text"] for t in tokens[start:end]).strip()


def encode_text_to_sb(text: str) -> Dict[str, List[Dict[str, str]]]:
    """Encode text into Semantic Bit triples.

    Returns a dict with a single key "sentences" containing a list of
    {point1, line1, point2} mappings.
    """
    results: List[Dict[str, str]] = []
    for sentence in _split_sentences(text):
        toks = _tokens(sentence)
        if not toks:
            continue

        # point1 ~ leading noun phrase
        p1, idx = _collect_phrase(toks, 0, include_prepositions=False)
        if not p1:
            continue

        # line1 ~ verb phrase (+ optional preposition)
        l1, idx2 = _collect_phrase(toks, idx, include_prepositions=True)
        if not l1:
            continue

        # point2 ~ trailing noun phrase
        p2, _ = _collect_phrase(toks, idx2, include_prepositions=False)
        if not p2:
            continue

        results.append(SBTriple(p1, l1, p2).to_dict())

    return {"sentences": results}


def decode_sb_to_dot(sb: Dict[str, List[Dict[str, str]]], graph_name: str = "SBGraph") -> str:
    """Decode Semantic Bit JSON structure to a Graphviz DOT string."""
    lines: List[str] = [f"digraph {graph_name} {{"]

    node_ids: Dict[str, str] = {}
    next_id = 1

    def get_node_id(label: str) -> str:
        nonlocal next_id
        if label not in node_ids:
            node_id = f"p{next_id}"
            next_id += 1
            node_ids[label] = node_id
            # Quote label; escape quotes
            safe_label = label.replace('"', '\\"')
            lines.append(f'  {node_id} [label="{safe_label}"];')
        return node_ids[label]

    for entry in sb.get("sentences", []):
        p1 = entry.get("point1", "")
        l1 = entry.get("line1", "")
        p2 = entry.get("point2", "")
        if not p1 or not p2 or not l1:
            continue
        a = get_node_id(p1)
        b = get_node_id(p2)
        safe_edge = l1.replace('"', '\\"')
        lines.append(f'  {a} -> {b} [label="{safe_edge}"];')

    lines.append("}")
    return "\n".join(lines)
