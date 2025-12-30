# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Itential MCP TOON serializers module.

This module contains serialization functions for converting Python objects
to TOON (Token-Oriented Object Notation) format, optimized for LLM consumption
with 30-60% token reduction compared to JSON.

Available Functions:
    serialize_toon: Serialize a Python object to TOON format.
    serialize_toon_list: Serialize a list of Python objects to TOON format.

Example:
    ```python
    from itential_mcp.serializers import serialize_toon

    device = {"name": "router-01", "host": "192.168.1.1"}
    toon_output = serialize_toon(device)
    ```
"""

from typing import Any

from toon_python import encode


def serialize_toon(
    data: Any,
    **kwargs: Any,
) -> str:
    """Serialize a Python object to TOON format.

    TOON (Token-Oriented Object Notation) is an LLM-optimized serialization
    format that uses significantly fewer tokens than JSON while maintaining
    readability and structure. This function converts any Python object
    (dict, list, primitive types) to a compact TOON representation.

    TOON Format Features:
        - Eliminates unnecessary braces and quotation marks
        - Uses colons for key-value separation
        - Implements indentation-based structure clarity
        - Applies square brackets to denote array lengths
        - Automatic tabular format for uniform arrays

    Args:
        data: The Python object to serialize (dict, list, str, int, etc.).
        **kwargs: Additional keyword arguments passed to the TOON encoder.
            Supported options include:
            - delimiter: String to use for key-value separation (default: ":")
            - indent: Number of spaces for indentation (default: 2)
            - fold_keys: Whether to use compact header notation for arrays

    Returns:
        A string containing the object serialized in TOON format. The output
        format depends on the input type:
        - Dicts use key:value pairs
        - Lists use tabular format with headers (if uniform)
        - Primitives are converted to strings

    Raises:
        Exception: If the TOON library encounters an error during
            serialization. This may occur with unsupported data types.

    Example:
        ```python
        device = {
            "name": "router-01",
            "host": "192.168.1.1",
            "deviceType": "cisco_ios",
            "status": "active"
        }

        # Basic serialization
        toon_str = serialize_toon(device)
        ```

    Note:
        The resulting TOON format is optimized for LLM consumption,
        reducing token usage by approximately 30-60% compared to
        equivalent JSON representations.
    """
    return encode(data, **kwargs)


def serialize_toon_list(
    data: list[Any],
    **kwargs: Any,
) -> str:
    """Serialize a list of Python objects to TOON format.

    This function efficiently serializes multiple objects into a single
    TOON representation. When serializing lists, TOON automatically uses a compact
    tabular format with headers, significantly reducing token usage for array data.

    Args:
        data: A list of Python objects to serialize (typically dicts).
            All objects should have compatible structures for optimal formatting.
        **kwargs: Additional keyword arguments passed to the TOON encoder.

    Returns:
        A string containing the list serialized in TOON tabular format.
        The format uses headers and rows for efficient representation:
        ```
        [2]{id,name,email}:
        1,Alice,alice@example.com
        2,Bob,bob@example.com
        ```

    Raises:
        Exception: If the TOON library encounters an error during
            serialization.

    Example:
        ```python
        devices = [
            {"name": "router-01", "host": "192.168.1.1"},
            {"name": "router-02", "host": "192.168.1.2"},
        ]

        toon_str = serialize_toon_list(devices)
        # Output uses compact tabular format with headers
        ```

    Note:
        This function is particularly efficient for serializing multiple
        objects, as the TOON format uses a single header row followed
        by data rows, avoiding repetition of field names.
    """
    return encode(data, **kwargs)
