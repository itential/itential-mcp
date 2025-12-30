# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the heuristics sensitive data scanner module."""

import pytest
import re
from itential_mcp.core.heuristics import (
    Scanner,
    get_scanner,
    configure_scanner,
    scan_and_redact,
    has_sensitive_data,
)


class TestScanner:
    """Test cases for the Scanner class."""

    def setup_method(self):
        """Reset the singleton before each test."""
        Scanner.reset_singleton()

    def test_scanner_initialization(self):
        """Test that scanner initializes with default patterns."""
        scanner = Scanner()
        patterns = scanner.list_patterns()

        # Check that default patterns are loaded
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

    def test_singleton_behavior(self):
        """Test that scanner follows singleton pattern."""
        scanner1 = Scanner()
        scanner2 = Scanner()

        # Both references should point to the same instance
        assert scanner1 is scanner2

        # Adding a pattern to one should affect the other
        scanner1.add_pattern("test_singleton", r"TEST-\d{4}")
        assert "test_singleton" in scanner2.list_patterns()

    def test_singleton_reset(self):
        """Test that singleton can be reset."""
        scanner1 = Scanner()
        scanner1.add_pattern("test_reset", r"RESET-\d{4}")

        # Reset the singleton
        Scanner.reset_singleton()

        # New instance should not have the custom pattern
        scanner2 = Scanner()
        assert "test_reset" not in scanner2.list_patterns()

        # But should still be a singleton
        scanner3 = Scanner()
        assert scanner2 is scanner3

    def test_custom_patterns_initialization(self):
        """Test scanner initialization with custom patterns."""
        custom_patterns = {
            "custom_token": r"CUSTOM-[A-Z0-9]{16}",
            "test_secret": r"test_secret:\s*([a-z0-9]+)",
        }

        scanner = Scanner(custom_patterns)
        patterns = scanner.list_patterns()

        assert "custom_token" in patterns
        assert "test_secret" in patterns

    def test_invalid_regex_pattern(self):
        """Test that invalid regex patterns raise appropriate errors."""
        scanner = Scanner()

        with pytest.raises(re.error):
            scanner.add_pattern("invalid", "[invalid regex")

    def test_add_remove_patterns(self):
        """Test adding and removing patterns."""
        scanner = Scanner()

        # Add a new pattern
        scanner.add_pattern("test_pattern", r"TEST-\d{4}")
        assert "test_pattern" in scanner.list_patterns()

        # Remove the pattern
        assert scanner.remove_pattern("test_pattern") is True
        assert "test_pattern" not in scanner.list_patterns()

        # Try to remove non-existent pattern
        assert scanner.remove_pattern("non_existent") is False

    def test_api_key_pattern_exists(self):
        """Test that API key pattern is registered."""
        scanner = Scanner()
        patterns = scanner.list_patterns()
        assert "api_key" in patterns

    def test_bearer_token_pattern_exists(self):
        """Test that bearer token pattern is registered."""
        scanner = Scanner()
        patterns = scanner.list_patterns()
        assert "bearer_token" in patterns

    def test_jwt_token_detection(self):
        """Test detection and redaction of JWT tokens."""
        scanner = Scanner()

        jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        text = f"Token: {jwt_token}"

        assert scanner.has_sensitive_data(text)
        redacted = scanner.scan_and_redact(text)
        assert "[REDACTED_JWT_TOKEN]" in redacted
        assert jwt_token not in redacted

    def test_password_detection(self):
        """Test detection and redaction of passwords."""
        scanner = Scanner()

        test_cases = [
            "password=mySecretPass123",
            'PASSWORD: "SuperSecret456"',
            "pwd='P@ssw0rd!'",
        ]

        for test_case in test_cases:
            assert scanner.has_sensitive_data(test_case)
            redacted = scanner.scan_and_redact(test_case)
            assert "[REDACTED_PASSWORD]" in redacted

    def test_email_in_auth_detection(self):
        """Test detection of email addresses in authentication contexts."""
        scanner = Scanner()

        test_cases = [
            "username=user@example.com",
            "email: 'test.user@domain.org'",
            'user="admin@company.net"',
        ]

        for test_case in test_cases:
            assert scanner.has_sensitive_data(test_case)
            redacted = scanner.scan_and_redact(test_case)
            assert "[REDACTED_EMAIL_IN_AUTH]" in redacted

    def test_auth_url_detection(self):
        """Test detection of URLs with authentication."""
        scanner = Scanner()

        test_cases = [
            "https://dbuser:mypassword@api.example.com/data",
            "http://admin:secret123@database.internal/",
        ]

        for test_case in test_cases:
            assert scanner.has_sensitive_data(test_case)
            redacted = scanner.scan_and_redact(test_case)
            assert "[REDACTED_AUTH_URL]" in redacted

    def test_db_connection_detection(self):
        """Test detection of database connection strings."""
        scanner = Scanner()

        test_cases = [
            "mongodb://user:password@localhost:27017/database",
            "postgresql://admin:secret@db.example.com:5432/mydb",
            "mysql://root:password123@mysql.server.com/app",
        ]

        for test_case in test_cases:
            assert scanner.has_sensitive_data(test_case)
            redacted = scanner.scan_and_redact(test_case)
            assert "[REDACTED_DB_CONNECTION]" in redacted

    def test_private_key_detection(self):
        """Test detection of private keys."""
        scanner = Scanner()

        private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA7Z8kGzxc0123456789abcdefghijklmnopqrstuvwxyz
-----END RSA PRIVATE KEY-----"""

        assert scanner.has_sensitive_data(private_key)
        redacted = scanner.scan_and_redact(private_key)
        assert "[REDACTED_PRIVATE_KEY]" in redacted
        assert "BEGIN RSA PRIVATE KEY" not in redacted

    def test_multiple_sensitive_data_types(self):
        """Test text with multiple types of sensitive data."""
        scanner = Scanner()

        text = "API_KEY=abc123def456789012 and password=secret123 and user=admin@company.com"

        detected_types = scanner.get_sensitive_data_types(text)
        assert "api_key" in detected_types
        assert "password" in detected_types
        assert "email_in_auth" in detected_types

        redacted = scanner.scan_and_redact(text)
        assert "[REDACTED_API_KEY]" in redacted
        assert "[REDACTED_PASSWORD]" in redacted
        assert "[REDACTED_EMAIL_IN_AUTH]" in redacted

    def test_pattern_management(self):
        """Test pattern addition and removal."""
        scanner = Scanner()

        # Test adding patterns
        scanner.add_pattern("test_pattern", r"TEST-\d{4}")
        assert "test_pattern" in scanner.list_patterns()

        # Test removing patterns
        assert scanner.remove_pattern("test_pattern") is True
        assert "test_pattern" not in scanner.list_patterns()

    def test_empty_or_none_input(self):
        """Test handling of empty or None inputs."""
        scanner = Scanner()

        assert not scanner.has_sensitive_data("")
        assert not scanner.has_sensitive_data(None)
        assert scanner.scan_and_redact("") == ""
        assert scanner.scan_and_redact(None) is None
        assert scanner.get_sensitive_data_types("") == []
        assert scanner.get_sensitive_data_types(None) == []

    def test_custom_redaction_function(self):
        """Test custom redaction functions."""
        scanner = Scanner()

        def custom_redaction(match):
            return f"<HIDDEN:{len(match)}>"

        scanner.add_pattern("test_custom", r"CUSTOM-\w+", custom_redaction)

        text = "Token: CUSTOM-abc123def456"
        redacted = scanner.scan_and_redact(text)
        assert "<HIDDEN:" in redacted
        assert "CUSTOM-abc123def456" not in redacted


class TestGlobalScannerFunctions:
    """Test cases for global scanner convenience functions."""

    def setup_method(self):
        """Reset the singleton before each test."""
        Scanner.reset_singleton()

    def test_get_scanner_singleton(self):
        """Test that get_scanner returns the same instance."""
        scanner1 = get_scanner()
        scanner2 = get_scanner()
        assert scanner1 is scanner2

    def test_configure_scanner(self):
        """Test configuring the global scanner."""
        custom_patterns = {"test_global": r"GLOBAL-\d+"}

        scanner = configure_scanner(custom_patterns)
        assert "test_global" in scanner.list_patterns()

        # Test that the global scanner was updated
        global_scanner = get_scanner()
        assert "test_global" in global_scanner.list_patterns()

    def test_scan_and_redact_function(self):
        """Test the global scan_and_redact convenience function."""
        text = "API_KEY=test123456789abcdef"
        redacted = scan_and_redact(text)
        assert "[REDACTED_API_KEY]" in redacted

    def test_has_sensitive_data_function(self):
        """Test the global has_sensitive_data convenience function."""
        assert has_sensitive_data("password=secret123")
        assert not has_sensitive_data("normal log message")


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def setup_method(self):
        """Reset the singleton before each test."""
        Scanner.reset_singleton()

    def test_overlapping_patterns(self):
        """Test behavior with overlapping pattern matches."""
        scanner = Scanner()

        # This could match both api_key and password patterns
        text = "api_key=password1234567890"
        redacted = scanner.scan_and_redact(text)

        # Should be redacted (order of patterns may affect which one matches)
        assert "password1234567890" not in redacted
        assert "REDACTED" in redacted

    def test_pattern_case_sensitivity(self):
        """Test case sensitivity of patterns."""
        scanner = Scanner()

        test_cases = [
            "API_KEY=test1234567890abcdef",
            "api_key=test1234567890abcdef",
            "Api_Key=test1234567890abcdef",
        ]

        for test_case in test_cases:
            assert scanner.has_sensitive_data(test_case)

    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters."""
        scanner = Scanner()

        text = "password=tëst123!@#$%^&*()"
        assert scanner.has_sensitive_data(text)
        redacted = scanner.scan_and_redact(text)
        assert "[REDACTED_PASSWORD]" in redacted

    def test_very_long_strings(self):
        """Test performance with very long strings."""
        scanner = Scanner()

        # Create a long string with sensitive data embedded
        long_text = "a" * 10000 + " API_KEY=test1234567890abcdef " + "b" * 10000

        assert scanner.has_sensitive_data(long_text)
        redacted = scanner.scan_and_redact(long_text)
        assert "[REDACTED_API_KEY]" in redacted
        assert "test1234567890abcdef" not in redacted

    def test_multiline_strings(self):
        """Test handling of multiline strings."""
        scanner = Scanner()

        multiline_text = """Log entry 1: normal message
API_KEY=secret1234567890abcdef
Log entry 2: another normal message
password=mysecretpass"""

        assert scanner.has_sensitive_data(multiline_text)
        redacted = scanner.scan_and_redact(multiline_text)
        assert "[REDACTED_API_KEY]" in redacted
        assert "[REDACTED_PASSWORD]" in redacted
        assert "secret1234567890abcdef" not in redacted
        assert "mysecretpass" not in redacted
