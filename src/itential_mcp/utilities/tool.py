# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import inspect
import pathlib
import importlib.util

from typing import Any, Callable, Iterator, Tuple, Sequence
from typing import get_type_hints

from pydantic import BaseModel

from ..cli import terminal


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


def get_json_schema(fn: Callable) -> str:
    """
    Extract JSON schema from a function's return type annotation.

    This function analyzes a function's type hints to extract the JSON schema
    from the return type. The return type must be a Pydantic BaseModel subclass
    for schema generation to work properly.

    Args:
        fn (Callable): The function to extract the JSON schema from

    Returns:
        str: The JSON schema as a string representation

    Raises:
        ValueError: If the function's return type is not a BaseModel subclass
    """
    hints = get_type_hints(fn)
    ret = hints.get("return", Any)

    # Check if ret is actually a class before using issubclass
    if not inspect.isclass(ret) or not issubclass(ret, BaseModel):
        raise ValueError("tool functions must subclass BaseModel")

    return ret.model_json_schema()


def itertools(path: str) -> Iterator[Tuple[Callable, Sequence]]:
    """
    Iterate through all discovered tools.

    This function implements dynamic tool discovery by scanning a directory
    for Python modules and extracting callable functions. It supports a
    hierarchical tagging system where tags can be defined at both the module
    level and function level.

    **Tool Discovery Process:**
    1. Scan directory for .py files (excluding __init__.py and _private.py)
    2. Dynamically import each module using importlib
    3. Extract module-level __tags__ if present
    4. Inspect module for public functions (not starting with _)
    5. Combine module tags with function-level tags
    6. Yield function and complete tag set

    **Tagging Hierarchy:**
    - Module-level tags (__tags__): Apply to all functions in the module
    - Function-level tags (@tags decorator): Additional tags for specific functions
    - Function name: Automatically added as a tag
    - All tags are accumulated into a set per function

    Args:
        path (str): The filesystem path to scan for tool modules.

    Yields:
        Tuple[Callable, Sequence]: Each iteration yields a tuple of:
            - Callable: The tool function ready for registration
            - Sequence: Set of tags associated with this tool

    Raises:
        None: Errors during module loading are silently ignored to allow
            partial tool loading if some modules fail.
    """
    # Step 1: Discover all Python module files in the tools directory
    # Filter out __init__.py and any files without .py extension
    module_files = [
        f[:-3] for f in os.listdir(path) if f.endswith(".py") and f != "__init__.py"
    ]

    # Step 2: Import each discovered module and extract tools
    for module_name in module_files:
        # Skip private modules (those starting with underscore)
        if not module_name.startswith("_"):
            # Dynamically import the module using importlib.util
            # This allows runtime discovery without hardcoded imports
            spec = importlib.util.spec_from_file_location(
                module_name, os.path.join(path, f"{module_name}.py")
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Step 3: Extract module-level tags that apply to all functions
            # Module-level tags are defined via __tags__ = ("tag1", "tag2")
            module_tags = set()
            if hasattr(module, "__tags__"):
                module_tags = set(module.__tags__)

            # Step 4: Inspect module for all function members
            for name, f in inspect.getmembers(module, inspect.isfunction):
                # Only process public functions defined in this module
                # Skip: private functions (_func), imported functions
                if not name.startswith("_") and f.__module__ == module_name:
                    # Step 5: Build complete tag set for this function
                    # IMPORTANT: Copy module_tags to prevent cross-function pollution
                    tags = module_tags.copy()

                    # Add function name as a tag (enables filtering by function name)
                    tags.add(name)

                    # Add any decorator-applied tags from @tags() decorator
                    if hasattr(f, "tags"):
                        for ele in f.tags:
                            tags.add(ele)

                    # Step 6: Yield the function and its complete tag set
                    # The caller (server initialization) will register this as an MCP tool
                    yield f, tags


async def display_tools():
    """
    Print the list of available tools to stdout

    This function will display the list of all available tools to
    stdout including the tool description.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    tools = {}
    maxlen = 0

    path = pathlib.Path(__file__).parent.parent / "tools"

    for f, _ in itertools(path):
        if len(f.__name__) > maxlen:
            maxlen = len(f.__name__)
        tools[f.__name__] = f.__doc__

    maxlen += 3

    width = terminal.getcols()

    print(f"{'TOOLS':{maxlen}}DESCRIPTION")

    for key, value in dict(sorted(tools.items())).items():
        doc = value.splitlines()[1].strip()
        if maxlen + len(doc) > width:
            doclen = width - maxlen - 4
            doc = doc[:doclen]
            doc = f"{doc}..."
        print(f"{key:<{maxlen}}{doc}")
    print()


async def display_tags():
    """
    Print the last of available tags to stdout.

    This function will display the list of all availalbe tags to
    stdout

    Args:
        None

    Returns:
        None

    Raises:
        None

    """
    print("TAGS")

    tags = set()

    path = pathlib.Path(__file__).parent.parent / "tools"

    for _, t in itertools(path):
        tags = tags.union(t)

    for ele in sorted(list(tags)):
        print(ele)
    print()
