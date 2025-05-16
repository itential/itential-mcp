# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Any

import httpx


class Response(object):

    def __init__(self, res: httpx.Response):
        """
        Initialize a new response instance

        Args:
            res: An instance of httpx.Response
        """
        self.response = res

    @property
    def status_code(self) -> int:
        """
        Returns the HTTP status code
        """
        return self.response.status_code

    @property
    def reason(self) -> str:
        """
        Returns the HTTP status code message
        """
        return self.response.reason_phrase

    @property
    def text(self) -> str:
        """
        Return the response body as text
        """
        return self.response.text

    def json(self) -> Any:
        """
        Attempt to return the response body as a Python object

        Args:
            None

        Returns:
            Any: Returns the response text as a object

        Raises:
            None
        """
        return self.response.json()
