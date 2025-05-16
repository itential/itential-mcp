# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest
import httpx

from itential_mcp.response import Response

@pytest.fixture
def mock_response():
    return httpx.Response(
        status_code=200,
        content=b'{"message": "ok"}',
        headers={"Content-Type": "application/json"},
        request=httpx.Request("GET", "https://example.com")
    )


def test_status_code(mock_response):
    res = Response(mock_response)
    assert res.status_code == 200


def test_reason_phrase(mock_response):
    res = Response(mock_response)
    assert res.reason == "OK"  # httpx maps 200 to OK


def test_text_content(mock_response):
    res = Response(mock_response)
    assert res.text == '{"message": "ok"}'


def test_json_parsing(mock_response):
    res = Response(mock_response)
    assert res.json() == {"message": "ok"}

