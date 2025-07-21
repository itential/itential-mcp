# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import Mock, patch

from itential_mcp import commands, server


def test_run_function_exists():
    """Test that the run function exists and is callable."""
    assert hasattr(commands, 'run')
    assert callable(commands.run)


def test_run_returns_correct_tuple():
    """Test that run function returns the expected tuple structure."""
    args = Mock()
    result = commands.run(args)
    
    # Should return a tuple with server.run function and two None values
    assert isinstance(result, tuple)
    assert len(result) == 3
    assert result[0] == server.run
    assert result[1] is None
    assert result[2] is None


def test_run_with_various_args():
    """Test run function with different argument types."""
    # Test with None
    result = commands.run(None)
    assert result == (server.run, None, None)
    
    # Test with empty dict
    result = commands.run({})
    assert result == (server.run, None, None)
    
    # Test with string
    result = commands.run("test")
    assert result == (server.run, None, None)
    
    # Test with mock object
    mock_args = Mock()
    mock_args.transport = "stdio"
    mock_args.host = "localhost"
    result = commands.run(mock_args)
    assert result == (server.run, None, None)


def test_run_function_signature():
    """Test that run function has correct signature."""
    import inspect
    
    sig = inspect.signature(commands.run)
    params = list(sig.parameters.keys())
    
    # Should have exactly one parameter named 'args'
    assert len(params) == 1
    assert params[0] == 'args'


def test_run_function_docstring():
    """Test that run function has proper docstring."""
    assert commands.run.__doc__ is not None
    assert "Implements the `itential-mcp run` command" in commands.run.__doc__
    assert "`server` module" in commands.run.__doc__


@patch('itential_mcp.server.run')
def test_run_returns_server_run_function(mock_server_run):
    """Test that the returned function is indeed server.run."""
    args = Mock()
    result = commands.run(args)
    
    # The first element should be the server.run function
    assert result[0] == server.run
    
    # Verify it's the actual function we expect
    assert result[0] == mock_server_run


def test_module_imports():
    """Test that the module imports are correct."""
    # Test that server is imported correctly
    assert hasattr(commands, 'server')
    assert commands.server == server


def test_run_function_is_not_async():
    """Test that run function is not async."""
    import asyncio
    
    assert not asyncio.iscoroutinefunction(commands.run)


def test_run_function_return_value_immutable():
    """Test that the return value structure is consistent."""
    args1 = Mock()
    args2 = Mock()
    
    result1 = commands.run(args1)
    result2 = commands.run(args2)
    
    # Both calls should return the same structure
    assert result1 == result2
    assert result1 is not result2  # Different tuple instances
    assert result1[0] is result2[0]  # Same function reference


def test_commands_module_structure():
    """Test the overall module structure."""
    # Check that only expected functions/attributes are present
    expected_attrs = ['run', 'server']
    
    # Get all public attributes (not starting with _)
    public_attrs = [attr for attr in dir(commands) if not attr.startswith('_')]
    
    # Should contain at least our expected attributes
    for attr in expected_attrs:
        assert attr in public_attrs


class TestCommandsIntegration:
    """Integration tests for the commands module."""
    
    def test_run_with_realistic_args(self):
        """Test run with realistic argument structure."""
        # Simulate argparse.Namespace-like object
        class MockArgs:
            def __init__(self):
                self.transport = "stdio"
                self.host = "localhost"
                self.port = 8000
                self.log_level = "INFO"
        
        args = MockArgs()
        result = commands.run(args)
        
        assert result[0] == server.run
        assert result[1] is None
        assert result[2] is None
    
    def test_run_function_can_be_called_multiple_times(self):
        """Test that run function can be called multiple times safely."""
        args = Mock()
        
        # Call multiple times
        results = [commands.run(args) for _ in range(5)]
        
        # All results should be identical
        for result in results:
            assert result == (server.run, None, None)
    
    def test_run_with_edge_case_args(self):
        """Test run with edge case argument values."""
        edge_cases = [
            None,
            0,
            "",
            [],
            {},
            False,
            True,
            object(),
        ]
        
        for args in edge_cases:
            result = commands.run(args)
            assert result == (server.run, None, None)