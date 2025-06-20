# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Callable


def tags(*tag_list) -> Callable:
    """
    Decorator that will add tags to a function

    This decorator when called will add one or more tags to a function.  The
    tags are used to control which tools are exposed when the server is
    started.

    To use this decoator, import the function into the tools module and
    decorate the target tool as shown below.

    ```
    from itential_mcp.toolutils import tags

    @tags("public", "system")
    def get_server_info(ctx: Context) -> dict:
        return {}
    ```

    Args:
        *tag_list: The list of tags to be attached to the function

    Returns:
        Callable: A callable decorated function

    Raises:
        None
    """
    def decorator(func):
        setattr(func, "tags", list(tag_list))
        return func
    return decorator
