# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import ipsdk

from ipsdk.platform import AsyncPlatform

import httpx

from . import config
from . import response


class PlatformClient(object):

    def __init__(self):
        self.client = self._init_client()

    def _init_client(self) -> AsyncPlatform:
        """
        Initializes the client connection to Itential Platform

        Args:
            None

        Returns:
            AsyncPlatform: An instance of AsyncPlatform

        Raises:
            None
        """
        cfg = config.get()
        return ipsdk.platform_factory(want_async=True, **cfg.platform)

    async def _make_response(self, res: httpx.Response) -> response.Response:
        """
        Creates a response object and returns it

        Args:
            res (httpx.Response): The response object returned from the HTTP API
                request

        Returns:
            Response: A HTTP Response object

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
        res = await self.client._send_request(method, path, params, json)
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
        """
        Send a HTTP PUT request to the server
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
            method="PUT", path=path, params=params, json=json
        )

    async def delete(
        self,
        path: str,
        params: dict | None = None,
    ) -> response.Response:
        """
        Send a HTTP DELETE request to the server
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
            method="DELETE", path=path, params=params
        )
