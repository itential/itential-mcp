# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Any

import httpx


class Response(object):
    """Wrapper class for HTTP response objects.
    
    Provides a standardized interface for handling HTTP responses from
    the Itential Platform API by wrapping httpx.Response objects.
    """

    def __init__(self, res: httpx.Response):
        """Initialize a new response instance.
        
        Args:
            res (httpx.Response): An instance of httpx.Response from the HTTP request.
            
        Returns:
            None
            
        Raises:
            None
        """
        self.response = res

    @property
    def status_code(self) -> int:
        """Get the HTTP status code from the response.
        
        Returns:
            int: The HTTP status code (e.g., 200, 404, 500).
        """
        return self.response.status_code

    @property
    def reason(self) -> str:
        """Get the HTTP status code reason phrase.
        
        Returns:
            str: The HTTP status code message (e.g., "OK", "Not Found").
        """
        return self.response.reason_phrase

    @property
    def text(self) -> str:
        """Get the response body as text.
        
        Returns:
            str: The response body as a text string.
        """
        return self.response.text

    def json(self) -> Any:
        """Parse the response body as JSON and return as Python object.
        
        Attempts to parse the response body as JSON and return the
        resulting Python object (dict, list, etc.).
        
        Args:
            None
            
        Returns:
            Any: The response body parsed as a Python object.
            
        Raises:
            ValueError: If the response body cannot be parsed as valid JSON.
            TypeError: If the response content type is not JSON-compatible.
        """
        return self.response.json()
