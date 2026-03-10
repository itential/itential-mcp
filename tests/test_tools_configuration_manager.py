# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.tools.configuration_manager import render_template
from itential_mcp.models.configuration_manager import RenderTemplateResponse
from fastmcp import Context


class TestRenderTemplateTool:
    """Regression tests for Bug 07 — render_template must await the service call.

    Previously, client.configuration_manager.render_template() was called without
    await. Without await, data holds a coroutine object rather than the rendered
    string. Since RenderTemplateResponse.result is typed as str, Pydantic would raise:
        ValidationError: Input should be a valid string ... input_type=coroutine
    In a looser-typed model the tool would silently return a coroutine repr string
    instead of the actual rendered output — a silent data-correctness failure.
    """

    def setup_method(self):
        """Set up shared mock fixtures."""
        self.mock_context = AsyncMock(spec=Context)
        self.mock_context.info = AsyncMock()

        self.mock_client = MagicMock()
        self.mock_cm_service = MagicMock()
        self.mock_cm_service.render_template = AsyncMock()

        self.mock_client.configuration_manager = self.mock_cm_service
        self.mock_context.request_context.lifespan_context.get.return_value = (
            self.mock_client
        )

    @pytest.mark.asyncio
    async def test_render_template_awaits_service_call(self):
        """render_template must await the configuration_manager service call.

        The mock is an AsyncMock — if the tool does NOT await it, the coroutine
        object propagates to RenderTemplateResponse(result=data) and Pydantic raises
        ValidationError because result is typed as str. If it DOES await, the mock
        returns the configured rendered string and the response model is valid.
        """
        self.mock_cm_service.render_template.return_value = "Hello World!"

        result = await render_template(
            self.mock_context,
            template="Hello {{ name }}!",
            variables={"name": "World"},
        )

        self.mock_cm_service.render_template.assert_awaited_once()
        assert isinstance(result, RenderTemplateResponse)
        assert result.result == "Hello World!"

    @pytest.mark.asyncio
    async def test_render_template_passes_template_and_variables(self):
        """render_template must pass template and variables as kwargs to the service."""
        self.mock_cm_service.render_template.return_value = (
            "interface GigabitEthernet0/1"
        )

        await render_template(
            self.mock_context,
            template="interface {{ iface }}",
            variables={"iface": "GigabitEthernet0/1"},
        )

        self.mock_cm_service.render_template.assert_awaited_once_with(
            template="interface {{ iface }}",
            variables={"iface": "GigabitEthernet0/1"},
        )

    @pytest.mark.asyncio
    async def test_render_template_returns_correct_response_type(self):
        """render_template must return a RenderTemplateResponse instance."""
        self.mock_cm_service.render_template.return_value = "rendered output"

        result = await render_template(
            self.mock_context,
            template="some template",
            variables=None,
        )

        assert isinstance(result, RenderTemplateResponse)

    @pytest.mark.asyncio
    async def test_render_template_accepts_none_variables(self):
        """render_template must handle variables=None and pass it through to the service."""
        self.mock_cm_service.render_template.return_value = "static output"

        result = await render_template(
            self.mock_context,
            template="static template",
            variables=None,
        )

        self.mock_cm_service.render_template.assert_awaited_once_with(
            template="static template",
            variables=None,
        )
        assert result.result == "static output"

    @pytest.mark.asyncio
    async def test_render_template_parses_string_variables(self):
        """render_template must parse a JSON string into a dict before calling the service."""
        self.mock_cm_service.render_template.return_value = "Hello World!"

        await render_template(
            self.mock_context,
            template="Hello {{ name }}!",
            variables='{"name": "World"}',
        )

        call_kwargs = self.mock_cm_service.render_template.call_args
        assert call_kwargs.kwargs["variables"] == {"name": "World"}

    @pytest.mark.asyncio
    async def test_render_template_logs_entry(self):
        """render_template must log entry via ctx.info."""
        self.mock_cm_service.render_template.return_value = "output"

        await render_template(
            self.mock_context,
            template="t",
            variables=None,
        )

        self.mock_context.info.assert_called_once_with("inside render_template()")
