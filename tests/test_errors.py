# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from itential_mcp.errors import (
    ItentialMcpError,
    TimeoutExceededError,
    NotFoundError,
    InvalidStateError,
    AlreadyExistsError
)


class TestItentialMcpError:
    """Test the base ItentialMcpError exception class"""
    
    def test_inheritance(self):
        """Test that ItentialMcpError inherits from Exception"""
        assert issubclass(ItentialMcpError, Exception)
    
    def test_can_be_raised_without_message(self):
        """Test that ItentialMcpError can be raised without a message"""
        with pytest.raises(ItentialMcpError):
            raise ItentialMcpError()
    
    def test_can_be_raised_with_message(self):
        """Test that ItentialMcpError can be raised with a message"""
        message = "Test error message"
        with pytest.raises(ItentialMcpError) as exc_info:
            raise ItentialMcpError(message)
        
        assert str(exc_info.value) == message
    
    def test_can_be_raised_with_multiple_args(self):
        """Test that ItentialMcpError can be raised with multiple arguments"""
        arg1, arg2 = "First arg", "Second arg"
        with pytest.raises(ItentialMcpError) as exc_info:
            raise ItentialMcpError(arg1, arg2)
        
        assert exc_info.value.args == (arg1, arg2)
    
    def test_instance_creation(self):
        """Test creating an instance of ItentialMcpError"""
        error = ItentialMcpError("test message")
        assert isinstance(error, Exception)
        assert isinstance(error, ItentialMcpError)
        assert str(error) == "test message"
    
    def test_repr(self):
        """Test the string representation of ItentialMcpError"""
        message = "test error"
        error = ItentialMcpError(message)
        assert repr(error) == f"ItentialMcpError('{message}')"


class TestTimeoutExceededError:
    """Test the TimeoutExceededError exception class"""
    
    def test_inheritance(self):
        """Test that TimeoutExceededError inherits from ItentialMcpError"""
        assert issubclass(TimeoutExceededError, ItentialMcpError)
        assert issubclass(TimeoutExceededError, Exception)
    
    def test_can_be_raised_without_message(self):
        """Test that TimeoutExceededError can be raised without a message"""
        with pytest.raises(TimeoutExceededError):
            raise TimeoutExceededError()
    
    def test_can_be_raised_with_message(self):
        """Test that TimeoutExceededError can be raised with a message"""
        message = "Operation timed out after 30 seconds"
        with pytest.raises(TimeoutExceededError) as exc_info:
            raise TimeoutExceededError(message)
        
        assert str(exc_info.value) == message
    
    def test_catches_as_base_exception(self):
        """Test that TimeoutExceededError can be caught as ItentialMcpError"""
        with pytest.raises(ItentialMcpError):
            raise TimeoutExceededError("timeout")
    
    def test_instance_creation(self):
        """Test creating an instance of TimeoutExceededError"""
        timeout_value = 60
        error = TimeoutExceededError(f"Timeout exceeded: {timeout_value}s")
        assert isinstance(error, TimeoutExceededError)
        assert isinstance(error, ItentialMcpError)
        assert isinstance(error, Exception)
    
    def test_typical_use_case(self):
        """Test a typical use case for TimeoutExceededError"""
        def mock_operation_with_timeout(timeout):
            if timeout < 30:
                raise TimeoutExceededError(f"Operation timed out after {timeout} seconds")
            return "success"
        
        with pytest.raises(TimeoutExceededError) as exc_info:
            mock_operation_with_timeout(15)
        
        assert "timed out after 15 seconds" in str(exc_info.value)


class TestNotFoundError:
    """Test the NotFoundError exception class"""
    
    def test_inheritance(self):
        """Test that NotFoundError inherits from ItentialMcpError"""
        assert issubclass(NotFoundError, ItentialMcpError)
        assert issubclass(NotFoundError, Exception)
    
    def test_can_be_raised_without_message(self):
        """Test that NotFoundError can be raised without a message"""
        with pytest.raises(NotFoundError):
            raise NotFoundError()
    
    def test_can_be_raised_with_message(self):
        """Test that NotFoundError can be raised with a message"""
        message = "Resource 'workflow-123' not found"
        with pytest.raises(NotFoundError) as exc_info:
            raise NotFoundError(message)
        
        assert str(exc_info.value) == message
    
    def test_catches_as_base_exception(self):
        """Test that NotFoundError can be caught as ItentialMcpError"""
        with pytest.raises(ItentialMcpError):
            raise NotFoundError("not found")
    
    def test_instance_creation(self):
        """Test creating an instance of NotFoundError"""
        resource_id = "device-abc123"
        error = NotFoundError(f"Device {resource_id} not found")
        assert isinstance(error, NotFoundError)
        assert isinstance(error, ItentialMcpError)
        assert isinstance(error, Exception)
    
    def test_typical_use_case(self):
        """Test a typical use case for NotFoundError"""
        def mock_get_resource(resource_id):
            valid_ids = ["res1", "res2", "res3"]
            if resource_id not in valid_ids:
                raise NotFoundError(f"Resource '{resource_id}' not found")
            return {"id": resource_id, "data": "mock data"}
        
        with pytest.raises(NotFoundError) as exc_info:
            mock_get_resource("invalid-id")
        
        assert "Resource 'invalid-id' not found" == str(exc_info.value)


class TestInvalidStateError:
    """Test the InvalidStateError exception class"""
    
    def test_inheritance(self):
        """Test that InvalidStateError inherits from ItentialMcpError"""
        assert issubclass(InvalidStateError, ItentialMcpError)
        assert issubclass(InvalidStateError, Exception)
    
    def test_can_be_raised_without_message(self):
        """Test that InvalidStateError can be raised without a message"""
        with pytest.raises(InvalidStateError):
            raise InvalidStateError()
    
    def test_can_be_raised_with_message(self):
        """Test that InvalidStateError can be raised with a message"""
        message = "Workflow is in 'error' state and cannot be executed"
        with pytest.raises(InvalidStateError) as exc_info:
            raise InvalidStateError(message)
        
        assert str(exc_info.value) == message
    
    def test_catches_as_base_exception(self):
        """Test that InvalidStateError can be caught as ItentialMcpError"""
        with pytest.raises(ItentialMcpError):
            raise InvalidStateError("invalid state")
    
    def test_instance_creation(self):
        """Test creating an instance of InvalidStateError"""
        current_state = "disabled"
        expected_state = "enabled"
        error = InvalidStateError(f"Expected state '{expected_state}' but found '{current_state}'")
        assert isinstance(error, InvalidStateError)
        assert isinstance(error, ItentialMcpError)
        assert isinstance(error, Exception)
    
    def test_typical_use_case(self):
        """Test a typical use case for InvalidStateError"""
        def mock_execute_workflow(workflow_state):
            valid_states = ["ready", "running"]
            if workflow_state not in valid_states:
                raise InvalidStateError(
                    f"Cannot execute workflow in '{workflow_state}' state. "
                    f"Expected one of: {', '.join(valid_states)}"
                )
            return "execution started"
        
        with pytest.raises(InvalidStateError) as exc_info:
            mock_execute_workflow("paused")
        
        error_message = str(exc_info.value)
        assert "Cannot execute workflow in 'paused' state" in error_message
        assert "Expected one of: ready, running" in error_message


class TestAlreadyExistsError:
    """Test the AlreadyExistsError exception class"""
    
    def test_inheritance(self):
        """Test that AlreadyExistsError inherits from ItentialMcpError"""
        assert issubclass(AlreadyExistsError, ItentialMcpError)
        assert issubclass(AlreadyExistsError, Exception)
    
    def test_can_be_raised_without_message(self):
        """Test that AlreadyExistsError can be raised without a message"""
        with pytest.raises(AlreadyExistsError):
            raise AlreadyExistsError()
    
    def test_can_be_raised_with_message(self):
        """Test that AlreadyExistsError can be raised with a message"""
        message = "Device with hostname 'server01' already exists"
        with pytest.raises(AlreadyExistsError) as exc_info:
            raise AlreadyExistsError(message)
        
        assert str(exc_info.value) == message
    
    def test_catches_as_base_exception(self):
        """Test that AlreadyExistsError can be caught as ItentialMcpError"""
        with pytest.raises(ItentialMcpError):
            raise AlreadyExistsError("already exists")
    
    def test_instance_creation(self):
        """Test creating an instance of AlreadyExistsError"""
        resource_name = "workflow-backup"
        error = AlreadyExistsError(f"Workflow '{resource_name}' already exists")
        assert isinstance(error, AlreadyExistsError)
        assert isinstance(error, ItentialMcpError)
        assert isinstance(error, Exception)
    
    def test_typical_use_case(self):
        """Test a typical use case for AlreadyExistsError"""
        existing_users = ["admin", "user1", "operator"]
        
        def mock_create_user(username):
            if username in existing_users:
                raise AlreadyExistsError(f"User '{username}' already exists")
            existing_users.append(username)
            return f"User '{username}' created successfully"
        
        with pytest.raises(AlreadyExistsError) as exc_info:
            mock_create_user("admin")
        
        assert "User 'admin' already exists" == str(exc_info.value)


class TestErrorHierarchy:
    """Test the overall error hierarchy and relationships"""
    
    def test_all_errors_inherit_from_base(self):
        """Test that all custom errors inherit from ItentialMcpError"""
        error_classes = [
            TimeoutExceededError,
            NotFoundError,
            InvalidStateError,
            AlreadyExistsError
        ]
        
        for error_class in error_classes:
            assert issubclass(error_class, ItentialMcpError)
            assert issubclass(error_class, Exception)
    
    def test_catch_all_with_base_exception(self):
        """Test that all custom errors can be caught with the base exception"""
        errors_to_test = [
            TimeoutExceededError("timeout"),
            NotFoundError("not found"),
            InvalidStateError("invalid"),
            AlreadyExistsError("exists")
        ]
        
        for error in errors_to_test:
            with pytest.raises(ItentialMcpError):
                raise error
    
    def test_error_differentiation(self):
        """Test that different error types can be caught specifically"""
        def raise_specific_error(error_type):
            error_map = {
                "timeout": TimeoutExceededError("Timeout occurred"),
                "not_found": NotFoundError("Resource not found"),
                "invalid_state": InvalidStateError("Invalid state"),
                "already_exists": AlreadyExistsError("Already exists")
            }
            raise error_map[error_type]
        
        # Test specific catching
        with pytest.raises(TimeoutExceededError):
            raise_specific_error("timeout")
        
        with pytest.raises(NotFoundError):
            raise_specific_error("not_found")
        
        with pytest.raises(InvalidStateError):
            raise_specific_error("invalid_state")
        
        with pytest.raises(AlreadyExistsError):
            raise_specific_error("already_exists")
    
    def test_error_class_names(self):
        """Test that error classes have the expected names"""
        expected_classes = {
            "ItentialMcpError": ItentialMcpError,
            "TimeoutExceededError": TimeoutExceededError,
            "NotFoundError": NotFoundError,
            "InvalidStateError": InvalidStateError,
            "AlreadyExistsError": AlreadyExistsError
        }
        
        for name, error_class in expected_classes.items():
            assert error_class.__name__ == name
    
    def test_error_module_attributes(self):
        """Test that all error classes are properly defined in the module"""
        import itential_mcp.errors as errors_module
        
        expected_errors = [
            "ItentialMcpError",
            "TimeoutExceededError", 
            "NotFoundError",
            "InvalidStateError",
            "AlreadyExistsError"
        ]
        
        for error_name in expected_errors:
            assert hasattr(errors_module, error_name)
            error_class = getattr(errors_module, error_name)
            assert isinstance(error_class, type)
            assert issubclass(error_class, Exception)


class TestErrorChaining:
    """Test error chaining and context functionality"""
    
    def test_error_chaining_with_cause(self):
        """Test chaining errors with __cause__"""
        original_error = ValueError("Original error")
        
        try:
            raise original_error
        except ValueError as e:
            with pytest.raises(ItentialMcpError) as exc_info:
                raise ItentialMcpError("Wrapped error") from e
            
            assert exc_info.value.__cause__ is original_error
    
    def test_error_chaining_with_context(self):
        """Test error chaining with __context__"""
        try:
            raise ValueError("Original error")
        except ValueError:
            with pytest.raises(NotFoundError) as exc_info:
                raise NotFoundError("Resource not found during error handling")
            
            assert isinstance(exc_info.value.__context__, ValueError)
    
    def test_nested_custom_errors(self):
        """Test nesting custom errors"""
        try:
            raise InvalidStateError("Invalid workflow state")
        except InvalidStateError as e:
            with pytest.raises(TimeoutExceededError) as exc_info:
                raise TimeoutExceededError("Timeout while handling invalid state") from e
            
            assert isinstance(exc_info.value.__cause__, InvalidStateError)
            assert exc_info.value.__cause__.args[0] == "Invalid workflow state"


class TestErrorDocstrings:
    """Test that all error classes have proper docstrings"""
    
    def test_base_error_has_docstring(self):
        """Test that ItentialMcpError has a docstring"""
        assert ItentialMcpError.__doc__ is not None
        assert "base exception class" in ItentialMcpError.__doc__.lower()
    
    def test_timeout_error_has_docstring(self):
        """Test that TimeoutExceededError has a docstring"""
        assert TimeoutExceededError.__doc__ is not None
        assert "timeout" in TimeoutExceededError.__doc__.lower()
    
    def test_not_found_error_has_docstring(self):
        """Test that NotFoundError has a docstring"""
        assert NotFoundError.__doc__ is not None
        assert "could not be found" in NotFoundError.__doc__.lower()
    
    def test_invalid_state_error_has_docstring(self):
        """Test that InvalidStateError has a docstring"""
        assert InvalidStateError.__doc__ is not None
        assert "invalid state" in InvalidStateError.__doc__.lower()
    
    def test_already_exists_error_has_docstring(self):
        """Test that AlreadyExistsError has a docstring"""
        assert AlreadyExistsError.__doc__ is not None
        assert "already exists" in AlreadyExistsError.__doc__.lower()