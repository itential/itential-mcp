# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from importlib.metadata import version

from .cli import run

__version__ = version("itential_mcp")

__all__ = ("run",)
