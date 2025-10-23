"""Semantic Bit Theory - Core Processing Module

This module implements the foundational components of Semantic Bit Theory (SBT),
providing lightweight, dependency-free semantic parsing and graph generation.

Core Functions:
- encode_text_to_sb(): Convert natural language text into Point-Line-Point triples
- decode_sb_to_dot(): Transform semantic triples into Graphviz DOT graphs

The implementation follows a three-phase linguistic analysis:
1. Sentence Segmentation: Split text at sentence boundaries
2. Lexical Analysis: Tokenize while preserving surface forms  
3. Syntactic Role Assignment: Extract Point₁, Line, Point₂ using heuristics

Design Philosophy:
- High precision over high recall (conservative extraction)
- Zero external dependencies for maximum portability
- Graceful degradation when sentences don't match expected patterns
- Transparent, interpretable processing pipeline

Example:
    "The cat is sitting on the mat." → 
    {"point1": "The cat", "line1": "is sitting on", "point2": "the mat"}
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple, Optional
import re

# =============================================================================
# Linguistic Pattern Definitions
# =============================================================================

# Tokenization pattern: words including contractions and possessives
_WORD_PATTERN = re.compile(r"\b[\w']+\b")

# Sentence boundary pattern: split on .!? followed by whitespace or end of text
_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")

# Auxiliary verbs: core structural elements indicating verb phrases
_AUXILIARY_VERBS = {
    # Primary auxiliaries
    "am", "is", "are", "was", "were", "be", "been", "being",
    # Perfect auxiliaries  
    "have", "has", "had",
    # Do-support auxiliaries
    "do", "does", "did",
    # Modal auxiliaries
    "can", "could", "will", "would", "shall", "should", 
    "may", "might", "must", "ought",
}

# Prepositions that commonly attach to verb phrases
_VERBAL_PREPOSITIONS = {
    # Spatial prepositions
    "on", "in", "at", "over", "under", "above", "below", "beside",
    "through", "across", "around", "into", "onto", "upon",
    # Directional prepositions
    "to", "from", "toward", "towards", "away",
    # Temporal prepositions  
    "during", "before", "after", "since", "until",
    # Abstract prepositions
    "with", "without", "by", "for", "of", "about", "against",
}

# Determiners: help identify noun phrase boundaries
_DETERMINERS = {
    # Articles
    "the", "a", "an",
    # Demonstratives
    "this", "that", "these", "those",
    # Possessives
    "my", "your", "his", "her", "its", "our", "their",
    # Quantifiers (basic)
    "some", "any", "many", "few", "several", "all", "no",
}


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class Token:
    """Represents a single lexical token with its surface form and normalized form."""
    text: str          # Original surface form (preserves casing, punctuation)
    normalized: str    # Lowercased form for linguistic analysis
    
    def __post_init__(self) -> None:
        """Ensure normalized form is properly lowercased."""
        self.normalized = self.text.lower()


@dataclass  
class SBTriple:
    """Represents a semantic triple: Point₁ ← Line → Point₂"""
    point1: str  # Subject entity or concept
    line1: str   # Relationship, action, or semantic connector
    point2: str  # Object entity or target concept
    
    def to_dict(self) -> Dict[str, str]:
        """Convert triple to dictionary format for JSON serialization."""
        return {
            "point1": self.point1,
            "line1": self.line1, 
            "point2": self.point2
        }
    
    def is_valid(self) -> bool:
        """Check if triple contains non-empty components."""
        return bool(self.point1.strip() and self.line1.strip() and self.point2.strip())


@dataclass
class SemanticBitDocument:
    """Container for multiple semantic triples extracted from text."""
    sentences: List[SBTriple]
    
    def to_dict(self) -> Dict[str, List[Dict[str, str]]]:
        """Convert document to dictionary format for JSON serialization.""" 
        return {
            "sentences": [triple.to_dict() for triple in self.sentences if triple.is_valid()]
        }
    
    def add_triple(self, triple: SBTriple) -> None:
        """Add a triple to the document if it's valid."""
        if triple.is_valid():
            self.sentences.append(triple)


# =============================================================================
# Phase 1: Sentence Segmentation 
# =============================================================================

def segment_sentences(text: str) -> List[str]:
    """Split text into discrete sentences at punctuation boundaries.
    
    Uses sentence-ending punctuation (.!?) followed by whitespace or end-of-text
    as segmentation boundaries. Preserves sentence-level semantic scope.
    
    Args:
        text: Input text to segment
        
    Returns:
        List of sentence strings, stripped of leading/trailing whitespace
    """
    if not text or not text.strip():
        return []
    
    # Split on sentence boundaries and filter empty results
    sentences = _SENTENCE_BOUNDARY.split(text.strip())
    return [sentence.strip() for sentence in sentences if sentence.strip()]


# =============================================================================
# Phase 2: Lexical Analysis
# =============================================================================

def tokenize_sentence(sentence: str) -> List[Token]:
    """Convert a sentence into a sequence of tokens.
    
    Uses regex pattern matching to extract words while preserving:
    - Contractions (don't, won't, etc.)
    - Possessives (cat's, children's, etc.) 
    - Original surface form casing
    
    Args:
        sentence: Input sentence to tokenize
        
    Returns:
        List of Token objects with text and normalized forms
    """
    if not sentence or not sentence.strip():
        return []
        
    tokens = []
    for match in _WORD_PATTERN.finditer(sentence):
        word = match.group(0)
        tokens.append(Token(text=word, normalized=word.lower()))
    
    return tokens


# =============================================================================
# Phase 3: Syntactic Role Assignment
# =============================================================================

def is_verb_like(token: Token) -> bool:
    """Determine if a token exhibits verb-like characteristics.
    
    Uses both lexical lookup and morphological pattern matching to identify
    potential verb tokens that can anchor semantic relationships.
    
    Args:
        token: Token to analyze
        
    Returns:
        True if token appears to be verb-like, False otherwise
    """
    word = token.normalized
    
    # Direct auxiliary verb lookup
    if word in _AUXILIARY_VERBS:
        return True
    
    # Morphological verb indicators
    if word.endswith("ing") or word.endswith("ed"):
        return True
        
    # Additional common verb patterns
    if len(word) > 3 and word.endswith("s") and word[:-1] in _AUXILIARY_VERBS:
        return True  # handles "goes", "does", etc.
    
    return False


def extract_point1(tokens: List[Token], start_idx: int = 0) -> Tuple[str, int]:
    """Extract the initial noun phrase (Point₁) from token sequence.
    
    Collects tokens from start_idx until encountering a verb-like pattern,
    representing the subject entity or concept in the semantic relationship.
    
    Args:
        tokens: List of tokens to process
        start_idx: Starting position in token list
        
    Returns:
        Tuple of (extracted_phrase, next_index)
    """
    if start_idx >= len(tokens):
        return "", start_idx
    
    current_idx = start_idx
    phrase_tokens = []
    
    # Collect tokens until we hit a verb-like token
    while current_idx < len(tokens):
        token = tokens[current_idx]
        
        # Stop at obvious verb indicators (but only after collecting at least one token)
        if phrase_tokens and is_verb_like(token):
            break
            
        phrase_tokens.append(token.text)
        current_idx += 1
    
    phrase = " ".join(phrase_tokens).strip()
    return phrase, current_idx


def extract_line(tokens: List[Token], start_idx: int) -> Tuple[str, int]:
    """Extract the verb phrase with optional preposition (Line) from token sequence.
    
    Identifies the core relationship through verb phrase recognition, including
    auxiliary verbs and optionally attached prepositions for phrasal constructions.
    
    Args:
        tokens: List of tokens to process
        start_idx: Starting position in token list
        
    Returns:
        Tuple of (extracted_phrase, next_index)  
    """
    if start_idx >= len(tokens):
        return "", start_idx
    
    current_idx = start_idx
    phrase_tokens = []
    found_verb = False
    
    # First, collect all verb-like tokens
    while current_idx < len(tokens):
        token = tokens[current_idx]
        
        if is_verb_like(token):
            phrase_tokens.append(token.text)
            found_verb = True
            current_idx += 1
        elif found_verb:
            # After finding verbs, stop at non-verb tokens
            break
        else:
            # Haven't found a verb yet - this might be a determiner before object
            break
    
    # Optionally attach a single preposition
    if current_idx < len(tokens) and found_verb:
        next_token = tokens[current_idx]
        if next_token.normalized in _VERBAL_PREPOSITIONS:
            phrase_tokens.append(next_token.text)
            current_idx += 1
    
    phrase = " ".join(phrase_tokens).strip()
    return phrase, current_idx


def extract_point2(tokens: List[Token], start_idx: int) -> Tuple[str, int]:
    """Extract the remaining noun phrase (Point₂) from token sequence.
    
    Collects all remaining tokens as the object entity or target concept
    in the semantic relationship.
    
    Args:
        tokens: List of tokens to process
        start_idx: Starting position in token list
        
    Returns:
        Tuple of (extracted_phrase, next_index)
    """
    if start_idx >= len(tokens):
        return "", start_idx
    
    # Collect all remaining tokens as the object phrase
    phrase_tokens = [token.text for token in tokens[start_idx:]]
    phrase = " ".join(phrase_tokens).strip()
    
    return phrase, len(tokens)


# =============================================================================
# Main Encoding Function
# =============================================================================

def encode_text_to_sb(text: str) -> Dict[str, List[Dict[str, str]]]:
    """Encode natural language text into Semantic Bit triples.
    
    Implements the complete three-phase linguistic analysis pipeline:
    1. Sentence Segmentation: Split text at punctuation boundaries
    2. Lexical Analysis: Tokenize while preserving surface forms
    3. Syntactic Role Assignment: Extract Point₁, Line, Point₂ using heuristics
    
    Args:
        text: Input natural language text
        
    Returns:
        Dictionary with "sentences" key containing list of semantic triples.
        Each triple has "point1", "line1", "point2" string keys.
        
    Example:
        >>> encode_text_to_sb("The cat is sitting on the mat.")
        {"sentences": [{"point1": "The cat", "line1": "is sitting on", "point2": "the mat"}]}
    """
    if not text or not text.strip():
        return {"sentences": []}
    
    document = SemanticBitDocument(sentences=[])
    
    # Phase 1: Sentence Segmentation
    sentences = segment_sentences(text)
    
    for sentence in sentences:
        # Phase 2: Lexical Analysis
        tokens = tokenize_sentence(sentence)
        if not tokens:
            continue
        
        # Phase 3: Syntactic Role Assignment
        point1, line_start = extract_point1(tokens)
        if not point1:
            continue  # Skip sentences without clear subject
            
        line1, point2_start = extract_line(tokens, line_start)
        if not line1:
            continue  # Skip sentences without clear verb phrase
            
        point2, _ = extract_point2(tokens, point2_start)
        if not point2:
            continue  # Skip sentences without clear object
        
        # Create and validate triple
        triple = SBTriple(point1=point1, line1=line1, point2=point2)
        document.add_triple(triple)
    
    return document.to_dict()


# =============================================================================
# Graph Synthesis Pipeline  
# =============================================================================

def escape_dot_string(text: str) -> str:
    """Escape special characters for DOT format compliance.
    
    Ensures that node labels and edge labels are properly escaped
    to prevent DOT syntax errors.
    
    Args:
        text: Raw text to escape
        
    Returns:
        DOT-safe escaped string
    """
    if not text:
        return ""
    
    # Escape quotes and backslashes for DOT format
    escaped = text.replace('\\', '\\\\')  # Escape backslashes first
    escaped = escaped.replace('"', '\\"')  # Then escape quotes
    escaped = escaped.replace('\n', '\\n')  # Handle newlines
    escaped = escaped.replace('\t', '\\t')  # Handle tabs
    
    return escaped


def decode_sb_to_dot(sb: Dict[str, List[Dict[str, str]]], graph_name: str = "SBGraph") -> str:
    """Transform Semantic Bit triples into Graphviz DOT format.
    
    Implements the complete graph synthesis pipeline:
    - Node Consolidation: Deduplicate identical point labels
    - Edge Construction: Create directed relationships
    - Output Generation: Produce standards-compliant DOT
    
    Args:
        sb: Semantic Bit document dictionary with "sentences" key
        graph_name: Name for the generated graph (default: "SBGraph")
        
    Returns:
        Complete DOT format string ready for Graphviz processing
        
    Example:
        >>> sb = {"sentences": [{"point1": "The cat", "line1": "is sitting on", "point2": "the mat"}]}
        >>> decode_sb_to_dot(sb)
        'digraph SBGraph {\\n  p1 [label="The cat"];\\n  p2 [label="the mat"];\\n  p1 -> p2 [label="is sitting on"];\\n}'
    """
    if not sb or "sentences" not in sb:
        return f'digraph {graph_name} {{\n}}'
    
    dot_lines = [f'digraph {graph_name} {{']
    
    # Node consolidation: track unique point labels  
    node_registry: Dict[str, str] = {}
    node_counter = 1
    
    def get_or_create_node_id(point_label: str) -> str:
        """Get existing node ID or create new one for a point label."""
        nonlocal node_counter
        
        if point_label not in node_registry:
            # Create new node with systematic ID
            node_id = f"p{node_counter}"
            node_counter += 1
            node_registry[point_label] = node_id
            
            # Add node definition to DOT output
            safe_label = escape_dot_string(point_label)
            dot_lines.append(f'  {node_id} [label="{safe_label}"];')
        
        return node_registry[point_label]
    
    # Edge construction: process all semantic triples
    for triple_dict in sb.get("sentences", []):
        point1 = triple_dict.get("point1", "").strip()
        line1 = triple_dict.get("line1", "").strip()  
        point2 = triple_dict.get("point2", "").strip()
        
        # Skip incomplete triples
        if not (point1 and line1 and point2):
            continue
        
        # Get or create node IDs for both points
        node1_id = get_or_create_node_id(point1)
        node2_id = get_or_create_node_id(point2)
        
        # Create directed edge with semantic label
        safe_edge_label = escape_dot_string(line1)
        dot_lines.append(f'  {node1_id} -> {node2_id} [label="{safe_edge_label}"];')
    
    dot_lines.append('}')
    return '\n'.join(dot_lines)


# =============================================================================
# Validation Functions
# =============================================================================

def validate_semantic_bit_json(data: any) -> Tuple[bool, Optional[str]]:
    """Validate a data structure against the Semantic Bit JSON schema.
    
    Performs comprehensive validation according to the formal JSON schema
    specification defined in the project documentation.
    
    Args:
        data: The data structure to validate
        
    Returns:
        Tuple of (is_valid, error_message). If valid, error_message is None.
        
    Example:
        >>> valid_data = {"sentences": [{"point1": "A", "line1": "B", "point2": "C"}]}
        >>> is_valid, error = validate_semantic_bit_json(valid_data)
        >>> assert is_valid and error is None
    """
    # Top-level structure validation
    if not isinstance(data, dict):
        return False, "Root must be a JSON object"
    
    if "sentences" not in data:
        return False, "Missing required 'sentences' key"
    
    sentences = data["sentences"]
    if not isinstance(sentences, list):
        return False, "'sentences' must be an array"
    
    # Validate each sentence triple
    for i, sentence in enumerate(sentences):
        if not isinstance(sentence, dict):
            return False, f"Sentence {i} must be an object"
        
        # Check required fields
        required_fields = ["point1", "line1", "point2"]
        for field in required_fields:
            if field not in sentence:
                return False, f"Sentence {i} missing required field '{field}'"
            
            value = sentence[field]
            if not isinstance(value, str):
                return False, f"Sentence {i} field '{field}' must be a string"
            
            if len(value.strip()) == 0:
                return False, f"Sentence {i} field '{field}' cannot be empty"
    
    # Check for additional properties at top level (should only have 'sentences')
    extra_keys = set(data.keys()) - {"sentences"}
    if extra_keys:
        return False, f"Unexpected top-level keys: {', '.join(extra_keys)}"
    
    return True, None


# Semantic Bit JSON Schema (as constant for reference)
SEMANTIC_BIT_JSON_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "sentences": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["point1", "line1", "point2"],
                "properties": {
                    "point1": {"type": "string", "minLength": 1},
                    "line1": {"type": "string", "minLength": 1},
                    "point2": {"type": "string", "minLength": 1}
                },
                "additionalProperties": False
            }
        }
    },
    "required": ["sentences"],
    "additionalProperties": False
}
