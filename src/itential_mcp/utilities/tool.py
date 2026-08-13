# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
import inspect
import pathlib
import importlib.util
import types

from typing import Any, Callable, Iterator, Sequence, Union
from typing import get_type_hints, get_origin, get_args

from pydantic import BaseModel, TypeAdapter

from mcp.types import ToolAnnotations

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


def annotate(
    *,
    read_only: bool | None = None,
    destructive: bool | None = None,
    idempotent: bool | None = None,
    open_world: bool | None = None,
    title: str | None = None,
) -> Callable:
    """
    Decorator that attaches MCP tool annotation hints to a function

    This decorator when called will attach a `mcp.types.ToolAnnotations`
    instance to a function as its `annotations` attribute. The annotations
    are advisory hints (`readOnlyHint`, `destructiveHint`, `idempotentHint`,
    `openWorldHint`, `title`) describing the tool's behavior to MCP clients,
    which is separate from and unrelated to the tags system.

    To use this decorator, import the function into the tools module and
    decorate the target tool as shown below.

    ```
    from itential_mcp.utilities.tool import annotate

    @annotate(read_only=True, idempotent=True, title="Get Health")
    async def get_health(ctx: Context) -> HealthResponse:
        ...
    ```

    Args:
        read_only (bool | None): Whether the tool only reads state and never
            modifies it. Defaults to None (unspecified).
        destructive (bool | None): Whether the tool may perform destructive
            updates (only meaningful when `read_only` is not True). Defaults
            to None (unspecified).
        idempotent (bool | None): Whether calling the tool repeatedly with
            the same arguments has no additional effect. Defaults to None
            (unspecified).
        open_world (bool | None): Whether the tool interacts with an "open
            world" of external entities (e.g. live network devices).
            Defaults to None (unspecified).
        title (str | None): A human-readable title for the tool. Defaults to
            None (unspecified).

    Returns:
        Callable: A callable decorated function

    Raises:
        None
    """

    def decorator(func):
        setattr(
            func,
            "annotations",
            ToolAnnotations(
                readOnlyHint=read_only,
                destructiveHint=destructive,
                idempotentHint=idempotent,
                openWorldHint=open_world,
                title=title,
            ),
        )
        return func

    return decorator


def get_json_schema(fn: Callable) -> dict[str, Any]:
    """
    Extract JSON schema from a function's return type annotation.

    This function analyzes a function's type hints to extract the JSON schema
    from the return type. The return type must either be a Pydantic BaseModel
    subclass, or a Union (`X | Y` / `typing.Union[X, Y]`) whose members are all
    Pydantic BaseModel subclasses, for schema generation to work properly.

    Args:
        fn (Callable): The function to extract the JSON schema from

    Returns:
        dict[str, Any]: The JSON schema as a dictionary

    Raises:
        ValueError: If the function's return type is not a BaseModel subclass
            and not a Union of BaseModel subclasses
    """
    hints = get_type_hints(fn)
    ret = hints.get("return", Any)

    origin = get_origin(ret)

    # Handle a Union (`X | Y` or `typing.Union[X, Y]`) of BaseModel subclasses
    if origin is types.UnionType or origin is Union:
        members = get_args(ret)
        if not members or not all(
            inspect.isclass(member) and issubclass(member, BaseModel)
            for member in members
        ):
            raise ValueError(
                "tool functions must subclass BaseModel or return a union of "
                "BaseModel subclasses"
            )

        return TypeAdapter(ret).json_schema()

    # Check if ret is actually a class before using issubclass
    if not inspect.isclass(ret) or not issubclass(ret, BaseModel):
        raise ValueError("tool functions must subclass BaseModel")

    return ret.model_json_schema()


def itertools(
    path: str,
) -> Iterator[tuple[Callable, Sequence, ToolAnnotations | None]]:
    """
    Iterate through all discovered tools.

    This function implements dynamic tool discovery by scanning a directory
    for Python modules and extracting callable functions. It supports a
    hierarchical tagging system where tags can be defined at both the module
    level and function level, and reads back any `ToolAnnotations` attached
    via the `@annotate(...)` decorator.

    **Tool Discovery Process:**
    1. Scan directory for .py files (excluding __init__.py and _private.py)
    2. Dynamically import each module using importlib
    3. Extract module-level __tags__ if present
    4. Inspect module for public functions (not starting with _)
    5. Combine module tags with function-level tags
    6. Read back any function-level ToolAnnotations
    7. Yield function, complete tag set, and annotations

    **Tagging Hierarchy:**
    - Module-level tags (__tags__): Apply to all functions in the module
    - Function-level tags (@tags decorator): Additional tags for specific functions
    - Function name: Automatically added as a tag
    - All tags are accumulated into a set per function

    **Ordering:**
    Module files and function members are both discovered in a stable,
    name-sorted order so that `tools/list` registration order is
    deterministic across runs and platforms.

    Args:
        path (str): The filesystem path to scan for tool modules.

    Yields:
        tuple[Callable, Sequence, ToolAnnotations | None]: Each iteration
            yields a tuple of:
            - Callable: The tool function ready for registration
            - Sequence: Set of tags associated with this tool
            - ToolAnnotations | None: The tool's annotation hints, if any
                were attached via the `@annotate(...)` decorator

    Raises:
        None: Errors during module loading are silently ignored to allow
            partial tool loading if some modules fail.
    """
    # Step 1: Discover all Python module files in the tools directory
    # Filter out __init__.py and any files without .py extension. Sort the
    # result so module import (and therefore tool registration) order is
    # deterministic across runs/platforms rather than depending on
    # os.listdir()'s unspecified ordering.
    module_files = sorted(
        f[:-3] for f in os.listdir(path) if f.endswith(".py") and f != "__init__.py"
    )

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

            # Step 4: Inspect module for all function members. inspect.getmembers
            # already returns members sorted by name, so combined with the
            # sorted module_files above this makes discovery fully
            # deterministic.
            for name, f in inspect.getmembers(module, inspect.isfunction):
                # Only process public functions defined in this module
                # Skip: private functions (_func), imported functions
                if not name.startswith("_") and (
                    f.__module__ == module_name
                    or f.__module__.endswith(f".{module_name}")
                ):
                    # Step 5: Build complete tag set for this function
                    # IMPORTANT: Copy module_tags to prevent cross-function pollution
                    tags = module_tags.copy()

                    # Add function name as a tag (enables filtering by function name)
                    tags.add(name)

                    # Add any decorator-applied tags from @tags() decorator
                    if hasattr(f, "tags"):
                        for ele in f.tags:
                            tags.add(ele)

                    # Step 6: Read back any ToolAnnotations attached via the
                    # @annotate(...) decorator
                    annotations = getattr(f, "annotations", None)

                    # Step 7: Yield the function, its complete tag set, and
                    # its annotations. The caller (server initialization)
                    # will register this as an MCP tool.
                    yield f, tags, annotations


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

    for f, _, _annotations in itertools(path):
        if len(f.__name__) > maxlen:
            maxlen = len(f.__name__)
        tools[f.__name__] = inspect.getdoc(f)

    maxlen += 3

    width = terminal.getcols()

    print(f"{'TOOLS':{maxlen}}DESCRIPTION")

    for key, value in dict(sorted(tools.items())).items():
        doc = ""
        if value:
            for line in value.splitlines():
                stripped = line.strip()
                if stripped:
                    doc = stripped
                    break
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

    for _, t, _annotations in itertools(path):
        tags = tags.union(t)

    for ele in sorted(list(tags)):
        print(ele)
    print()
