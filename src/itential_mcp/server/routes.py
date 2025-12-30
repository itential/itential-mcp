# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from starlette.requests import Request
from starlette.responses import JSONResponse

from ..platform import PlatformClient


async def get_healthz(request: Request) -> JSONResponse:
    """
    Kubernetes healthz endpoint - general health check.

    Returns HTTP 200 if the server is healthy, otherwise HTTP 503.
    This is used by Kubernetes for general health monitoring.

    Args:
        request: The incoming HTTP request

    Returns:
        JSONResponse: Status response with HTTP 200 for healthy, 503 for unhealthy
    """
    try:
        # Basic server health check - server is running if we reach here
        return JSONResponse(content={"status": "ok"}, status_code=200)
    except Exception:
        return JSONResponse(content={"status": "unhealthy"}, status_code=503)


async def get_readyz(request: Request) -> JSONResponse:
    """
    Kubernetes readyz endpoint - readiness probe.

    Returns HTTP 200 if the server is ready to accept traffic, otherwise HTTP 503.
    Used by Kubernetes to determine if the pod should receive traffic.

    This endpoint checks if the server can successfully communicate with the
    Itential Platform by performing a /whoami request. If successful, the
    server is considered ready to handle requests.

    Args:
        request: The incoming HTTP request

    Returns:
        JSONResponse: Status response with HTTP 200 for ready, 503 for not ready
    """
    try:
        async with PlatformClient() as client_instance:
            await client_instance.get("/whoami")
        return JSONResponse(content={"status": "ready"}, status_code=200)
    except Exception as e:
        return JSONResponse(
            content={"status": "not ready", "reason": str(e)}, status_code=503
        )


async def get_livez(request: Request) -> JSONResponse:
    """
    Kubernetes livez endpoint - liveness probe.

    Returns HTTP 200 if the server is alive, otherwise HTTP 503.
    Used by Kubernetes to determine if the pod should be restarted.

    Args:
        request: The incoming HTTP request

    Returns:
        JSONResponse: Status response with HTTP 200 for alive, 503 for dead
    """
    try:
        # Basic liveness check - if we can respond, we're alive
        return JSONResponse(content={"status": "alive"}, status_code=200)
    except Exception:
        return JSONResponse(content={"status": "dead"}, status_code=503)
