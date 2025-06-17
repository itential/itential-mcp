# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from datetime import datetime, timezone

from itential_mcp.timeutils import epoch_to_timestamp


def test_epoch_to_timestamp_basic():
    dt = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    ms = int(dt.timestamp() * 1000)
    assert epoch_to_timestamp(ms) == "2023-01-01T00:00:00Z"


def test_epoch_to_timestamp_leap_year():
    dt = datetime(2020, 2, 29, 12, 30, 45, tzinfo=timezone.utc)
    ms = int(dt.timestamp() * 1000)
    assert epoch_to_timestamp(ms) == "2020-02-29T12:30:45Z"


def test_epoch_to_timestamp_epoch_start():
    assert epoch_to_timestamp(0) == "1970-01-01T00:00:00Z"


def test_epoch_to_timestamp_recent():
    now = datetime.now(tz=timezone.utc)
    ms = int(now.timestamp() * 1000)
    expected = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert epoch_to_timestamp(ms) == expected

