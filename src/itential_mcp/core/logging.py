# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Logging configuration and utilities for Itential MCP.

This module provides standardized logging functionality for the Itential MCP server,
including custom log levels, file handlers, and logger management for the application
and its dependencies.
"""

from __future__ import annotations

import sys
import logging
import traceback

from pathlib import Path
from functools import partial
from typing import Literal

from . import metadata
from . import heuristics

logging_message_format = "%(asctime)s: [%(name)s] %(levelname)s: %(message)s"
logging.getLogger(metadata.name).setLevel(100)

# Add the FATAL logging level
logging.FATAL = 90
logging.addLevelName(logging.FATAL, "FATAL")

logging.NONE = logging.FATAL + 10
logging.addLevelName(logging.NONE, "NONE")

# Logging level constants that wrap stdlib logging module constants
NOTSET = logging.NOTSET
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
FATAL = logging.FATAL
NONE = logging.NONE

# Global flag to control sensitive data filtering
_sensitive_data_filtering_enabled = True


def _sync_scan_and_redact(text: str) -> str:
    """Scan and redact sensitive data from text for logging.

    This function calls the heuristics scanner to redact sensitive
    information before writing to logs.

    Args:
        text (str): The text to scan and redact.

    Returns:
        str: The text with sensitive data redacted.

    Raises:
        None
    """
    try:
        return heuristics.scan_and_redact(text)
    except Exception:
        # If anything goes wrong, return the original text to avoid breaking logging
        return text


def log(lvl: int, msg: str) -> None:
    """Send the log message with the specified level

    This function will send the log message to the logger with the specified
    logging level.  This function should not be directly invoked.  Use one
    of the partials to send a log message with a given level.

    The message is automatically scanned for sensitive data and redacted
    before being logged to prevent data leakage.

    Args:
        lvl (int): The logging level of the message
        msg (str): The message to write to the logger
    """
    # Scan and redact sensitive data from the message if filtering is enabled
    if _sensitive_data_filtering_enabled:
        redacted_msg = _sync_scan_and_redact(msg)
    else:
        redacted_msg = msg
    logging.getLogger(metadata.name).log(lvl, redacted_msg)


debug = partial(log, logging.DEBUG)
info = partial(log, logging.INFO)
warning = partial(log, logging.WARNING)
error = partial(log, logging.ERROR)
critical = partial(log, logging.CRITICAL)


def exception(exc: Exception) -> None:
    """Log an exception error with full traceback.

    This function logs an exception at ERROR level, including the full
    traceback information to help with debugging. The traceback shows
    the complete call stack from where the exception was raised.

    Args:
        exc (Exception): Exception to log as an error.

    Returns:
        None

    Raises:
        None
    """
    # Format the exception with full traceback
    tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
    tb_text = "".join(tb_lines)
    log(logging.ERROR, tb_text)


def fatal(msg: str) -> None:
    """
    Log a fatal error

    A fatal error will log the message using level 90 (FATAL) and print
    an error message to stdout.  It will then exit the application with
    return code 1

    Args:
        msg (str): The message to print

    Returns:
        None

    Raises:
        None
    """
    log(logging.FATAL, msg)
    print(f"ERROR: {msg}")
    sys.exit(1)


def _get_loggers() -> set[logging.Logger]:
    """Get all relevant loggers for the application.

    Retrieves loggers that belong to the Itential MCP application and its
    dependencies (ipsdk, FastMCP).

    Returns:
        set[logging.Logger]: Set of logger instances for the application and dependencies.
    """
    loggers = set()
    for name in logging.Logger.manager.loggerDict:
        if (
            name.startswith(metadata.name)
            or name.startswith("ipsdk")
            or name.startswith("FastMCP")
            or name.startswith("fastmcp")
        ):
            loggers.add(logging.getLogger(name))
    return loggers


def get_logger() -> logging.Logger:
    """Get the main application logger.

    Returns:
        logging.Logger: The logger instance for the Itential MCP application.
    """
    return logging.getLogger(metadata.name)


def set_level(lvl: int, propagate: bool = False) -> None:
    """Set logging level for all loggers in the current Python process.

    Args:
        lvl (int): Logging level (e.g., logging.INFO, logging.DEBUG).  This
            is a required argument

        propagate (bool): Setting this value to True will also turn on
            logging for httpx and httpcore.

    Returns:
        None

    Raises:
        None
    """
    logger = get_logger()

    if lvl == "NONE":
        lvl = NONE

    logger.setLevel(lvl)
    logger.propagate = False

    logger.log(logging.INFO, f"{metadata.name} version {metadata.version}")
    logger.log(logging.INFO, f"Logging level set to {lvl}")

    if propagate is True:
        for logger in _get_loggers():
            logger.setLevel(lvl)


def add_file_handler(
    file_path: str, level: int | None = None, format_string: str | None = None
) -> None:
    """Add a file handler to the Itential MCP logger.

    Args:
        file_path (str): Path to the log file. Parent directories will be created if they don't exist.
        level (int | None): Logging level for the file handler. If None, uses the logger's current level.
        format_string (str | None): Custom format string for the file handler.
                                     If None, uses the default logging_message_format.

    Returns:
        None

    Raises:
        OSError: If the log file cannot be created or accessed.
    """
    logger = logging.getLogger(metadata.name)

    # Create parent directories if they don't exist
    log_file = Path(file_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Create file handler
    file_handler = logging.FileHandler(file_path)

    # Set level - use provided level or current logger level
    if level is not None:
        file_handler.setLevel(level)
    else:
        file_handler.setLevel(logger.level)

    # Set format - use provided format or default
    if format_string is not None:
        formatter = logging.Formatter(format_string)
    else:
        formatter = logging.Formatter(logging_message_format)

    file_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(file_handler)

    # Disable propagation to prevent duplicate messages from root logger
    logger.propagate = False

    logger.log(logging.INFO, f"File logging enabled: {file_path}")


def remove_file_handlers() -> None:
    """Remove all file handlers from the Itential MCP logger.

    Returns:
        None
    """
    logger = logging.getLogger(metadata.name)

    # Get all file handlers
    file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]

    # Remove each file handler
    for handler in file_handlers:
        logger.removeHandler(handler)
        handler.close()

    if file_handlers:
        logger.log(logging.INFO, f"Removed {len(file_handlers)} file handler(s)")


def configure_file_logging(
    file_path: str,
    level: int = logging.INFO,
    propagate: bool = False,
    format_string: str | None = None,
) -> None:
    """Configure both console and file logging in one call.

    This is a convenience function that sets the logging level and adds file logging.

    Args:
        file_path (str): Path to the log file. Parent directories will be created if they don't exist.
        level (int): Logging level (e.g., logging.INFO, logging.DEBUG). Default is INFO.
        propagate (bool): Setting this value to True will also turn on logging for httpx and httpcore.
        format_string (str | None): Custom format string for the file handler.
                                     If None, uses the default logging_message_format.

    Returns:
        None

    Raises:
        OSError: If the log file cannot be created or accessed.
    """
    # Set the logging level first
    set_level(level, propagate)

    # Add file handler
    add_file_handler(file_path, level, format_string)


def set_console_output(stream: Literal["stdout", "stderr"] = "stderr") -> None:
    """
    Set console logging output to stdout or stderr.

    Args:
        stream (str): Output stream ("stdout" or "stderr"). Defaults to "stderr".

    Returns:
        None

    Raises:
        ValueError: If stream is not "stdout" or "stderr".
    """
    if stream not in ("stdout", "stderr"):
        raise ValueError("stream must be 'stdout' or 'stderr'")

    logger = logging.getLogger(metadata.name)

    # Remove existing console handlers
    console_handlers = [
        h
        for h in logger.handlers
        if isinstance(h, logging.StreamHandler) and h.stream in (sys.stdout, sys.stderr)
    ]

    for handler in console_handlers:
        logger.removeHandler(handler)
        handler.close()

    # Add new console handler with specified stream
    output_stream = sys.stdout if stream == "stdout" else sys.stderr
    console_handler = logging.StreamHandler(output_stream)
    console_handler.setFormatter(logging.Formatter(logging_message_format))
    logger.addHandler(console_handler)

    # Disable propagation to prevent duplicate messages from root logger
    logger.propagate = False

    logger.log(logging.INFO, f"Console logging output set to {stream}")


def add_stdout_handler(
    level: int | None = None, format_string: str | None = None
) -> None:
    """
    Add a stdout handler to the logger.

    Args:
        level (int | None): Logging level for the stdout handler. If None, uses the logger's current level.
        format_string (str | None): Custom format string for the stdout handler.
                                     If None, uses the default logging_message_format.

    Returns:
        None
    """
    logger = logging.getLogger(metadata.name)

    # Create stdout handler
    stdout_handler = logging.StreamHandler(sys.stdout)

    # Set level - use provided level or current logger level
    if level is not None:
        stdout_handler.setLevel(level)
    else:
        stdout_handler.setLevel(logger.level)

    # Set format - use provided format or default
    if format_string is not None:
        formatter = logging.Formatter(format_string)
    else:
        formatter = logging.Formatter(logging_message_format)

    stdout_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(stdout_handler)

    # Disable propagation to prevent duplicate messages from root logger
    logger.propagate = False

    logger.log(logging.INFO, "Stdout logging handler added")


def add_stderr_handler(
    level: int | None = None, format_string: str | None = None
) -> None:
    """
    Add a stderr handler to the logger.

    Args:
        level (int | None): Logging level for the stderr handler. If None, uses the logger's current level.
        format_string (str | None): Custom format string for the stderr handler.
                                     If None, uses the default logging_message_format.

    Returns:
        None
    """
    logger = logging.getLogger(metadata.name)

    # Create stderr handler
    stderr_handler = logging.StreamHandler(sys.stderr)

    # Set level - use provided level or current logger level
    if level is not None:
        stderr_handler.setLevel(level)
    else:
        stderr_handler.setLevel(logger.level)

    # Set format - use provided format or default
    if format_string is not None:
        formatter = logging.Formatter(format_string)
    else:
        formatter = logging.Formatter(logging_message_format)

    stderr_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(stderr_handler)

    # Disable propagation to prevent duplicate messages from root logger
    logger.propagate = False

    logger.log(logging.INFO, "Stderr logging handler added")


def enable_sensitive_data_filtering() -> None:
    """Enable sensitive data filtering in log messages.

    When enabled, log messages will be scanned for potentially sensitive
    information and redacted before being written to the log.

    Returns:
        None

    Raises:
        None
    """
    global _sensitive_data_filtering_enabled
    _sensitive_data_filtering_enabled = True


def disable_sensitive_data_filtering() -> None:
    """Disable sensitive data filtering in log messages.

    When disabled, log messages will be written as-is without scanning
    for sensitive information. Use with caution in production environments.

    Returns:
        None

    Raises:
        None
    """
    global _sensitive_data_filtering_enabled
    _sensitive_data_filtering_enabled = False


def is_sensitive_data_filtering_enabled() -> bool:
    """Check if sensitive data filtering is currently enabled.

    Returns:
        bool: True if filtering is enabled, False otherwise.

    Raises:
        None
    """
    return _sensitive_data_filtering_enabled


def configure_sensitive_data_patterns(
    custom_patterns: dict[str, str] | None = None,
) -> None:
    """Configure custom patterns for sensitive data detection.

    Args:
        custom_patterns (dict[str, str] | None): Custom regex patterns to add
            to the sensitive data scanner, where keys are pattern names and
            values are regex patterns.

    Returns:
        None

    Raises:
        re.error: If any of the custom patterns are invalid regex.
    """
    heuristics.configure_scanner(custom_patterns)


def get_sensitive_data_patterns() -> list[str]:
    """Get a list of all sensitive data patterns currently configured.

    Returns:
        list[str]: List of pattern names that are being scanned for.

    Raises:
        None
    """
    return heuristics.get_scanner().list_patterns()


def add_sensitive_data_pattern(name: str, pattern: str) -> None:
    """Add a new sensitive data pattern to scan for.

    Args:
        name (str): Name of the pattern for identification.
        pattern (str): Regular expression pattern to match sensitive data.

    Returns:
        None

    Raises:
        re.error: If the regex pattern is invalid.
    """
    heuristics.get_scanner().add_pattern(name, pattern)


def remove_sensitive_data_pattern(name: str) -> bool:
    """Remove a sensitive data pattern from scanning.

    Args:
        name (str): Name of the pattern to remove.

    Returns:
        bool: True if the pattern was removed, False if it didn't exist.

    Raises:
        None
    """
    return heuristics.get_scanner().remove_pattern(name)


def initialize() -> None:
    """
    Remove all handlers for loggers starting with 'FastMCP' and replace with standard StreamHandler.

    This function finds all loggers that start with 'FastMCP', removes their existing handlers,
    and adds a new StreamHandler with stderr output and standard formatting.

    Returns:
        None
    """
    for logger in _get_loggers():
        handlers = logger.handlers[:]
        for handler in handlers:
            logger.removeHandler(handler)
            handler.close()

        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setFormatter(logging.Formatter(logging_message_format))

        logger.addHandler(stream_handler)
        logger.setLevel(NONE)
        logger.propagate = False
