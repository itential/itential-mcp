# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from importlib.metadata import version

name = "itential-mcp"
author = "Itential"
version = version(name)


async def display_version() -> None:
    """
    Prints the current app verion to stdout

    This function will print the current application version to stdout.

    Args:
        None:

    Returns:
        None

    Raises:
        None
    """
    print(f"{name} {version}\n")
