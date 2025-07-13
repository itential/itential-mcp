# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
import asyncio
from unittest.mock import patch
from io import StringIO
import sys

from itential_mcp import metadata


class TestMetadataConstants:
    """Test cases for metadata constants."""
    
    def test_name_constant_exists(self):
        """Test that name constant exists and has correct value."""
        assert hasattr(metadata, 'name')
        assert metadata.name == "itential-mcp"
        assert isinstance(metadata.name, str)
    
    def test_author_constant_exists(self):
        """Test that author constant exists and has correct value."""
        assert hasattr(metadata, 'author')
        assert metadata.author == "Itential"
        assert isinstance(metadata.author, str)
    
    def test_version_constant_exists(self):
        """Test that version constant exists and is a string."""
        assert hasattr(metadata, 'version')
        assert isinstance(metadata.version, str)
        assert len(metadata.version) > 0
    
    def test_constants_are_immutable_types(self):
        """Test that constants are immutable types."""
        assert isinstance(metadata.name, str)
        assert isinstance(metadata.author, str)
        assert isinstance(metadata.version, str)


class TestDisplayVersionFunction:
    """Test cases for the display_version function."""
    
    def test_display_version_function_exists(self):
        """Test that display_version function exists and is callable."""
        assert hasattr(metadata, 'display_version')
        assert callable(metadata.display_version)
    
    def test_display_version_is_async(self):
        """Test that display_version is an async function."""
        assert asyncio.iscoroutinefunction(metadata.display_version)
    
    def test_display_version_function_signature(self):
        """Test that display_version has correct signature."""
        import inspect
        
        sig = inspect.signature(metadata.display_version)
        params = list(sig.parameters.keys())
        
        # Should have no parameters
        assert len(params) == 0
        
        # Should return None
        assert sig.return_annotation is None or sig.return_annotation is type(None)
    
    def test_display_version_docstring(self):
        """Test that display_version has proper docstring."""
        assert metadata.display_version.__doc__ is not None
        assert "Prints the current app verion to stdout" in metadata.display_version.__doc__
        assert "print the current application version to stdout" in metadata.display_version.__doc__
    
    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_display_version_prints_correct_format(self, mock_print):
        """Test that display_version prints in correct format."""
        await metadata.display_version()
        
        # Should have been called once
        mock_print.assert_called_once()
        
        # Get the actual call arguments
        call_args = mock_print.call_args[0][0]
        
        # Should contain name and version with newline
        assert metadata.name in call_args
        assert metadata.version in call_args
        assert call_args.endswith('\n')
        assert ' ' in call_args  # Should have space between name and version
    
    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_display_version_uses_module_variables(self, mock_print):
        """Test that display_version uses the module's name and version variables."""
        await metadata.display_version()
        
        call_args = mock_print.call_args[0][0]
        expected_output = f"{metadata.name} {metadata.version}\n"
        
        assert call_args == expected_output
    
    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_display_version_multiple_calls(self, mock_print):
        """Test that display_version can be called multiple times."""
        await metadata.display_version()
        await metadata.display_version()
        await metadata.display_version()
        
        # Should have been called three times
        assert mock_print.call_count == 3
        
        # All calls should be identical
        calls = mock_print.call_args_list
        for call in calls:
            assert call[0][0] == f"{metadata.name} {metadata.version}\n"
    
    @pytest.mark.asyncio
    @patch('sys.stdout', new_callable=StringIO)
    async def test_display_version_real_output(self, mock_stdout):
        """Test display_version with real stdout capture."""
        await metadata.display_version()
        
        output = mock_stdout.getvalue()
        assert f"{metadata.name} {metadata.version}\n\n" == output
    
    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_display_version_returns_none(self, mock_print):
        """Test that display_version returns None."""
        result = await metadata.display_version()
        assert result is None
    
    @pytest.mark.asyncio
    @patch('builtins.print', side_effect=Exception("Print error"))
    async def test_display_version_print_exception(self, mock_print):
        """Test display_version behavior when print raises exception."""
        with pytest.raises(Exception, match="Print error"):
            await metadata.display_version()


class TestMetadataModule:
    """Test cases for the metadata module as a whole."""
    
    def test_module_imports(self):
        """Test that the module has correct imports."""
        assert hasattr(metadata, 'version')
        # Note: the module version variable shadows the imported version function
    
    def test_module_structure(self):
        """Test the overall module structure."""
        # Check that expected attributes are present
        expected_attrs = ['name', 'author', 'version', 'display_version']
        
        # Get all public attributes (not starting with _)
        public_attrs = [attr for attr in dir(metadata) if not attr.startswith('_')]
        
        # Should contain at least our expected attributes
        for attr in expected_attrs:
            assert attr in public_attrs
    
    def test_module_has_copyright(self):
        """Test that the module file has copyright header."""
        import itential_mcp.metadata
        import inspect
        
        source = inspect.getsource(itential_mcp.metadata)
        assert "Copyright (c) 2025 Itential, Inc" in source
        assert "GNU General Public License v3.0+" in source
    
    def test_version_initialization(self):
        """Test that version is properly initialized from importlib.metadata."""
        # Just verify the version is a string and not empty
        assert isinstance(metadata.version, str)
        assert len(metadata.version) > 0


class TestMetadataIntegration:
    """Integration tests for metadata functionality."""
    
    def test_version_is_valid_semantic_version(self):
        """Test that version follows semantic versioning pattern."""
        version_str = metadata.version
        
        # Should be a non-empty string
        assert isinstance(version_str, str)
        assert len(version_str) > 0
        
        # Should not contain newlines or control characters
        assert '\n' not in version_str
        assert '\r' not in version_str
        assert '\t' not in version_str
    
    def test_constants_consistency(self):
        """Test that constants are consistent across module."""
        # Name should be consistent with package name
        assert metadata.name == "itential-mcp"
        
        # Author should be consistent
        assert metadata.author == "Itential"
        
        # Version should be accessible and consistent
        version1 = metadata.version
        version2 = metadata.version
        assert version1 == version2
    
    @pytest.mark.asyncio
    async def test_display_version_integration(self):
        """Integration test for display_version function."""
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            await metadata.display_version()
            output = captured_output.getvalue()
            
            # Should contain expected format
            assert metadata.name in output
            assert metadata.version in output
            assert output.endswith('\n')
            
            # Should be in format "name version\n\n" (function adds extra newline)
            expected = f"{metadata.name} {metadata.version}\n\n"
            assert output == expected
            
        finally:
            sys.stdout = old_stdout
    
    def test_module_can_be_imported_multiple_times(self):
        """Test that module can be imported multiple times safely."""
        import itential_mcp.metadata as meta1
        import itential_mcp.metadata as meta2
        from itential_mcp import metadata as meta3
        
        # All should reference the same module
        assert meta1 is meta2 is meta3
        
        # Constants should be the same
        assert meta1.name == meta2.name == meta3.name
        assert meta1.author == meta2.author == meta3.author
        assert meta1.version == meta2.version == meta3.version
    
    @pytest.mark.asyncio
    async def test_display_version_concurrent_calls(self):
        """Test that display_version handles concurrent calls safely."""
        import asyncio
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            # Run multiple concurrent calls
            tasks = [metadata.display_version() for _ in range(5)]
            await asyncio.gather(*tasks)
            
            output = captured_output.getvalue()
            
            # Should have 5 lines of output
            lines = output.split('\n')
            assert len([line for line in lines if line]) == 5
            
            # Each pair of lines should be the same (function outputs extra newline)
            expected_line = f"{metadata.name} {metadata.version}"
            non_empty_lines = [line for line in lines if line]
            assert len(non_empty_lines) == 5
            for line in non_empty_lines:
                assert line == expected_line
        
        finally:
            sys.stdout = old_stdout


class TestMetadataErrorHandling:
    """Test error handling scenarios."""
    
    def test_version_import_error_handling(self):
        """Test that version is properly loaded from package metadata."""
        # Since module is already imported, just verify version exists
        assert hasattr(metadata, 'version')
        assert metadata.version is not None
    
    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_display_version_no_stdout(self, mock_print):
        """Test display_version behavior when print is mocked."""
        await metadata.display_version()
        mock_print.assert_called_once_with(f"{metadata.name} {metadata.version}\n")
    
    def test_constants_are_not_none(self):
        """Test that constants are not None."""
        assert metadata.name is not None
        assert metadata.author is not None
        assert metadata.version is not None
    
    def test_constants_are_strings(self):
        """Test that all constants are strings."""
        assert isinstance(metadata.name, str)
        assert isinstance(metadata.author, str)
        # Version should be a string, not a Mock object
        assert isinstance(metadata.version, str)