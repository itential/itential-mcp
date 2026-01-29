# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import os
from datetime import datetime
from typing import Any, Coroutine, Sequence, Mapping, Tuple, Optional

from . import runner
from .. import server
from ..core import metadata
from ..utilities import tool


def run(args: Any) -> Tuple[Coroutine, Sequence, Mapping]:
    """Implement the `itential-mcp run` command.

    This function implements the run command and returns the `run` function
    from the `server` module to start the MCP server.

    Args:
        args: The argparse Namespace instance containing command line arguments.

    Returns:
        A tuple consisting of a coroutine function, a sequence that represents
        the input args for the function, and a mapping that represents the
        keyword arguments for the function.

    Raises:
        None
    """
    return server.run, None, None


def version(args: Any) -> Tuple[Coroutine, Sequence, Mapping]:
    """Implement the `itential-mcp version` command.

    This function implements the version command and returns the `display_version`
    function from the `metadata` module to show version information.

    Args:
        args: The argparse Namespace instance containing command line arguments.

    Returns:
        A tuple consisting of a coroutine function, a sequence that represents
        the input args for the function, and a mapping that represents the
        keyword arguments for the function.

    Raises:
        None
    """
    return metadata.display_version, None, None


def tools(args: Any) -> Tuple[Coroutine, Sequence, Mapping]:
    """Implement the `itential-mcp tools` command.

    This function is the implementation of the `tools` command that
    will display the list of all available tools to stdout.

    Args:
        args: The argparse Namespace instance containing command line arguments.

    Returns:
        A tuple consisting of a coroutine function, a sequence that represents
        the input args for the function, and a mapping that represents the
        keyword arguments for the function.

    Raises:
        None
    """
    return tool.display_tools, None, None


def tags(args: Any) -> Tuple[Coroutine, Sequence, Mapping]:
    """Implement the `itential-mcp tags` command.

    This function is the implementation of the `tags` command that
    will display the list of all available tags to stdout.

    Args:
        args: The argparse Namespace instance containing command line arguments.

    Returns:
        A tuple consisting of a coroutine function, a sequence that represents
        the input args for the function, and a mapping that represents the
        keyword arguments for the function.

    Raises:
        None
    """
    return tool.display_tags, None, None


def call(args: Any) -> Tuple[Coroutine, Sequence, Mapping]:
    """Implement the `itential-mcp call` command.

    This function provides the implementation of the `call` command that
    will invoke a tool with (or without) parameters. The tool function
    executes and returns the result.

    Args:
        args: The argparse Namespace instance containing command line arguments,
              including the tool name and parameters to call.

    Returns:
        A tuple consisting of a coroutine function, a sequence that represents
        the input args for the function, and a mapping that represents the
        keyword arguments for the function.

    Raises:
        None
    """
    return runner.run, (args.tool, args.params), None


async def _execute_test_connection(
    config_file: Optional[str] = None,
    format: str = "human",
    verbose: bool = False,
    timeout: int = 30,
    quiet: bool = False,
) -> int:
    """Execute connection test to Itential Platform.

    Args:
        config_file: Path to configuration file.
        format: Output format (human or json).
        verbose: Show detailed diagnostic information.
        timeout: Maximum time for test in seconds.
        quiet: Suppress progress messages.

    Returns:
        int: Exit code (0=success, 1=failure).
    """
    from .. import config
    from ..platform.connection_test import ConnectionTestService
    from ..cli.terminal import print_error, print_info

    # Load configuration
    try:
        if config_file:
            os.environ["ITENTIAL_MCP_CONFIG"] = config_file

        cfg = config.get()
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        return 1

    # Create service
    service = ConnectionTestService(cfg)

    # Run checks
    if not quiet and format == "human":
        print_info("Testing connection to Itential Platform...")
        print()

    try:
        result = await service.run_all_checks(timeout=timeout)
    except Exception as e:
        print_error(f"Connection test failed with unexpected error: {e}")
        return 1

    # Output results
    if format == "json":
        _output_json(result)
    else:
        _output_human(result, verbose=verbose)

    return 0 if result.success else 1


def _output_human(result: Any, verbose: bool = False) -> None:
    """Output results in human-readable format.

    Args:
        result: Test results.
        verbose: Show detailed information.
    """
    from ..platform.connection_test import CheckStatus
    from ..cli.terminal import Colors

    # Print check results
    for check in result.checks:
        if check.status == CheckStatus.PASSED:
            symbol = "✓"
            color = Colors.GREEN
        elif check.status == CheckStatus.FAILED:
            symbol = "✗"
            color = Colors.RED
        elif check.status == CheckStatus.SKIPPED:
            symbol = "○"
            color = Colors.YELLOW
        else:  # WARNING
            symbol = "⚠"
            color = Colors.YELLOW

        print(f"{color}{symbol}{Colors.RESET} {check.message}")

        # Show timing in verbose mode
        if verbose:
            print(f"  {Colors.BLUE}Duration:{Colors.RESET} {check.duration_ms:.0f}ms")

        # Show details in verbose mode
        if verbose and check.details:
            print(f"  {Colors.BLUE}Details:{Colors.RESET}")
            for key, value in check.details.items():
                print(f"    • {key}: {value}")

        # Show error details in verbose mode
        if verbose and check.error:
            print(
                f"  {Colors.RED}Error:{Colors.RESET} {type(check.error).__name__}: {check.error}"
            )

        # Show suggestions for failures
        if check.status == CheckStatus.FAILED and check.suggestion:
            print()
            print(f"  {Colors.YELLOW}💡 Suggestion:{Colors.RESET}")
            for line in check.suggestion.split("\n"):
                if line.strip():
                    print(f"     {line}")
            print()

    print()
    print("─" * 60)
    print()

    # Print summary
    if result.success:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ Connection test: SUCCESS{Colors.RESET}")
        print()
        if result.platform_version:
            print(
                f"  Platform version: {Colors.BOLD}{result.platform_version}{Colors.RESET}"
            )
        if result.authenticated_user:
            print(
                f"  Authenticated as: {Colors.BOLD}{result.authenticated_user}{Colors.RESET}"
            )
        print(
            f"  Total duration: {Colors.BOLD}{result.duration_ms / 1000:.2f}s{Colors.RESET}"
        )
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Connection test: FAILED{Colors.RESET}")
        print()
        if result.error:
            print(f"  {Colors.RED}Error: {result.error}{Colors.RESET}")

    print()


def _output_json(result: Any) -> None:
    """Output results in JSON format.

    Args:
        result: Test results.
    """
    from ..platform.connection_test import CheckStatus

    # Build comprehensive JSON output
    data = {
        "success": result.success,
        "duration_ms": round(result.duration_ms, 2),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": [],
    }

    # Add check results
    for check in result.checks:
        check_data = {
            "name": check.name,
            "status": check.status,
            "message": check.message,
            "duration_ms": round(check.duration_ms, 2),
        }

        if check.details:
            check_data["details"] = check.details

        if check.suggestion:
            check_data["suggestion"] = check.suggestion

        if check.error:
            check_data["error"] = {
                "type": type(check.error).__name__,
                "message": str(check.error),
            }

        data["checks"].append(check_data)

    # Add metadata
    if result.platform_version:
        data["platform_version"] = result.platform_version
    if result.authenticated_user:
        data["authenticated_user"] = result.authenticated_user
    if result.error:
        data["error"] = result.error

    # Add summary statistics
    data["summary"] = {
        "total_checks": len(result.checks),
        "passed": sum(1 for c in result.checks if c.status == CheckStatus.PASSED),
        "failed": sum(1 for c in result.checks if c.status == CheckStatus.FAILED),
        "skipped": sum(1 for c in result.checks if c.status == CheckStatus.SKIPPED),
        "warnings": sum(1 for c in result.checks if c.status == CheckStatus.WARNING),
    }

    print(json.dumps(data, indent=2))


def test(args: Any) -> Tuple[Coroutine, Sequence, Mapping]:
    """Implement the `itential-mcp test` command.

    This function provides the implementation of the `test` command
    that tests connectivity to the Itential Platform.

    Args:
        args: The argparse Namespace instance containing command line arguments.

    Returns:
        A tuple consisting of a coroutine function, a sequence that represents
        the input args for the function, and a mapping that represents the
        keyword arguments for the function.
    """
    kwargs = {
        "config_file": getattr(args, "config", None),
        "format": getattr(args, "format", "human"),
        "verbose": getattr(args, "verbose", False),
        "timeout": getattr(args, "timeout", 30),
        "quiet": getattr(args, "quiet", False),
    }
    return _execute_test_connection, None, kwargs
