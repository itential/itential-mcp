# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import shutil


def getcols() -> int:
    """
    Get the number of columns for the current terminal session

    This function will get the current terminal size and return the number of
    columns in the current terminal.

    Args:
        None

    Returns:
        int: The number of columns for the current terminal

    Raises:
        None
    """
    return shutil.get_terminal_size().columns
