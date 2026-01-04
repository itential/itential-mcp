# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import pathlib
import importlib
import importlib.util

import ipsdk

from ipsdk.platform import AsyncPlatform
from ipsdk.connection import Response

from .. import config
from ..config.converters import platform_to_dict
from . import response
from ..core import exceptions
from ..core import logging


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

                service_instance = module.Service(self.client)

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

        try:
            # Wrap the request in asyncio.wait_for to enforce timeout
            res = await asyncio.wait_for(
                self.client._send_request(method, path, params, json),
                timeout=request_timeout,
            )
        except asyncio.TimeoutError:
            raise exceptions.TimeoutExceededError(
                f"Request to {path} timed out after {request_timeout}s"
            )
        except Exception as exc:
            raise exceptions.ItentialMcpException(str(exc))

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
