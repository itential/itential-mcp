# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import asyncio
import pathlib
import importlib
import importlib.util
from typing import Any

import ipsdk

from ipsdk.platform import AsyncPlatform
from ipsdk.connection import Response
from ipsdk.http import HTTPMethod

from .. import config
from ..config.converters import platform_to_dict
from . import response
from ..core import exceptions
from ..core import logging

# Maximum number of characters of an upstream response body to include in an
# error message. Longer bodies are truncated to keep error output readable.
MAX_ERROR_BODY_LENGTH = 2048


def _format_error_message(exc: Exception) -> str:
    """Build an error message that includes the upstream response body.

    When the underlying exception carries an HTTP response (e.g. from
    ipsdk/httpx), the response body text is appended to the exception
    message so callers can see the actual error returned by the
    platform, not just a terse status line. The body is truncated to
    `MAX_ERROR_BODY_LENGTH` characters to keep error output readable.

    Only response bodies are ever included here -- request bodies are
    never surfaced in error messages.

    Args:
        exc (Exception): The exception raised while sending the request.

    Returns:
        str: The formatted error message, including the response body
            when available, or the plain exception message otherwise.

    Raises:
        None
    """
    if hasattr(exc, "response") and exc.response is not None:
        try:
            body = exc.response.text
        except Exception:
            body = None

        if body:
            if len(body) > MAX_ERROR_BODY_LENGTH:
                body = f"{body[:MAX_ERROR_BODY_LENGTH]}... (truncated)"
            return f"{exc} | response: {body}"

    return str(exc)


def _build_http_error(exc: Exception) -> exceptions.ItentialMcpException:
    """Build an ItentialMcpException from an HTTP status error.

    The message is formatted with the upstream response body (see
    `_format_error_message`). When the underlying exception carries a
    response with an integer HTTP status code, that code is preserved on the
    returned exception's `http_status` attribute so callers can branch on it
    (for example to treat a 404 as "no results") instead of parsing the
    message text.

    Args:
        exc (Exception): The HTTP status error raised by the ipsdk client.

    Returns:
        exceptions.ItentialMcpException: The reformatted exception.

    Raises:
        None
    """
    status = getattr(getattr(exc, "response", None), "status_code", None)
    if isinstance(status, int) and not isinstance(status, bool):
        return exceptions.ItentialMcpException(
            _format_error_message(exc), http_status=status
        )
    return exceptions.ItentialMcpException(_format_error_message(exc))


class _ErrorFormattingClient:
    """Wraps a raw ipsdk client to surface upstream response bodies on error.

    Service plugins under `platform/services/*.py` call `get`/`post`/`put`/
    `delete` directly on the raw ipsdk `AsyncPlatform` client, bypassing
    `PlatformClient.send_request()` entirely. This wrapper sits between the
    service plugins and the raw client so that `ipsdk.exceptions.HTTPStatusError`
    raised from any of those calls is reformatted to include the upstream
    response body, matching the error detail already provided on the
    `send_request()`/CLI code path.

    Only `ipsdk.exceptions.HTTPStatusError` is intercepted here. All other
    exceptions (network errors, timeouts, SDK errors, etc.) propagate
    unchanged, exactly as they would without this wrapper.

    The raw ipsdk response object is returned unchanged on success -- it is
    not wrapped in `platform.response.Response` since services consume the
    raw response shape directly (e.g. via `.json()`).

    Attributes:
        _client (AsyncPlatform): The wrapped raw ipsdk client.
    """

    def __init__(self, client: AsyncPlatform):
        """Initialize the wrapper around a raw ipsdk client.

        Args:
            client (AsyncPlatform): The raw ipsdk client to wrap.

        Returns:
            None

        Raises:
            None
        """
        self._client = client

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Send an HTTP GET request via the wrapped client.

        Args:
            path (str): The URI path to request.
            params (dict[str, Any] | None): Query string parameters. Defaults to None.

        Returns:
            Any: The raw ipsdk response object, unchanged.

        Raises:
            exceptions.ItentialMcpException: If the server returns an HTTP
                error status, with the upstream response body included.
        """
        try:
            return await self._client.get(path, params=params)
        except ipsdk.exceptions.HTTPStatusError as exc:
            raise _build_http_error(exc)

    async def post(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        json: str | bytes | dict | list | None = None,
    ) -> Any:
        """Send an HTTP POST request via the wrapped client.

        Args:
            path (str): The URI path to request.
            params (dict[str, Any] | None): Query string parameters. Defaults to None.
            json (str | bytes | dict | list | None): JSON body to send. Defaults to None.

        Returns:
            Any: The raw ipsdk response object, unchanged.

        Raises:
            exceptions.ItentialMcpException: If the server returns an HTTP
                error status, with the upstream response body included.
        """
        try:
            return await self._client.post(path, params=params, json=json)
        except ipsdk.exceptions.HTTPStatusError as exc:
            raise _build_http_error(exc)

    async def put(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        json: str | bytes | dict | list | None = None,
    ) -> Any:
        """Send an HTTP PUT request via the wrapped client.

        Args:
            path (str): The URI path to request.
            params (dict[str, Any] | None): Query string parameters. Defaults to None.
            json (str | bytes | dict | list | None): JSON body to send. Defaults to None.

        Returns:
            Any: The raw ipsdk response object, unchanged.

        Raises:
            exceptions.ItentialMcpException: If the server returns an HTTP
                error status, with the upstream response body included.
        """
        try:
            return await self._client.put(path, params=params, json=json)
        except ipsdk.exceptions.HTTPStatusError as exc:
            raise _build_http_error(exc)

    async def patch(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        json: str | bytes | dict | list | None = None,
    ) -> Any:
        """Send an HTTP PATCH request via the wrapped client.

        Args:
            path (str): The URI path to request.
            params (dict[str, Any] | None): Query string parameters. Defaults to None.
            json (str | bytes | dict | list | None): JSON body to send. Defaults to None.

        Returns:
            Any: The raw ipsdk response object, unchanged.

        Raises:
            exceptions.ItentialMcpException: If the server returns an HTTP
                error status, with the upstream response body included and
                the HTTP status code preserved on `http_status`.
        """
        try:
            return await self._client.patch(path, params=params, json=json)
        except ipsdk.exceptions.HTTPStatusError as exc:
            raise _build_http_error(exc)

    async def delete(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Send an HTTP DELETE request via the wrapped client.

        Args:
            path (str): The URI path to request.
            params (dict[str, Any] | None): Query string parameters. Defaults to None.

        Returns:
            Any: The raw ipsdk response object, unchanged.

        Raises:
            exceptions.ItentialMcpException: If the server returns an HTTP
                error status, with the upstream response body included.
        """
        try:
            return await self._client.delete(path, params=params)
        except ipsdk.exceptions.HTTPStatusError as exc:
            raise _build_http_error(exc)

    def __getattr__(self, name: str) -> Any:
        """Delegate any other attribute access to the wrapped client.

        Args:
            name (str): The attribute name being accessed.

        Returns:
            Any: The attribute value from the wrapped client.

        Raises:
            AttributeError: If the wrapped client does not have the attribute.
        """
        return getattr(self._client, name)


class PlatformClient(object):
    """Client for connecting to and interacting with Itential Platform.

    This client wraps the ipsdk AsyncPlatform client to provide standardized
    HTTP methods for API communication and automatic service discovery.
    It handles authentication, connection management, and returns Response objects.
    """

    def __init__(self):
        """Initialize the PlatformClient with connection and service plugins.

        Creates an AsyncPlatform client connection and dynamically loads
        all service plugins from the services directory.

        Args:
            None

        Returns:
            None

        Raises:
            Exception: If client initialization or plugin loading fails.
        """
        self.client = self._init_client()
        self._init_plugins()

        # Get timeout from configuration for use in API requests
        cfg = config.get()
        self.timeout = cfg.platform.timeout

    async def __aenter__(self):
        """Async context manager entry point.

        Args:
            None

        Returns:
            PlatformClient: Returns self for use in context manager.

        Raises:
            None
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit point.

        Performs cleanup operations when exiting the context manager.
        Closes the underlying client connection if it has a close method.

        Args:
            exc_type: Exception type if an exception occurred, None otherwise.
            exc_val: Exception value if an exception occurred, None otherwise.
            exc_tb: Exception traceback if an exception occurred, None otherwise.

        Returns:
            None

        Raises:
            None
        """
        if hasattr(self.client, "close") and callable(getattr(self.client, "close")):
            await self.client.close()

    def _init_client(self) -> AsyncPlatform:
        """Initialize the client connection to Itential Platform.

        Creates an AsyncPlatform client using configuration settings
        from the platform configuration. Logs security warnings when
        TLS verification is disabled.

        Args:
            None

        Returns:
            AsyncPlatform: An instance of AsyncPlatform configured for async operations.

        Raises:
            Exception: If platform client initialization fails.
        """
        cfg = config.get()

        # Warn if TLS verification is disabled (security risk)
        if cfg.platform.disable_verify:
            logging.warning(
                "⚠️  TLS certificate verification is DISABLED for platform connection. "
                "This is insecure and should only be used in development environments. "
                "Man-in-the-middle attacks are possible when verification is disabled."
            )

        # Warn if TLS is completely disabled (even more dangerous)
        if cfg.platform.disable_tls:
            logging.warning(
                "⚠️  TLS is DISABLED for platform connection. "
                "All communication with the platform will be unencrypted. "
                "This should NEVER be used in production environments."
            )

        # Convert PlatformConfig to dict format for ipsdk
        platform_dict = platform_to_dict(cfg.platform)
        return ipsdk.platform_factory(want_async=True, **platform_dict)

    def _init_plugins(self):
        """Dynamically load service plugins from the services directory.

        Discovers and imports Python modules from the services directory,
        instantiates their Service classes, and registers them as attributes
        on the client instance.

        Args:
            None

        Returns:
            None

        Raises:
            ImportError: If a service module cannot be loaded.
            AttributeError: If a service module lacks a Service class.
            Exception: If service instantiation fails.
        """
        services_path = pathlib.Path(__file__).resolve().parent / "services"

        # Early return if services directory doesn't exist
        if not services_path.exists():
            return

        # Wrap the raw ipsdk client so that service plugins get response
        # bodies included in HTTP error messages, matching the behavior of
        # PlatformClient.send_request(). Service plugins call get/post/put/
        # delete directly on this wrapped client rather than going through
        # send_request().
        wrapped_client = _ErrorFormattingClient(self.client)

        # Get Python files, excluding private modules and __pycache__
        python_files = [
            f
            for f in services_path.iterdir()
            if f.is_file() and f.suffix == ".py" and not f.name.startswith("_")
        ]

        # Import and register services
        for module_file in python_files:
            module_name = module_file.stem

            try:
                spec = importlib.util.spec_from_file_location(module_name, module_file)
                if spec is None or spec.loader is None:
                    logging.warning(
                        f"Cannot create module spec for service '{module_name}', skipping"
                    )
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check if module has Service class
                if not hasattr(module, "Service"):
                    logging.debug(
                        f"Service module '{module_name}' has no Service class, skipping"
                    )
                    continue

                service_instance = module.Service(wrapped_client)

                # Validate service instance has a name attribute
                if not hasattr(service_instance, "name"):
                    logging.warning(
                        f"Service in '{module_name}' has no name attribute, skipping"
                    )
                    continue

                # Validate service name is a valid Python identifier
                if (
                    not isinstance(service_instance.name, str)
                    or not service_instance.name
                ):
                    logging.warning(
                        f"Service in '{module_name}' has invalid name: {service_instance.name!r}"
                    )
                    continue

                if not service_instance.name.isidentifier():
                    logging.warning(
                        f"Service name '{service_instance.name}' is not a valid Python identifier"
                    )
                    continue

                setattr(self, service_instance.name, service_instance)
                logging.debug(f"Successfully loaded service: {service_instance.name}")

            except ImportError as e:
                # Module import failed - this is expected for optional dependencies
                logger = logging.get_logger()
                if logger.isEnabledFor(logging.logging.DEBUG):
                    logger.warning(
                        f"Failed to import service module '{module_name}': {e}",
                        exc_info=True,
                    )
                else:
                    logging.warning(
                        f"Failed to import service module '{module_name}': {e}"
                    )
                continue

            except AttributeError as e:
                # Service class instantiation or attribute access failed
                logger = logging.get_logger()
                if logger.isEnabledFor(logging.logging.DEBUG):
                    logger.warning(
                        f"Service '{module_name}' has attribute error: {e}",
                        exc_info=True,
                    )
                else:
                    logging.warning(f"Service '{module_name}' has attribute error: {e}")
                continue

            except Exception as e:
                # Unexpected error - log with full traceback and continue
                # We don't want a single bad service to crash the entire client
                logger = logging.get_logger()
                logger.error(
                    f"Unexpected error loading service '{module_name}': {e}",
                    exc_info=True,
                )
                continue

    async def _make_response(self, res: Response) -> response.Response:
        """Create a response object and return it.

        Wraps the ipsdk Response object in our custom Response class
        to provide consistent interface for handling API responses.

        Args:
            res (Response): The response object returned from the HTTP API request.

        Returns:
            response.Response: A wrapped HTTP Response object.

        Raises:
            None
        """
        return response.Response(res)

    async def send_request(
        self,
        method: str,
        path: str,
        params: dict = None,
        json: str | bytes | dict | list | None = None,
        timeout: int | None = None,
    ) -> response.Response:
        """Send an HTTP request to the server and return the response.

        Executes an HTTP request using the specified method and parameters,
        handling errors and wrapping the response in a standardized format.
        Includes timeout protection to prevent hung requests from blocking
        the server indefinitely.

        Args:
            method (str): The HTTP method to invoke. This should be one of
                "GET", "POST", "PUT", "DELETE".
            path (str): The full URL path to send the request to.
            params (dict | None): A Python dict object to be converted into a query
                string and appended to the URL. Defaults to None.
            json (str | bytes | dict | list | None): A Python object that can be serialized
                into a JSON object and sent as the request body. Defaults to None.
            timeout (int | None): Request timeout in seconds. If None, uses the
                configured platform timeout value. Defaults to None.

        Returns:
            response.Response: The HTTP response from the server wrapped in our
                custom Response class.

        Raises:
            exceptions.TimeoutExceededError: If the request exceeds the timeout.
            exceptions.ItentialMcpException: If there is an error communicating with
                the server or if the API returns an error response.
        """
        # Use provided timeout or fall back to configured default
        request_timeout = timeout if timeout is not None else self.timeout

        # Convert string method to HTTPMethod enum
        http_method = HTTPMethod[method.upper()]

        try:
            # Wrap the request in asyncio.wait_for to enforce timeout
            res = await asyncio.wait_for(
                self.client._send_request(http_method, path, params, json),
                timeout=request_timeout,
            )
        except asyncio.TimeoutError:
            raise exceptions.TimeoutExceededError(
                f"Request to {path} timed out after {request_timeout}s"
            )
        except Exception as exc:
            raise exceptions.ItentialMcpException(_format_error_message(exc))

        return await self._make_response(res)

    async def get(self, path: str, params: dict | None = None) -> response.Response:
        """Send an HTTP GET request to the server.

        Performs an HTTP GET request to the specified path with optional
        query parameters.

        Args:
            path (str): The full path to send the HTTP request to.
            params (dict | None): A Python dict object to be converted to a query
                string and appended to the path. Defaults to None.

        Returns:
            response.Response: An HTTP Response object from the server.

        Raises:
            exceptions.ItentialMcpException: If there is an error communicating with
                the server or if the API returns an error response.
        """
        return await self.send_request(method="GET", path=path, params=params)

    async def post(
        self,
        path: str,
        params: dict | None = None,
        json: str | dict | list | None = None,
    ) -> response.Response:
        """Send an HTTP POST request to the server.

        Performs an HTTP POST request to the specified path with optional
        query parameters and JSON body data.

        Args:
            path (str): The full path to send the HTTP request to.
            params (dict | None): A Python dict object to be converted to a query
                string and appended to the path. Defaults to None.
            json (str | dict | list | None): A Python object that can be serialized
                to a JSON string and sent as the body of the request. Defaults to None.

        Returns:
            response.Response: An HTTP Response object from the server.

        Raises:
            exceptions.ItentialMcpException: If there is an error communicating with
                the server or if the API returns an error response.
        """
        return await self.send_request(
            method="POST", path=path, params=params, json=json
        )

    async def put(
        self,
        path: str,
        params: dict | None = None,
        json: str | dict | list | None = None,
    ) -> response.Response:
        """Send a HTTP PUT request to the server.

        Args:
            path (str): The full path to send the HTTP request to.
            params (dict | None): A Python dict object to be converted to a query
                string and appended to the path. Defaults to None.
            json (str | dict | list | None): A Python object that can be serialized
                to a JSON string and sent as the body of the request. Defaults to None.

        Returns:
            response.Response: An HTTP Response object from the server.

        Raises:
            exceptions.ItentialMcpException: If the HTTP request fails.
        """
        return await self.send_request(
            method="PUT", path=path, params=params, json=json
        )

    async def delete(
        self,
        path: str,
        params: dict | None = None,
    ) -> response.Response:
        """Send a HTTP DELETE request to the server.

        Args:
            path (str): The full path to send the HTTP request to.
            params (dict | None): A Python dict object to be converted to a query
                string and appended to the path. Defaults to None.

        Returns:
            response.Response: An HTTP Response object from the server.

        Raises:
            exceptions.ItentialMcpException: If the HTTP request fails.
        """
        return await self.send_request(method="DELETE", path=path, params=params)
