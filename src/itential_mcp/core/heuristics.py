# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Heuristics scanner for filtering sensitive data from log messages.

This module provides functionality to detect and redact sensitive information
such as API keys, passwords, tokens, and other personally
identifiable information (PII) from log messages before they are written.
"""

from __future__ import annotations

import re

from typing import Callable
from typing import Pattern


class Scanner:
    """Scanner for detecting and redacting sensitive data patterns in text.

    This scanner uses heuristic pattern matching to identify potentially sensitive
    information and replace it with redacted placeholders to prevent data leakage
    in log files.

    This class implements the Singleton pattern to ensure only one instance
    exists throughout the application.

    Usage:
        scanner = Scanner()
        redacted = scanner.scan_and_redact("API_KEY=secret123456789")
    """

    _instance: Scanner | None = None
    _initialized: bool = False

    def __new__(cls, _custom_patterns: dict[str, str | None] | None = None) -> Scanner:
        """Create or return the singleton instance.

        Args:
            _custom_patterns (dict[str, str | None]): Additional patterns
                to scan for, where keys are pattern names and values are
                regex patterns. Passed to __init__ after instance creation.

        Returns:
            Scanner: The singleton instance.

        Raises:
            None
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, custom_patterns: dict[str, str | None] | None = None) -> None:
        """Initialize the sensitive data scanner.

        This method will only initialize the instance once due to the Singleton pattern.
        Subsequent calls will not re-initialize the patterns.

        Args:
            custom_patterns (dict[str, str | None]): Additional patterns to scan for,
                where keys are pattern names and values are regex patterns.
                Only applied on first initialization.

        Returns:
            None

        Raises:
            re.error: If any of the regex patterns are invalid.
        """
        # Only initialize once due to Singleton pattern
        if not self._initialized:
            self._patterns: dict[str, Pattern] = {}
            self._redaction_functions: dict[str, Callable[[str], str]] = {}

            # Initialize default patterns
            self._init_default_patterns()

            # Add custom patterns if provided
            if custom_patterns is not None:
                for name, pattern in custom_patterns.items():
                    self.add_pattern(name, pattern)

            # Mark as initialized
            Scanner._initialized = True

    def _init_default_patterns(self) -> None:
        """Initialize default sensitive data patterns.

        Sets up regex patterns for common sensitive data types including API keys,
        passwords, tokens, credit card numbers, and other PII.

        Returns:
            None

        Raises:
            None
        """
        # API Keys and tokens (various formats)
        self.add_pattern(
            "api_key",
            r"(?i)\b(?:api[_-]?key|apikey)\s*[=:]\s*[\"']?([a-zA-Z0-9_\-]{16,})[\"']?",
        )
        self.add_pattern("bearer_token", r"(?i)\bbearer\s+([a-zA-Z0-9_\-\.]{20,})")
        self.add_pattern(
            "jwt_token",
            r"\b(eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+)\b",
        )
        self.add_pattern(
            "access_token",
            r"(?i)\b(?:access[_-]?token|accesstoken)\s*[=:]\s*[\"']?([a-zA-Z0-9_\-]{20,})[\"']?",
        )

        # Password patterns
        self.add_pattern(
            "password",
            r"(?i)\b(?:password|passwd|pwd)\s*[=:]\s*[\"']?([^\s\"']{6,})[\"']?",
        )
        self.add_pattern(
            "secret",
            r"(?i)\b(?:secret|client_secret)\s*[=:]\s*[\"']?([a-zA-Z0-9_\-]{16,})[\"']?",
        )

        # URLs with authentication (check before email patterns)
        self.add_pattern("auth_url", r"https?://[a-zA-Z0-9_\-]+:[a-zA-Z0-9_\-]+@[^\s]+")

        # Basic email pattern (when used in sensitive contexts)
        self.add_pattern(
            "email_in_auth",
            r"(?i)(?:username|user|email)\s*[=:]\s*[\"']?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})[\"']?",
        )

        # Database connection strings
        self.add_pattern(
            "db_connection",
            r"(?i)\b(?:mongodb|mysql|postgresql|postgres)://[^\s]+:[^\s]+@[^\s]+",
        )

        # Private keys (basic detection)
        self.add_pattern(
            "private_key",
            r"-----BEGIN (?:RSA )?PRIVATE KEY-----[\s\S]*?"
            r"-----END (?:RSA )?PRIVATE KEY-----",
        )

    def add_pattern(
        self,
        name: str,
        pattern: str,
        redaction_func: Callable[[str | None, str]] | None = None,
    ) -> None:
        """Add a new sensitive data pattern to scan for.

        Args:
            name (str): Name of the pattern for identification.
            pattern (str): Regular expression pattern to match sensitive data.
            redaction_func (Callable[[str | None, str]]): Custom function
                to redact matches. If None, uses default redaction with
                pattern name.

        Returns:
            None

        Raises:
            re.error: If the regex pattern is invalid.
        """
        try:
            compiled_pattern = re.compile(pattern)
            self._patterns[name] = compiled_pattern

            if redaction_func is not None:
                self._redaction_functions[name] = redaction_func
            else:
                self._redaction_functions[name] = lambda _: f"[REDACTED_{name.upper()}]"
        except re.error as e:
            msg = f"Invalid regex pattern for '{name}': {e}"
            raise re.error(msg) from e

    def remove_pattern(self, name: str) -> bool:
        """Remove a pattern from the scanner.

        Args:
            name (str): Name of the pattern to remove.

        Returns:
            bool: True if pattern was removed, False if it didn't exist.

        Raises:
            None
        """
        if name in self._patterns:
            del self._patterns[name]
            del self._redaction_functions[name]
            return True
        return False

    def list_patterns(self) -> list[str]:
        """Get a list of all pattern names currently registered.

        Returns:
            list[str]: List of pattern names.

        Raises:
            None
        """
        return list(self._patterns.keys())

    def scan_and_redact(self, text: str) -> str:
        """Scan text for sensitive data and redact any matches.

        Args:
            text (str): The text to scan and potentially redact.

        Returns:
            str: The text with sensitive data redacted.

        Raises:
            None
        """
        if not text:
            return text

        result = text

        for pattern_name, pattern in self._patterns.items():
            redaction_func = self._redaction_functions[pattern_name]
            # Use lambda with default arg to capture current redaction_func
            result = pattern.sub(
                lambda match, func=redaction_func: func(match.group(0)), result
            )

        return result

    def has_sensitive_data(self, text: str) -> bool:
        """Check if text contains any sensitive data without redacting it.

        Args:
            text (str): The text to check for sensitive data.

        Returns:
            bool: True if sensitive data is detected, False otherwise.

        Raises:
            None
        """
        if not text:
            return False

        return any(pattern.search(text) for pattern in self._patterns.values())

    def get_sensitive_data_types(self, text: str) -> list[str]:
        """Get a list of sensitive data types detected in the text.

        Args:
            text (str): The text to analyze.

        Returns:
            list[str]: List of pattern names that matched in the text.

        Raises:
            None
        """
        if not text:
            return []

        detected_types = []

        for pattern_name, pattern in self._patterns.items():
            if pattern.search(text):
                detected_types.append(pattern_name)

        return detected_types

    @classmethod
    def reset_singleton(cls) -> None:
        """Reset the singleton instance.

        This method is primarily for testing purposes to allow creating
        a fresh instance with different configurations.

        Returns:
            None

        Raises:
            None
        """
        cls._instance = None
        cls._initialized = False


def get_scanner() -> Scanner:
    """Get the global sensitive data scanner instance.

    Returns the singleton instance of the scanner.

    Returns:
        Scanner: The singleton scanner instance.

    Raises:
        None
    """
    return Scanner()


def configure_scanner(
    custom_patterns: dict[str, str | None] | None = None,
) -> Scanner:
    """Configure the global scanner with custom patterns.

    Note: Due to the singleton pattern, this will only apply custom patterns
    if the scanner hasn't been initialized yet. To reconfigure an existing
    scanner, use reset_singleton() first.

    Args:
        custom_patterns (dict[str, str | None]): Custom patterns to add
            to the scanner.

    Returns:
        Scanner: The configured singleton scanner instance.

    Raises:
        re.error: If any custom patterns are invalid.
    """
    # Reset the singleton to allow reconfiguration
    Scanner.reset_singleton()
    return Scanner(custom_patterns)


def scan_and_redact(text: str) -> str:
    """Convenience function to scan and redact text using the global scanner.

    Args:
        text (str): The text to scan and redact.

    Returns:
        str: The text with sensitive data redacted.

    Raises:
        None
    """
    scanner = get_scanner()
    return scanner.scan_and_redact(text)


def has_sensitive_data(text: str) -> bool:
    """Convenience function to check for sensitive data using the global scanner.

    Args:
        text (str): The text to check.

    Returns:
        bool: True if sensitive data is detected, False otherwise.

    Raises:
        None
    """
    scanner = get_scanner()
    return scanner.has_sensitive_data(text)
