# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from datetime import datetime, timezone


def epoch_to_timestamp(ms: int) -> str:
    """
    Converts a timestamp in milliseconds to a string

    This function accepts a single argument `ms` and will convert the value
    to a string that represents the date and time in zulu ISO 8601 format.

    Args:
        ms (int): The time stamp to convert to a string

    Returns:
        str: The converted timestamp a a string

    Raises:
        None
    """
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
