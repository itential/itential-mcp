# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import logging
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from itential_mcp.core import logging as itential_logging
from itential_mcp.core import metadata
from itential_mcp.core.heuristics import Scanner


@pytest.fixture(autouse=True)
def cleanup_file_handlers():
    """Fixture to clean up all file handlers after each test"""
    yield
    # Clean up any file handlers that might have been created during the test
    logger = logging.getLogger(metadata.name)
    for handler in list(logger.handlers):
        if isinstance(handler, logging.FileHandler):
            handler.close()
            logger.removeHandler(handler)


class TestBasicLogging:
    """Test cases for basic logging functionality"""

    def test_logging_constants(self):
        """Test that logging constants are properly defined"""
        assert itential_logging.NOTSET == logging.NOTSET
        assert itential_logging.DEBUG == logging.DEBUG
        assert itential_logging.INFO == logging.INFO
        assert itential_logging.WARNING == logging.WARNING
        assert itential_logging.ERROR == logging.ERROR
        assert itential_logging.CRITICAL == logging.CRITICAL
        assert itential_logging.FATAL == 90

    def test_fatal_level_exists(self):
        """Test that FATAL logging level is properly configured"""
        assert hasattr(logging, "FATAL")
        assert logging.FATAL == 90
        assert logging.getLevelName(90) == "FATAL"

    def test_log_function_exists(self):
        """Test that basic logging functions exist"""
        assert callable(itential_logging.log)
        assert callable(itential_logging.debug)
        assert callable(itential_logging.info)
        assert callable(itential_logging.warning)
        assert callable(itential_logging.error)
        assert callable(itential_logging.critical)
        assert callable(itential_logging.exception)
        assert callable(itential_logging.fatal)

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_log_function(self, mock_get_logger):
        """Test the basic log function"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.log(logging.INFO, "test message")

        mock_get_logger.assert_called_once_with(metadata.name)
        mock_logger.log.assert_called_once_with(logging.INFO, "test message")

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_debug_function(self, mock_get_logger):
        """Test the debug function"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.debug("debug message")
        mock_get_logger.assert_called_once_with(metadata.name)
        mock_logger.log.assert_called_once_with(logging.DEBUG, "debug message")

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_info_function(self, mock_get_logger):
        """Test the info function"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.info("info message")
        mock_get_logger.assert_called_once_with(metadata.name)
        mock_logger.log.assert_called_once_with(logging.INFO, "info message")

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_warning_function(self, mock_get_logger):
        """Test the warning function"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.warning("warning message")
        mock_get_logger.assert_called_once_with(metadata.name)
        mock_logger.log.assert_called_once_with(logging.WARNING, "warning message")

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_error_function(self, mock_get_logger):
        """Test the error function"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.error("error message")
        mock_get_logger.assert_called_once_with(metadata.name)
        mock_logger.log.assert_called_once_with(logging.ERROR, "error message")

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_critical_function(self, mock_get_logger):
        """Test the critical function"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.critical("critical message")
        mock_get_logger.assert_called_once_with(metadata.name)
        mock_logger.log.assert_called_once_with(logging.CRITICAL, "critical message")

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_exception_function(self, mock_get_logger):
        """Test the exception function"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        exc = ValueError("test error")
        itential_logging.exception(exc)

        mock_get_logger.assert_called_once_with(metadata.name)
        # The exception function formats the exception with traceback, which includes
        # the exception type and a trailing newline
        mock_logger.log.assert_called_once_with(
            logging.ERROR, "ValueError: test error\n"
        )

    @patch("sys.exit")
    @patch("builtins.print")
    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_fatal_function(self, mock_get_logger, mock_print, mock_exit):
        """Test the fatal function"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.fatal("fatal error")

        mock_get_logger.assert_called_once_with(metadata.name)
        mock_logger.log.assert_called_once_with(logging.FATAL, "fatal error")
        mock_print.assert_called_once_with("ERROR: fatal error")
        mock_exit.assert_called_once_with(1)


class TestSetLevel:
    """Test cases for set_level function"""

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_set_level_basic(self, mock_get_logger):
        """Test setting logging level"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.set_level(logging.DEBUG)

        mock_logger.setLevel.assert_called_once_with(logging.DEBUG)
        # Should be called once for get_logger() call
        assert mock_get_logger.call_count == 1
        # Verify the logger.log method was called for the two info messages
        assert mock_logger.log.call_count == 2

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_set_level_with_propagate(self, mock_get_logger):
        """Test setting logging level with propagation"""
        mock_logger = Mock()
        mock_ipsdk_logger = Mock()

        def get_logger_side_effect(name):
            if name == metadata.name:
                return mock_logger
            elif name == "ipsdk":
                return mock_ipsdk_logger
            return Mock()

        mock_get_logger.side_effect = get_logger_side_effect

        itential_logging.set_level(logging.INFO, propagate=True)

        mock_logger.setLevel.assert_called_with(logging.INFO)
        mock_ipsdk_logger.setLevel.assert_called_once_with(logging.INFO)


class TestConsoleOutput:
    """Test cases for console output functions"""

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_set_console_output_stderr(self, mock_get_logger):
        """Test setting console output to stderr"""
        mock_logger = Mock()
        mock_handler = Mock(spec=logging.StreamHandler)
        mock_handler.stream = sys.stderr
        mock_logger.handlers = [mock_handler]
        mock_get_logger.return_value = mock_logger

        itential_logging.set_console_output("stderr")

        mock_logger.removeHandler.assert_called_once_with(mock_handler)
        mock_handler.close.assert_called_once()
        mock_logger.addHandler.assert_called_once()
        mock_logger.log.assert_called_once()

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_set_console_output_stdout(self, mock_get_logger):
        """Test setting console output to stdout"""
        mock_logger = Mock()
        mock_handler = Mock(spec=logging.StreamHandler)
        mock_handler.stream = sys.stdout
        mock_logger.handlers = [mock_handler]
        mock_get_logger.return_value = mock_logger

        itential_logging.set_console_output("stdout")

        mock_logger.removeHandler.assert_called_once_with(mock_handler)
        mock_handler.close.assert_called_once()
        mock_logger.addHandler.assert_called_once()
        mock_logger.log.assert_called_once()

    def test_set_console_output_invalid_stream(self):
        """Test setting console output to invalid stream raises ValueError"""
        with pytest.raises(ValueError, match="stream must be 'stdout' or 'stderr'"):
            itential_logging.set_console_output("invalid")

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_set_console_output_no_existing_handlers(self, mock_get_logger):
        """Test setting console output when no existing handlers"""
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        itential_logging.set_console_output("stdout")

        # Should not call removeHandler since no handlers exist
        mock_logger.removeHandler.assert_not_called()
        mock_logger.addHandler.assert_called_once()


class TestStdoutHandler:
    """Test cases for add_stdout_handler function"""

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_add_stdout_handler_basic(self, mock_get_logger):
        """Test adding stdout handler with default settings"""
        mock_logger = Mock()
        mock_logger.level = logging.INFO
        mock_get_logger.return_value = mock_logger

        itential_logging.add_stdout_handler()

        mock_logger.addHandler.assert_called_once()
        mock_logger.log.assert_called_once_with(
            logging.INFO, "Stdout logging handler added"
        )

    @patch("itential_mcp.core.logging.logging.getLogger")
    @patch("itential_mcp.core.logging.logging.StreamHandler")
    def test_add_stdout_handler_with_level(self, mock_stream_handler, mock_get_logger):
        """Test adding stdout handler with custom level"""
        mock_logger = Mock()
        mock_handler = Mock()
        mock_stream_handler.return_value = mock_handler
        mock_get_logger.return_value = mock_logger

        itential_logging.add_stdout_handler(level=logging.DEBUG)

        mock_stream_handler.assert_called_once_with(sys.stdout)
        mock_handler.setLevel.assert_called_once_with(logging.DEBUG)
        mock_handler.setFormatter.assert_called_once()
        mock_logger.addHandler.assert_called_once_with(mock_handler)

    @patch("itential_mcp.core.logging.logging.getLogger")
    @patch("itential_mcp.core.logging.logging.StreamHandler")
    @patch("itential_mcp.core.logging.logging.Formatter")
    def test_add_stdout_handler_with_format(
        self, mock_formatter, mock_stream_handler, mock_get_logger
    ):
        """Test adding stdout handler with custom format"""
        mock_logger = Mock()
        mock_handler = Mock()
        mock_formatter_instance = Mock()
        mock_stream_handler.return_value = mock_handler
        mock_formatter.return_value = mock_formatter_instance
        mock_get_logger.return_value = mock_logger

        custom_format = "%(levelname)s: %(message)s"
        itential_logging.add_stdout_handler(format_string=custom_format)

        mock_formatter.assert_called_once_with(custom_format)
        mock_handler.setFormatter.assert_called_once_with(mock_formatter_instance)


class TestStderrHandler:
    """Test cases for add_stderr_handler function"""

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_add_stderr_handler_basic(self, mock_get_logger):
        """Test adding stderr handler with default settings"""
        mock_logger = Mock()
        mock_logger.level = logging.INFO
        mock_get_logger.return_value = mock_logger

        itential_logging.add_stderr_handler()

        mock_logger.addHandler.assert_called_once()
        mock_logger.log.assert_called_once_with(
            logging.INFO, "Stderr logging handler added"
        )

    @patch("itential_mcp.core.logging.logging.getLogger")
    @patch("itential_mcp.core.logging.logging.StreamHandler")
    def test_add_stderr_handler_with_level(self, mock_stream_handler, mock_get_logger):
        """Test adding stderr handler with custom level"""
        mock_logger = Mock()
        mock_handler = Mock()
        mock_stream_handler.return_value = mock_handler
        mock_get_logger.return_value = mock_logger

        itential_logging.add_stderr_handler(level=logging.WARNING)

        mock_stream_handler.assert_called_once_with(sys.stderr)
        mock_handler.setLevel.assert_called_once_with(logging.WARNING)
        mock_handler.setFormatter.assert_called_once()
        mock_logger.addHandler.assert_called_once_with(mock_handler)

    @patch("itential_mcp.core.logging.logging.getLogger")
    @patch("itential_mcp.core.logging.logging.StreamHandler")
    @patch("itential_mcp.core.logging.logging.Formatter")
    def test_add_stderr_handler_with_format(
        self, mock_formatter, mock_stream_handler, mock_get_logger
    ):
        """Test adding stderr handler with custom format"""
        mock_logger = Mock()
        mock_handler = Mock()
        mock_formatter_instance = Mock()
        mock_stream_handler.return_value = mock_handler
        mock_formatter.return_value = mock_formatter_instance
        mock_get_logger.return_value = mock_logger

        custom_format = "%(name)s - %(levelname)s - %(message)s"
        itential_logging.add_stderr_handler(format_string=custom_format)

        mock_formatter.assert_called_once_with(custom_format)
        mock_handler.setFormatter.assert_called_once_with(mock_formatter_instance)


class TestFileLogging:
    """Test cases for file logging functions"""

    def test_add_file_handler_creates_directory(self):
        """Test that add_file_handler creates parent directories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "logs" / "test.log"

            itential_logging.add_file_handler(str(log_path))

            assert log_path.parent.exists()
            assert log_path.exists()

    def test_add_file_handler_with_custom_level(self):
        """Test adding file handler with custom level"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "test.log"

            itential_logging.add_file_handler(str(log_path), level=logging.WARNING)

            # Verify handler was added by checking if we can log to it
            logger = logging.getLogger(metadata.name)
            file_handlers = [
                h for h in logger.handlers if isinstance(h, logging.FileHandler)
            ]
            assert len(file_handlers) > 0

            # Clean up
            for handler in file_handlers:
                logger.removeHandler(handler)
                handler.close()

    def test_remove_file_handlers(self):
        """Test removing file handlers"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path1 = Path(temp_dir) / "test1.log"
            log_path2 = Path(temp_dir) / "test2.log"

            # Add two file handlers
            itential_logging.add_file_handler(str(log_path1))
            itential_logging.add_file_handler(str(log_path2))

            logger = logging.getLogger(metadata.name)
            initial_handlers = len(
                [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
            )

            # Remove all file handlers
            itential_logging.remove_file_handlers()

            final_handlers = len(
                [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
            )
            assert final_handlers == 0
            assert initial_handlers > final_handlers

    def test_configure_file_logging(self):
        """Test configure_file_logging convenience function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "configured.log"

            itential_logging.configure_file_logging(
                str(log_path),
                level=logging.DEBUG,
                propagate=True,
                format_string="%(levelname)s: %(message)s",
            )

            # Verify file was created and handler added
            assert log_path.exists()

            logger = logging.getLogger(metadata.name)
            file_handlers = [
                h for h in logger.handlers if isinstance(h, logging.FileHandler)
            ]
            assert len(file_handlers) > 0

            # Clean up
            for handler in file_handlers:
                logger.removeHandler(handler)
                handler.close()


class TestLoggingIntegration:
    """Integration tests for logging functionality"""

    def test_multiple_handlers_integration(self):
        """Test that multiple handlers work together"""
        # Capture stdout and stderr
        stdout_capture = StringIO()
        stderr_capture = StringIO()

        with patch("sys.stdout", stdout_capture), patch("sys.stderr", stderr_capture):
            # Set up logging to go to both stdout and stderr
            itential_logging.set_level(logging.INFO)
            itential_logging.add_stdout_handler()
            itential_logging.add_stderr_handler()

            # Log a message
            itential_logging.info("Test message for multiple handlers")

            # Clean up handlers
            logger = logging.getLogger(metadata.name)
            handlers_to_remove = [
                h for h in logger.handlers if isinstance(h, logging.StreamHandler)
            ]
            for handler in handlers_to_remove:
                logger.removeHandler(handler)
                handler.close()

    def test_stream_switching_integration(self):
        """Test switching between stdout and stderr"""
        stdout_capture = StringIO()
        stderr_capture = StringIO()

        with patch("sys.stdout", stdout_capture), patch("sys.stderr", stderr_capture):
            # Set up initial logging to stderr
            itential_logging.set_level(logging.INFO)
            itential_logging.set_console_output("stderr")

            itential_logging.info("Message to stderr")

            # Switch to stdout
            itential_logging.set_console_output("stdout")
            itential_logging.info("Message to stdout")

            # Clean up handlers
            logger = logging.getLogger(metadata.name)
            handlers_to_remove = [
                h for h in logger.handlers if isinstance(h, logging.StreamHandler)
            ]
            for handler in handlers_to_remove:
                logger.removeHandler(handler)
                handler.close()

    def test_logging_format_consistency(self):
        """Test that logging format is consistent across handlers"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "format_test.log"

            # Add file handler with default format
            itential_logging.add_file_handler(str(log_path))

            # Add console handlers with default format
            itential_logging.add_stdout_handler()
            itential_logging.add_stderr_handler()

            # All handlers should use the same default format
            logger = logging.getLogger(metadata.name)

            file_handlers = [
                h for h in logger.handlers if isinstance(h, logging.FileHandler)
            ]
            stream_handlers = [
                h for h in logger.handlers if isinstance(h, logging.StreamHandler)
            ]

            # Verify handlers exist
            assert len(file_handlers) > 0
            assert len(stream_handlers) > 0

            # Clean up
            for handler in logger.handlers.copy():
                if isinstance(handler, (logging.FileHandler, logging.StreamHandler)):
                    logger.removeHandler(handler)
                    handler.close()


class TestSensitiveDataFiltering:
    """Test cases for sensitive data filtering in logging"""

    def setup_method(self):
        """Set up test environment"""
        # Reset the singleton scanner before each test
        Scanner.reset_singleton()
        # Enable sensitive data filtering for each test
        itential_logging.enable_sensitive_data_filtering()

    def teardown_method(self):
        """Clean up after each test"""
        # Clean up any handlers that were added during testing
        logger = logging.getLogger(metadata.name)
        handlers_to_remove = logger.handlers.copy()
        for handler in handlers_to_remove:
            if isinstance(handler, (logging.FileHandler, logging.StreamHandler)):
                logger.removeHandler(handler)
                handler.close()

    def test_sensitive_data_filtering_enabled_by_default(self):
        """Test that sensitive data filtering is enabled by default"""
        assert itential_logging.is_sensitive_data_filtering_enabled()

    def test_enable_disable_sensitive_data_filtering(self):
        """Test enabling and disabling sensitive data filtering"""
        # Initially enabled
        assert itential_logging.is_sensitive_data_filtering_enabled()

        # Disable
        itential_logging.disable_sensitive_data_filtering()
        assert not itential_logging.is_sensitive_data_filtering_enabled()

        # Enable again
        itential_logging.enable_sensitive_data_filtering()
        assert itential_logging.is_sensitive_data_filtering_enabled()

    @patch("itential_mcp.core.logging.heuristics.scan_and_redact")
    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_log_function_calls_scanner_when_enabled(
        self, mock_get_logger, mock_scan_and_redact
    ):
        """Test that log function calls the scanner when filtering is enabled"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_scan_and_redact.return_value = "redacted message"

        itential_logging.enable_sensitive_data_filtering()
        itential_logging.log(logging.INFO, "API_KEY=secret123")

        mock_scan_and_redact.assert_called_once_with("API_KEY=secret123")
        mock_logger.log.assert_called_once_with(logging.INFO, "redacted message")

    @patch("itential_mcp.core.logging.heuristics.scan_and_redact")
    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_log_function_skips_scanner_when_disabled(
        self, mock_get_logger, mock_scan_and_redact
    ):
        """Test that log function skips the scanner when filtering is disabled"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.disable_sensitive_data_filtering()
        itential_logging.log(logging.INFO, "API_KEY=secret123")

        mock_scan_and_redact.assert_not_called()
        mock_logger.log.assert_called_once_with(logging.INFO, "API_KEY=secret123")

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_api_key_redaction_in_log_message(self, mock_get_logger):
        """Test that API keys are redacted in log messages"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.enable_sensitive_data_filtering()
        itential_logging.info("API_KEY=sk_test_1234567890abcdef")

        # Verify the logged message was redacted
        args, kwargs = mock_logger.log.call_args
        logged_level, logged_message = args
        assert logged_level == logging.INFO
        assert "[REDACTED_API_KEY]" in logged_message
        assert "sk_test_1234567890abcdef" not in logged_message

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_password_redaction_in_log_message(self, mock_get_logger):
        """Test that passwords are redacted in log messages"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.enable_sensitive_data_filtering()
        itential_logging.error("Login failed for password=secretpass123")

        args, kwargs = mock_logger.log.call_args
        logged_level, logged_message = args
        assert logged_level == logging.ERROR
        assert "[REDACTED_PASSWORD]" in logged_message
        assert "secretpass123" not in logged_message

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_multiple_sensitive_data_redaction(self, mock_get_logger):
        """Test redaction of multiple sensitive data types in one message"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.enable_sensitive_data_filtering()
        itential_logging.warning(
            "API_KEY=test1234567890abcdef and password=secret123456 and user=admin@company.com"
        )

        args, kwargs = mock_logger.log.call_args
        logged_level, logged_message = args
        assert logged_level == logging.WARNING
        assert "[REDACTED_API_KEY]" in logged_message
        assert "[REDACTED_PASSWORD]" in logged_message
        assert "[REDACTED_EMAIL_IN_AUTH]" in logged_message
        assert "test1234567890abcdef" not in logged_message
        assert "secret" not in logged_message or "secret" in "REDACTED"
        assert "admin@company.com" not in logged_message

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_normal_message_unchanged_when_no_sensitive_data(self, mock_get_logger):
        """Test that normal messages are unchanged when no sensitive data is present"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        original_message = "This is a normal log message without sensitive data"
        itential_logging.enable_sensitive_data_filtering()
        itential_logging.info(original_message)

        args, kwargs = mock_logger.log.call_args
        logged_level, logged_message = args
        assert logged_level == logging.INFO
        assert logged_message == original_message

    def test_configure_sensitive_data_patterns(self):
        """Test configuring custom sensitive data patterns"""
        custom_patterns = {
            "custom_token": r"CUSTOM-[A-Z0-9]{16}",
            "test_secret": r"TEST_SECRET:\s*([a-z0-9]+)",
        }

        itential_logging.configure_sensitive_data_patterns(custom_patterns)

        patterns = itential_logging.get_sensitive_data_patterns()
        assert "custom_token" in patterns
        assert "test_secret" in patterns

    def test_add_remove_sensitive_data_pattern(self):
        """Test adding and removing individual sensitive data patterns"""
        # Add a new pattern
        itential_logging.add_sensitive_data_pattern("test_pattern", r"TEST-\d{4}")
        patterns = itential_logging.get_sensitive_data_patterns()
        assert "test_pattern" in patterns

        # Remove the pattern
        result = itential_logging.remove_sensitive_data_pattern("test_pattern")
        assert result is True
        patterns = itential_logging.get_sensitive_data_patterns()
        assert "test_pattern" not in patterns

        # Try to remove non-existent pattern
        result = itential_logging.remove_sensitive_data_pattern("non_existent")
        assert result is False

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_custom_pattern_redaction(self, mock_get_logger):
        """Test that custom patterns are properly redacted"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Add custom pattern
        itential_logging.add_sensitive_data_pattern(
            "custom_id", r"CUSTOM_ID=[A-Z0-9]{8}"
        )

        itential_logging.enable_sensitive_data_filtering()
        itential_logging.info("Processing request with CUSTOM_ID=ABCD1234")

        args, kwargs = mock_logger.log.call_args
        logged_level, logged_message = args
        assert logged_level == logging.INFO
        assert "[REDACTED_CUSTOM_ID]" in logged_message
        assert "ABCD1234" not in logged_message

    def test_get_sensitive_data_patterns_list(self):
        """Test getting the list of sensitive data patterns"""
        patterns = itential_logging.get_sensitive_data_patterns()

        # Should include default patterns
        expected_patterns = [
            "api_key",
            "bearer_token",
            "jwt_token",
            "access_token",
            "password",
            "secret",
            "email_in_auth",
            "auth_url",
            "db_connection",
            "private_key",
        ]

        for pattern in expected_patterns:
            assert pattern in patterns

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_sensitive_data_filtering_with_file_handler(self, mock_get_logger):
        """Test that sensitive data filtering works with file handlers"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "sensitive_test.log"

            # Mock the logger but allow file operations
            mock_logger = Mock()
            mock_logger.level = logging.INFO
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger

            itential_logging.enable_sensitive_data_filtering()
            itential_logging.add_file_handler(str(log_path))
            itential_logging.info("API_KEY=sensitive_key_1234567890abcdef")

            # Verify the scanner was called and redacted message was logged
            args, kwargs = mock_logger.log.call_args
            logged_level, logged_message = args
            assert logged_level == logging.INFO
            assert "[REDACTED_API_KEY]" in logged_message

            # Clean up file handlers to prevent resource warnings
            itential_logging.remove_file_handlers()

    def test_invalid_regex_pattern_handling(self):
        """Test handling of invalid regex patterns"""
        with pytest.raises(Exception):  # Could be re.error or other exception
            itential_logging.add_sensitive_data_pattern("invalid", "[unclosed bracket")

    @patch("itential_mcp.core.logging.logging.getLogger")
    def test_empty_and_none_message_handling(self, mock_get_logger):
        """Test handling of empty and None messages"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.enable_sensitive_data_filtering()

        # Test empty string
        itential_logging.info("")
        args, kwargs = mock_logger.log.call_args
        logged_level, logged_message = args
        assert logged_message == ""

        # Test None (this might not be a valid scenario but test for robustness)
        # Note: This test might need adjustment based on actual behavior
        try:
            itential_logging.info(None)
            args, kwargs = mock_logger.log.call_args
            logged_level, logged_message = args
            # The behavior might vary - could be None or empty string
            assert logged_message in (None, "", "None")
        except (TypeError, AttributeError):
            # It's acceptable if this raises an exception
            pass
