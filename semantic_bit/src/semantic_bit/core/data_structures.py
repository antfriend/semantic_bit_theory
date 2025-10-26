"""Data structures for Semantic Bit Theory v2.0

This module defines the core data structures for representing semantic patterns,
using a polymorphic union approach for flexible pattern types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Literal, Union
from enum import Enum


# =============================================================================
# Enums
# =============================================================================

class PatternType(str, Enum):
    """Semantic pattern types supported in v2.0"""
    POINT = "point"
    LINE = "line"
    POINT_POINT = "point-point"
    POINT_LINE = "point-line"
    LINE_POINT = "line-point"
    TRIPLE = "triple"


# =============================================================================
# Token (unchanged from v1.0)
# =============================================================================

@dataclass
class Token:
    """Represents a single lexical token with its surface form and normalized form."""
    text: str          # Original surface form (preserves casing, punctuation)
    normalized: str    # Lowercased form for linguistic analysis

    def __post_init__(self) -> None:
        """Ensure normalized form is properly lowercased."""
        self.normalized = self.text.lower()


# =============================================================================
# v2.0 Content Structures (Always-Object Pattern)
# =============================================================================

@dataclass
class SBContent:
    """Container for semantic content (Point or Line) with optional enrichment.

    Points and Lines are ALWAYS objects in v2.0 to prevent mixed-typing issues.
    Assets/functions are optional and only appear when mappings exist.
    """
    content: str
    assets: Optional[List[Dict[str, str]]] = None      # Only present if matches exist
    functions: Optional[List[Dict[str, str]]] = None   # Only present if matches exist

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, omitting optional fields if not present."""
        result: Dict[str, Any] = {"content": self.content}
        if self.assets:
            result["assets"] = self.assets
        if self.functions:
            result["functions"] = self.functions
        return result

    @classmethod
    def from_string(cls, text: str) -> SBContent:
        """Create SBContent from a plain string."""
        return cls(content=text)


# =============================================================================
# Base Sentence Class
# =============================================================================

@dataclass
class SBSentenceBase:
    """Base class for all sentence pattern types in v2.0"""
    type: PatternType
    original_text: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON serialization.

        Subclasses must implement this to include pattern-specific fields.
        """
        raise NotImplementedError("Subclasses must implement to_dict()")

    def is_valid(self) -> bool:
        """Check if sentence structure is valid.

        Subclasses should override to add pattern-specific validation.
        """
        return bool(self.original_text.strip())


# =============================================================================
# Pattern 1: Point Only
# =============================================================================

@dataclass
class SBPoint(SBSentenceBase):
    """Pure Point pattern - static concept, entity, or state"""
    content: SBContent
    type: PatternType = field(default=PatternType.POINT, init=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "content": self.content.to_dict(),
            "original_text": self.original_text
        }

    def is_valid(self) -> bool:
        return super().is_valid() and bool(self.content.content.strip())


# =============================================================================
# Pattern 2: Line Only
# =============================================================================

@dataclass
class SBLine(SBSentenceBase):
    """Pure Line pattern - dynamic action, relationship, or process"""
    content: SBContent
    type: PatternType = field(default=PatternType.LINE, init=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "content": self.content.to_dict(),
            "original_text": self.original_text
        }

    def is_valid(self) -> bool:
        return super().is_valid() and bool(self.content.content.strip())


# =============================================================================
# Pattern 3: Point-Point (Apposition/Identity)
# =============================================================================

@dataclass
class SBPointPoint(SBSentenceBase):
    """Point-Point pattern - apposition or identity relationship"""
    point1: SBContent
    point2: SBContent
    type: PatternType = field(default=PatternType.POINT_POINT, init=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "point1": self.point1.to_dict(),
            "point2": self.point2.to_dict(),
            "original_text": self.original_text
        }

    def is_valid(self) -> bool:
        return (super().is_valid() and
                bool(self.point1.content.strip()) and
                bool(self.point2.content.strip()))


# =============================================================================
# Pattern 4: Point-Line (Subject-Action)
# =============================================================================

@dataclass
class SBPointLine(SBSentenceBase):
    """Point-Line pattern - subject with action"""
    point: SBContent
    line: SBContent
    type: PatternType = field(default=PatternType.POINT_LINE, init=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "point": self.point.to_dict(),
            "line": self.line.to_dict(),
            "original_text": self.original_text
        }

    def is_valid(self) -> bool:
        return (super().is_valid() and
                bool(self.point.content.strip()) and
                bool(self.line.content.strip()))


# =============================================================================
# Pattern 5: Line-Point (Action-Object / Questions)
# =============================================================================

@dataclass
class SBLinePoint(SBSentenceBase):
    """Line-Point pattern - action to object, common in questions"""
    line: SBContent
    point: SBContent
    type: PatternType = field(default=PatternType.LINE_POINT, init=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "line": self.line.to_dict(),
            "point": self.point.to_dict(),
            "original_text": self.original_text
        }

    def is_valid(self) -> bool:
        return (super().is_valid() and
                bool(self.line.content.strip()) and
                bool(self.point.content.strip()))


# =============================================================================
# Pattern 6: Triple (Classic Point-Line-Point)
# =============================================================================

@dataclass
class SBTriple(SBSentenceBase):
    """Classic triple pattern - Point₁ → Line → Point₂"""
    point1: SBContent
    line1: SBContent
    point2: SBContent
    type: PatternType = field(default=PatternType.TRIPLE, init=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "point1": self.point1.to_dict(),
            "line1": self.line1.to_dict(),
            "point2": self.point2.to_dict(),
            "original_text": self.original_text
        }

    def is_valid(self) -> bool:
        return (super().is_valid() and
                bool(self.point1.content.strip()) and
                bool(self.line1.content.strip()) and
                bool(self.point2.content.strip()))


# =============================================================================
# Document Container
# =============================================================================

# Union type for all sentence patterns
SBSentence = Union[SBPoint, SBLine, SBPointPoint, SBPointLine, SBLinePoint, SBTriple]


@dataclass
class SemanticBitDocument:
    """Container for multiple semantic sentences extracted from text.

    Version 2.0 flexible pattern format.
    """
    sentences: List[SBSentence]
    version: str = "2.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary format for JSON serialization."""
        return {
            "version": self.version,
            "sentences": [
                sentence.to_dict()
                for sentence in self.sentences
                if sentence.is_valid()
            ]
        }

    def add_sentence(self, sentence: SBSentence) -> None:
        """Add a sentence to the document if it's valid."""
        if sentence.is_valid():
            self.sentences.append(sentence)
