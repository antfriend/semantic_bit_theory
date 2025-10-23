"""Semantic Bit Theory - Natural Language to Graph Conversion

This package implements Semantic Bit Theory (SBT), providing lightweight,
dependency-free conversion of natural language into semantic graphs.

Core functionality:
- encode_text_to_sb(): Convert text to Point-Line-Point semantic triples
- decode_sb_to_dot(): Transform triples into Graphviz DOT format

Data structures:
- SBTriple: Individual semantic relationship
- SemanticBitDocument: Collection of triples
- Token: Lexical token with surface and normalized forms

Legacy analysis:
- analyze_text(): Text statistics and metadata (backward compatibility)

Example:
    >>> import semantic_bit
    >>> result = semantic_bit.encode_text_to_sb("The cat is sitting on the mat.")
    >>> print(result)
    {"sentences": [{"point1": "The cat", "line1": "is sitting on", "point2": "the mat"}]}
    
    >>> dot_graph = semantic_bit.decode_sb_to_dot(result)
    >>> print(dot_graph)
    digraph SBGraph {
      p1 [label="The cat"];
      p2 [label="the mat"];
      p1 -> p2 [label="is sitting on"];
    }
"""

# Legacy analyzer functionality (backward compatibility)
from .analyzer import analyze_text, analyze_text_as_json, MAX_INPUT_LENGTH

# Core Semantic Bit Theory functionality
from .semantic import (
    encode_text_to_sb,
    decode_sb_to_dot,
    SBTriple,
    SemanticBitDocument,
    Token,
    # Phase functions for advanced usage
    segment_sentences,
    tokenize_sentence,
    extract_point1,
    extract_line,
    extract_point2,
)

__all__ = [
    # Legacy API (backward compatibility)
    "analyze_text",
    "analyze_text_as_json", 
    "MAX_INPUT_LENGTH",
    
    # Core SBT API
    "encode_text_to_sb",
    "decode_sb_to_dot",
    
    # Data structures
    "SBTriple",
    "SemanticBitDocument", 
    "Token",
    
    # Advanced API (individual phases)
    "segment_sentences",
    "tokenize_sentence",
    "extract_point1",
    "extract_line", 
    "extract_point2",
]

__version__ = "0.1.0"
