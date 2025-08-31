# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import inspect
import importlib.util

from typing import Any, Callable, Iterator, Tuple, Sequence
from typing import get_type_hints

from pydantic import BaseModel

from . import terminal


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

    if not issubclass(ret, BaseModel):
        raise ValueError("tool functions must subclass BaseModel")

    return ret.model_json_schema()


def itertools(path: str=None) -> Iterator[Tuple[Callable, Sequence]]:
    """
    Iterate through all discovered tools

    This function will recursively load all modules found in the `tools`
    folder as long as they module name does not start with underscore (_).  It
    will then inspect the module to find all public functions and attach
    them to the instance of mcp as a tool.

    Args:
        path (str): The path to look for tools in.  If the argument is null
            the standard `tools` folder is searched.

    Returns:
        tuple: The list of functions and associated tags

    Raises:
        None
    """
    path = path or os.path.join(os.path.dirname(os.path.realpath(__file__)), "tools")

    # Get a list of all files in the directory
    module_files = [f[:-3] for f in os.listdir(path) if f.endswith(".py") and f != "__init__.py"]

    # Import the modules, add them to globals and mcp
    for module_name in module_files:
        if not module_name.startswith("_"):
            spec = importlib.util.spec_from_file_location(module_name, os.path.join(path, f"{module_name}.py"))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # create a new tags set for the module and add any tags
            # that have been configured using the `__tags__` variable
            tags = set()
            if hasattr(module, "__tags__"):
                tags = tags.union(module.__tags__)

            # Inspect the module to retreive all of the functions.
            for name, f in inspect.getmembers(module, inspect.isfunction):
                if not name.startswith("_") and f.__module__ == module_name:
                    # add the function name to the set of tags
                    tags.add(name)

                    # add any custom tags that have been attached to the
                    # function using the tags decorator
                    if hasattr(f, "tags"):
                        for ele in f.tags:
                            tags.add(ele)

                    # add the function as a new mcp tool along with the set of
                    # tags associated with the function.
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

    for f, _ in itertools():
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
    for _, t in itertools():
        tags = tags.union(t)

    for ele in sorted(list(tags)):
        print(ele)
    print()
