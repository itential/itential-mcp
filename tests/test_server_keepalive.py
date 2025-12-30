# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for server keepalive functionality."""

import asyncio
import pytest
from unittest.mock import AsyncMock, Mock

from itential_mcp.server.keepalive import keepalive_task, start_keepalive


class MockPlatformClient:
    def __init__(self):
        self.get = AsyncMock()


class TestKeepaliveTask:
    """Test cases for keepalive_task function."""

    @pytest.mark.asyncio
    async def test_keepalive_task_makes_request(self):
        """Test that keepalive task makes GET requests to /whoami."""
        client = MockPlatformClient()
        mock_response = Mock()
        mock_response.status = 200
        client.get.return_value = mock_response

        # Create task and let it run for a short time
        task = asyncio.create_task(keepalive_task(client, 0.1))
        await asyncio.sleep(0.15)  # Let it run for one iteration
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        # Verify the client.get was called with /whoami
        client.get.assert_called_with("/whoami")
        assert client.get.call_count >= 1

    @pytest.mark.asyncio
    async def test_keepalive_task_continues_on_error(self):
        """Test that keepalive task continues running even when requests fail."""
        client = MockPlatformClient()
        client.get.side_effect = Exception("Connection failed")

        # Create task and let it run for a short time
        task = asyncio.create_task(keepalive_task(client, 0.1))
        await asyncio.sleep(0.25)  # Let it run for multiple iterations
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        # Verify multiple calls were made despite errors
        assert client.get.call_count >= 2

    @pytest.mark.asyncio
    async def test_keepalive_task_respects_interval(self):
        """Test that keepalive task waits for the specified interval."""
        client = MockPlatformClient()
        mock_response = Mock()
        mock_response.status = 200
        client.get.return_value = mock_response

        start_time = asyncio.get_event_loop().time()

        # Create task with 0.2 second interval
        task = asyncio.create_task(keepalive_task(client, 0.2))
        await asyncio.sleep(0.45)  # Let it run for 2+ intervals
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        elapsed_time = asyncio.get_event_loop().time() - start_time

        # Should have made at least 2 calls in 0.45 seconds with 0.2 interval
        assert client.get.call_count >= 2
        assert elapsed_time >= 0.4  # At least 2 intervals


class TestStartKeepalive:
    """Test cases for start_keepalive function."""

    @pytest.mark.asyncio
    async def test_start_keepalive_returns_task(self):
        """Test that start_keepalive returns an asyncio Task."""
        client = MockPlatformClient()

        task = start_keepalive(client, 300)

        assert isinstance(task, asyncio.Task)
        assert not task.done()

        # Clean up the task
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_start_keepalive_task_runs(self):
        """Test that the task returned by start_keepalive actually runs."""
        client = MockPlatformClient()
        mock_response = Mock()
        mock_response.status = 200
        client.get.return_value = mock_response

        task = start_keepalive(client, 0.1)

        # Let the task run briefly
        await asyncio.sleep(0.15)
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        # Verify the keepalive task made at least one request
        client.get.assert_called_with("/whoami")


class TestKeepaliveIntegration:
    """Integration tests for keepalive functionality."""

    @pytest.mark.asyncio
    async def test_keepalive_with_real_async_patterns(self):
        """Test keepalive works with realistic async patterns."""
        client = MockPlatformClient()
        responses = [
            Mock(status=200),
            Mock(status=200),
            Exception("Network error"),
            Mock(status=200),
        ]
        client.get.side_effect = responses

        task = start_keepalive(client, 0.05)  # Very short interval for testing

        # Let it run through multiple iterations including an error
        await asyncio.sleep(0.25)
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        # Should have attempted multiple calls
        assert client.get.call_count >= 3
