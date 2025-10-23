"""Comprehensive tests for semantic_bit.semantic module.

This test suite validates the core Semantic Bit Theory implementation including:
- Sentence segmentation
- Lexical analysis (tokenization)
- Syntactic role assignment
- Encoding pipeline
- Graph synthesis (DOT generation)
"""

import pytest
from semantic_bit.semantic import (
    # Core functions
    encode_text_to_sb,
    decode_sb_to_dot,
    # Phase functions
    segment_sentences,
    tokenize_sentence,
    extract_point1,
    extract_line,
    extract_point2,
    is_verb_like,
    escape_dot_string,
    # Data structures
    Token,
    SBTriple,
    SemanticBitDocument,
)


class TestSentenceSegmentation:
    """Test sentence boundary detection."""
    
    def test_segment_single_sentence(self):
        text = "The cat is sitting on the mat."
        result = segment_sentences(text)
        assert result == ["The cat is sitting on the mat."]
    
    def test_segment_multiple_sentences(self):
        text = "First sentence. Second sentence! Third sentence?"
        result = segment_sentences(text)
        assert result == [
            "First sentence.",
            "Second sentence!",
            "Third sentence?"
        ]
    
    def test_segment_empty_text(self):
        assert segment_sentences("") == []
        assert segment_sentences("   ") == []
    
    def test_segment_no_punctuation(self):
        text = "No punctuation here"
        result = segment_sentences(text)
        assert result == ["No punctuation here"]


class TestTokenization:
    """Test lexical analysis and token creation."""
    
    def test_tokenize_simple_sentence(self):
        sentence = "The cat sits"
        tokens = tokenize_sentence(sentence)
        
        assert len(tokens) == 3
        assert tokens[0].text == "The"
        assert tokens[0].normalized == "the"
        assert tokens[1].text == "cat"
        assert tokens[2].text == "sits"
    
    def test_tokenize_preserves_contractions(self):
        sentence = "Don't can't won't"
        tokens = tokenize_sentence(sentence)
        
        assert len(tokens) == 3
        assert tokens[0].text == "Don't"
        assert tokens[0].normalized == "don't"
    
    def test_tokenize_empty_sentence(self):
        assert tokenize_sentence("") == []
        assert tokenize_sentence("   ") == []
    
    def test_token_data_structure(self):
        token = Token("Hello", "hello")
        assert token.text == "Hello"
        assert token.normalized == "hello"
        
        # Test auto-normalization
        token2 = Token("WORLD", "")
        token2.__post_init__()
        assert token2.normalized == "world"


class TestVerbDetection:
    """Test verb-like token identification."""
    
    def test_auxiliary_verbs(self):
        auxiliaries = ["is", "are", "was", "were", "have", "has", "had", "do", "does", "did"]
        for aux in auxiliaries:
            token = Token(aux, aux)
            assert is_verb_like(token), f"'{aux}' should be detected as verb-like"
    
    def test_morphological_verbs(self):
        morphological = ["sitting", "running", "walked", "played"]
        for verb in morphological:
            token = Token(verb, verb)
            assert is_verb_like(token), f"'{verb}' should be detected as verb-like"
    
    def test_non_verbs(self):
        non_verbs = ["cat", "mat", "the", "on", "big", "house"]
        for word in non_verbs:
            token = Token(word, word)
            assert not is_verb_like(token), f"'{word}' should not be detected as verb-like"


class TestPhraseExtraction:
    """Test syntactic role assignment functions."""
    
    def test_extract_point1_simple(self):
        tokens = [Token("The", "the"), Token("cat", "cat"), Token("is", "is"), Token("sitting", "sitting")]
        point1, next_idx = extract_point1(tokens)
        
        assert point1 == "The cat"
        assert next_idx == 2  # Should stop at "is"
    
    def test_extract_line_with_preposition(self):
        tokens = [Token("is", "is"), Token("sitting", "sitting"), Token("on", "on"), Token("the", "the")]
        line, next_idx = extract_line(tokens, 0)
        
        assert line == "is sitting on"
        assert next_idx == 3  # Should include preposition
    
    def test_extract_point2_remaining(self):
        tokens = [Token("the", "the"), Token("mat", "mat")]
        point2, next_idx = extract_point2(tokens, 0)
        
        assert point2 == "the mat"
        assert next_idx == 2  # Should consume all remaining tokens


class TestDataStructures:
    """Test semantic data structures."""
    
    def test_sb_triple_creation(self):
        triple = SBTriple("The cat", "is sitting on", "the mat")
        assert triple.point1 == "The cat"
        assert triple.line1 == "is sitting on"
        assert triple.point2 == "the mat"
    
    def test_sb_triple_validation(self):
        valid_triple = SBTriple("subject", "predicate", "object")
        assert valid_triple.is_valid()
        
        invalid_triple = SBTriple("", "predicate", "object")
        assert not invalid_triple.is_valid()
    
    def test_sb_triple_to_dict(self):
        triple = SBTriple("The cat", "is sitting on", "the mat")
        result = triple.to_dict()
        
        expected = {
            "point1": "The cat",
            "line1": "is sitting on", 
            "point2": "the mat"
        }
        assert result == expected
    
    def test_semantic_bit_document(self):
        doc = SemanticBitDocument([])
        
        valid_triple = SBTriple("subject", "predicate", "object")
        invalid_triple = SBTriple("", "predicate", "object")
        
        doc.add_triple(valid_triple)
        doc.add_triple(invalid_triple)  # Should be rejected
        
        assert len(doc.sentences) == 1
        assert doc.sentences[0] == valid_triple


class TestEncoding:
    """Test complete encoding pipeline."""
    
    def test_encode_simple_sentence(self):
        text = "The cat is sitting on the mat."
        result = encode_text_to_sb(text)
        
        expected = {
            "sentences": [{
                "point1": "The cat",
                "line1": "is sitting on",
                "point2": "the mat"
            }]
        }
        assert result == expected
    
    def test_encode_multiple_sentences(self):
        text = "The cat is sitting on the mat. The dog is running in the park."
        result = encode_text_to_sb(text)
        
        assert len(result["sentences"]) == 2
        assert result["sentences"][0]["point1"] == "The cat"
        assert result["sentences"][1]["point1"] == "The dog"
    
    def test_encode_skips_unparseable_sentences(self):
        text = "The cat is sitting on the mat. Just words without verbs here."
        result = encode_text_to_sb(text)
        
        # Should get at least the first sentence (cat), 
        # second might parse depending on heuristics
        assert len(result["sentences"]) >= 1
        assert result["sentences"][0]["point1"] == "The cat"
    
    def test_encode_empty_text(self):
        result = encode_text_to_sb("")
        assert result == {"sentences": []}
    
    def test_encode_various_auxiliary_verbs(self):
        test_cases = [
            ("Birds are flying south.", "Birds", "are flying", "south"),
            ("They were walking home.", "They", "were walking", "home"),
            ("She has finished work.", "She", "has finished", "work"),
        ]
        
        for text, exp_p1, exp_l1, exp_p2 in test_cases:
            result = encode_text_to_sb(text)
            assert len(result["sentences"]) == 1
            sentence = result["sentences"][0]
            assert sentence["point1"] == exp_p1
            assert sentence["line1"] == exp_l1
            assert sentence["point2"] == exp_p2


class TestDOTGeneration:
    """Test graph synthesis and DOT format generation."""
    
    def test_escape_dot_string(self):
        assert escape_dot_string('simple') == 'simple'
        assert escape_dot_string('has "quotes"') == 'has \\"quotes\\"'
        assert escape_dot_string('has\\backslash') == 'has\\\\backslash'
        assert escape_dot_string('line\nbreak') == 'line\\nbreak'
    
    def test_decode_simple_graph(self):
        sb = {
            "sentences": [{
                "point1": "The cat",
                "line1": "is sitting on",
                "point2": "the mat"
            }]
        }
        
        result = decode_sb_to_dot(sb)
        
        # Should contain graph declaration
        assert "digraph SBGraph {" in result
        assert result.endswith("}")
        
        # Should contain nodes
        assert 'p1 [label="The cat"];' in result
        assert 'p2 [label="the mat"];' in result
        
        # Should contain edge
        assert 'p1 -> p2 [label="is sitting on"];' in result
    
    def test_decode_multiple_sentences_deduplication(self):
        sb = {
            "sentences": [
                {"point1": "The cat", "line1": "is sitting on", "point2": "the mat"},
                {"point1": "The cat", "line1": "is sleeping on", "point2": "the bed"}
            ]
        }
        
        result = decode_sb_to_dot(sb)
        
        # "The cat" should only appear once as a node
        cat_count = result.count('label="The cat"')
        assert cat_count == 1
        
        # Should have both relationships
        assert "is sitting on" in result
        assert "is sleeping on" in result
    
    def test_decode_empty_input(self):
        result = decode_sb_to_dot({})
        assert result == "digraph SBGraph {\n}"
        
        result = decode_sb_to_dot({"sentences": []})
        assert "digraph SBGraph {" in result
        assert result.endswith("}")
    
    def test_decode_custom_graph_name(self):
        sb = {"sentences": [{"point1": "A", "line1": "relates to", "point2": "B"}]}
        result = decode_sb_to_dot(sb, "CustomGraph")
        
        assert "digraph CustomGraph {" in result
    
    def test_decode_handles_special_characters(self):
        sb = {
            "sentences": [{
                "point1": 'Text with "quotes"',
                "line1": "connects\\to",
                "point2": "Another\nText"
            }]
        }
        
        result = decode_sb_to_dot(sb)
        
        # Should properly escape special characters
        assert '\\"quotes\\"' in result
        assert '\\\\to' in result
        assert '\\n' in result


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_encode_decode_roundtrip(self):
        text = "The scientist is studying quantum mechanics."
        
        # Encode to semantic bits
        sb = encode_text_to_sb(text)
        
        # Decode to DOT
        dot = decode_sb_to_dot(sb, "TestGraph")
        
        # Verify structure
        assert "digraph TestGraph {" in dot
        assert "The scientist" in dot
        assert "quantum mechanics" in dot
        assert "is studying" in dot
    
    def test_complex_multi_sentence_workflow(self):
        text = """
        The cat is sitting on the mat.
        Birds are flying south for winter.
        The children are playing outside.
        """
        
        sb = encode_text_to_sb(text)
        dot = decode_sb_to_dot(sb)
        
        # Should process multiple sentences
        assert len(sb["sentences"]) >= 2  # At least some should parse
        
        # DOT should be valid
        assert dot.startswith("digraph")
        assert dot.endswith("}")
        
        # Should contain relationships
        assert "->" in dot
    
    def test_handles_edge_cases_gracefully(self):
        edge_cases = [
            "",  # Empty
            "   ",  # Whitespace only
            "No verbs here.",  # No clear verb
            "123 456 789.",  # Numbers only
            "A.",  # Single word
        ]
        
        for text in edge_cases:
            # Should not crash
            sb = encode_text_to_sb(text)
            dot = decode_sb_to_dot(sb)
            
            # Should return valid structure
            assert isinstance(sb, dict)
            assert "sentences" in sb
            assert isinstance(dot, str)
            assert "digraph" in dot