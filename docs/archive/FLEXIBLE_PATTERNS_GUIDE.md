# Flexible Semantic Patterns - Quick Reference Guide

## Understanding the Shift from Rigid Triples

### The Original Requirement
> "SB JSON is not required to always be triples in a Point, Line, Point pattern.
> A whole sentence can be a single concept Point, or a single Line, or any
> combination of points and lines."

---

## My Interpretation

The current implementation **forces** every sentence into a Point₁-Line-Point₂ structure. This is **too restrictive** because:

1. **Not all meaning has three components**
   - "A cactus." is just a concept (Point only)
   - "What is?" is just a question (Line only)
   - Some sentences naturally have 2 components, not 3

2. **Semantic Bit Theory uses dual axes**, not rigid triples:
   - Noun/Verb distinction
   - Object/Predicate distinction
   - Particle/Wave distinction
   - Person/Feeling distinction

   → These suggest **flexibility**, not rigid structure!

3. **Real language varies in complexity**
   - Simple declarations → Points
   - Pure actions/questions → Lines
   - Subject-verb sentences → Point-Line
   - Questions → Line-Point
   - Full propositions → Point-Line-Point

---

## The Six Core Patterns

### Pattern 1: POINT ONLY
**Use When**: Sentence is a static concept, entity, or state

```
Input: "A cactus."
Output: {
  "type": "point",
  "content": "A cactus"
}
```

**Examples**:
- "Water."
- "The desert."
- "A beautiful sunset."
- "Interesting."

**Theoretical Alignment**:
- Pure noun/object
- Particle (discrete concept)
- Static entity

---

### Pattern 2: LINE ONLY
**Use When**: Sentence is a pure action, relationship, or question

```
Input: "What is?"
Output: {
  "type": "line",
  "content": "What is"
}
```

**Examples**:
- "Go!"
- "Stop."
- "Running."
- "Why?"

**Theoretical Alignment**:
- Pure verb/predicate
- Wave (action/process)
- Dynamic relationship

---

### Pattern 3: LINE → POINT
**Use When**: Sentence is action/question followed by object

```
Input: "What is a cactus?"
Output: {
  "type": "line-point",
  "line": "What is",
  "point": "a cactus"
}
```

**Examples**:
- "Consider this scenario."
- "Examine the evidence."
- "Where is the car?"
- "Fetch data."

**Theoretical Alignment**:
- Action → Object
- Predicate → Noun
- Common in interrogative and imperative sentences

**Special Case**: Questions often start with a Line!
- "What is" → asking for definition (predicate/relationship)
- "a cactus" → the concept being questioned (object/entity)

---

### Pattern 4: POINT → LINE
**Use When**: Sentence is subject followed by action (no object)

```
Input: "The dog barks."
Output: {
  "type": "point-line",
  "point": "The dog",
  "line": "barks"
}
```

**Examples**:
- "Water flows."
- "The sun rises."
- "Babies cry."
- "Time passes."

**Theoretical Alignment**:
- Noun → Verb
- Object → Action
- Common in intransitive sentences

---

### Pattern 5: POINT → LINE → POINT (Classic Triple)
**Use When**: Sentence has clear subject, action, and object

```
Input: "The cat is sitting on the mat."
Output: {
  "type": "triple",
  "point1": "The cat",
  "line1": "is sitting on",
  "point2": "the mat"
}
```

**Examples**:
- "Alice loves Bob."
- "The scientist studies quantum mechanics."
- "Water covers the Earth."

**Theoretical Alignment**:
- Complete semantic relationship
- Subject-Predicate-Object
- Traditional SBT representation

**Note**: This pattern is **still fully supported** – we're not removing it, just making it optional!

---

### Pattern 6: POINT → POINT (Apposition/Identity)
**Use When**: Sentence equates two concepts without explicit verb

```
Input: "My friend, a talented artist."
Output: {
  "type": "point-point",
  "point1": "My friend",
  "point2": "a talented artist"
}
```

**Examples**:
- "The winner: Team Blue."
- "Result: success."
- "The capital, Paris."

**Theoretical Alignment**:
- Identity relationship
- Two entities/concepts in apposition
- Implicit "is" or "equals"

---

## Decision Tree: Which Pattern to Use?

```
Start with sentence
    ↓
Does it have a clear verb/action?
    ↓ NO → Is it a concept/entity? → YES → POINT ONLY
    ↓ YES
    ↓
Does it have a subject (before the verb)?
    ↓ NO → Does it have an object (after)?
           ↓ YES → LINE → POINT
           ↓ NO  → LINE ONLY
    ↓ YES
    ↓
Does it have an object (after the verb)?
    ↓ NO  → POINT → LINE
    ↓ YES → POINT → LINE → POINT (classic triple)
    ↓
Special case: Two entities without verb?
    → POINT → POINT
    ↓
Cannot determine structure?
    → DEFAULT TO POINT (ambiguous sentence rule)
```

---

## Default Rule for Ambiguous Cases

**Rule**: If sentence type is ambiguous or cannot be determined → **POINT**

**Rationale**:
- Points represent static concepts/states
- When in doubt, treat as conceptual declaration
- Aligns with "particle" in particle/wave duality (discrete snapshot)

**Examples**:
- "Hmm."
- "Perhaps..."
- "Well, yes and no."
- "It depends."

All become:
```json
{
  "type": "point",
  "content": "Hmm."
}
```

---

## Implementation Strategy

### Current Code Flow (Rigid)
```python
# Current: REQUIRES all three
point1 = extract_point1(tokens)
if not point1:
    return None  # REJECT

line1 = extract_line(tokens, ...)
if not line1:
    return None  # REJECT

point2 = extract_point2(tokens, ...)
if not point2:
    return None  # REJECT

return {"point1": point1, "line1": line1, "point2": point2}
```

### Enhanced Code Flow (Flexible)
```python
# Enhanced: Accept partial structures
point1 = extract_point1(tokens)
line1 = extract_line(tokens, ...)
point2 = extract_point2(tokens, ...)

# Classify pattern based on what we found
if point1 and line1 and point2:
    return {"type": "triple", "point1": point1, "line1": line1, "point2": point2}
elif line1 and point2:
    return {"type": "line-point", "line": line1, "point": point2}
elif point1 and line1:
    return {"type": "point-line", "point": point1, "line": line1}
elif point1 and point2:
    return {"type": "point-point", "point1": point1, "point2": point2}
elif point1:
    return {"type": "point", "content": point1}
elif line1:
    return {"type": "line", "content": line1}
else:
    # Ambiguous: default to Point with full sentence
    return {"type": "point", "content": original_sentence}
```

---

## Benefits of Flexible Patterns

### 1. **Wider Language Coverage**
- Simple sentences: "Water." → Point
- Commands: "Go!" → Line
- Questions: "What is X?" → Line-Point
- Intransitive: "Dog barks." → Point-Line
- Transitive: "Cat chases mouse." → Point-Line-Point

### 2. **Theory Alignment**
- Respects dual axes (noun/verb, object/predicate)
- Doesn't force artificial structure
- Acknowledges varying semantic complexity

### 3. **Natural Representation**
- Matches how humans conceptualize meaning
- Some thoughts ARE just concepts (Points)
- Some thoughts ARE just actions (Lines)
- Some thoughts ARE complex relationships (Triples)

### 4. **Graceful Degradation**
- No more rejected sentences
- Every sentence gets SOME representation
- Ambiguous defaults to Point

---

## Example Transformations

| Sentence | Current | Enhanced |
|----------|---------|----------|
| "A cactus." | ❌ Rejected | ✅ `{"type": "point", "content": "A cactus"}` |
| "What is a cactus?" | ❌ Rejected or malformed | ✅ `{"type": "line-point", "line": "What is", "point": "a cactus"}` |
| "The dog barks." | ❌ Rejected (no object) | ✅ `{"type": "point-line", "point": "The dog", "line": "barks"}` |
| "Run!" | ❌ Rejected | ✅ `{"type": "line", "content": "Run"}` |
| "The cat sits on the mat." | ✅ Triple | ✅ Triple (still supported!) |

---

## Compatibility with Enhancements 7 & 8

### Assets map to Points (regardless of pattern)
```json
// Pattern: Point only
{
  "type": "point",
  "content": "cactus",
  "asset": {"url": "...", "label": "cactus"}
}

// Pattern: Line-Point (asset on Point)
{
  "type": "line-point",
  "line": "What is",
  "point": {
    "content": "a cactus",
    "asset": {"url": "...", "label": "cactus"}
  }
}
```

### Functions map to Lines (regardless of pattern)
```json
// Pattern: Line only
{
  "type": "line",
  "content": "calculate",
  "function": {"name": "calculate_distance", "description": "..."}
}

// Pattern: Point-Line (function on Line)
{
  "type": "point-line",
  "point": "The system",
  "line": {
    "content": "calculates",
    "function": {"name": "calculate_distance", "description": "..."}
  }
}
```

---

## Key Takeaway

**Flexible patterns respect the reality that meaning comes in different shapes:**
- Some meanings are static (Points)
- Some meanings are dynamic (Lines)
- Some meanings are relationships (Triples or combinations)

**We're not abandoning triples – we're making them optional when they're not natural.**

This aligns with the theoretical foundation: dual axes, not rigid structures!

---

*This guide provides the conceptual framework for implementing flexible semantic patterns in Semantic Bit Theory.*
