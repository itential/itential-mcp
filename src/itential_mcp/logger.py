# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import sys

import logging
import logging.handlers

from functools import partial
from pathlib import Path
from typing import Optional

from . import metadata

# Configure global logging
logging_message_format = "%(asctime)s: %(levelname)s: %(message)s"
logging.basicConfig(format=logging_message_format)
logging.getLogger(metadata.name).setLevel(100)

logging.FATAL = 90
logging.addLevelName(logging.FATAL, "FATAL")

# Logging level constants that wrap stdlib logging module constants
NOTSET = logging.NOTSET
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
FATAL = logging.FATAL


def log(lvl: int, msg: str) -> None:
    """Send the log message with the specified level

    This function will send the log message to the logger with the specified
    logging level.  This function should not be directly invoked.  Use one
    of the partials to send a log message with a given level.

    Args:
        lvl (int): The logging level of the message
        msg (str): The message to write to the logger
    """
    logging.getLogger(metadata.name).log(lvl, msg)


debug = partial(log, logging.DEBUG)
info = partial(log, logging.INFO)
warning = partial(log, logging.WARNING)
error = partial(log, logging.ERROR)
critical = partial(log, logging.CRITICAL)


def exception(exc: Exception) -> None:
    """
    Log an exception error

    Args:
        exc (Exception): Exception to log as an error

    Returns:
        None
    """
    log(logging.ERROR, str(exc))


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
    logging.getLogger(metadata.name).setLevel(lvl)

    if propagate is True:
        logging.getLogger("httpx").setLevel(lvl)
        logging.getLogger("httpcore").setLevel(lvl)

    logging.getLogger(metadata.name).log(
        logging.INFO, f"{metadata.name} version {metadata.version}"
    )
    logging.getLogger(metadata.name).log(logging.INFO, f"Logging level set to {lvl}")
    logging.getLogger(metadata.name).log(
        logging.INFO, f"Logging propagation is {propagate}"
    )


def add_file_handler(
    file_path: str,
    level: Optional[int] = None,
    format_string: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB default
    backup_count: int = 5,
    rotate: bool = True
) -> None:
    """Add a file handler to the ipsdk logger with optional rotation.

    Args:
        file_path (str): Path to the log file. Parent directories will be created if they don't exist.
        level (Optional[int]): Logging level for the file handler. If None, uses the logger's current level.
        format_string (Optional[str]): Custom format string for the file handler.
                                     If None, uses the default logging_message_format.
        max_bytes (int): Maximum size of the log file before rotation. Default is 10MB.
        backup_count (int): Number of backup files to keep. Default is 5.
        rotate (bool): Whether to enable log rotation. If False, uses a basic FileHandler.

    Returns:
        None

    Raises:
        OSError: If the log file cannot be created or accessed.
    """
    logger = logging.getLogger(metadata.name)

    # Create parent directories if they don't exist
    log_file = Path(file_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Create file handler - rotating or basic depending on rotate parameter
    if rotate:
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
    else:
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

    rotation_info = f" (rotation: {max_bytes} bytes, {backup_count} backups)" if rotate else " (no rotation)"
    logger.log(logging.INFO, f"File logging enabled: {file_path}{rotation_info}")


def add_rotating_file_handler(
    file_path: str,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB default
    backup_count: int = 5,
    level: Optional[int] = None,
    format_string: Optional[str] = None
) -> None:
    """Add a rotating file handler to the ipsdk logger.

    This function explicitly creates a rotating file handler, which is useful
    when you specifically want log rotation features.

    Args:
        file_path (str): Path to the log file. Parent directories will be created if they don't exist.
        max_bytes (int): Maximum size of the log file before rotation. Default is 10MB.
        backup_count (int): Number of backup files to keep. Default is 5.
        level (Optional[int]): Logging level for the file handler. If None, uses the logger's current level.
        format_string (Optional[str]): Custom format string for the file handler.
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

    # Create rotating file handler
    rotating_handler = logging.handlers.RotatingFileHandler(
        file_path,
        maxBytes=max_bytes,
        backupCount=backup_count
    )

    # Set level - use provided level or current logger level
    if level is not None:
        rotating_handler.setLevel(level)
    else:
        rotating_handler.setLevel(logger.level)

    # Set format - use provided format or default
    if format_string is not None:
        formatter = logging.Formatter(format_string)
    else:
        formatter = logging.Formatter(logging_message_format)

    rotating_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(rotating_handler)

    logger.log(logging.INFO, f"Rotating file logging enabled: {file_path} (max: {max_bytes} bytes, backups: {backup_count})")


def add_syslog_handler(
    level: Optional[int] = None,
    format_string: Optional[str] = None,
    facility: int = logging.handlers.SysLogHandler.LOG_USER,
    address: str = "/dev/log"
) -> None:
    """Add a systemd syslog handler to the itential-mcp logger.

    Args:
        level (Optional[int]): Logging level for the syslog handler. If None, uses the logger's current level.
        format_string (Optional[str]): Custom format string for the syslog handler.
                                     If None, uses the default logging_message_format.
        facility (int): Syslog facility to use. Default is LOG_USER.
        address (str): Address for the syslog handler. Default is "/dev/log" for local systemd.

    Returns:
        None

    Raises:
        OSError: If the syslog handler cannot be created or accessed.
    """
    logger = logging.getLogger(metadata.name)

    try:
        # Create syslog handler
        syslog_handler = logging.handlers.SysLogHandler(address=address, facility=facility)

        # Set level - use provided level or current logger level
        if level is not None:
            syslog_handler.setLevel(level)
        else:
            syslog_handler.setLevel(logger.level)

        # Set format - use provided format or default
        if format_string is not None:
            formatter = logging.Formatter(format_string)
        else:
            # For syslog, we don't need timestamp as systemd adds it
            syslog_format = "%(name)s: %(levelname)s: %(message)s"
            formatter = logging.Formatter(syslog_format)

        syslog_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(syslog_handler)

        logger.log(logging.INFO, f"Syslog logging enabled: {address} (facility: {facility})")

    except Exception as e:
        raise OSError(f"Failed to create syslog handler: {e}")


def remove_file_handlers() -> None:
    """Remove all file handlers (including rotating file handlers) from the ipsdk logger.

    This function removes both basic FileHandler and RotatingFileHandler instances.

    Returns:
        None
    """
    logger = logging.getLogger(metadata.name)

    # Get all file handlers (this includes RotatingFileHandler as it inherits from FileHandler)
    file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]

    # Remove each file handler
    for handler in file_handlers:
        logger.removeHandler(handler)
        handler.close()

    if file_handlers:
        # Count different types for informative logging
        rotating_handlers = [h for h in file_handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
        basic_handlers = [h for h in file_handlers if not isinstance(h, logging.handlers.RotatingFileHandler)]

        if rotating_handlers and basic_handlers:
            logger.log(logging.INFO, f"Removed {len(file_handlers)} file handler(s): {len(rotating_handlers)} rotating, {len(basic_handlers)} basic")
        elif rotating_handlers:
            logger.log(logging.INFO, f"Removed {len(rotating_handlers)} rotating file handler(s)")
        else:
            logger.log(logging.INFO, f"Removed {len(basic_handlers)} basic file handler(s)")


def remove_syslog_handlers() -> None:
    """Remove all syslog handlers from the itential-mcp logger.

    Returns:
        None
    """
    logger = logging.getLogger(metadata.name)

    # Get all syslog handlers
    syslog_handlers = [h for h in logger.handlers if isinstance(h, logging.handlers.SysLogHandler)]

    # Remove each syslog handler
    for handler in syslog_handlers:
        logger.removeHandler(handler)
        handler.close()

    if syslog_handlers:
        logger.log(logging.INFO, f"Removed {len(syslog_handlers)} syslog handler(s)")


def configure_file_logging(
    file_path: str,
    level: int = logging.INFO,
    propagate: bool = False,
    format_string: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB default
    backup_count: int = 5,
    rotate: bool = True
) -> None:
    """Configure both console and file logging in one call.

    This is a convenience function that sets the logging level and adds file logging.

    Args:
        file_path (str): Path to the log file. Parent directories will be created
            if they don't exist.
        level (int): Logging level (e.g., logging.INFO, logging.DEBUG).
            Default is INFO.
        propagate (bool): Setting this value to True will also turn on logging
            for httpx and httpcore.
        format_string (Optional[str]): Custom format string for the file handler.
                                     If None, uses the default logging_message_format.
        max_bytes (int): Maximum size of the log file before rotation. Default is 10MB.
        backup_count (int): Number of backup files to keep. Default is 5.
        rotate (bool): Whether to enable log rotation. If False, uses a basic FileHandler.

    Returns:
        None

    Raises:
        OSError: If the log file cannot be created or accessed.
    """
    # Set the logging level first
    set_level(level, propagate)

    # Add file handler with rotation parameters
    add_file_handler(file_path, level, format_string, max_bytes, backup_count, rotate)


def configure_syslog_logging(
    level: int = logging.INFO,
    propagate: bool = False,
    facility: int = logging.handlers.SysLogHandler.LOG_USER,
    address: str = "/dev/log",
    format_string: Optional[str] = None,
) -> None:
    """Configure both console and syslog logging in one call.

    This is a convenience function that sets the logging level and adds syslog logging.
    Systemd handles log rotation automatically, so no additional rotation configuration is needed.

    Args:
        level (int): Logging level (e.g., logging.INFO, logging.DEBUG).
            Default is INFO.
        propagate (bool): Setting this value to True will also turn on logging
            for httpx and httpcore.
        facility (int): Syslog facility to use. Default is LOG_USER.
        address (str): Address for the syslog handler. Default is "/dev/log" for local systemd.
        format_string (Optional[str]): Custom format string for the syslog handler.
                                     If None, uses a syslog-optimized format.

    Returns:
        None

    Raises:
        OSError: If the syslog handler cannot be created or accessed.
    """
    # Set the logging level first
    set_level(level, propagate)

    # Add syslog handler
    add_syslog_handler(level, format_string, facility, address)
