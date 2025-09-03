# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import tempfile
import logging
import logging.handlers
from unittest.mock import patch, MagicMock, call

import pytest

from itential_mcp import logger, metadata


class TestLoggerConstants:
    """Test cases for logger constants."""
    
    def test_logging_constants_exist(self):
        """Test that logging level constants exist."""
        assert hasattr(logger, 'NOTSET')
        assert hasattr(logger, 'DEBUG')
        assert hasattr(logger, 'INFO')
        assert hasattr(logger, 'WARNING')
        assert hasattr(logger, 'ERROR')
        assert hasattr(logger, 'CRITICAL')
        assert hasattr(logger, 'FATAL')
    
    def test_logging_constants_values(self):
        """Test that logging level constants have correct values."""
        assert logger.NOTSET == logging.NOTSET
        assert logger.DEBUG == logging.DEBUG
        assert logger.INFO == logging.INFO
        assert logger.WARNING == logging.WARNING
        assert logger.ERROR == logging.ERROR
        assert logger.CRITICAL == logging.CRITICAL
        assert logger.FATAL == 90
    
    def test_logging_message_format_exists(self):
        """Test that logging message format exists."""
        assert hasattr(logger, 'logging_message_format')
        assert isinstance(logger.logging_message_format, str)
        assert 'asctime' in logger.logging_message_format
        assert 'levelname' in logger.logging_message_format
        assert 'message' in logger.logging_message_format


class TestBasicLoggingFunctions:
    """Test cases for basic logging functions."""
    
    def test_log_function_exists(self):
        """Test that log function exists and is callable."""
        assert hasattr(logger, 'log')
        assert callable(logger.log)
    
    @patch('logging.getLogger')
    def test_log_function_calls_logger(self, mock_get_logger):
        """Test that log function calls the logger with correct parameters."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        logger.log(logging.INFO, "test message")
        
        mock_get_logger.assert_called_once_with(metadata.name)
        mock_logger.log.assert_called_once_with(logging.INFO, "test message")
    
    def test_logging_level_functions_exist(self):
        """Test that all logging level functions exist."""
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'critical')
        assert callable(logger.debug)
        assert callable(logger.info)
        assert callable(logger.warning)
        assert callable(logger.error)
        assert callable(logger.critical)
    
    @patch('logging.getLogger')
    def test_debug_function(self, mock_get_logger):
        """Test debug function calls log with DEBUG level."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        logger.debug("debug message")
        mock_logger.log.assert_called_once_with(logging.DEBUG, "debug message")
    
    @patch('logging.getLogger')
    def test_info_function(self, mock_get_logger):
        """Test info function calls log with INFO level."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        logger.info("info message")
        mock_logger.log.assert_called_once_with(logging.INFO, "info message")
    
    @patch('logging.getLogger')
    def test_warning_function(self, mock_get_logger):
        """Test warning function calls log with WARNING level."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        logger.warning("warning message")
        mock_logger.log.assert_called_once_with(logging.WARNING, "warning message")
    
    @patch('logging.getLogger')
    def test_error_function(self, mock_get_logger):
        """Test error function calls log with ERROR level."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        logger.error("error message")
        mock_logger.log.assert_called_once_with(logging.ERROR, "error message")
    
    @patch('logging.getLogger')
    def test_critical_function(self, mock_get_logger):
        """Test critical function calls log with CRITICAL level."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        logger.critical("critical message")
        mock_logger.log.assert_called_once_with(logging.CRITICAL, "critical message")
    
    @patch('itential_mcp.logger.log')
    def test_exception_function(self, mock_log):
        """Test exception function calls log with ERROR level."""
        test_exception = ValueError("test error")
        logger.exception(test_exception)
        mock_log.assert_called_once_with(logging.ERROR, "test error")
    
    def test_exception_function_signature(self):
        """Test exception function has correct signature."""
        import inspect
        sig = inspect.signature(logger.exception)
        params = list(sig.parameters.keys())
        assert len(params) == 1
        assert params[0] == 'exc'
    
    @patch('itential_mcp.logger.log')
    @patch('builtins.print')
    @patch('sys.exit')
    def test_fatal_function(self, mock_exit, mock_print, mock_log):
        """Test fatal function calls log, print, and sys.exit."""
        logger.fatal("fatal message")
        
        mock_log.assert_called_once_with(logging.FATAL, "fatal message")
        mock_print.assert_called_once_with("ERROR: fatal message")
        mock_exit.assert_called_once_with(1)


class TestSetLevelFunction:
    """Test cases for set_level function."""
    
    @patch('logging.getLogger')
    def test_set_level_basic(self, mock_get_logger):
        """Test set_level with basic parameters."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        logger.set_level(logging.INFO)
        
        mock_logger.setLevel.assert_called_once_with(logging.INFO)
        assert mock_logger.log.call_count == 3  # version, level set, propagation
    
    @patch('logging.getLogger')
    def test_set_level_with_propagate(self, mock_get_logger):
        """Test set_level with propagate=True."""
        mock_main_logger = MagicMock()
        mock_httpx_logger = MagicMock()
        mock_httpcore_logger = MagicMock()
        
        def get_logger_side_effect(name):
            if name == metadata.name:
                return mock_main_logger
            elif name == "httpx":
                return mock_httpx_logger
            elif name == "httpcore":
                return mock_httpcore_logger
            return MagicMock()
        
        mock_get_logger.side_effect = get_logger_side_effect
        
        logger.set_level(logging.DEBUG, propagate=True)
        
        mock_main_logger.setLevel.assert_called_once_with(logging.DEBUG)
        mock_httpx_logger.setLevel.assert_called_once_with(logging.DEBUG)
        mock_httpcore_logger.setLevel.assert_called_once_with(logging.DEBUG)
    
    @patch('logging.getLogger')
    def test_set_level_without_propagate(self, mock_get_logger):
        """Test set_level with propagate=False (default)."""
        mock_main_logger = MagicMock()
        mock_httpx_logger = MagicMock()
        mock_httpcore_logger = MagicMock()
        
        def get_logger_side_effect(name):
            if name == metadata.name:
                return mock_main_logger
            elif name == "httpx":
                return mock_httpx_logger
            elif name == "httpcore":
                return mock_httpcore_logger
            return MagicMock()
        
        mock_get_logger.side_effect = get_logger_side_effect
        
        logger.set_level(logging.WARNING, propagate=False)
        
        mock_main_logger.setLevel.assert_called_once_with(logging.WARNING)
        mock_httpx_logger.setLevel.assert_not_called()
        mock_httpcore_logger.setLevel.assert_not_called()
    
    def test_set_level_function_signature(self):
        """Test set_level function has correct signature."""
        import inspect
        sig = inspect.signature(logger.set_level)
        params = list(sig.parameters.keys())
        assert len(params) == 2
        assert params[0] == 'lvl'
        assert params[1] == 'propagate'
        
        # Check defaults
        assert sig.parameters['propagate'].default is False


class TestFileHandlerFunctions:
    """Test cases for file handler functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, "test.log")
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('logging.getLogger')
    @patch('pathlib.Path.mkdir')
    def test_add_file_handler_basic(self, mock_mkdir, mock_get_logger):
        """Test add_file_handler with basic parameters."""
        mock_logger = MagicMock()
        mock_logger.level = logging.INFO
        mock_get_logger.return_value = mock_logger
        
        with tempfile.NamedTemporaryFile() as tmp:
            logger.add_file_handler(tmp.name)
        
        mock_get_logger.assert_called_with(metadata.name)
        mock_logger.addHandler.assert_called_once()
        mock_logger.log.assert_called()
    
    @patch('logging.getLogger')
    @patch('pathlib.Path.mkdir')
    def test_add_file_handler_with_rotation(self, mock_mkdir, mock_get_logger):
        """Test add_file_handler with rotation parameters."""
        mock_logger = MagicMock()
        mock_logger.level = logging.INFO
        mock_get_logger.return_value = mock_logger
        
        with tempfile.NamedTemporaryFile() as tmp:
            logger.add_file_handler(
                tmp.name, 
                max_bytes=1024, 
                backup_count=3, 
                rotate=True
            )
        
        # Should have added a RotatingFileHandler
        handler_call = mock_logger.addHandler.call_args[0][0]
        assert isinstance(handler_call, logging.handlers.RotatingFileHandler)
    
    @patch('logging.getLogger')
    @patch('pathlib.Path.mkdir')
    def test_add_file_handler_without_rotation(self, mock_mkdir, mock_get_logger):
        """Test add_file_handler with rotation disabled."""
        mock_logger = MagicMock()
        mock_logger.level = logging.INFO
        mock_get_logger.return_value = mock_logger
        
        with tempfile.NamedTemporaryFile() as tmp:
            logger.add_file_handler(tmp.name, rotate=False)
        
        # Should have added a basic FileHandler
        handler_call = mock_logger.addHandler.call_args[0][0]
        assert isinstance(handler_call, logging.FileHandler)
        assert not isinstance(handler_call, logging.handlers.RotatingFileHandler)
    
    @patch('logging.getLogger')
    @patch('pathlib.Path.mkdir')
    @patch('logging.FileHandler')
    def test_add_file_handler_custom_level(self, mock_file_handler, mock_mkdir, mock_get_logger):
        """Test add_file_handler with custom level."""
        mock_logger = MagicMock()
        mock_logger.level = logging.INFO
        mock_get_logger.return_value = mock_logger
        
        mock_handler = MagicMock()
        mock_file_handler.return_value = mock_handler
        
        with tempfile.NamedTemporaryFile() as tmp:
            logger.add_file_handler(tmp.name, level=logging.DEBUG, rotate=False)
        
        mock_handler.setLevel.assert_called_with(logging.DEBUG)
    
    @patch('logging.getLogger')
    @patch('pathlib.Path.mkdir')
    @patch('logging.FileHandler')
    def test_add_file_handler_custom_format(self, mock_file_handler, mock_mkdir, mock_get_logger):
        """Test add_file_handler with custom format string."""
        mock_logger = MagicMock()
        mock_logger.level = logging.INFO
        mock_get_logger.return_value = mock_logger
        
        mock_handler = MagicMock()
        mock_file_handler.return_value = mock_handler
        
        custom_format = "%(name)s - %(message)s"
        
        with tempfile.NamedTemporaryFile() as tmp:
            logger.add_file_handler(tmp.name, format_string=custom_format, rotate=False)
        
        mock_handler.setFormatter.assert_called_once()
    
    @patch('logging.getLogger')
    @patch('pathlib.Path.mkdir')
    @patch('logging.handlers.RotatingFileHandler')
    def test_add_file_handler_creates_directories(self, mock_rotating_handler, mock_mkdir, mock_get_logger):
        """Test add_file_handler creates parent directories."""
        mock_logger = MagicMock()
        mock_logger.level = logging.INFO
        mock_get_logger.return_value = mock_logger
        
        mock_handler = MagicMock()
        mock_rotating_handler.return_value = mock_handler
        
        test_path = "/tmp/nested/dir/test.log"
        logger.add_file_handler(test_path)
        
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    @patch('logging.getLogger')
    @patch('pathlib.Path.mkdir')
    def test_add_rotating_file_handler(self, mock_mkdir, mock_get_logger):
        """Test add_rotating_file_handler function."""
        mock_logger = MagicMock()
        mock_logger.level = logging.INFO
        mock_get_logger.return_value = mock_logger
        
        with tempfile.NamedTemporaryFile() as tmp:
            logger.add_rotating_file_handler(
                tmp.name,
                max_bytes=2048,
                backup_count=4
            )
        
        handler_call = mock_logger.addHandler.call_args[0][0]
        assert isinstance(handler_call, logging.handlers.RotatingFileHandler)
    
    def test_add_rotating_file_handler_signature(self):
        """Test add_rotating_file_handler has correct signature."""
        import inspect
        sig = inspect.signature(logger.add_rotating_file_handler)
        params = list(sig.parameters.keys())
        
        expected_params = ['file_path', 'max_bytes', 'backup_count', 'level', 'format_string']
        assert params == expected_params
        
        # Check defaults
        assert sig.parameters['max_bytes'].default == 10 * 1024 * 1024
        assert sig.parameters['backup_count'].default == 5


class TestRemoveFileHandlers:
    """Test cases for remove_file_handlers function."""
    
    @patch('logging.getLogger')
    def test_remove_file_handlers_basic(self, mock_get_logger):
        """Test remove_file_handlers with basic file handlers."""
        mock_logger = MagicMock()
        mock_handler1 = MagicMock(spec=logging.FileHandler)
        mock_handler2 = MagicMock(spec=logging.StreamHandler)
        mock_handler3 = MagicMock(spec=logging.FileHandler)
        
        mock_logger.handlers = [mock_handler1, mock_handler2, mock_handler3]
        mock_get_logger.return_value = mock_logger
        
        logger.remove_file_handlers()
        
        # Should remove only file handlers
        mock_logger.removeHandler.assert_has_calls([
            call(mock_handler1),
            call(mock_handler3)
        ])
        mock_handler1.close.assert_called_once()
        mock_handler3.close.assert_called_once()
        mock_handler2.close.assert_not_called()
    
    @patch('logging.getLogger')
    def test_remove_file_handlers_with_rotating(self, mock_get_logger):
        """Test remove_file_handlers with rotating file handlers."""
        mock_logger = MagicMock()
        mock_basic_handler = MagicMock()
        mock_rotating_handler = MagicMock()
        mock_stream_handler = MagicMock()
        
        # Set up handler types for isinstance checks
        mock_basic_handler.__class__ = logging.FileHandler
        mock_rotating_handler.__class__ = logging.handlers.RotatingFileHandler
        mock_stream_handler.__class__ = logging.StreamHandler
        
        mock_logger.handlers = [mock_basic_handler, mock_rotating_handler, mock_stream_handler]
        mock_get_logger.return_value = mock_logger
        
        logger.remove_file_handlers()
        
        # Should remove both file handlers (RotatingFileHandler inherits from FileHandler)
        expected_calls = [call(mock_basic_handler), call(mock_rotating_handler)]
        mock_logger.removeHandler.assert_has_calls(expected_calls, any_order=True)
        mock_basic_handler.close.assert_called_once()
        mock_rotating_handler.close.assert_called_once()
    
    @patch('logging.getLogger')
    def test_remove_file_handlers_empty(self, mock_get_logger):
        """Test remove_file_handlers with no file handlers."""
        mock_logger = MagicMock()
        mock_stream_handler = MagicMock(spec=logging.StreamHandler)
        
        mock_logger.handlers = [mock_stream_handler]
        mock_get_logger.return_value = mock_logger
        
        logger.remove_file_handlers()
        
        # Should not remove any handlers or log anything
        mock_logger.removeHandler.assert_not_called()
        mock_logger.log.assert_not_called()


class TestSyslogHandlerFunctions:
    """Test cases for syslog handler functions."""
    
    @patch('logging.getLogger')
    @patch('logging.handlers.SysLogHandler')
    def test_add_syslog_handler_basic(self, mock_syslog_handler_class, mock_get_logger):
        """Test add_syslog_handler with basic parameters."""
        mock_logger = MagicMock()
        mock_logger.level = logging.INFO
        mock_get_logger.return_value = mock_logger
        
        mock_handler = MagicMock()
        mock_syslog_handler_class.return_value = mock_handler
        
        logger.add_syslog_handler()
        
        mock_syslog_handler_class.assert_called_once_with(
            address="/dev/log",
            facility=1  # LOG_USER value is 1
        )
        mock_logger.addHandler.assert_called_once_with(mock_handler)
    
    @patch('logging.getLogger')
    @patch('logging.handlers.SysLogHandler')
    def test_add_syslog_handler_custom_params(self, mock_syslog_handler_class, mock_get_logger):
        """Test add_syslog_handler with custom parameters."""
        mock_logger = MagicMock()
        mock_logger.level = logging.INFO
        mock_get_logger.return_value = mock_logger
        
        mock_handler = MagicMock()
        mock_syslog_handler_class.return_value = mock_handler
        
        logger.add_syslog_handler(
            level=logging.DEBUG,
            facility=logging.handlers.SysLogHandler.LOG_DAEMON,
            address=("localhost", 514)
        )
        
        mock_syslog_handler_class.assert_called_once_with(
            address=("localhost", 514),
            facility=logging.handlers.SysLogHandler.LOG_DAEMON
        )
        mock_handler.setLevel.assert_called_once_with(logging.DEBUG)
    
    @patch('logging.getLogger')
    @patch('logging.handlers.SysLogHandler')
    def test_add_syslog_handler_exception(self, mock_syslog_handler_class, mock_get_logger):
        """Test add_syslog_handler handles exceptions."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        mock_syslog_handler_class.side_effect = Exception("Syslog error")
        
        with pytest.raises(OSError, match="Failed to create syslog handler"):
            logger.add_syslog_handler()
    
    @patch('logging.getLogger')
    def test_remove_syslog_handlers(self, mock_get_logger):
        """Test remove_syslog_handlers function."""
        mock_logger = MagicMock()
        mock_syslog_handler = MagicMock(spec=logging.handlers.SysLogHandler)
        mock_file_handler = MagicMock(spec=logging.FileHandler)
        
        mock_logger.handlers = [mock_syslog_handler, mock_file_handler]
        mock_get_logger.return_value = mock_logger
        
        logger.remove_syslog_handlers()
        
        # Should remove only syslog handlers
        mock_logger.removeHandler.assert_called_once_with(mock_syslog_handler)
        mock_syslog_handler.close.assert_called_once()
        mock_file_handler.close.assert_not_called()


class TestConfigurationFunctions:
    """Test cases for configuration functions."""
    
    @patch('itential_mcp.logger.set_level')
    @patch('itential_mcp.logger.add_file_handler')
    def test_configure_file_logging_basic(self, mock_add_file_handler, mock_set_level):
        """Test configure_file_logging with basic parameters."""
        logger.configure_file_logging("/tmp/test.log")
        
        mock_set_level.assert_called_once_with(logging.INFO, False)
        mock_add_file_handler.assert_called_once_with(
            "/tmp/test.log", 
            logging.INFO, 
            None, 
            10 * 1024 * 1024, 
            5, 
            True
        )
    
    @patch('itential_mcp.logger.set_level')
    @patch('itential_mcp.logger.add_file_handler')
    def test_configure_file_logging_custom_params(self, mock_add_file_handler, mock_set_level):
        """Test configure_file_logging with custom parameters."""
        logger.configure_file_logging(
            "/tmp/custom.log",
            level=logging.DEBUG,
            propagate=True,
            format_string="%(message)s",
            max_bytes=2048,
            backup_count=3,
            rotate=False
        )
        
        mock_set_level.assert_called_once_with(logging.DEBUG, True)
        mock_add_file_handler.assert_called_once_with(
            "/tmp/custom.log",
            logging.DEBUG,
            "%(message)s",
            2048,
            3,
            False
        )
    
    def test_configure_file_logging_signature(self):
        """Test configure_file_logging has correct signature."""
        import inspect
        sig = inspect.signature(logger.configure_file_logging)
        params = list(sig.parameters.keys())
        
        expected_params = [
            'file_path', 'level', 'propagate', 'format_string',
            'max_bytes', 'backup_count', 'rotate'
        ]
        assert params == expected_params
        
        # Check defaults
        assert sig.parameters['level'].default == logging.INFO
        assert sig.parameters['propagate'].default is False
        assert sig.parameters['max_bytes'].default == 10 * 1024 * 1024
        assert sig.parameters['backup_count'].default == 5
        assert sig.parameters['rotate'].default is True
    
    @patch('itential_mcp.logger.set_level')
    @patch('itential_mcp.logger.add_syslog_handler')
    def test_configure_syslog_logging_basic(self, mock_add_syslog_handler, mock_set_level):
        """Test configure_syslog_logging with basic parameters."""
        logger.configure_syslog_logging()
        
        mock_set_level.assert_called_once_with(logging.INFO, False)
        mock_add_syslog_handler.assert_called_once_with(
            logging.INFO,
            None,
            logging.handlers.SysLogHandler.LOG_USER,
            "/dev/log"
        )
    
    @patch('itential_mcp.logger.set_level')
    @patch('itential_mcp.logger.add_syslog_handler')
    def test_configure_syslog_logging_custom_params(self, mock_add_syslog_handler, mock_set_level):
        """Test configure_syslog_logging with custom parameters."""
        logger.configure_syslog_logging(
            level=logging.WARNING,
            propagate=True,
            facility=logging.handlers.SysLogHandler.LOG_DAEMON,
            address=("localhost", 514),
            format_string="%(name)s: %(message)s"
        )
        
        mock_set_level.assert_called_once_with(logging.WARNING, True)
        mock_add_syslog_handler.assert_called_once_with(
            logging.WARNING,
            "%(name)s: %(message)s",
            logging.handlers.SysLogHandler.LOG_DAEMON,
            ("localhost", 514)
        )


class TestLoggerIntegration:
    """Integration tests for logger functionality."""
    
    def test_logger_module_structure(self):
        """Test the overall logger module structure."""
        expected_functions = [
            'log', 'debug', 'info', 'warning', 'error', 'critical', 'exception', 'fatal',
            'set_level', 'add_file_handler', 'add_rotating_file_handler', 'remove_file_handlers',
            'add_syslog_handler', 'remove_syslog_handlers', 
            'configure_file_logging', 'configure_syslog_logging'
        ]
        
        for func_name in expected_functions:
            assert hasattr(logger, func_name)
            assert callable(getattr(logger, func_name))
    
    def test_logger_module_constants(self):
        """Test logger module constants."""
        expected_constants = [
            'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'FATAL',
            'logging_message_format'
        ]
        
        for const_name in expected_constants:
            assert hasattr(logger, const_name)
    
    def test_logger_docstrings_exist(self):
        """Test that key functions have docstrings."""
        functions_with_docs = [
            'log', 'exception', 'fatal', 'set_level', 'add_file_handler',
            'add_rotating_file_handler', 'remove_file_handlers', 'add_syslog_handler',
            'remove_syslog_handlers', 'configure_file_logging', 'configure_syslog_logging'
        ]
        
        for func_name in functions_with_docs:
            func = getattr(logger, func_name)
            assert func.__doc__ is not None
            assert len(func.__doc__.strip()) > 0
    
    def test_fatal_level_configuration(self):
        """Test that FATAL level is properly configured."""
        assert logging.getLevelName(logger.FATAL) == "FATAL"
        assert logger.FATAL == 90
    
    def test_basic_config_applied(self):
        """Test that basic logging configuration is applied."""
        # The module should have configured basic logging
        root_logger = logging.getLogger()
        assert root_logger.level != logging.NOTSET or len(root_logger.handlers) > 0


class TestLoggerErrorHandling:
    """Test error handling scenarios."""
    
    @patch('pathlib.Path.mkdir')
    @patch('logging.getLogger')
    def test_add_file_handler_directory_creation_error(self, mock_get_logger, mock_mkdir):
        """Test add_file_handler handles directory creation errors."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_mkdir.side_effect = OSError("Permission denied")
        
        with pytest.raises(OSError):
            logger.add_file_handler("/restricted/test.log")
    
    def test_exception_function_with_different_exception_types(self):
        """Test exception function with various exception types."""
        exceptions = [
            ValueError("value error"),
            TypeError("type error"),
            RuntimeError("runtime error"),
            Exception("generic exception")
        ]
        
        for exc in exceptions:
            with patch('itential_mcp.logger.log') as mock_log:
                logger.exception(exc)
                mock_log.assert_called_once_with(logging.ERROR, str(exc))
    
    @patch('itential_mcp.logger.log')
    @patch('builtins.print')
    @patch('sys.exit')
    def test_fatal_function_parameters(self, mock_exit, mock_print, mock_log):
        """Test fatal function with various message types."""
        messages = ["simple message", "", "message with\nnewline", "unicode: 中文"]
        
        for msg in messages:
            mock_log.reset_mock()
            mock_print.reset_mock()
            mock_exit.reset_mock()
            
            logger.fatal(msg)
            
            mock_log.assert_called_once_with(logging.FATAL, msg)
            mock_print.assert_called_once_with(f"ERROR: {msg}")
            mock_exit.assert_called_once_with(1)


class TestLoggerFileOperations:
    """Test actual file operations with temporary files."""
    
    def test_real_file_handler_creation(self):
        """Test creating actual file handlers with temporary files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            
            # Remove any existing handlers first
            logger.remove_file_handlers()
            
            # Add a file handler
            logger.add_file_handler(log_file, level=logging.INFO, rotate=False)
            
            # Verify file was created
            assert os.path.exists(log_file)
            
            # Clean up
            logger.remove_file_handlers()
    
    def test_real_rotating_file_handler_creation(self):
        """Test creating actual rotating file handlers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "rotating.log")
            
            # Remove any existing handlers first
            logger.remove_file_handlers()
            
            # Add a rotating file handler
            logger.add_rotating_file_handler(
                log_file,
                max_bytes=1024,
                backup_count=2,
                level=logging.DEBUG
            )
            
            # Verify file was created
            assert os.path.exists(log_file)
            
            # Clean up
            logger.remove_file_handlers()
    
    def test_nested_directory_creation(self):
        """Test creating nested directories for log files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_log = os.path.join(temp_dir, "nested", "dir", "test.log")
            
            # Remove any existing handlers first
            logger.remove_file_handlers()
            
            # Add file handler with nested path
            logger.add_file_handler(nested_log, rotate=False)
            
            # Verify nested directories and file were created
            assert os.path.exists(nested_log)
            assert os.path.exists(os.path.dirname(nested_log))
            
            # Clean up
            logger.remove_file_handlers()