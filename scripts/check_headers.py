#!/usr/bin/env python3
# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Check and optionally fix copyright headers in Python source files.

This script scans all Python files in the repository (src/ and tests/ directories)
to ensure they have the required copyright and license header.

Usage:
    python scripts/check_headers.py              # Check headers
    python scripts/check_headers.py --fix        # Fix missing/incorrect headers
    python scripts/check_headers.py --verbose    # Show detailed output
"""

import argparse
import sys
from pathlib import Path
from typing import NamedTuple


class HeaderCheck(NamedTuple):
    """Result of checking a file's header."""

    file_path: Path
    has_copyright: bool
    has_license: bool
    has_spdx: bool
    line_numbers: tuple[int | None, int | None, int | None]  # (copyright_line, license_line, spdx_line)


REQUIRED_COPYRIGHT = "# Copyright (c) 2025 Itential, Inc"
REQUIRED_LICENSE = "# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)"
REQUIRED_SPDX = "# SPDX-License-Identifier: GPL-3.0-or-later"

HEADER_LINES = [
    REQUIRED_COPYRIGHT,
    REQUIRED_LICENSE,
    REQUIRED_SPDX,
]


def _find_python_files(base_dir: Path) -> list[Path]:
    """Find all Python files in src/ and tests/ directories.

    Args:
        base_dir: Base directory of the repository

    Returns:
        List of Path objects for all .py files found
    """
    python_files = []

    for directory in ["src", "tests"]:
        dir_path = base_dir / directory
        if dir_path.exists():
            python_files.extend(dir_path.rglob("*.py"))

    return sorted(python_files)


def _check_file_header(file_path: Path) -> HeaderCheck:
    """Check if a file has the required copyright header.

    Args:
        file_path: Path to the Python file to check

    Returns:
        HeaderCheck object with the results
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return HeaderCheck(file_path, False, False, False, (None, None, None))

    # Check first 5 lines for copyright, license, and SPDX
    copyright_line = None
    license_line = None
    spdx_line = None

    for i, line in enumerate(lines[:5], start=1):
        if REQUIRED_COPYRIGHT in line:
            copyright_line = i
        if REQUIRED_LICENSE in line:
            license_line = i
        if REQUIRED_SPDX in line:
            spdx_line = i

    has_copyright = copyright_line is not None
    has_license = license_line is not None
    has_spdx = spdx_line is not None

    return HeaderCheck(file_path, has_copyright, has_license, has_spdx, (copyright_line, license_line, spdx_line))


def _fix_file_header(file_path: Path) -> bool:
    """Add or fix the copyright header in a file.

    Args:
        file_path: Path to the Python file to fix

    Returns:
        True if the file was modified, False otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines(keepends=True)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

    # Find what exists and where
    copyright_line_idx = None
    license_line_idx = None
    spdx_line_idx = None

    for i, line in enumerate(lines[:10]):
        if REQUIRED_COPYRIGHT in line:
            copyright_line_idx = i
        if REQUIRED_LICENSE in line:
            license_line_idx = i
        if REQUIRED_SPDX in line:
            spdx_line_idx = i

    has_copyright = copyright_line_idx is not None
    has_license = license_line_idx is not None
    has_spdx = spdx_line_idx is not None

    if has_copyright and has_license and has_spdx:
        return False  # Header already correct

    modified = False

    # If completely missing header, add all three lines
    if not has_copyright and not has_license and not has_spdx:
        insert_index = 0
        if lines and lines[0].startswith("#!"):
            insert_index = 1

        header = [
            REQUIRED_COPYRIGHT + "\n",
            REQUIRED_LICENSE + "\n",
            REQUIRED_SPDX + "\n",
            "\n",
        ]
        lines[insert_index:insert_index] = header
        modified = True
    else:
        # Header exists but is incomplete - add what's missing
        # Add SPDX after license line if missing
        if has_license and not has_spdx:
            insert_idx = license_line_idx + 1
            lines.insert(insert_idx, REQUIRED_SPDX + "\n")
            modified = True

    if not modified:
        return False

    # Write back to file
    try:
        file_path.write_text("".join(lines), encoding="utf-8")
        return True
    except Exception as e:
        print(f"Error writing {file_path}: {e}")
        return False


def _check_headers(base_dir: Path, verbose: bool = False) -> tuple[list[HeaderCheck], list[HeaderCheck]]:
    """Check all Python files for required headers.

    Args:
        base_dir: Base directory of the repository
        verbose: Whether to show detailed output

    Returns:
        Tuple of (files_with_issues, files_ok)
    """
    python_files = _find_python_files(base_dir)

    if verbose:
        print(f"Found {len(python_files)} Python files to check\n")

    files_with_issues = []
    files_ok = []

    for file_path in python_files:
        result = _check_file_header(file_path)

        if result.has_copyright and result.has_license and result.has_spdx:
            files_ok.append(result)
            if verbose:
                print(f"✓ {file_path.relative_to(base_dir)}")
        else:
            files_with_issues.append(result)
            if verbose:
                rel_path = file_path.relative_to(base_dir)
                missing = []
                if not result.has_copyright:
                    missing.append("copyright")
                if not result.has_license:
                    missing.append("license")
                if not result.has_spdx:
                    missing.append("SPDX")
                print(f"✗ {rel_path} - missing: {', '.join(missing)}")

    return files_with_issues, files_ok


def _fix_headers(base_dir: Path, verbose: bool = False) -> tuple[int, int]:
    """Fix headers in all Python files that are missing them.

    Args:
        base_dir: Base directory of the repository
        verbose: Whether to show detailed output

    Returns:
        Tuple of (files_fixed, files_failed)
    """
    python_files = _find_python_files(base_dir)

    files_fixed = 0
    files_failed = 0

    for file_path in python_files:
        result = _check_file_header(file_path)

        if not (result.has_copyright and result.has_license and result.has_spdx):
            if verbose:
                print(f"Fixing {file_path.relative_to(base_dir)}...")

            if _fix_file_header(file_path):
                files_fixed += 1
                if verbose:
                    print(f"  ✓ Fixed")
            else:
                files_failed += 1
                if verbose:
                    print(f"  ✗ Failed to fix")

    return files_fixed, files_failed


def main() -> int:
    """Main entry point for the script.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Check and optionally fix copyright headers in Python files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Fix missing or incorrect headers",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output",
    )

    args = parser.parse_args()

    # Find repository root (where pyproject.toml is)
    script_dir = Path(__file__).parent.resolve()
    repo_root = script_dir.parent

    if not (repo_root / "pyproject.toml").exists():
        print("Error: Could not find repository root (pyproject.toml not found)", file=sys.stderr)
        return 1

    if args.fix:
        print("Fixing headers in Python files...\n")
        files_fixed, files_failed = _fix_headers(repo_root, args.verbose)

        print(f"\nSummary:")
        print(f"  Files fixed: {files_fixed}")
        if files_failed > 0:
            print(f"  Files failed: {files_failed}")
            return 1

        print("\n✓ All headers fixed successfully")
        return 0
    else:
        print("Checking headers in Python files...\n")
        files_with_issues, files_ok = _check_headers(repo_root, args.verbose)

        if not args.verbose and files_with_issues:
            print("Files with missing or incorrect headers:\n")
            for result in files_with_issues:
                rel_path = result.file_path.relative_to(repo_root)
                missing = []
                if not result.has_copyright:
                    missing.append("copyright")
                if not result.has_license:
                    missing.append("license")
                if not result.has_spdx:
                    missing.append("SPDX")
                print(f"  ✗ {rel_path} - missing: {', '.join(missing)}")

        print(f"\nSummary:")
        print(f"  Files checked: {len(files_with_issues) + len(files_ok)}")
        print(f"  Files OK: {len(files_ok)}")
        print(f"  Files with issues: {len(files_with_issues)}")

        if files_with_issues:
            print("\n✗ Some files are missing required headers")
            print("  Run with --fix to add missing headers")
            return 1

        print("\n✓ All files have correct headers")
        return 0


if __name__ == "__main__":
    sys.exit(main())
