# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import sys
import asyncio
import argparse
import traceback
import inspect

from collections.abc import Sequence
from dataclasses import fields

from . import config
from . import terminal
from . import commands


LEGACY_ENV_VARS = frozenset((
    ("ITENTIAL_MCP_TRANSPORT", "ITENTIAL_MCP_SERVER_TRANSPORT"),
    ("ITENTIAL_MCP_HOST", "ITENTIAL_MCP_SERVER_HOST"),
    ("ITENTIAL_MCP_PORT", "ITENTIAL_MCP_SERVER_PORT"),
    ("ITENTIAL_MCP_LOG_LEVEL", "ITENTIAL_MCP_SERVER_LOG_LEVEL"),
))



class Cli(argparse.ArgumentParser):

    def print_app_help(self, file=None):
        """
        """
        print(self.description)
        print(f"\nUsage:\n  {self.prog} <command> [options]")

        print("\nCommands:")
        commands = dict(sorted(self._subparsers._group_actions[0].choices.items()))
        for key, value in commands.items():
            print(f"  {key:<20}{value.description}")

        print("\nOptions:")

        actions = {}

        for index, action in enumerate(self._actions):
            if not isinstance(action, argparse._SubParsersAction):
                actions[action.option_strings[0]] = action


        for key, value in dict(sorted(actions.items())).items():
            helpstr = value.help or "NO HELP AVAILABLE!!"
            if len(value.option_strings) == 1:
                print(f"      {value.option_strings[0]:<16}{helpstr}")
            else:
                print(f"  {', '.join(value.option_strings):<20}{helpstr}")

        print("\nUse \"itential-mcp <command> --help\" for more information about a command.\n")


    def print_help(self, file=None):
        """
        """
        print(self.description)
        print(f"\nUsage:\n  {self.prog} [options]\n")

        actions = {}

        for index, action in enumerate(self._actions):
            if not isinstance(action, argparse._SubParsersAction):
                if action.container.title not in actions:
                    actions[action.container.title] = {}
                actions[action.container.title][action.option_strings[0]] = action

        options = actions.pop("options")

        for key, value in dict(sorted(actions.items())).items():
            print(f"{key}")

            for k, v in value.items():
                helpstr = v.help or "NO HELP AVAILABLE!!"

                if len(v.option_strings) == 1:
                    if v.metavar is not None:
                        option = f"{v.option_strings[0]} {v.metavar}"
                    else:
                        option = v.option_strings[0]

                    if len(option) > 21:
                        n = terminal.getcols()
                        helpstr = [helpstr[i:i+n] for i in range(0, len(helpstr), n)]
                        print(f"{' ':6}{option:<22}")
                        for s in helpstr:
                            print(f"{' ':28}{s}")
                    else:
                        print(f"{' ':6}{option:<22}{helpstr}")

                else:
                    option = f"{', '.join(value.option_strings)} {value.metavar}"
                    if len(option) > 15:
                        n = terminal.getcols()
                        helpstr = [helpstr[i:i+n] for i in range(0, len(helpstr), n)]
                        print(f"      {option:<22}")
                        for s in helpstr:
                            print(f"{' ':28}{s}")
                    else:
                        print(f"      {option:<22}{helpstr}")



        print("\nGlobal Options")

        for key, value in dict(sorted(options.items())).items():
            helpstr = value.help or "NO HELP AVAILABLE!!"

            if len(value.option_strings) == 1:
                if value.metavar is not None:
                    option = f"{value.option_strings[0]} {value.metavar}"
                else:
                    option = value.option_strings[0]

                if len(option) > 15:
                    n = terminal.getcols()
                    helpstr = [helpstr[i:i+n] for i in range(0, len(helpstr), n)]
                    print(f"{' ':6}{option:<22}")
                    for s in helpstr:
                        print(f"{' ':28}{s}")
                else:
                    print(f"{' ':10}{option:<18}{helpstr}")

            else:
                option = f"{', '.join(value.option_strings)} {value.metavar}"
                if len(option) > 15:
                    n = terminal.getcols()
                    helpstr = [helpstr[i:i+n] for i in range(0, len(helpstr), n)]
                    print(f"{' ':6}{option:<22}")
                    for s in helpstr:
                        print(f"{' ':28}{s}")
                else:
                    print(f"{' ':6}{option:<22}{helpstr}")

        print("\nUse \"itential-mcp <command> --help\" for more information about a command.\n")


def parse_args(args: Sequence) -> None:
    """
    Parses any arguments

    This function will parse the arguments identified by the `args` argument
    and return a Namespace object with the values. Typically this is used
    to parse command line arguments passed when the application starts.

    Args:
        args (Sequence): The list of arguments to parse

    Returns:
        None

    Raises:
        None
    """
    parser = Cli(
        prog="itential-mcp",
        add_help=False,
        description="Itential MCP\n\n  Find more information at: https://github.com/itential/itential-mcp"
    )

    parser.add_argument(
        "--config",
        help="The Itential MCP configuration file"
    )

    parser.add_argument(
        '-h', '--help',
        action='store_true',
        help="Prints this help message and exits"
    )

    subparsers = parser.add_subparsers(dest="command")

    run_cmd = subparsers.add_parser(
        "run",
        description="Run the MCP server"
    )

    subparsers.add_parser(
        "version",
        description="Print the version information"
    )

    run_cmd.add_argument(
        "--config",
        help="The Itential MCP configuration file"
    )

    # MCP Server arguments
    server_group = run_cmd.add_argument_group(
        "MCP Server Options",
        "Configuration options for the MCP Server instance"
    )

    # Itential Platform arguments
    platform_group = run_cmd.add_argument_group(
        "Itential Platform Options",
        "Configuration options for connecting to Itential Platform API"
    )

    data = [f for f in fields(config.Config)]

    for ele in data:
        attrs = ele.default.json_schema_extra
        if attrs and attrs.get("x-itential-mcp-cli-enabled"):
            helpstr = ele.default.description
            if helpstr is not None:
                helpstr += f" (default={ele.default.default})"
            else:
                helpstr = "NO HELP AVAILABLE!!"

            kwargs = {
                "dest": ele.name,
                "help": helpstr
            }

            kwargs.update(attrs.get("x-itential-mcp-options") or {})
            posargs = attrs.get("x-itential-mcp-arguments")


        if ele.name.startswith("server"):
            server_group.add_argument(*posargs, **kwargs)
        elif ele.name.startswith("platform"):
            platform_group.add_argument(*posargs, **kwargs)


    args = parser.parse_args(args=args)

    if args.help or args.command is None:
        parser.print_app_help()
        sys.exit(0)

    for key, value in dict(args._get_kwargs()).items():
        envkey = f"ITENTIAL_MCP_{key}".upper()
        if key.startswith("platform") or key.startswith("server"):
            if value is not None:
                if envkey not in os.environ:
                    if isinstance(value, str):
                        value = ", ".join(value.split(","))
                    os.environ[envkey] = str(value)

    conf_file = args.config
    if conf_file is not None:
        os.environ["ITENTIAL_MCP_CONFIG"] = conf_file

    # XXX (privateip) This will check for any values that use the legacy
    # environment variables which did not include the _SERVER_ in the name.
    for oldvar, newvar in LEGACY_ENV_VARS:
        if oldvar in os.environ and newvar not in os.environ:
            os.environ[newvar] = os.environ.pop(oldvar)

    f, args, kwargs = getattr(commands, args.command)(args)

    if not callable(f) or not inspect.iscoroutinefunction(f):
        raise TypeError("handler must be callable and awaitable")

    return f, (args or ()), (kwargs or {})


def run() -> int:
    """
    Main entry point for the application

    Args:
        None

    Returns:
        int: The application return code

    Raises:
        None
    """
    try:
        f, args, kwargs = parse_args(sys.argv[1:])
        return asyncio.run(f(*args, **kwargs))
    except Exception:
        traceback.print_exc()
        sys.exit(1)
