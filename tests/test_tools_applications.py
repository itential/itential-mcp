# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.tools.applications import start_application
from itential_mcp.models.applications import StartApplicationResponse
from fastmcp import Context


class TestStartApplicationTool:
    """Regression tests for Bug 06 — start_application must await the service call.

    Previously, client.applications.start_application() was called without await,
    causing a TypeError: 'coroutine' object is not subscriptable when the tool
    attempted data["id"] on the unawaited coroutine.

    The sibling tools stop_application (line 129) and restart_application (line 168)
    in the same file both correctly await their service calls. This test class ensures
    start_application is consistent with that pattern.
    """

    def setup_method(self):
        """Set up shared mock fixtures."""
        self.mock_context = AsyncMock(spec=Context)
        self.mock_context.info = AsyncMock()

        self.mock_client = MagicMock()
        self.mock_app_service = MagicMock()
        self.mock_app_service.start_application = AsyncMock()

        self.mock_client.applications = self.mock_app_service
        self.mock_context.request_context.lifespan_context.get.return_value = (
            self.mock_client
        )

    @pytest.mark.asyncio
    async def test_start_application_awaits_service_call(self):
        """start_application must await the applications service call.

        The mock is an AsyncMock — if the tool does NOT await it, the coroutine
        object propagates and data["id"] raises TypeError. If it DOES await,
        the mock returns the configured dict and the response model is valid.
        """
        self.mock_app_service.start_application.return_value = {
            "id": "WorkFlowEngine",
            "state": "RUNNING",
        }

        result = await start_application(
            self.mock_context, name="WorkFlowEngine", timeout=10
        )

        self.mock_app_service.start_application.assert_awaited_once()
        assert isinstance(result, StartApplicationResponse)
        assert result.name == "WorkFlowEngine"
        assert result.state == "RUNNING"

    @pytest.mark.asyncio
    async def test_start_application_passes_name_and_timeout(self):
        """start_application must pass name and timeout positionally to the service."""
        self.mock_app_service.start_application.return_value = {
            "id": "AutomationStudio",
            "state": "RUNNING",
        }

        await start_application(self.mock_context, name="AutomationStudio", timeout=30)

        self.mock_app_service.start_application.assert_awaited_once_with(
            "AutomationStudio", 30
        )

    @pytest.mark.asyncio
    async def test_start_application_returns_correct_response_type(self):
        """start_application must return a StartApplicationResponse instance."""
        self.mock_app_service.start_application.return_value = {
            "id": "FormBuilder",
            "state": "RUNNING",
        }

        result = await start_application(
            self.mock_context, name="FormBuilder", timeout=10
        )

        assert isinstance(result, StartApplicationResponse)

    @pytest.mark.asyncio
    async def test_start_application_maps_id_to_name(self):
        """start_application must map the platform's id field to the response name field."""
        self.mock_app_service.start_application.return_value = {
            "id": "Search",
            "state": "RUNNING",
        }

        result = await start_application(self.mock_context, name="Search", timeout=10)

        assert result.name == "Search"

    @pytest.mark.asyncio
    async def test_start_application_logs_entry(self):
        """start_application must log entry via ctx.info."""
        self.mock_app_service.start_application.return_value = {
            "id": "Tags",
            "state": "RUNNING",
        }

        await start_application(self.mock_context, name="Tags", timeout=10)

        self.mock_context.info.assert_called_once_with("inside start_application(...)")
