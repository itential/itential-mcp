# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pathlib
import importlib
import importlib.util

import ipsdk

from ipsdk.platform import AsyncPlatform
from ipsdk.connection import Response

from . import config
from . import response
from . import exceptions


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

    def _init_client(self) -> AsyncPlatform:
        """Initialize the client connection to Itential Platform.
        
        Creates an AsyncPlatform client using configuration settings
        from the platform configuration.
        
        Args:
            None
            
        Returns:
            AsyncPlatform: An instance of AsyncPlatform configured for async operations.
            
        Raises:
            Exception: If platform client initialization fails.
        """
        cfg = config.get()
        return ipsdk.platform_factory(want_async=True, **cfg.platform)

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
            f for f in services_path.iterdir()
            if f.is_file() and f.suffix == ".py" and not f.name.startswith("_")
        ]

        # Import and register services
        for module_file in python_files:
            module_name = module_file.stem
            try:
                spec = importlib.util.spec_from_file_location(module_name, module_file)
                if spec is None or spec.loader is None:
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check if module has Service class
                if not hasattr(module, "Service"):
                    continue

                service_instance = module.Service(self.client)
                setattr(self, service_instance.name, service_instance)

            except (ImportError, AttributeError, Exception) as exc:
                # Log error but continue loading other services
                # Consider adding proper logging here in the future
                print(exc)
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
        json: str | bytes | dict | list | None = None
    ) -> response.Response:
        """
        Send the request to the server and return the response

        Args:
            method (str): The HTTP method to invoke. This should be one of
                "GET", "POST", "PUT", "DELETE"

            path (str): The full URL path to send the reques to

            params (dict): A Python dict objec to be converted into a query
                string and appeneded to the URL

            json (str|bytes|dict|list): A Python object that can be serialized
                into a JSON object.

        Returns:
            Response: The HTTP response from the server

        Raises:
            None
        """
        try:
            res = await self.client._send_request(method, path, params, json)
        except Exception as exc:
            raise exceptions.ItentialMcpException(exc.response.text)
        return await self._make_response(res)

    async def get(
        self,
        path: str,
        params: dict | None = None
    ) -> response.Response:
        """
        Send a HTTP GET request to the server

        Args:
            path (str): The full path to send the HTTP request to

            params (dict): A Python dict object to be converted to a query
                string and appended to the path

        Returns:
            Response: An HTTP Response object from the server

        Raises:
            None
        """
        return await self.send_request(
            method="GET", path=path, params=params
        )

    async def post(
        self,
        path: str,
        params: dict | None = None,
        json: str | dict | list | None = None,
    ) -> response.Response:
        """
        Send a HTTP POST request to the server

        Args:
            path (str): The full path to send the HTTP request to

            params (dict): A Python dict object to be converted to a query
                string and appended to the path

            json (str | dict | list): A Python object that can be serialized
                to a JSON string and sent as the body of the request

        Returns:
            Response: An HTTP Response object from the server

        Raises:
            None
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
        return await self.send_request(
            method="DELETE", path=path, params=params
        )
