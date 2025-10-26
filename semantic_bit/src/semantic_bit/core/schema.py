"""JSON Schema definitions for Semantic Bit Theory

Defines schemas for both v1.0 (classic triples) and v2.0 (flexible patterns).
"""

from typing import Dict, Any


# =============================================================================
# v2.0 Schema (Flexible Patterns)
# =============================================================================

# Content structure (always-object pattern)
_SB_CONTENT_SCHEMA = {
    "type": "object",
    "required": ["content"],
    "properties": {
        "content": {"type": "string", "minLength": 1},
        "assets": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["url", "label"],
                "properties": {
                    "url": {"type": "string"},
                    "label": {"type": "string", "minLength": 1}
                },
                "additionalProperties": False
            }
        },
        "functions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "description"],
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "description": {"type": "string", "minLength": 1}
                },
                "additionalProperties": False
            }
        }
    },
    "unevaluatedProperties": False
}

# Pattern type schemas using oneOf with type discriminator
SEMANTIC_BIT_JSON_SCHEMA_V2: Dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://github.com/your-org/semantic-bit-theory/schema/v2.0.json",
    "title": "Semantic Bit JSON v2.0",
    "description": "Flexible pattern format supporting multiple semantic structures",
    "type": "object",
    "required": ["version", "sentences"],
    "properties": {
        "version": {
            "type": "string",
            "const": "2.0"
        },
        "sentences": {
            "type": "array",
            "items": {
                "oneOf": [
                    # Pattern 1: Point only
                    {
                        "type": "object",
                        "required": ["type", "content", "original_text"],
                        "properties": {
                            "type": {"const": "point"},
                            "content": _SB_CONTENT_SCHEMA,
                            "original_text": {"type": "string"}
                        },
                        "unevaluatedProperties": False
                    },
                    # Pattern 2: Line only
                    {
                        "type": "object",
                        "required": ["type", "content", "original_text"],
                        "properties": {
                            "type": {"const": "line"},
                            "content": _SB_CONTENT_SCHEMA,
                            "original_text": {"type": "string"}
                        },
                        "unevaluatedProperties": False
                    },
                    # Pattern 3: Point-Point
                    {
                        "type": "object",
                        "required": ["type", "point1", "point2", "original_text"],
                        "properties": {
                            "type": {"const": "point-point"},
                            "point1": _SB_CONTENT_SCHEMA,
                            "point2": _SB_CONTENT_SCHEMA,
                            "original_text": {"type": "string"}
                        },
                        "unevaluatedProperties": False
                    },
                    # Pattern 4: Point-Line
                    {
                        "type": "object",
                        "required": ["type", "point", "line", "original_text"],
                        "properties": {
                            "type": {"const": "point-line"},
                            "point": _SB_CONTENT_SCHEMA,
                            "line": _SB_CONTENT_SCHEMA,
                            "original_text": {"type": "string"}
                        },
                        "unevaluatedProperties": False
                    },
                    # Pattern 5: Line-Point
                    {
                        "type": "object",
                        "required": ["type", "line", "point", "original_text"],
                        "properties": {
                            "type": {"const": "line-point"},
                            "line": _SB_CONTENT_SCHEMA,
                            "point": _SB_CONTENT_SCHEMA,
                            "original_text": {"type": "string"}
                        },
                        "unevaluatedProperties": False
                    },
                    # Pattern 6: Triple (classic)
                    {
                        "type": "object",
                        "required": ["type", "point1", "line1", "point2", "original_text"],
                        "properties": {
                            "type": {"const": "triple"},
                            "point1": _SB_CONTENT_SCHEMA,
                            "line1": _SB_CONTENT_SCHEMA,
                            "point2": _SB_CONTENT_SCHEMA,
                            "original_text": {"type": "string"}
                        },
                        "unevaluatedProperties": False
                    }
                ]
            }
        }
    },
    "unevaluatedProperties": False
}


# =============================================================================
# Default Export
# =============================================================================

# Export v2.0 as the default schema
SEMANTIC_BIT_JSON_SCHEMA = SEMANTIC_BIT_JSON_SCHEMA_V2
