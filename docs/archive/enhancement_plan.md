# Semantic Bit Theory Enhancement Plan

## Overview

This document outlines a series of enhancements to make Semantic Bit Theory more flexible, robust, and extensible while preserving its core principles. The changes shift from rigid Point-Line-Point triples to a more adaptive semantic encoding system.

---

## Current Architecture

### Existing Triple Pattern (Rigid)

```
Current Requirement: ALWAYS Point₁ → Line → Point₂

Example: "The cat is sitting on the mat."
┌─────────┐      ┌──────────────┐      ┌─────────┐
│ The cat │ ───→ │ is sitting on│ ───→ │ the mat │
│ Point₁  │      │    Line      │      │ Point₂  │
└─────────┘      └──────────────┘      └─────────┘
```

**Limitation**: Every sentence must fit this pattern, or it's rejected.

![Pattern Comparison](images/pattern_comparison.png)
*Figure 1: Comparison between current rigid triple pattern and enhanced flexible patterns*

---

## Enhancement 1: Preserve Original Text & Punctuation

### Current Behavior
- Tokens are extracted and normalized
- Original spacing and punctuation context may be lost
- Cannot reliably reconstruct the original sentence

### Proposed Enhancement
**Preserve complete original text at the sentence level**

```python
# Current Output
{
  "sentences": [
    {"point1": "The cat", "line1": "is sitting on", "point2": "the mat"}
  ]
}

# Enhanced Output (with original_text field)
{
  "sentences": [
    {
      "point1": "The cat",
      "line1": "is sitting on",
      "point2": "the mat",
      "original_text": "The cat is sitting on the mat."
    }
  ]
}
```

**Benefit**: Consuming applications can:
- Display the complete, unmodified text
- Highlight semantic segments within original context
- Preserve authorial intent and formatting

**Implementation**:
- Add `original_text: str` field to `SBTriple` dataclass
- Capture full sentence before tokenization
- Include in JSON output schema

---

## Enhancement 2: Add Pre-Encoding Validation

### Purpose
Ensure content can be successfully encoded BEFORE processing

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Input Text  │ ──→ │  Validate    │ ──→ │  Encode to  │
│             │     │  - JSON safe │     │  SB JSON    │
│             │     │  - Size OK   │     │             │
└─────────────┘     └──────────────┘     └─────────────┘
                            │
                            ↓ FAIL
                    ┌──────────────┐
                    │  Return      │
                    │  Error Info  │
                    └──────────────┘
```

![Validation Flow](images/validation_flow.png)
*Figure 2: Complete enhanced processing pipeline with validation*

### Validation Method

```python
def validate_text_for_encoding(text: str, max_chars: int = 10000) -> Tuple[bool, Optional[str]]:
    """
    Validate that text can be successfully encoded to SB JSON.

    Checks:
    1. Text length is below character limit
    2. Text contains at least one sentence after segmentation
    3. At least one sentence can produce a valid pattern

    Returns:
        (is_valid, error_message)

    Note: Python strings are inherently JSON-safe, no serialization check needed.
    """
```

**Guarantees**:
- If validation passes → SB processing will return valid JSON
- If validation fails → Clear error message explaining why
- No partial failures or encoding errors during processing

---

## Enhancement 3: Flexible Semantic Patterns

### The Core Conceptual Shift

**Current**: Every sentence MUST be `Point → Line → Point`

**Enhanced**: Semantic bits can be:
- **Pure Point**: Static concept, entity, state (noun-like)
- **Pure Line**: Dynamic action, relationship, process (verb-like)
- **Hybrid Patterns**: Any meaningful combination

### Visual Representation

```
┌─────────────────────────────────────────────────────────────┐
│  FLEXIBLE SEMANTIC BIT PATTERNS                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Pattern 1: POINT ONLY (Static Concept)                    │
│  ┌──────────────────────┐                                  │
│  │   "A cactus."        │  ← Whole sentence = one concept  │
│  │   Point              │                                  │
│  └──────────────────────┘                                  │
│                                                             │
│  Pattern 2: LINE ONLY (Pure Action/Question)               │
│  ┌──────────────────────┐                                  │
│  │   "What is?"         │  ← Whole sentence = relationship │
│  │   Line               │                                  │
│  └──────────────────────┘                                  │
│                                                             │
│  Pattern 3: LINE → POINT (Action-to-Object)                │
│  ┌─────────┐      ┌──────────┐                            │
│  │ What is │ ───→ │ a cactus │                            │
│  │  Line   │      │  Point   │                            │
│  └─────────┘      └──────────┘                            │
│                                                             │
│  Pattern 4: POINT → LINE (Subject-Action)                  │
│  ┌─────────┐      ┌─────────┐                             │
│  │ The dog │ ───→ │  barks  │                             │
│  │  Point  │      │  Line   │                             │
│  └─────────┘      └─────────┘                             │
│                                                             │
│  Pattern 5: POINT → LINE → POINT (Classic Triple)          │
│  ┌─────────┐      ┌──────────┐      ┌─────────┐          │
│  │ The cat │ ───→ │ sits on  │ ───→ │ the mat │          │
│  │ Point₁  │      │   Line   │      │ Point₂  │          │
│  └─────────┘      └──────────┘      └─────────┘          │
│                                                             │
│  Pattern 6: POINT → POINT (Apposition/Identity)            │
│  ┌─────────────┐      ┌──────────────────┐               │
│  │ My friend   │ ───→ │ a talented artist│               │
│  │   Point₁    │      │     Point₂       │               │
│  └─────────────┘      └──────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### My Interpretation

The requirement "SB JSON is not required to always be triples in a Point, Line, Point pattern" means:

**Theoretical Alignment**:
- Semantic Bit Theory uses dual axes (noun/verb, object/predicate, particle/wave, person/feeling)
- NOT every piece of meaning requires all components
- Some meanings are inherently static (Points) or dynamic (Lines)

**Practical Implementation**:
- A sentence might be a pure declaration → Point only
- A sentence might be a pure question/action → Line only
- Traditional subject-verb-object → Point-Line-Point
- Questions often start with Lines: "What is" + "a cactus" = Line + Point

**JSON Schema Changes**:

```javascript
// CURRENT (Rigid)
{
  "sentences": [
    {
      "point1": "required",
      "line1": "required",
      "point2": "required"
    }
  ]
}

// ENHANCED (Flexible) - Always-Object Structure
{
  "version": "2.0",
  "sentences": [
    // Pattern 1: Point only
    {
      "type": "point",
      "content": {
        "content": "A cactus"
      },
      "original_text": "A cactus."
    },

    // Pattern 2: Line only
    {
      "type": "line",
      "content": {
        "content": "What is"
      },
      "original_text": "What is?"
    },

    // Pattern 3: Point-Line-Point (classic)
    {
      "type": "triple",
      "point1": {
        "content": "The cat"
      },
      "line1": {
        "content": "is sitting on"
      },
      "point2": {
        "content": "the mat"
      },
      "original_text": "The cat is sitting on the mat."
    },

    // Pattern 4: Line-Point
    {
      "type": "line-point",
      "line": {
        "content": "What is"
      },
      "point": {
        "content": "a cactus"
      },
      "original_text": "What is a cactus?"
    },

    // Pattern 5: Point-Line
    {
      "type": "point-line",
      "point": {
        "content": "The dog"
      },
      "line": {
        "content": "barks"
      },
      "original_text": "The dog barks."
    }
  ]
}

Note: Points and Lines are ALWAYS objects with "content" field.
Assets/functions are optional and only appear when mappings exist.
```

---

## Enhancement 4: Ambiguous Sentence Handling

### Rule
**If sentence type is ambiguous or cannot be determined → classify as Point**

```
┌──────────────────┐
│ "Interesting."   │ → Cannot determine structure
└──────────────────┘
         ↓
    ┌────────┐
    │ Point  │ ← Default classification
    └────────┘

JSON Output:
{
  "type": "point",
  "content": {
    "content": "Interesting."
  },
  "original_text": "Interesting."
}
```

**Rationale**:
- Points represent static concepts/states
- When in doubt, treat utterance as a conceptual declaration
- Aligns with "particle" in particle/wave duality (discrete snapshot)

**Design Decision**: We considered adding a "fragment" type for truly ambiguous cases, but opted to keep the simpler default-to-point approach. This maintains theoretical consistency and avoids adding complexity for consumers who would need to handle an additional type with unclear semantics.

---

## Enhancement 5: Article Detection Rules

### Rule
**If "a", "an", or "the" precedes a word → that word is part of a noun/Point clause**

**Scope**: This is an **English-specific heuristic**. Article-based detection will not work for other languages (e.g., Chinese, Japanese, Russian). Version 2.0 is explicitly scoped for English text.

```
Visual Detection Pattern:

"The cat is on the mat"
 ↑       ↑       ↑
 │       │       └── "the" → "mat" is part of Point₂
 │       └────────── "is on" = Line (no article)
 └────────────────── "The" → "cat" is part of Point₁

Result:
Point₁: "The cat"
Line:   "is on"
Point₂: "the mat"
```

### Implementation Logic

```python
def starts_with_article(tokens: List[Token], start_idx: int) -> bool:
    """Check if token sequence at start_idx begins with article."""
    if start_idx >= len(tokens):
        return False
    return tokens[start_idx].normalized in {"a", "an", "the"}

# Use this to detect Point boundaries during parsing
```

![Article Detection](images/article_detection.png)
*Figure 4: Article detection mechanism for identifying Point boundaries*

---

## Enhancement 6: Sentences Can Begin with Lines

### Example: "What is a cactus?"

```
Traditional Parsing (WRONG):
┌─────────┐      ┌────┐      ┌──────────┐
│  What   │      │ is │      │ a cactus │
│ Point?  │      │Line│      │  Point?  │
└─────────┘      └────┘      └──────────┘
         ❌ Doesn't capture question structure

Correct Parsing (Line-first):
┌─────────────┐      ┌──────────┐
│   What is   │ ───→ │ a cactus │
│    Line     │      │  Point   │
└─────────────┘      └──────────┘
         ✓ Captures interrogative relationship

"What is" = asking for definition (Line/predicate)
"a cactus" = the concept being questioned (Point/object)
```

### Question Starters as Lines

```
Common question patterns that are Lines:
- "What is"
- "Who are"
- "Where does"
- "When did"
- "Why would"
- "How can"

Detection: Sentence starts with WH-word or auxiliary verb
         → Initial segment likely forms a Line
```

---

## Enhancement 7: Named Assets Mapping

### Purpose
Link Points to external resources (images, documents, entities)

### Structure

```
Named Asset = {
  "url": "https://example.com/image.png",
  "label": "cactus"
}

Mapping Process:
1. Identify all Points in SB JSON
2. For each Point, tokenize content and asset labels
3. Match using token-based exact word matching (case/punctuation insensitive)
4. Add all matching assets to Points (array of matches)

Matching Strategy (Approved):
- Token-based: Extract words from both Point content and asset labels
- Normalize using Unicode NFKC + casefold() for case-insensitivity
- Exact word match: "cactus" in "The cactus plant" ✓
- Not substring: "cat" does NOT match "catch" ✓
- Multiple matches: Return all matching assets as an array

Future Optimization: Pre-index assets by normalized token sequences for O(n + m) performance
```

### Visual Example

```
Input SB JSON:
{
  "sentences": [
    {"type": "triple", "point1": "The cactus", "line1": "grows in", "point2": "desert"}
  ]
}

Named Assets:
[
  {"url": "https://wiki.org/cactus", "label": "cactus"},
  {"url": "https://wiki.org/desert", "label": "desert"}
]

Enhanced Output:
{
  "version": "2.0",
  "sentences": [
    {
      "type": "triple",
      "point1": {
        "content": "The cactus",
        "assets": [
          {"url": "https://wiki.org/cactus", "label": "cactus"}
        ]
      },
      "line1": {
        "content": "grows in"
      },
      "point2": {
        "content": "desert",
        "assets": [
          {"url": "https://wiki.org/desert", "label": "desert"}
        ]
      },
      "original_text": "The cactus grows in desert."
    }
  ]
}

Note: Assets field only appears when there are matches (optional presence)
```

### Method Signature

```python
def map_assets_to_points(
    sb_json: Dict,
    assets: List[Dict[str, str]]
) -> Dict:
    """
    Map named assets to Points with matching content.

    Args:
        sb_json: Semantic Bit JSON structure
        assets: List of {"url": str, "label": str} dictionaries

    Returns:
        Enhanced SB JSON with asset references in Points
    """
```

### Use Cases
- Link entities to knowledge base articles
- Attach images to visual concepts
- Connect narrative elements to multimedia resources
- Enable rich, hyperlinked semantic graphs

![Asset and Function Mapping](images/asset_function_mapping.png)
*Figure 3: Visual representation of asset mapping to Points and function mapping to Lines*

---

## Enhancement 8: Named Functions Mapping

### Purpose
Link Lines to executable functions or API endpoints

### Structure

```
Named Function = {
  "name": "calculate_distance",  // Valid function name (no spaces)
  "description": "calculates distance between two points"
}

Mapping Process:
1. Identify all Lines in SB JSON
2. For each Line, tokenize content and function descriptions
3. Match using token-based exact word matching (case/punctuation insensitive)
4. Add all matching functions to Lines (array of matches)

Matching Strategy (Same as Assets):
- Token-based: Extract words from both Line content and function descriptions
- Normalize using Unicode NFKC + casefold() for case-insensitivity
- Exact word match: "calculates" matches "calculates distance" ✓
- Not substring: "calc" does NOT match "calculates" ✓
- Multiple matches: Return all matching functions as an array

Future Optimization: Pre-index functions by normalized token sequences
```

### Visual Example

```
Input SB JSON:
{
  "sentences": [
    {"type": "triple", "point1": "The system", "line1": "calculates", "point2": "distance"}
  ]
}

Named Functions:
[
  {
    "name": "calculate_distance",
    "description": "calculates distance"
  },
  {
    "name": "fetch_data",
    "description": "retrieves data"
  }
]

Enhanced Output:
{
  "version": "2.0",
  "sentences": [
    {
      "type": "triple",
      "point1": {
        "content": "The system"
      },
      "line1": {
        "content": "calculates",
        "functions": [
          {
            "name": "calculate_distance",
            "description": "calculates distance"
          }
        ]
      },
      "point2": {
        "content": "distance"
      },
      "original_text": "The system calculates distance."
    }
  ]
}

Note: Functions field only appears when there are matches (optional presence)
```

### Method Signature

```python
def map_functions_to_lines(
    sb_json: Dict,
    functions: List[Dict[str, str]]
) -> Dict:
    """
    Map named functions to Lines with matching content.

    Args:
        sb_json: Semantic Bit JSON structure
        functions: List of {"name": str, "description": str} dictionaries
                  (name must be valid identifier, no spaces)

    Returns:
        Enhanced SB JSON with function references in Lines
    """
```

### Use Cases
- Map natural language to API calls
- Link narrative actions to code execution
- Enable executable semantic graphs
- Build natural language programming interfaces

---

## Summary Diagram: Complete Enhancement Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ENHANCED SB PROCESSING PIPELINE                  │
└─────────────────────────────────────────────────────────────────────┘

1. VALIDATION PHASE
   ┌──────────────┐
   │  Input Text  │
   └──────┬───────┘
          ↓
   ┌──────────────────┐
   │ validate_text_   │ → FAIL? Return error
   │ for_encoding()   │
   └──────┬───────────┘
          ↓ PASS

2. ENCODING PHASE (Flexible Patterns)
   ┌───────────────────────────────────────────┐
   │ Sentence Analysis:                        │
   │ • Preserve original_text                  │
   │ • Detect articles ("a", "an", "the")      │
   │ • Allow Line-first patterns               │
   │ • Support Point-only, Line-only patterns  │
   │ • Default ambiguous → Point               │
   └───────────────┬───────────────────────────┘
                   ↓
   ┌───────────────────────────┐
   │ Generate Flexible SB JSON │
   │ (not always triples)      │
   └───────────┬───────────────┘
               ↓

3. ENRICHMENT PHASE
   ┌─────────────────────┐
   │ map_assets_to_      │ → Add URLs/labels to Points
   │ points()            │
   └──────┬──────────────┘
          ↓
   ┌─────────────────────┐
   │ map_functions_to_   │ → Add function refs to Lines
   │ lines()             │
   └──────┬──────────────┘
          ↓

4. OUTPUT
   ┌─────────────────────────────────────┐
   │ Rich, Flexible, Validated SB JSON   │
   │ • Original text preserved           │
   │ • Flexible semantic patterns        │
   │ • Linked to external resources      │
   │ • Executable via function mappings  │
   └─────────────────────────────────────┘
```

---

## Implementation Checklist

### Phase 0: Refactoring & Scaffolding (0.5 week)
- [ ] Split semantic.py into modular structure (core/, enrichment/)
- [ ] Create new data structure classes with polymorphic union approach
- [ ] Define JSON Schema v2.0 skeleton with oneOf patterns
- [ ] Set up test harness patterns for new features
- [ ] Maintain semantic.py as public API facade

### Phase 1: Core Enhancements (1 week)
- [ ] Add `original_text` field to all sentence structures
- [ ] Implement always-object structure for Points/Lines
- [ ] Implement `validate_text_for_encoding()` method (moderate level)
- [ ] Update JSON schema to support `version` field
- [ ] Enhance article detection with English-only scope
- [ ] Add backward compatibility mode parameter

### Phase 2: Pattern Detection (1.5 weeks)
- [ ] Implement rule-based decision tree for pattern classification
- [ ] Add logic to detect Line-first sentences (questions)
- [ ] Create pattern classification for all 6 types
- [ ] Implement "ambiguous → Point" fallback logic
- [ ] Update tests to cover all pattern types
- [ ] Add determinism tests (same input = same output)

### Phase 3: External Mapping (1 week)
- [ ] Implement token-based matching with Unicode normalization (NFKC + casefold)
- [ ] Implement `map_assets_to_points()` method
- [ ] Implement `map_functions_to_lines()` method
- [ ] Add optional assets/functions fields (only when matches exist)
- [ ] Return all matches as arrays
- [ ] Document pre-indexing as future optimization

### Phase 4: Testing & Documentation (1 week)
- [ ] Write 12-20 curated test cases per pattern type
- [ ] Create 100-200 sentence edge-case corpus
- [ ] Test validation edge cases
- [ ] Test asset and function mapping with edge cases
- [ ] JSON Schema validation tests
- [ ] Update API documentation
- [ ] Document migration considerations (v1 → v2 limitations)

---

## Backward Compatibility Strategy

### Option A: Dual Output Modes
```python
encode_text_to_sb(text, mode="flexible")  # New default
encode_text_to_sb(text, mode="classic")   # Old triple-only behavior
```

### Option B: Version Field
```json
{
  "version": "2.0",
  "sentences": [...]
}
```

### Recommendation
Use **Option B** with automatic detection:
- If output contains only classic triples → version 1.0 format
- If output uses new patterns → version 2.0 format
- Consumers check version field to handle appropriately

---

## Questions for Clarification

1. **Character limit for validation**: What should `max_chars` be? (Suggested: 10,000)

2. **Asset/Function matching**: Should we support:
   - Exact string match only?
   - Fuzzy matching (e.g., "cactus" matches "the cactus")?
   - Semantic similarity?

3. **Type field naming**: For flexible patterns, should we use:
   - `"type": "point" | "line" | "triple" | "point-line" | "line-point"`?
   - Or a different naming scheme?

4. **Multiple matches**: If a Point matches multiple assets, include all or first match?

---

## Expected Benefits

✅ **Flexibility**: Handle wider variety of sentence structures
✅ **Robustness**: Validation prevents encoding failures
✅ **Richness**: External links add context and functionality
✅ **Fidelity**: Original text preservation maintains authorial intent
✅ **Usability**: Clear patterns for different semantic situations
✅ **Extensibility**: Asset/function mapping enables advanced applications

---

## Codex Review & Approved Refinements

**Review Date**: 2025-10-26

### Key Improvements from Codex Review:

1. **Always-Object Structure** ✅ ADOPTED
   - Points and Lines are always objects with `"content"` field
   - Prevents mixed string/object typing issues for consumers
   - Assets/functions fields remain optional (only when matches exist)

2. **Token-Based Matching** ✅ ADOPTED
   - Use word tokenization, not substring matching
   - Unicode normalization (NFKC + casefold) for robustness
   - Prevents "cat" from matching "catch"

3. **JSON Schema Correction** ✅ ADOPTED
   - Use `oneOf` with `type` as discriminator
   - JSON Schema 2020-12 does not standardize "discriminator" (OpenAPI concept)

4. **Validation Simplification** ✅ ADOPTED
   - Remove redundant "JSON serializable" check for Python strings
   - Focus on length, segmentation, and pattern extractability

5. **Phase 0 Addition** ✅ ADOPTED
   - Add 0.5 week refactoring phase before feature implementation
   - Allocate more time to pattern detection (1.5 weeks)

6. **English-Only Scope** ✅ ADOPTED
   - Article detection is English-specific heuristic
   - Clearly document language scope limitations

### Rejected Suggestions:

1. **Fragment/Unknown Type** ❌ REJECTED
   - Keeps system simpler, default-to-point aligns with theory
   - Avoids extra complexity for consumers

2. **Confidence Scores** ❌ REJECTED
   - No clear way to calculate without ML dependencies
   - Would complicate output without strong use case

3. **Hypothesis Testing** ❌ REJECTED
   - Violates zero-dependency constraint
   - Can write excellent tests with stdlib only

4. **Structured ValidationResult** ❌ REJECTED
   - YAGNI - simple tuple is sufficient for v2.0
   - Can add later if needed

5. **Strict/Lenient Modes** ❌ REJECTED
   - Unnecessary complexity without clear use case

---

*This plan preserves the core insights of Semantic Bit Theory while making the implementation more adaptive, robust, and practical for real-world applications.*
