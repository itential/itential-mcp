# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import asyncio

from .runtime import parse_args
from .core import env
from .core import logging


def run() -> int:
    """
    Main entry point for the application.

    Returns:
        int: The application return code (0 for success, 1 for failure)

    Raises:
        SystemExit: Always exits with the return code
    """
    try:
        handler_func, handler_args, handler_kwargs = parse_args(sys.argv[1:])
        return asyncio.run(handler_func(*handler_args, **handler_kwargs))
    except KeyboardInterrupt:
        logging.info("Application interrupted by user")
        return 130  # Standard exit code for SIGINT
    except SystemExit:
        # Re-raise SystemExit (from argument parsing errors)
        raise
    except Exception as e:
        logging.error(f"Application error: {e}")
        if env.getbool("ITENTIAL_MCP_DEBUG", False):
            import traceback

            traceback.print_exc()
        return 1
