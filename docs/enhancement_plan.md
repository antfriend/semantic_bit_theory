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
    1. Text can be JSON serialized (no invalid characters)
    2. Text length is below character limit
    3. Text contains at least one valid sentence

    Returns:
        (is_valid, error_message)
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

// ENHANCED (Flexible)
{
  "sentences": [
    // Pattern 1: Point only
    {
      "type": "point",
      "content": "A cactus"
    },

    // Pattern 2: Line only
    {
      "type": "line",
      "content": "What is"
    },

    // Pattern 3: Point-Line-Point (classic)
    {
      "type": "triple",
      "point1": "The cat",
      "line1": "is sitting on",
      "point2": "the mat"
    },

    // Pattern 4: Line-Point
    {
      "type": "line-point",
      "line": "What is",
      "point": "a cactus"
    },

    // Pattern 5: Point-Line
    {
      "type": "point-line",
      "point": "The dog",
      "line": "barks"
    }
  ]
}
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
  "content": "Interesting."
}
```

**Rationale**:
- Points represent static concepts/states
- When in doubt, treat utterance as a conceptual declaration
- Aligns with "particle" in particle/wave duality (discrete snapshot)

---

## Enhancement 5: Article Detection Rules

### Rule
**If "a", "an", or "the" precedes a word → that word is part of a noun/Point clause**

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
2. For each Point, check if content matches asset label
3. Add asset reference to matching Points
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
  "sentences": [
    {
      "type": "triple",
      "point1": {
        "content": "The cactus",
        "asset": {"url": "https://wiki.org/cactus", "label": "cactus"}
      },
      "line1": "grows in",
      "point2": {
        "content": "desert",
        "asset": {"url": "https://wiki.org/desert", "label": "desert"}
      }
    }
  ]
}
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
2. For each Line, check if content semantically matches function description
3. Add function reference to matching Lines
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
  "sentences": [
    {
      "type": "triple",
      "point1": "The system",
      "line1": {
        "content": "calculates",
        "function": {
          "name": "calculate_distance",
          "description": "calculates distance"
        }
      },
      "point2": "distance"
    }
  ]
}
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

### Phase 1: Core Enhancements
- [ ] Add `original_text` field to semantic structures
- [ ] Implement `validate_text_for_encoding()` method
- [ ] Update JSON schema to support flexible patterns (type field)
- [ ] Modify parsing logic to detect and create non-triple patterns
- [ ] Implement "ambiguous → Point" fallback logic
- [ ] Enhance article detection in Point boundary identification

### Phase 2: Pattern Detection
- [ ] Add logic to detect Line-first sentences (questions)
- [ ] Create pattern classification system (point, line, point-line, line-point, triple)
- [ ] Update tests to cover all new pattern types

### Phase 3: External Mapping
- [ ] Implement `map_assets_to_points()` method
- [ ] Implement `map_functions_to_lines()` method
- [ ] Add optional asset/function fields to output schema
- [ ] Create matching logic (exact match, fuzzy match, semantic similarity)

### Phase 4: Testing & Documentation
- [ ] Write comprehensive tests for each pattern type
- [ ] Test validation edge cases
- [ ] Test asset and function mapping
- [ ] Update API documentation
- [ ] Create migration guide for existing code

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

*This plan preserves the core insights of Semantic Bit Theory while making the implementation more adaptive, robust, and practical for real-world applications.*
