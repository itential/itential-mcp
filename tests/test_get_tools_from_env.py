# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import configparser

import pytest

from itential_mcp import config as config_module
from itential_mcp.config import _get_tools_from_env


@pytest.fixture(autouse=True)
def clear_config_cache():
    """Ensure config.get() doesn't cache between tests"""
    config_module.get.cache_clear()
    yield
    config_module.get.cache_clear()


class TestGetToolsFromEnv:
    """Test cases for _get_tools_from_env function."""

    def test_get_tools_from_env_empty_environment(self, monkeypatch):
        """Test _get_tools_from_env returns empty dict when no tool env vars exist."""
        # Clear any existing ITENTIAL_MCP_TOOL_ variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_TOOL_"):
                monkeypatch.delenv(key, raising=False)

        result = _get_tools_from_env()
        assert result == {}

    def test_get_tools_from_env_single_tool(self, monkeypatch):
        """Test _get_tools_from_env with a single tool configuration."""
        # Clear existing variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_TOOL_"):
                monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv("ITENTIAL_MCP_TOOL_mytool_NAME", "My Tool")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_mytool_TYPE", "endpoint")
        monkeypatch.setenv(
            "ITENTIAL_MCP_TOOL_mytool_DESCRIPTION", "Test tool description"
        )

        result = _get_tools_from_env()

        expected = {
            "mytool": {
                "name": "My Tool",
                "type": "endpoint",
                "description": "Test tool description",
            }
        }
        assert result == expected

    def test_get_tools_from_env_multiple_tools(self, monkeypatch):
        """Test _get_tools_from_env with multiple tool configurations."""
        # Clear existing variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_TOOL_"):
                monkeypatch.delenv(key, raising=False)

        # Tool 1
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_tool1_NAME", "Tool One")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_tool1_TYPE", "endpoint")

        # Tool 2
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_tool2_NAME", "Tool Two")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_tool2_TYPE", "endpoint")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_tool2_AUTOMATION", "test-automation")

        result = _get_tools_from_env()

        expected = {
            "tool1": {"name": "Tool One", "type": "endpoint"},
            "tool2": {
                "name": "Tool Two",
                "type": "endpoint",
                "automation": "test-automation",
            },
        }
        assert result == expected

    def test_get_tools_from_env_config_keys_no_underscores(self, monkeypatch):
        """Test _get_tools_from_env with simple config keys (no underscores in keys).

        Note: With rsplit on last underscore to support underscores in tool names,
        config keys cannot contain underscores.
        """
        # Clear existing variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_TOOL_"):
                monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv("ITENTIAL_MCP_TOOL_mytool_NAME", "My Tool")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_mytool_DESCRIPTION", "A description")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_mytool_TYPE", "endpoint")

        result = _get_tools_from_env()

        expected = {
            "mytool": {
                "name": "My Tool",
                "description": "A description",
                "type": "endpoint",
            }
        }
        assert result == expected

    def test_get_tools_from_env_ignores_non_tool_variables(self, monkeypatch):
        """Test _get_tools_from_env ignores non-tool environment variables."""
        # Clear existing variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_TOOL_"):
                monkeypatch.delenv(key, raising=False)

        # Set non-tool variables
        monkeypatch.setenv("ITENTIAL_MCP_SERVER_HOST", "localhost")
        monkeypatch.setenv("ITENTIAL_MCP_PLATFORM_USER", "admin")
        monkeypatch.setenv("OTHER_TOOL_CONFIG", "should be ignored")

        # Set one tool variable
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_test_NAME", "Test Tool")

        result = _get_tools_from_env()

        expected = {"test": {"name": "Test Tool"}}
        assert result == expected

    def test_get_tools_from_env_invalid_format_too_few_parts(self, monkeypatch):
        """Test _get_tools_from_env raises ValueError for invalid format with too few parts."""
        # Clear existing variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_TOOL_"):
                monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv("ITENTIAL_MCP_TOOL_invalidformat", "value")

        with pytest.raises(ValueError) as exc_info:
            _get_tools_from_env()

        assert "Invalid tool environment variable format" in str(exc_info.value)
        assert "ITENTIAL_MCP_TOOL_invalidformat" in str(exc_info.value)
        assert "Expected format: ITENTIAL_MCP_TOOL_<tool_name>_<key>=<value>" in str(
            exc_info.value
        )

    def test_get_tools_from_env_empty_tool_name(self, monkeypatch):
        """Test _get_tools_from_env raises ValueError for empty tool name."""
        # Clear existing variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_TOOL_"):
                monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv("ITENTIAL_MCP_TOOL__KEY", "value")

        with pytest.raises(ValueError) as exc_info:
            _get_tools_from_env()

        assert "Tool name and config key cannot be empty" in str(exc_info.value)
        assert "ITENTIAL_MCP_TOOL__KEY" in str(exc_info.value)

    def test_get_tools_from_env_empty_config_key(self, monkeypatch):
        """Test _get_tools_from_env raises ValueError for empty config key."""
        # Clear existing variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_TOOL_"):
                monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv("ITENTIAL_MCP_TOOL_mytool_", "value")

        with pytest.raises(ValueError) as exc_info:
            _get_tools_from_env()

        assert "Tool name and config key cannot be empty" in str(exc_info.value)
        assert "ITENTIAL_MCP_TOOL_mytool_" in str(exc_info.value)

    def test_get_tools_from_env_empty_values_allowed(self, monkeypatch):
        """Test _get_tools_from_env allows empty values for configuration."""
        # Clear existing variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_TOOL_"):
                monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv("ITENTIAL_MCP_TOOL_mytool_NAME", "")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_mytool_DESCRIPTION", "")

        result = _get_tools_from_env()

        expected = {"mytool": {"name": "", "description": ""}}
        assert result == expected

    def test_get_tools_from_env_special_characters_in_values(self, monkeypatch):
        """Test _get_tools_from_env handles special characters in values."""
        # Clear existing variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_TOOL_"):
                monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv(
            "ITENTIAL_MCP_TOOL_mytool_NAME", "Tool with spaces & special chars!"
        )
        monkeypatch.setenv(
            "ITENTIAL_MCP_TOOL_mytool_DESCRIPTION",
            "Description with\nnewlines\tand\ttabs",
        )
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_mytool_CONFIG", "key=value,other=123")

        result = _get_tools_from_env()

        expected = {
            "mytool": {
                "name": "Tool with spaces & special chars!",
                "description": "Description with\nnewlines\tand\ttabs",
                "config": "key=value,other=123",
            }
        }
        assert result == expected

    def test_get_tools_from_env_numeric_tool_names(self, monkeypatch):
        """Test _get_tools_from_env with numeric characters in tool names."""
        # Clear existing variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_TOOL_"):
                monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv("ITENTIAL_MCP_TOOL_tool123_NAME", "Tool 123")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_abc123def_TYPE", "endpoint")

        result = _get_tools_from_env()

        expected = {"tool123": {"name": "Tool 123"}, "abc123def": {"type": "endpoint"}}
        assert result == expected

    def test_get_tools_from_env_underscores_in_tool_names(self, monkeypatch):
        """Test _get_tools_from_env with underscores in tool names."""
        # Clear existing variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_TOOL_"):
                monkeypatch.delenv(key, raising=False)

        # Test the exact scenario from the user's config
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_RUN_CLI_COMMAND_TYPE", "service")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_RUN_CLI_COMMAND_NAME", "run-cli-command")
        monkeypatch.setenv(
            "ITENTIAL_MCP_TOOL_RUN_CLI_COMMAND_CLUSTER", "autocon_cluster"
        )
        monkeypatch.setenv(
            "ITENTIAL_MCP_TOOL_RUN_CLI_COMMAND_DESCRIPTION",
            "Execute CLI command on network devices",
        )
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_RUN_CLI_COMMAND_TAGS", "custom")

        result = _get_tools_from_env()

        expected = {
            "RUN_CLI_COMMAND": {
                "type": "service",
                "name": "run-cli-command",
                "cluster": "autocon_cluster",
                "description": "Execute CLI command on network devices",
                "tags": "custom",
            }
        }
        assert result == expected


class TestConfigIntegration:
    """Test cases for integration of _get_tools_from_env with main config loading."""

    def test_config_integration_tools_from_env_and_file(self, tmp_path, monkeypatch):
        """Test that tools from environment variables are merged with file config."""
        # Clear existing tool variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_TOOL_"):
                monkeypatch.delenv(key, raising=False)

        # Create config file with tool
        config_path = tmp_path / "test.ini"
        cp = configparser.ConfigParser()
        cp["tool:filetool"] = {
            "name": "File Tool",
            "type": "endpoint",
            "automation": "file-automation",
        }

        with open(config_path, "w") as f:
            cp.write(f)

        # Set environment variables for tools
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_envtool_NAME", "Env Tool")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_envtool_TYPE", "endpoint")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_envtool_AUTOMATION", "env-automation")

        # Override file tool with env vars
        monkeypatch.setenv(
            "ITENTIAL_MCP_TOOL_filetool_DESCRIPTION", "Overridden by env"
        )

        monkeypatch.setenv("ITENTIAL_MCP_CONFIG", str(config_path))

        cfg = config_module.get()

        # Should have both tools
        assert len(cfg.tools) == 2

        # Find tools by name
        file_tool = next((t for t in cfg.tools if t.tool_name == "filetool"), None)
        env_tool = next((t for t in cfg.tools if t.tool_name == "envtool"), None)

        assert file_tool is not None
        assert env_tool is not None

        # File tool should have env override
        assert file_tool.name == "File Tool"  # from file
        assert file_tool.description == "Overridden by env"  # from env
        assert file_tool.automation == "file-automation"  # from file

        # Env tool should be created correctly
        assert env_tool.name == "Env Tool"
        assert env_tool.automation == "env-automation"

    def test_config_integration_tools_from_env_only(self, monkeypatch):
        """Test that tools are loaded from environment variables when no config file exists."""
        # Clear existing tool variables
        for key in list(os.environ.keys()):
            if key.startswith("ITENTIAL_MCP_TOOL_"):
                monkeypatch.delenv(key, raising=False)

        # Clear config file
        monkeypatch.delenv("ITENTIAL_MCP_CONFIG", raising=False)

        # Set environment variables for tools
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_envtool1_NAME", "Env Tool 1")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_envtool1_TYPE", "endpoint")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_envtool1_AUTOMATION", "automation1")

        monkeypatch.setenv("ITENTIAL_MCP_TOOL_envtool2_NAME", "Env Tool 2")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_envtool2_TYPE", "endpoint")
        monkeypatch.setenv("ITENTIAL_MCP_TOOL_envtool2_AUTOMATION", "automation2")

        cfg = config_module.get()

        # Should have both environment tools
        assert len(cfg.tools) == 2

        # Find tools by name
        tool1 = next((t for t in cfg.tools if t.tool_name == "envtool1"), None)
        tool2 = next((t for t in cfg.tools if t.tool_name == "envtool2"), None)

        assert tool1 is not None
        assert tool2 is not None

        # Check tool1
        assert tool1.name == "Env Tool 1"
        assert tool1.automation == "automation1"

        # Check tool2
        assert tool2.name == "Env Tool 2"
        assert tool2.automation == "automation2"
