# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from unittest.mock import AsyncMock, MagicMock

from itential_mcp.platform.services import ServiceBase
from itential_mcp.platform.services.workflow_engine import Service


def make_response(results, total):
    response = MagicMock()
    response.json.return_value = {"results": results, "total": total}
    return response


class TestWorkflowEngineService:
    """Test cases for the Workflow Engine Service class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_client = AsyncMock()
        self.workflow_service = Service(self.mock_client)

    def test_service_name(self):
        """Test that the service has the correct name."""
        assert self.workflow_service.name == "workflow_engine"

    def test_service_initialization(self):
        """Test service initialization with client."""
        assert self.workflow_service.client == self.mock_client

    def test_service_inherits_from_service_base(self):
        """Test the service inherits from ServiceBase."""
        assert isinstance(self.workflow_service, ServiceBase)

    @pytest.mark.asyncio
    async def test_get_job_metrics_defaults(self):
        """get_job_metrics issues one bounded GET and returns (items, total)."""
        items = [{"_id": "job-metric-1", "jobsComplete": 100}]
        self.mock_client.get.return_value = make_response(items, 1)

        result = await self.workflow_service.get_job_metrics()

        self.mock_client.get.assert_called_once_with(
            "/workflow_engine/jobs/metrics", params={"limit": 200, "skip": 0}
        )
        assert result == (items, 1)

    @pytest.mark.asyncio
    async def test_get_job_metrics_with_filters_and_paging(self):
        """Sibling filters are preserved alongside skip/limit."""
        params = {"containsField": "workflow.name", "contains": "wf"}
        self.mock_client.get.return_value = make_response([{"_id": "x"}], 450)

        items, total = await self.workflow_service.get_job_metrics(
            params, limit=50, skip=100
        )

        self.mock_client.get.assert_called_once_with(
            "/workflow_engine/jobs/metrics",
            params={
                "containsField": "workflow.name",
                "contains": "wf",
                "limit": 50,
                "skip": 100,
            },
        )
        assert items == [{"_id": "x"}]
        assert total == 450
        # caller's params are not mutated
        assert params == {"containsField": "workflow.name", "contains": "wf"}

    @pytest.mark.asyncio
    async def test_get_task_metrics_defaults(self):
        """get_task_metrics issues one bounded GET and returns (items, total)."""
        items = [{"taskId": "t1", "name": "task"}]
        self.mock_client.get.return_value = make_response(items, 1)

        result = await self.workflow_service.get_task_metrics()

        self.mock_client.get.assert_called_once_with(
            "/workflow_engine/tasks/metrics", params={"limit": 200, "skip": 0}
        )
        assert result == (items, 1)

    @pytest.mark.asyncio
    async def test_get_task_metrics_with_filters_and_paging(self):
        """equals/equalsField filters keep working with skip/limit."""
        self.mock_client.get.return_value = make_response([], 0)

        await self.workflow_service.get_task_metrics(
            {"equalsField": "app", "equals": "WorkFlowEngine"}, limit=10, skip=20
        )

        self.mock_client.get.assert_called_once_with(
            "/workflow_engine/tasks/metrics",
            params={
                "equalsField": "app",
                "equals": "WorkFlowEngine",
                "limit": 10,
                "skip": 20,
            },
        )

    @pytest.mark.asyncio
    async def test_does_not_follow_additional_pages(self):
        """Even when total exceeds the page, only one request is made."""
        self.mock_client.get.return_value = make_response(
            [{"i": n} for n in range(200)], 5000
        )

        items, total = await self.workflow_service.get_task_metrics()

        assert self.mock_client.get.call_count == 1
        assert len(items) == 200
        assert total == 5000

    @pytest.mark.asyncio
    async def test_get_metrics_error_propagates(self):
        """Client errors propagate to the caller."""
        self.mock_client.get.side_effect = Exception("boom")

        with pytest.raises(Exception, match="boom"):
            await self.workflow_service.get_job_metrics()
        with pytest.raises(Exception, match="boom"):
            await self.workflow_service.get_task_metrics()


class TestServiceBaseGetPage:
    """Test the ServiceBase._get_page single-page helper."""

    def setup_method(self):
        self.mock_client = AsyncMock()
        self.service = ServiceBase(self.mock_client)

    @pytest.mark.asyncio
    async def test_single_get_with_params(self):
        self.mock_client.get.return_value = make_response([{"a": 1}], 9)

        items, total = await self.service._get_page(
            "/some/path", params={"equals": "x"}, limit=5, skip=2
        )

        self.mock_client.get.assert_called_once_with(
            "/some/path", params={"equals": "x", "limit": 5, "skip": 2}
        )
        assert items == [{"a": 1}]
        assert total == 9

    @pytest.mark.asyncio
    async def test_custom_keys(self):
        response = MagicMock()
        response.json.return_value = {"data": [{"a": 1}], "count": 3}
        self.mock_client.get.return_value = response

        items, total = await self.service._get_page(
            "/p", data_key="data", total_key="count"
        )

        assert items == [{"a": 1}]
        assert total == 3

    @pytest.mark.asyncio
    async def test_missing_total_falls_back_to_skip_plus_items(self):
        response = MagicMock()
        response.json.return_value = {"results": [{"a": 1}, {"a": 2}]}
        self.mock_client.get.return_value = response

        items, total = await self.service._get_page("/p", skip=10)

        assert total == 12

    @pytest.mark.asyncio
    async def test_empty_response(self):
        response = MagicMock()
        response.json.return_value = {}
        self.mock_client.get.return_value = response

        assert await self.service._get_page("/p") == ([], 0)
