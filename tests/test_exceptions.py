# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
from itential_mcp.exceptions import (
    # Base exceptions
    ItentialMcpException,
    ClientException,
    ServerException,
    BusinessLogicException,
    
    # Client exceptions (4xx)
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    NotFoundError,
    ConflictException,
    AlreadyExistsError,
    InvalidStateError,
    RateLimitException,
    
    # Server exceptions (5xx)
    ConfigurationException,
    ConnectionException,
    TimeoutExceededError,
    ServiceUnavailableException,
    
    # Business logic exceptions
    WorkflowException,
    DeviceException,
    ComplianceException,
    
    # Legacy compatibility
    ItentialMcpError,
    
    # Utility functions
    get_exception_for_http_status,
    create_exception_from_response,
    is_client_error,
    is_server_error,
    is_business_error,
)


class TestItentialMcpException:
    """Test the base ItentialMcpException class"""
    
    def test_inheritance(self):
        """Test that ItentialMcpException inherits from Exception"""
        assert issubclass(ItentialMcpException, Exception)
    
    def test_can_be_raised_without_message(self):
        """Test that ItentialMcpException can be raised without a message"""
        with pytest.raises(ItentialMcpException):
            raise ItentialMcpException()
    
    def test_can_be_raised_with_message(self):
        """Test that ItentialMcpException can be raised with a message"""
        message = "Test error message"
        with pytest.raises(ItentialMcpException) as exc_info:
            raise ItentialMcpException(message)
        
        assert exc_info.value.message == message
        assert str(exc_info.value) == message
    
    def test_can_be_raised_with_details(self):
        """Test that ItentialMcpException can be raised with details"""
        message = "Test error"
        details = {"key": "value", "count": 42}
        
        with pytest.raises(ItentialMcpException) as exc_info:
            raise ItentialMcpException(message, details=details)
        
        assert exc_info.value.message == message
        assert exc_info.value.details == details
    
    def test_http_status_default(self):
        """Test default HTTP status code"""
        error = ItentialMcpException("test")
        assert error.http_status == 500
    
    def test_http_status_override(self):
        """Test HTTP status code override"""
        error = ItentialMcpException("test", http_status=422)
        assert error.http_status == 422
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        message = "Test error"
        details = {"field": "invalid"}
        error = ItentialMcpException(message, details=details, http_status=400)
        
        result = error.to_dict()
        expected = {
            "error": "ItentialMcpException",
            "message": message,
            "details": details,
            "http_status": 400
        }
        
        assert result == expected
    
    def test_instance_creation(self):
        """Test creating an instance of ItentialMcpException"""
        error = ItentialMcpException("test message")
        assert isinstance(error, Exception)
        assert isinstance(error, ItentialMcpException)
        assert str(error) == "test message"


class TestLegacyCompatibility:
    """Test backward compatibility with legacy error names"""
    
    def test_legacy_alias(self):
        """Test that ItentialMcpError is an alias for ItentialMcpException"""
        assert ItentialMcpError is ItentialMcpException
    
    def test_legacy_usage(self):
        """Test using legacy alias"""
        with pytest.raises(ItentialMcpError) as exc_info:
            raise ItentialMcpError("legacy test")
        
        assert isinstance(exc_info.value, ItentialMcpException)
        assert exc_info.value.message == "legacy test"


class TestClientExceptions:
    """Test client-side exception classes (4xx)"""
    
    def test_validation_exception(self):
        """Test ValidationException"""
        error = ValidationException("Invalid input")
        assert error.http_status == 400
        assert isinstance(error, ClientException)
        assert isinstance(error, ItentialMcpException)
    
    def test_authentication_exception(self):
        """Test AuthenticationException"""
        error = AuthenticationException("Invalid credentials")
        assert error.http_status == 401
        assert isinstance(error, ClientException)
    
    def test_authorization_exception(self):
        """Test AuthorizationException"""
        error = AuthorizationException("Access denied")
        assert error.http_status == 403
        assert isinstance(error, ClientException)
    
    def test_not_found_error(self):
        """Test NotFoundError"""
        error = NotFoundError("Resource not found")
        assert error.http_status == 404
        assert isinstance(error, ClientException)
    
    def test_conflict_exception(self):
        """Test ConflictException"""
        error = ConflictException("Resource conflict")
        assert error.http_status == 409
        assert isinstance(error, ClientException)
    
    def test_already_exists_error(self):
        """Test AlreadyExistsError inherits from ConflictException"""
        error = AlreadyExistsError("Resource already exists")
        assert error.http_status == 409
        assert isinstance(error, ConflictException)
        assert isinstance(error, ClientException)
    
    def test_invalid_state_error(self):
        """Test InvalidStateError inherits from ConflictException"""
        error = InvalidStateError("Invalid state")
        assert error.http_status == 409
        assert isinstance(error, ConflictException)
        assert isinstance(error, ClientException)
    
    def test_rate_limit_exception(self):
        """Test RateLimitException"""
        error = RateLimitException("Rate limit exceeded")
        assert error.http_status == 429
        assert isinstance(error, ClientException)


class TestServerExceptions:
    """Test server-side exception classes (5xx)"""
    
    def test_configuration_exception(self):
        """Test ConfigurationException"""
        error = ConfigurationException("Invalid configuration")
        assert error.http_status == 500
        assert isinstance(error, ServerException)
        assert isinstance(error, ItentialMcpException)
    
    def test_connection_exception(self):
        """Test ConnectionException"""
        error = ConnectionException("Connection failed")
        assert error.http_status == 502
        assert isinstance(error, ServerException)
    
    def test_timeout_exceeded_error(self):
        """Test TimeoutExceededError"""
        error = TimeoutExceededError("Operation timed out")
        assert error.http_status == 504
        assert isinstance(error, ServerException)
    
    def test_service_unavailable_exception(self):
        """Test ServiceUnavailableException"""
        error = ServiceUnavailableException("Service unavailable")
        assert error.http_status == 503
        assert isinstance(error, ServerException)


class TestBusinessLogicExceptions:
    """Test business logic exception classes"""
    
    def test_workflow_exception(self):
        """Test WorkflowException"""
        error = WorkflowException("Workflow failed")
        assert error.http_status == 422
        assert isinstance(error, BusinessLogicException)
        assert isinstance(error, ItentialMcpException)
    
    def test_device_exception(self):
        """Test DeviceException"""
        error = DeviceException("Device error")
        assert error.http_status == 422
        assert isinstance(error, BusinessLogicException)
    
    def test_compliance_exception(self):
        """Test ComplianceException"""
        error = ComplianceException("Compliance violation")
        assert error.http_status == 422
        assert isinstance(error, BusinessLogicException)


class TestUtilityFunctions:
    """Test utility functions for exception handling"""
    
    def test_get_exception_for_http_status(self):
        """Test getting exception class for HTTP status code"""
        assert get_exception_for_http_status(400) == ValidationException
        assert get_exception_for_http_status(401) == AuthenticationException
        assert get_exception_for_http_status(404) == NotFoundError
        assert get_exception_for_http_status(409) == ConflictException
        assert get_exception_for_http_status(500) == ServerException
        assert get_exception_for_http_status(504) == TimeoutExceededError
        
        # Test unknown status code
        assert get_exception_for_http_status(999) == ItentialMcpException
    
    def test_create_exception_from_response(self):
        """Test creating exception from HTTP response"""
        exception = create_exception_from_response(
            404, 
            "Resource not found", 
            {"resource_id": "12345"}
        )
        
        assert isinstance(exception, NotFoundError)
        assert exception.message == "Resource not found"
        assert exception.details == {"resource_id": "12345"}
        assert exception.http_status == 404
    
    def test_is_client_error(self):
        """Test client error detection"""
        assert is_client_error(ValidationException("test"))
        assert is_client_error(NotFoundError("test"))
        assert is_client_error(AlreadyExistsError("test"))
        
        assert not is_client_error(ServerException("test"))
        assert not is_client_error(WorkflowException("test"))
        assert not is_client_error(Exception("test"))
    
    def test_is_server_error(self):
        """Test server error detection"""
        assert is_server_error(ServerException("test"))
        assert is_server_error(TimeoutExceededError("test"))
        assert is_server_error(ConnectionException("test"))
        
        assert not is_server_error(ClientException("test"))
        assert not is_server_error(WorkflowException("test"))
        assert not is_server_error(Exception("test"))
    
    def test_is_business_error(self):
        """Test business logic error detection"""
        assert is_business_error(WorkflowException("test"))
        assert is_business_error(DeviceException("test"))
        assert is_business_error(ComplianceException("test"))
        
        assert not is_business_error(ClientException("test"))
        assert not is_business_error(ServerException("test"))
        assert not is_business_error(Exception("test"))


class TestExceptionHierarchy:
    """Test exception hierarchy integrity"""
    
    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from ItentialMcpException"""
        exceptions_to_test = [
            ValidationException, AuthenticationException, NotFoundError,
            AlreadyExistsError, InvalidStateError, TimeoutExceededError,
            WorkflowException, DeviceException, ComplianceException
        ]
        
        for exc_class in exceptions_to_test:
            assert issubclass(exc_class, ItentialMcpException)
    
    def test_catch_all_with_base_exception(self):
        """Test that base exception can catch all custom exceptions"""
        exceptions_to_test = [
            ValidationException("test"),
            NotFoundError("test"),
            TimeoutExceededError("test"),
            WorkflowException("test")
        ]
        
        for exc in exceptions_to_test:
            with pytest.raises(ItentialMcpException):
                raise exc
    
    def test_exception_categories(self):
        """Test that exceptions are properly categorized"""
        # Client exceptions
        client_exceptions = [
            ValidationException, AuthenticationException, NotFoundError,
            AlreadyExistsError, InvalidStateError, RateLimitException
        ]
        
        for exc_class in client_exceptions:
            assert issubclass(exc_class, ClientException)
        
        # Server exceptions
        server_exceptions = [
            ConfigurationException, ConnectionException,
            TimeoutExceededError, ServiceUnavailableException
        ]
        
        for exc_class in server_exceptions:
            assert issubclass(exc_class, ServerException)
        
        # Business logic exceptions
        business_exceptions = [
            WorkflowException, DeviceException, ComplianceException
        ]
        
        for exc_class in business_exceptions:
            assert issubclass(exc_class, BusinessLogicException)


class TestExceptionChaining:
    """Test exception chaining functionality"""
    
    def test_exception_chaining_with_cause(self):
        """Test exception chaining using 'from' syntax"""
        original_error = ValueError("Original error")
        
        try:
            try:
                raise original_error
            except ValueError as e:
                raise NotFoundError("Resource not found") from e
        except NotFoundError as exc:
            assert exc.__cause__ is original_error
            assert str(exc.__cause__) == "Original error"
    
    def test_exception_chaining_with_context(self):
        """Test exception chaining with context"""
        try:
            try:
                raise ValueError("Original error")
            except ValueError:
                raise TimeoutExceededError("Operation timed out")
        except TimeoutExceededError as exc:
            assert isinstance(exc.__context__, ValueError)
            assert str(exc.__context__) == "Original error"
    
    def test_nested_custom_errors(self):
        """Test chaining custom exceptions"""
        try:
            try:
                raise ConnectionException("Database connection failed")
            except ConnectionException as e:
                raise WorkflowException("Workflow execution failed") from e
        except WorkflowException as exc:
            assert isinstance(exc.__cause__, ConnectionException)
            assert exc.__cause__.http_status == 502
            assert exc.http_status == 422


class TestExceptionDocstrings:
    """Test that exceptions have proper documentation"""
    
    def test_base_exception_has_docstring(self):
        """Test base exception docstring"""
        assert ItentialMcpException.__doc__ is not None
        assert len(ItentialMcpException.__doc__.strip()) > 0
    
    def test_client_exceptions_have_docstrings(self):
        """Test client exceptions have docstrings"""
        exceptions = [ValidationException, NotFoundError, AlreadyExistsError]
        for exc_class in exceptions:
            assert exc_class.__doc__ is not None
            assert len(exc_class.__doc__.strip()) > 0
    
    def test_server_exceptions_have_docstrings(self):
        """Test server exceptions have docstrings"""
        exceptions = [TimeoutExceededError, ConnectionException]
        for exc_class in exceptions:
            assert exc_class.__doc__ is not None
            assert len(exc_class.__doc__.strip()) > 0
    
    def test_business_exceptions_have_docstrings(self):
        """Test business logic exceptions have docstrings"""
        exceptions = [WorkflowException, DeviceException, ComplianceException]
        for exc_class in exceptions:
            assert exc_class.__doc__ is not None
            assert len(exc_class.__doc__.strip()) > 0


class TestExceptionIntegration:
    """Integration tests for exception handling"""
    
    def test_exception_with_all_features(self):
        """Test exception with message, details, and custom HTTP status"""
        message = "Validation failed"
        details = {
            "field": "username",
            "value": "invalid_user",
            "constraint": "min_length"
        }
        http_status = 422
        
        error = ValidationException(
            message=message,
            details=details,
            http_status=http_status
        )
        
        assert error.message == message
        assert error.details == details
        assert error.http_status == http_status
        
        # Test dictionary conversion
        error_dict = error.to_dict()
        assert error_dict["error"] == "ValidationException"
        assert error_dict["message"] == message
        assert error_dict["details"] == details
        assert error_dict["http_status"] == http_status
    
    def test_real_world_usage_scenario(self):
        """Test realistic exception usage scenario"""
        def validate_device(device_name):
            if not device_name:
                raise ValidationException(
                    "Device name is required",
                    details={"field": "device_name", "constraint": "required"}
                )
            
            if device_name == "unknown":
                raise NotFoundError(
                    f"Device '{device_name}' not found",
                    details={"device_name": device_name, "available_count": 10}
                )
        
        # Test validation error
        with pytest.raises(ValidationException) as exc_info:
            validate_device("")
        
        assert exc_info.value.http_status == 400
        assert "required" in exc_info.value.message
        
        # Test not found error
        with pytest.raises(NotFoundError) as exc_info:
            validate_device("unknown")
        
        assert exc_info.value.http_status == 404
        assert "not found" in exc_info.value.message
        assert exc_info.value.details["device_name"] == "unknown"