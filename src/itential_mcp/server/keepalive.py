# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Background keepalive module for preventing authentication session timeouts.

This module provides background task functionality to maintain active sessions
with the Itential Platform by periodically making authenticated requests to
prevent session timeouts.
"""

import asyncio

from ..core import logging
from ..platform import PlatformClient


async def keepalive_task(client: PlatformClient, interval: int) -> None:
    """Background task to maintain authentication session by making periodic requests.

    This function runs in the background and periodically makes GET requests to the
    /whoami endpoint to prevent authentication sessions from timing out due to
    inactivity.

    Args:
        client (PlatformClient): The platform client instance to use for requests.
        interval (int): Sleep interval in seconds between keepalive requests.

    Returns:
        None

    Raises:
        Exception: Any exception from the HTTP request is logged but does not
            stop the keepalive loop to maintain robustness.
    """
    logger = logging.get_logger()
    logger.info(f"Starting keepalive task with {interval}s interval")

    while True:
        try:
            await asyncio.sleep(interval)

            # Make the keepalive request to prevent session timeout
            response = await client.get("/whoami")
            logger.debug(f"Keepalive request completed: status={response.status_code}")

        except Exception as exc:
            # Log the error but don't stop the keepalive task
            logger.warning(f"Keepalive request failed: {exc}")


def start_keepalive(client: "PlatformClient", interval: int) -> asyncio.Task:
    """Start the background keepalive task.

    Creates and starts a background asyncio task that will run the keepalive
    function with the provided client and interval.

    Args:
        client (PlatformClient): The platform client instance to use for requests.
        interval (int): Sleep interval in seconds between keepalive requests.

    Returns:
        asyncio.Task: The created background task.

    Raises:
        None
    """
    task = asyncio.create_task(keepalive_task(client, interval))
    return task
