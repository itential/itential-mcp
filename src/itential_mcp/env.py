# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os

from typing import Callable, Any

from functools import partial

from . import stringutils


def get(f: Callable, key: str, default: Any | None=None) -> Any:
    """
    Get the value for key from the current environment

    Args:
        f (Callable): The function to transform the value
        key (str): The key to looking in the environment
        default (Any): The default value to use if the key doesn't exist

    Returns:
        Any: The transformed value from the environment or the default vaule
            if the key doesn't exist

    Raises:
        None
    """
    return f(os.getenv(key, default=default))


getstr = partial(get, stringutils.tostr)
getstr.__doc__ = "Get a string value from the environment"

getint = partial(get, stringutils.toint)
getint.__doc__ = "Get a integer value from the envirnment"

getbool = partial(get, stringutils.tobool)
getbool.__doc__ = "Get a boolean value from the environment"
