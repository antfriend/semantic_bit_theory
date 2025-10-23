"""Tests for semantic_bit.cli module.

This test suite validates CLI functionality including:
- Argument parsing and subcommand routing
- Backward compatibility with legacy usage
- File I/O operations
- Error handling and user feedback
- Pipeline operations
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
from io import StringIO
import sys

from semantic_bit.cli import main, _load_text, _read_stdin


class TestArgumentParsing:
    """Test CLI argument parsing and subcommand detection."""
    
    def test_legacy_mode_text_argument(self):
        """Test that bare text arguments trigger legacy analyze mode."""
        with patch('semantic_bit.cli.analyze_text') as mock_analyze:
            mock_analyze.return_value = {"test": "result"}
            
            result = main(["Hello world"])
            
            mock_analyze.assert_called_once_with("Hello world")
            assert result == 0
    
    def test_legacy_mode_file_argument(self):
        """Test that -f flag triggers legacy analyze mode."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            temp_path = f.name
        
        try:
            with patch('semantic_bit.cli.analyze_text') as mock_analyze:
                mock_analyze.return_value = {"test": "result"}
                
                result = main(["-f", temp_path])
                
                mock_analyze.assert_called_once_with("Test content")
                assert result == 0
        finally:
            Path(temp_path).unlink()
    
    def test_explicit_analyze_subcommand(self):
        """Test explicit analyze subcommand."""
        with patch('semantic_bit.cli.analyze_text') as mock_analyze:
            mock_analyze.return_value = {"test": "result"}
            
            result = main(["analyze", "Hello world"])
            
            mock_analyze.assert_called_once_with("Hello world")
            assert result == 0
    
    def test_encode_subcommand(self):
        """Test encode subcommand."""
        with patch('semantic_bit.cli.encode_text_to_sb') as mock_encode:
            mock_encode.return_value = {"sentences": []}
            
            result = main(["encode", "Hello world"])
            
            mock_encode.assert_called_once_with("Hello world")
            assert result == 0
    
    def test_decode_subcommand(self):
        """Test decode subcommand with stdin."""
        test_json = '{"sentences": [{"point1": "A", "line1": "relates to", "point2": "B"}]}'
        
        with patch('semantic_bit.cli._read_stdin', return_value=test_json):
            with patch('semantic_bit.cli.decode_sb_to_dot') as mock_decode:
                mock_decode.return_value = "digraph Test {}"
                
                result = main(["decode"])
                
                mock_decode.assert_called_once()
                assert result == 0


class TestFileOperations:
    """Test file input/output operations."""
    
    def test_load_text_from_file(self):
        """Test loading text from a file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test file content")
            temp_path = Path(f.name)
        
        try:
            result = _load_text(None, temp_path)
            assert result == "Test file content"
        finally:
            temp_path.unlink()
    
    def test_load_text_from_argument(self):
        """Test loading text from command line argument."""
        result = _load_text("Test argument", None)
        assert result == "Test argument"
    
    def test_load_text_file_not_found(self):
        """Test error handling for nonexistent files."""
        nonexistent = Path("/nonexistent/file.txt")
        
        with pytest.raises(ValueError, match="File not found"):
            _load_text(None, nonexistent)
    
    def test_encode_to_file(self):
        """Test encoding output to file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            result = main(["encode", "The cat is sitting on the mat.", "-o", str(temp_path)])
            
            assert result == 0
            assert temp_path.exists()
            
            # Verify file content
            content = json.loads(temp_path.read_text())
            assert "sentences" in content
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_decode_from_file(self):
        """Test decoding from JSON file."""
        test_data = {"sentences": [{"point1": "A", "line1": "relates to", "point2": "B"}]}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = Path(f.name)
        
        try:
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = main(["decode", "-f", str(temp_path)])
                
                assert result == 0
                output = mock_stdout.getvalue()
                assert "digraph SBGraph" in output
                assert "relates to" in output
        finally:
            temp_path.unlink()


class TestErrorHandling:
    """Test error handling and user feedback."""
    
    def test_invalid_json_input(self):
        """Test handling of malformed JSON input."""
        with patch('semantic_bit.cli._read_stdin', return_value="invalid json"):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                result = main(["decode"])
                
                assert result == 1
                error_output = mock_stderr.getvalue()
                assert "Invalid JSON input" in error_output
    
    def test_missing_sentences_key(self):
        """Test handling of JSON without required 'sentences' key."""
        invalid_json = '{"wrong": "structure"}'
        
        with patch('semantic_bit.cli._read_stdin', return_value=invalid_json):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                result = main(["decode"])
                
                assert result == 1
                error_output = mock_stderr.getvalue()
                assert "must contain a 'sentences' key" in error_output
    
    def test_file_permission_error(self):
        """Test handling of file permission errors."""
        with patch('semantic_bit.cli._load_text') as mock_load:
            mock_load.side_effect = ValueError("Permission denied reading file")
            
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                result = main(["encode", "-f", "/some/file.txt"])
                
                assert result == 1
                error_output = mock_stderr.getvalue()
                assert "Permission denied" in error_output
    
    def test_keyboard_interrupt_handling(self):
        """Test graceful handling of Ctrl+C."""
        with patch('semantic_bit.cli._load_text') as mock_load:
            mock_load.side_effect = KeyboardInterrupt()
            
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                result = main(["encode", "test"])
                
                assert result == 130  # Standard SIGINT exit code
                error_output = mock_stderr.getvalue()
                assert "cancelled by user" in error_output


class TestBackwardCompatibility:
    """Test backward compatibility with legacy usage patterns."""
    
    def test_legacy_stdin_mode(self):
        """Test legacy mode with stdin input."""
        with patch('semantic_bit.cli._read_stdin', return_value="stdin content"):
            with patch('semantic_bit.cli.analyze_text') as mock_analyze:
                mock_analyze.return_value = {"test": "result"}
                
                # No arguments should trigger legacy mode with stdin
                result = main([])
                
                mock_analyze.assert_called_once_with("stdin content")
                assert result == 0
    
    def test_legacy_no_indent_option(self):
        """Test legacy --no-indent option."""
        with patch('semantic_bit.cli.analyze_text') as mock_analyze:
            mock_analyze.return_value = {"test": "result"}
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = main(["analyze", "test", "--no-indent"])
                
                assert result == 0
                output = mock_stdout.getvalue()
                # Should be compact JSON (no indentation)
                assert output.strip() == '{"test": "result"}'
    
    def test_legacy_custom_indent(self):
        """Test legacy --indent option."""
        with patch('semantic_bit.cli.analyze_text') as mock_analyze:
            mock_analyze.return_value = {"test": "result"}
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = main(["analyze", "test", "--indent", "4"])
                
                assert result == 0
                output = mock_stdout.getvalue()
                # Should be indented with 4 spaces
                assert "    " in output  # 4-space indentation


class TestPipelineOperations:
    """Test pipeline and chaining operations."""
    
    def test_encode_decode_pipeline_simulation(self):
        """Test encode → decode pipeline through separate calls."""
        # First, encode
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            encode_result = main(["encode", "The cat is sitting on the mat."])
            encode_output = mock_stdout.getvalue()
        
        assert encode_result == 0
        
        # Then decode the output
        with patch('semantic_bit.cli._read_stdin', return_value=encode_output):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                decode_result = main(["decode"])
                decode_output = mock_stdout.getvalue()
        
        assert decode_result == 0
        assert "digraph SBGraph" in decode_output
        assert "The cat" in decode_output
        assert "is sitting on" in decode_output
    
    def test_custom_graph_name(self):
        """Test decode with custom graph name."""
        test_json = '{"sentences": [{"point1": "A", "line1": "relates to", "point2": "B"}]}'
        
        with patch('semantic_bit.cli._read_stdin', return_value=test_json):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = main(["decode", "--name", "CustomGraph"])
                
                assert result == 0
                output = mock_stdout.getvalue()
                assert "digraph CustomGraph" in output


class TestJSONFormatting:
    """Test JSON output formatting options."""
    
    def test_encode_compact_output(self):
        """Test encode with compact JSON output."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = main(["encode", "The cat is sitting.", "--indent", "0"])
            
            assert result == 0
            output = mock_stdout.getvalue()
            # Should be more compact than pretty-printed
            # Even with indent=0, some structure may remain
            parsed = json.loads(output)
            assert "sentences" in parsed
    
    def test_encode_pretty_output(self):
        """Test encode with pretty-printed JSON output."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = main(["encode", "The cat is sitting.", "--indent", "2"])
            
            assert result == 0
            output = mock_stdout.getvalue()
            # Should be pretty-printed (multiple lines)
            assert output.count('\n') > 2


class TestHelpSystem:
    """Test help and usage information."""
    
    def test_main_help(self):
        """Test main help message."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])
        
        assert exc_info.value.code == 0
    
    def test_subcommand_help(self):
        """Test subcommand help messages."""
        subcommands = ["analyze", "encode", "decode"]
        
        for subcmd in subcommands:
            with pytest.raises(SystemExit) as exc_info:
                main([subcmd, "--help"])
            
            assert exc_info.value.code == 0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_input_handling(self):
        """Test handling of empty input."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = main(["encode", ""])
            
            assert result == 0
            output = json.loads(mock_stdout.getvalue())
            assert output == {"sentences": []}
    
    def test_whitespace_only_input(self):
        """Test handling of whitespace-only input."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = main(["encode", "   \n\t   "])
            
            assert result == 0
            output = json.loads(mock_stdout.getvalue())
            assert output == {"sentences": []}
    
    def test_very_long_input(self):
        """Test handling of very long input."""
        long_text = "The cat is sitting on the mat. " * 1000
        
        with patch('sys.stdout', new_callable=StringIO):
            result = main(["encode", long_text])
            
            # Should not crash
            assert result == 0
    
    def test_unicode_input(self):
        """Test handling of Unicode input."""
        unicode_text = "El gato está sentado en la alfombra. 🐱"
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = main(["encode", unicode_text])
            
            assert result == 0
            output = json.loads(mock_stdout.getvalue())
            # Should handle Unicode gracefully
            assert isinstance(output, dict)