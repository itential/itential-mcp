# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from itential_mcp.errors import resource_not_found


class TestResourceNotFound:
    """Test the resource_not_found utility function"""
    
    def test_resource_not_found_with_default_message(self):
        """Test resource_not_found returns default message when no custom message is provided"""
        result = resource_not_found()
        
        expected = {"message": "A resource could not be found on the server"}
        assert result == expected
        assert isinstance(result, dict)
        assert "message" in result
    
    def test_resource_not_found_with_custom_message(self):
        """Test resource_not_found returns custom message when provided"""
        custom_message = "Device 'router-01' could not be found"
        result = resource_not_found(custom_message)
        
        expected = {"message": custom_message}
        assert result == expected
        assert result["message"] == custom_message
    
    def test_resource_not_found_with_empty_string_message(self):
        """Test resource_not_found with empty string message uses default"""
        result = resource_not_found("")
        
        expected = {"message": "A resource could not be found on the server"}
        assert result == expected
    
    def test_resource_not_found_with_none_message(self):
        """Test resource_not_found with None message uses default"""
        result = resource_not_found(None)
        
        expected = {"message": "A resource could not be found on the server"}
        assert result == expected
    
    def test_resource_not_found_with_whitespace_only_message(self):
        """Test resource_not_found preserves whitespace-only messages"""
        whitespace_message = "   "
        result = resource_not_found(whitespace_message)
        
        expected = {"message": whitespace_message}
        assert result == expected
        assert result["message"] == whitespace_message
    
    def test_resource_not_found_with_multiline_message(self):
        """Test resource_not_found handles multiline messages"""
        multiline_message = "Resource not found.\nPlease check the resource name and try again."
        result = resource_not_found(multiline_message)
        
        expected = {"message": multiline_message}
        assert result == expected
        assert result["message"] == multiline_message
    
    def test_resource_not_found_with_unicode_message(self):
        """Test resource_not_found handles unicode characters"""
        unicode_message = "Resource '测试设备' not found"
        result = resource_not_found(unicode_message)
        
        expected = {"message": unicode_message}
        assert result == expected
        assert result["message"] == unicode_message
    
    def test_resource_not_found_return_type(self):
        """Test that resource_not_found always returns a dictionary"""
        result_default = resource_not_found()
        result_custom = resource_not_found("custom message")
        
        assert isinstance(result_default, dict)
        assert isinstance(result_custom, dict)
    
    def test_resource_not_found_return_structure(self):
        """Test that resource_not_found returns dict with exactly one 'message' key"""
        result = resource_not_found("test message")
        
        assert len(result) == 1
        assert list(result.keys()) == ["message"]
        assert isinstance(result["message"], str)
    
    def test_resource_not_found_with_very_long_message(self):
        """Test resource_not_found handles very long messages"""
        long_message = "A" * 1000  # 1000 character message
        result = resource_not_found(long_message)
        
        expected = {"message": long_message}
        assert result == expected
        assert len(result["message"]) == 1000
    
    def test_resource_not_found_message_is_json_serializable(self):
        """Test that the returned dictionary is JSON serializable"""
        import json
        
        result = resource_not_found("test message")
        
        # This should not raise an exception
        json_string = json.dumps(result)
        parsed_back = json.loads(json_string)
        
        assert parsed_back == result
    
    def test_resource_not_found_with_special_characters(self):
        """Test resource_not_found handles special characters in message"""
        special_message = "Resource with ID 'test@#$%^&*()' not found!"
        result = resource_not_found(special_message)
        
        expected = {"message": special_message}
        assert result == expected
        assert result["message"] == special_message
    
    def test_resource_not_found_immutability(self):
        """Test that modifying the returned dict doesn't affect subsequent calls"""
        result1 = resource_not_found("test message")
        result1["additional_key"] = "should not affect other calls"
        
        result2 = resource_not_found("test message")
        
        # result2 should not have the additional key added to result1
        assert "additional_key" not in result2
        assert list(result2.keys()) == ["message"]
    
    def test_resource_not_found_function_signature(self):
        """Test the function signature and parameter defaults"""
        # Test that function can be called without parameters
        result_no_params = resource_not_found()
        assert result_no_params is not None
        
        # Test that function can be called with positional argument
        result_positional = resource_not_found("positional message")
        assert result_positional["message"] == "positional message"
        
        # Test that function can be called with keyword argument
        result_keyword = resource_not_found(msg="keyword message")
        assert result_keyword["message"] == "keyword message"


class TestResourceNotFoundIntegration:
    """Integration tests for resource_not_found function"""
    
    def test_resource_not_found_usage_in_api_response(self):
        """Test realistic usage scenario for API error responses"""
        def mock_api_handler(resource_id):
            # Simulate resource lookup failure
            if resource_id == "nonexistent":
                return {
                    "status": "error",
                    "error": resource_not_found(f"Resource with ID '{resource_id}' not found")
                }
            return {"status": "success", "data": {"id": resource_id}}
        
        # Test error case
        error_response = mock_api_handler("nonexistent")
        assert error_response["status"] == "error"
        assert "message" in error_response["error"]
        assert "nonexistent" in error_response["error"]["message"]
        
        # Test success case
        success_response = mock_api_handler("valid-id")
        assert success_response["status"] == "success"
    
    def test_resource_not_found_with_formatted_strings(self):
        """Test resource_not_found with formatted string messages"""
        resource_type = "device"
        resource_id = "router-01"
        message = f"{resource_type.title()} '{resource_id}' could not be found"
        
        result = resource_not_found(message)
        
        assert result["message"] == "Device 'router-01' could not be found"
    
    def test_resource_not_found_error_logging_scenario(self):
        """Test usage scenario for error logging"""
        def log_resource_error(resource_name, details=None):
            base_message = f"Failed to locate resource: {resource_name}"
            if details:
                base_message += f" - {details}"
            return resource_not_found(base_message)
        
        # Test with just resource name
        simple_error = log_resource_error("test-resource")
        assert "test-resource" in simple_error["message"]
        
        # Test with additional details
        detailed_error = log_resource_error("test-resource", "Connection timeout")
        assert "test-resource" in detailed_error["message"]
        assert "Connection timeout" in detailed_error["message"]
    
    def test_resource_not_found_consistency_across_calls(self):
        """Test that multiple calls with same input return equivalent results"""
        message = "Test resource not found"
        
        result1 = resource_not_found(message)
        result2 = resource_not_found(message)
        result3 = resource_not_found(message)
        
        assert result1 == result2 == result3
        assert result1 is not result2  # Different objects
        assert result1 is not result3  # Different objects