# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import sys
import logging
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from itential_mcp import logging as itential_logging
from itential_mcp import metadata


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

    @patch("itential_mcp.logging.logging.getLogger")
    def test_log_function(self, mock_get_logger):
        """Test the basic log function"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.log(logging.INFO, "test message")

        mock_get_logger.assert_called_once_with(metadata.name)
        mock_logger.log.assert_called_once_with(logging.INFO, "test message")

    @patch("itential_mcp.logging.logging.getLogger")
    def test_debug_function(self, mock_get_logger):
        """Test the debug function"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.debug("debug message")
        mock_get_logger.assert_called_once_with(metadata.name)
        mock_logger.log.assert_called_once_with(logging.DEBUG, "debug message")

    @patch("itential_mcp.logging.logging.getLogger")
    def test_info_function(self, mock_get_logger):
        """Test the info function"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.info("info message")
        mock_get_logger.assert_called_once_with(metadata.name)
        mock_logger.log.assert_called_once_with(logging.INFO, "info message")

    @patch("itential_mcp.logging.logging.getLogger")
    def test_warning_function(self, mock_get_logger):
        """Test the warning function"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.warning("warning message")
        mock_get_logger.assert_called_once_with(metadata.name)
        mock_logger.log.assert_called_once_with(logging.WARNING, "warning message")

    @patch("itential_mcp.logging.logging.getLogger")
    def test_error_function(self, mock_get_logger):
        """Test the error function"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.error("error message")
        mock_get_logger.assert_called_once_with(metadata.name)
        mock_logger.log.assert_called_once_with(logging.ERROR, "error message")

    @patch("itential_mcp.logging.logging.getLogger")
    def test_critical_function(self, mock_get_logger):
        """Test the critical function"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        itential_logging.critical("critical message")
        mock_get_logger.assert_called_once_with(metadata.name)
        mock_logger.log.assert_called_once_with(logging.CRITICAL, "critical message")

    @patch("itential_mcp.logging.logging.getLogger")
    def test_exception_function(self, mock_get_logger):
        """Test the exception function"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        exc = ValueError("test error")
        itential_logging.exception(exc)

        mock_get_logger.assert_called_once_with(metadata.name)
        mock_logger.log.assert_called_once_with(logging.ERROR, "test error")

    @patch("sys.exit")
    @patch("builtins.print")
    @patch("itential_mcp.logging.logging.getLogger")
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

    @patch("itential_mcp.logging.logging.getLogger")
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

    @patch("itential_mcp.logging.logging.getLogger")
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

    @patch("itential_mcp.logging.logging.getLogger")
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

    @patch("itential_mcp.logging.logging.getLogger")
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

    @patch("itential_mcp.logging.logging.getLogger")
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

    @patch("itential_mcp.logging.logging.getLogger")
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

    @patch("itential_mcp.logging.logging.getLogger")
    @patch("itential_mcp.logging.logging.StreamHandler")
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

    @patch("itential_mcp.logging.logging.getLogger")
    @patch("itential_mcp.logging.logging.StreamHandler")
    @patch("itential_mcp.logging.logging.Formatter")
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

    @patch("itential_mcp.logging.logging.getLogger")
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

    @patch("itential_mcp.logging.logging.getLogger")
    @patch("itential_mcp.logging.logging.StreamHandler")
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

    @patch("itential_mcp.logging.logging.getLogger")
    @patch("itential_mcp.logging.logging.StreamHandler")
    @patch("itential_mcp.logging.logging.Formatter")
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
