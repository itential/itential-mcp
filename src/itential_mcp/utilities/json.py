# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import traceback

from typing import Union

from ..core import exceptions
from ..core import logging


def loads(s: str) -> Union[dict, list]:
    """Convert a JSON formatted string to a dict or list object

    Args:
        s (str): The JSON object represented as a string

    Returns:
        A dict or list object
    """
    try:
        return json.loads(s)
    except json.JSONDecodeError as exc:
        logging.error(traceback.format_exc())
        input_data = str(s)[:200] if s is not None else "None"
        msg = f"Failed to parse JSON: {exc!s}"
        raise exceptions.ValidationException(
            msg,
            details={"input_data": input_data, "json_error": str(exc)},
        )
    except Exception as exc:
        logging.error(traceback.format_exc())
        input_data = str(s)[:200] if s is not None else "None"
        msg = f"Unexpected error parsing JSON: {exc!s}"
        raise exceptions.ValidationException(
            msg,
            details={"input_data": input_data, "original_error": str(exc)},
        )


def dumps(o: Union[dict, list]) -> str:
    """Convert a dict or list to a JSON string

    Args:
        o (list, dict): The list or dict object to dump to a string

    Returns:
        A JSON string representation
    """
    try:
        return json.dumps(o)
    except (TypeError, ValueError) as exc:
        logging.error(traceback.format_exc())
        msg = f"Failed to serialize object to JSON: {exc!s}"
        raise exceptions.ValidationException(
            msg,
            details={"object_type": str(type(o)), "json_error": str(exc)},
        )
    except Exception as exc:
        logging.error(traceback.format_exc())
        msg = f"Unexpected error serializing JSON: {exc!s}"
        raise exceptions.ValidationException(
            msg,
            details={"object_type": str(type(o)), "original_error": str(exc)},
        )
