# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Terminal utilities for CLI output formatting."""

import shutil


class Colors:
    """ANSI color codes for terminal output."""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def getcols() -> int:
    """Get the number of columns for the current terminal session.

    This function will get the current terminal size and return the number of
    columns in the current terminal.

    Returns:
        int: The number of columns for the current terminal.
    """
    return shutil.get_terminal_size().columns


def print_success(message: str) -> None:
    """Print success message in green.

    Args:
        message: The message to print.
    """
    print(f"{Colors.GREEN}{message}{Colors.RESET}")


def print_error(message: str) -> None:
    """Print error message in red.

    Args:
        message: The message to print.
    """
    print(f"{Colors.RED}{message}{Colors.RESET}")


def print_warning(message: str) -> None:
    """Print warning message in yellow.

    Args:
        message: The message to print.
    """
    print(f"{Colors.YELLOW}{message}{Colors.RESET}")


def print_info(message: str) -> None:
    """Print info message in blue.

    Args:
        message: The message to print.
    """
    print(f"{Colors.BLUE}{message}{Colors.RESET}")
