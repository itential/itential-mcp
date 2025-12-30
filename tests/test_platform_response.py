# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import httpx

from itential_mcp.platform.response import Response


@pytest.fixture
def mock_response():
    return httpx.Response(
        status_code=200,
        content=b'{"message": "ok"}',
        headers={"Content-Type": "application/json"},
        request=httpx.Request("GET", "https://example.com"),
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


def test_status_code_404():
    """Test Response with 404 status code"""
    response = httpx.Response(
        status_code=404,
        content=b'{"error": "Not Found"}',
        headers={"Content-Type": "application/json"},
        request=httpx.Request("GET", "https://example.com"),
    )
    res = Response(response)
    assert res.status_code == 404
    assert res.reason == "Not Found"


def test_status_code_500():
    """Test Response with 500 status code"""
    response = httpx.Response(
        status_code=500,
        content=b'{"error": "Internal Server Error"}',
        headers={"Content-Type": "application/json"},
        request=httpx.Request("GET", "https://example.com"),
    )
    res = Response(response)
    assert res.status_code == 500
    assert res.reason == "Internal Server Error"


def test_status_code_201():
    """Test Response with 201 created status code"""
    response = httpx.Response(
        status_code=201,
        content=b'{"id": "123", "created": true}',
        headers={"Content-Type": "application/json"},
        request=httpx.Request("POST", "https://example.com"),
    )
    res = Response(response)
    assert res.status_code == 201
    assert res.reason == "Created"
    assert res.json() == {"id": "123", "created": True}


def test_empty_response_body():
    """Test Response with empty body"""
    response = httpx.Response(
        status_code=204,
        content=b"",
        headers={},
        request=httpx.Request("DELETE", "https://example.com"),
    )
    res = Response(response)
    assert res.status_code == 204
    assert res.text == ""


def test_invalid_json_raises_exception():
    """Test that invalid JSON raises appropriate exception"""
    response = httpx.Response(
        status_code=200,
        content=b"not valid json{{{",
        headers={"Content-Type": "application/json"},
        request=httpx.Request("GET", "https://example.com"),
    )
    res = Response(response)

    # httpx.Response.json() raises JSONDecodeError
    with pytest.raises(Exception):  # Could be JSONDecodeError or similar
        res.json()


def test_text_with_different_encoding():
    """Test Response with non-UTF8 content"""
    response = httpx.Response(
        status_code=200,
        content="测试内容".encode("utf-8"),
        headers={"Content-Type": "text/plain; charset=utf-8"},
        request=httpx.Request("GET", "https://example.com"),
    )
    res = Response(response)
    assert res.text == "测试内容"


def test_json_with_list():
    """Test Response with JSON list instead of dict"""
    response = httpx.Response(
        status_code=200,
        content=b'[{"id": 1}, {"id": 2}]',
        headers={"Content-Type": "application/json"},
        request=httpx.Request("GET", "https://example.com"),
    )
    res = Response(response)
    assert res.json() == [{"id": 1}, {"id": 2}]


def test_json_with_null():
    """Test Response with JSON null value"""
    response = httpx.Response(
        status_code=200,
        content=b"null",
        headers={"Content-Type": "application/json"},
        request=httpx.Request("GET", "https://example.com"),
    )
    res = Response(response)
    assert res.json() is None


def test_json_with_boolean():
    """Test Response with JSON boolean values"""
    response = httpx.Response(
        status_code=200,
        content=b"true",
        headers={"Content-Type": "application/json"},
        request=httpx.Request("GET", "https://example.com"),
    )
    res = Response(response)
    assert res.json() is True


def test_json_with_number():
    """Test Response with JSON number"""
    response = httpx.Response(
        status_code=200,
        content=b"42",
        headers={"Content-Type": "application/json"},
        request=httpx.Request("GET", "https://example.com"),
    )
    res = Response(response)
    assert res.json() == 42


def test_large_response_body():
    """Test Response with large body content"""
    large_content = {"data": "x" * 10000}
    import json as json_lib

    response = httpx.Response(
        status_code=200,
        content=json_lib.dumps(large_content).encode(),
        headers={"Content-Type": "application/json"},
        request=httpx.Request("GET", "https://example.com"),
    )
    res = Response(response)
    assert res.json() == large_content


def test_response_with_custom_headers():
    """Test Response preserves custom headers"""
    response = httpx.Response(
        status_code=200,
        content=b'{"message": "ok"}',
        headers={
            "Content-Type": "application/json",
            "X-Custom-Header": "custom-value",
            "X-Request-Id": "12345",
        },
        request=httpx.Request("GET", "https://example.com"),
    )
    res = Response(response)
    # Verify we can still access the underlying response
    assert res.response.headers.get("X-Custom-Header") == "custom-value"
    assert res.response.headers.get("X-Request-Id") == "12345"


def test_response_wrapper_preserves_original():
    """Test that Response wrapper preserves original response object"""
    original_response = httpx.Response(
        status_code=200,
        content=b'{"message": "ok"}',
        headers={"Content-Type": "application/json"},
        request=httpx.Request("GET", "https://example.com"),
    )
    res = Response(original_response)

    # Verify the original response is accessible
    assert res.response is original_response
    assert isinstance(res.response, httpx.Response)


def test_multiple_calls_to_json():
    """Test that json() can be called multiple times"""
    response = httpx.Response(
        status_code=200,
        content=b'{"count": 5}',
        headers={"Content-Type": "application/json"},
        request=httpx.Request("GET", "https://example.com"),
    )
    res = Response(response)

    # Call json() multiple times
    result1 = res.json()
    result2 = res.json()

    assert result1 == result2 == {"count": 5}


def test_multiple_calls_to_text():
    """Test that text property can be accessed multiple times"""
    response = httpx.Response(
        status_code=200,
        content=b"test content",
        headers={"Content-Type": "text/plain"},
        request=httpx.Request("GET", "https://example.com"),
    )
    res = Response(response)

    # Access text multiple times
    text1 = res.text
    text2 = res.text

    assert text1 == text2 == "test content"


def test_response_with_redirects():
    """Test Response with redirect status codes"""
    response = httpx.Response(
        status_code=302,
        content=b"",
        headers={"Location": "https://example.com/new-location"},
        request=httpx.Request("GET", "https://example.com"),
    )
    res = Response(response)
    assert res.status_code == 302
    assert res.reason == "Found"
