# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from itential_mcp.errors import resource_not_found, resource_already_exists, bad_request


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


class TestResourceAlreadyExists:
    """Test the resource_already_exists utility function"""
    
    def test_resource_already_exists_with_default_message(self):
        """Test resource_already_exists returns default message when no custom message is provided"""
        result = resource_already_exists()
        
        expected = {"message": "The specified resource already exists on the server"}
        assert result == expected
        assert isinstance(result, dict)
        assert "message" in result
    
    def test_resource_already_exists_with_custom_message(self):
        """Test resource_already_exists returns custom message when provided"""
        custom_message = "Device 'router-01' already exists"
        result = resource_already_exists(custom_message)
        
        expected = {"message": custom_message}
        assert result == expected
        assert result["message"] == custom_message
    
    def test_resource_already_exists_with_empty_string_message(self):
        """Test resource_already_exists with empty string message uses default"""
        result = resource_already_exists("")
        
        expected = {"message": "The specified resource already exists on the server"}
        assert result == expected
    
    def test_resource_already_exists_with_none_message(self):
        """Test resource_already_exists with None message uses default"""
        result = resource_already_exists(None)
        
        expected = {"message": "The specified resource already exists on the server"}
        assert result == expected
    
    def test_resource_already_exists_with_whitespace_only_message(self):
        """Test resource_already_exists preserves whitespace-only messages"""
        whitespace_message = "   "
        result = resource_already_exists(whitespace_message)
        
        expected = {"message": whitespace_message}
        assert result == expected
        assert result["message"] == whitespace_message
    
    def test_resource_already_exists_with_multiline_message(self):
        """Test resource_already_exists handles multiline messages"""
        multiline_message = "Resource already exists.\nPlease use a different name."
        result = resource_already_exists(multiline_message)
        
        expected = {"message": multiline_message}
        assert result == expected
        assert result["message"] == multiline_message
    
    def test_resource_already_exists_with_unicode_message(self):
        """Test resource_already_exists handles unicode characters"""
        unicode_message = "Resource '测试设备' already exists"
        result = resource_already_exists(unicode_message)
        
        expected = {"message": unicode_message}
        assert result == expected
        assert result["message"] == unicode_message
    
    def test_resource_already_exists_return_type(self):
        """Test that resource_already_exists always returns a dictionary"""
        result_default = resource_already_exists()
        result_custom = resource_already_exists("custom message")
        
        assert isinstance(result_default, dict)
        assert isinstance(result_custom, dict)
    
    def test_resource_already_exists_return_structure(self):
        """Test that resource_already_exists returns dict with exactly one 'message' key"""
        result = resource_already_exists("test message")
        
        assert len(result) == 1
        assert list(result.keys()) == ["message"]
        assert isinstance(result["message"], str)
    
    def test_resource_already_exists_with_very_long_message(self):
        """Test resource_already_exists handles very long messages"""
        long_message = "B" * 1000  # 1000 character message
        result = resource_already_exists(long_message)
        
        expected = {"message": long_message}
        assert result == expected
        assert len(result["message"]) == 1000
    
    def test_resource_already_exists_message_is_json_serializable(self):
        """Test that the returned dictionary is JSON serializable"""
        import json
        
        result = resource_already_exists("test message")
        
        # This should not raise an exception
        json_string = json.dumps(result)
        parsed_back = json.loads(json_string)
        
        assert parsed_back == result
    
    def test_resource_already_exists_with_special_characters(self):
        """Test resource_already_exists handles special characters in message"""
        special_message = "Resource with ID 'test@#$%^&*()' already exists!"
        result = resource_already_exists(special_message)
        
        expected = {"message": special_message}
        assert result == expected
        assert result["message"] == special_message
    
    def test_resource_already_exists_immutability(self):
        """Test that modifying the returned dict doesn't affect subsequent calls"""
        result1 = resource_already_exists("test message")
        result1["additional_key"] = "should not affect other calls"
        
        result2 = resource_already_exists("test message")
        
        # result2 should not have the additional key added to result1
        assert "additional_key" not in result2
        assert list(result2.keys()) == ["message"]
    
    def test_resource_already_exists_function_signature(self):
        """Test the function signature and parameter defaults"""
        # Test that function can be called without parameters
        result_no_params = resource_already_exists()
        assert result_no_params is not None
        
        # Test that function can be called with positional argument
        result_positional = resource_already_exists("positional message")
        assert result_positional["message"] == "positional message"
        
        # Test that function can be called with keyword argument
        result_keyword = resource_already_exists(msg="keyword message")
        assert result_keyword["message"] == "keyword message"


class TestBadRequest:
    """Test the bad_request utility function"""
    
    def test_bad_request_with_default_message(self):
        """Test bad_request returns default message when no custom message is provided"""
        result = bad_request()
        
        expected = {"message": "Bad Request"}
        assert result == expected
        assert isinstance(result, dict)
        assert "message" in result
    
    def test_bad_request_with_custom_message(self):
        """Test bad_request returns custom message when provided"""
        custom_message = "Invalid input parameters provided"
        result = bad_request(custom_message)
        
        expected = {"message": custom_message}
        assert result == expected
        assert result["message"] == custom_message
    
    def test_bad_request_with_empty_string_message(self):
        """Test bad_request with empty string message uses default"""
        result = bad_request("")
        
        expected = {"message": "Bad Request"}
        assert result == expected
    
    def test_bad_request_with_none_message(self):
        """Test bad_request with None message uses default"""
        result = bad_request(None)
        
        expected = {"message": "Bad Request"}
        assert result == expected
    
    def test_bad_request_with_whitespace_only_message(self):
        """Test bad_request preserves whitespace-only messages"""
        whitespace_message = "   "
        result = bad_request(whitespace_message)
        
        expected = {"message": whitespace_message}
        assert result == expected
        assert result["message"] == whitespace_message
    
    def test_bad_request_with_multiline_message(self):
        """Test bad_request handles multiline messages"""
        multiline_message = "Bad request.\nPlease check your input parameters."
        result = bad_request(multiline_message)
        
        expected = {"message": multiline_message}
        assert result == expected
        assert result["message"] == multiline_message
    
    def test_bad_request_with_unicode_message(self):
        """Test bad_request handles unicode characters"""
        unicode_message = "Invalid request: 无效参数"
        result = bad_request(unicode_message)
        
        expected = {"message": unicode_message}
        assert result == expected
        assert result["message"] == unicode_message
    
    def test_bad_request_return_type(self):
        """Test that bad_request always returns a dictionary"""
        result_default = bad_request()
        result_custom = bad_request("custom message")
        
        assert isinstance(result_default, dict)
        assert isinstance(result_custom, dict)
    
    def test_bad_request_return_structure(self):
        """Test that bad_request returns dict with exactly one 'message' key"""
        result = bad_request("test message")
        
        assert len(result) == 1
        assert list(result.keys()) == ["message"]
        assert isinstance(result["message"], str)
    
    def test_bad_request_with_very_long_message(self):
        """Test bad_request handles very long messages"""
        long_message = "C" * 1000  # 1000 character message
        result = bad_request(long_message)
        
        expected = {"message": long_message}
        assert result == expected
        assert len(result["message"]) == 1000
    
    def test_bad_request_message_is_json_serializable(self):
        """Test that the returned dictionary is JSON serializable"""
        import json
        
        result = bad_request("test message")
        
        # This should not raise an exception
        json_string = json.dumps(result)
        parsed_back = json.loads(json_string)
        
        assert parsed_back == result
    
    def test_bad_request_with_special_characters(self):
        """Test bad_request handles special characters in message"""
        special_message = "Invalid parameter value '@#$%^&*()' provided"
        result = bad_request(special_message)
        
        expected = {"message": special_message}
        assert result == expected
        assert result["message"] == special_message
    
    def test_bad_request_immutability(self):
        """Test that modifying the returned dict doesn't affect subsequent calls"""
        result1 = bad_request("test message")
        result1["additional_key"] = "should not affect other calls"
        
        result2 = bad_request("test message")
        
        # result2 should not have the additional key added to result1
        assert "additional_key" not in result2
        assert list(result2.keys()) == ["message"]
    
    def test_bad_request_function_signature(self):
        """Test the function signature and parameter defaults"""
        # Test that function can be called without parameters
        result_no_params = bad_request()
        assert result_no_params is not None
        
        # Test that function can be called with positional argument
        result_positional = bad_request("positional message")
        assert result_positional["message"] == "positional message"
        
        # Test that function can be called with keyword argument
        result_keyword = bad_request(msg="keyword message")
        assert result_keyword["message"] == "keyword message"


class TestResourceAlreadyExistsIntegration:
    """Integration tests for resource_already_exists function"""
    
    def test_resource_already_exists_usage_in_api_response(self):
        """Test realistic usage scenario for API error responses"""
        def mock_api_creation_handler(resource_id):
            # Simulate resource creation attempt
            existing_resources = ["device-01", "device-02"]
            if resource_id in existing_resources:
                return {
                    "status": "error",
                    "error": resource_already_exists(f"Resource with ID '{resource_id}' already exists")
                }
            return {"status": "success", "data": {"id": resource_id, "created": True}}
        
        # Test error case
        error_response = mock_api_creation_handler("device-01")
        assert error_response["status"] == "error"
        assert "message" in error_response["error"]
        assert "device-01" in error_response["error"]["message"]
        
        # Test success case
        success_response = mock_api_creation_handler("device-03")
        assert success_response["status"] == "success"
    
    def test_resource_already_exists_with_formatted_strings(self):
        """Test resource_already_exists with formatted string messages"""
        resource_type = "workflow"
        resource_name = "backup-procedure"
        message = f"{resource_type.title()} '{resource_name}' already exists in the system"
        
        result = resource_already_exists(message)
        
        assert result["message"] == "Workflow 'backup-procedure' already exists in the system"
    
    def test_resource_already_exists_consistency_across_calls(self):
        """Test that multiple calls with same input return equivalent results"""
        message = "Test resource already exists"
        
        result1 = resource_already_exists(message)
        result2 = resource_already_exists(message)
        result3 = resource_already_exists(message)
        
        assert result1 == result2 == result3
        assert result1 is not result2  # Different objects
        assert result1 is not result3  # Different objects


class TestBadRequestIntegration:
    """Integration tests for bad_request function"""
    
    def test_bad_request_usage_in_validation_scenario(self):
        """Test realistic usage scenario for input validation"""
        def validate_input(data):
            required_fields = ["name", "type"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return {
                    "status": "error",
                    "error": bad_request(f"Missing required fields: {', '.join(missing_fields)}")
                }
            return {"status": "success", "data": data}
        
        # Test error case
        invalid_data = {"name": "test-device"}
        error_response = validate_input(invalid_data)
        assert error_response["status"] == "error"
        assert "message" in error_response["error"]
        assert "type" in error_response["error"]["message"]
        
        # Test success case
        valid_data = {"name": "test-device", "type": "router"}
        success_response = validate_input(valid_data)
        assert success_response["status"] == "success"
    
    def test_bad_request_with_parameter_validation(self):
        """Test bad_request in parameter validation scenarios"""
        def validate_port(port):
            if not isinstance(port, int):
                return bad_request("Port must be an integer")
            if port < 1 or port > 65535:
                return bad_request("Port must be between 1 and 65535")
            return {"valid": True, "port": port}
        
        # Test type error
        type_error = validate_port("8080")
        assert "integer" in type_error["message"]
        
        # Test range error
        range_error = validate_port(70000)
        assert "between 1 and 65535" in range_error["message"]
        
        # Test valid input
        valid_result = validate_port(8080)
        assert valid_result["valid"] is True
    
    def test_bad_request_consistency_across_calls(self):
        """Test that multiple calls with same input return equivalent results"""
        message = "Invalid request format"
        
        result1 = bad_request(message)
        result2 = bad_request(message)
        result3 = bad_request(message)
        
        assert result1 == result2 == result3
        assert result1 is not result2  # Different objects
        assert result1 is not result3  # Different objects


class TestErrorFunctionsComparison:
    """Test comparing behavior across all error functions"""
    
    def test_all_functions_return_dict_with_message_key(self):
        """Test that all error functions return consistent structure"""
        result1 = resource_not_found("test")
        result2 = resource_already_exists("test")
        result3 = bad_request("test")
        
        for result in [result1, result2, result3]:
            assert isinstance(result, dict)
            assert len(result) == 1
            assert "message" in result
            assert isinstance(result["message"], str)
    
    def test_all_functions_handle_none_input(self):
        """Test that all error functions handle None input consistently"""
        result1 = resource_not_found(None)
        result2 = resource_already_exists(None)
        result3 = bad_request(None)
        
        # All should return their default messages
        assert result1["message"] == "A resource could not be found on the server"
        assert result2["message"] == "The specified resource already exists on the server"
        assert result3["message"] == "Bad Request"
    
    def test_all_functions_handle_empty_string_input(self):
        """Test that all error functions handle empty string input consistently"""
        result1 = resource_not_found("")
        result2 = resource_already_exists("")
        result3 = bad_request("")
        
        # All should return their default messages for empty string (falsy)
        assert result1["message"] == "A resource could not be found on the server"
        assert result2["message"] == "The specified resource already exists on the server"
        assert result3["message"] == "Bad Request"
    
    def test_all_functions_preserve_custom_messages(self):
        """Test that all error functions preserve custom messages"""
        custom_msg = "Custom error message"
        
        result1 = resource_not_found(custom_msg)
        result2 = resource_already_exists(custom_msg)
        result3 = bad_request(custom_msg)
        
        assert result1["message"] == custom_msg
        assert result2["message"] == custom_msg
        assert result3["message"] == custom_msg
    
    def test_all_functions_json_serializable(self):
        """Test that all error functions return JSON serializable results"""
        import json
        
        results = [
            resource_not_found("test"),
            resource_already_exists("test"),
            bad_request("test")
        ]
        
        for result in results:
            json_string = json.dumps(result)
            parsed_back = json.loads(json_string)
            assert parsed_back == result
    
    def test_all_functions_different_default_messages(self):
        """Test that all error functions have different default messages"""
        result1 = resource_not_found()
        result2 = resource_already_exists()
        result3 = bad_request()
        
        messages = [result1["message"], result2["message"], result3["message"]]
        
        # All messages should be different
        assert len(set(messages)) == 3
        assert result1["message"] != result2["message"]
        assert result1["message"] != result3["message"]
        assert result2["message"] != result3["message"]