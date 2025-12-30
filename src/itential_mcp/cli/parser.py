# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import argparse

from typing import IO

from .terminal import getcols


class Parser(argparse.ArgumentParser):
    def print_app_help(self, file: IO | None = None) -> None:
        """
        Print help for the root application

        This method will print the help message for the root application.  It
        is triggered with `itential-mcp --help` and displays the list of
        available commands and global options.

        Args:
            file (IO): The file to print the ouptut to.  The default is stdout

        Returns:
            None

        Raises:
            None
        """
        file = file or sys.stdout

        print(self.description, file=file)
        print(f"\nUsage:\n  {self.prog} <COMMAND> [OPTIONS]", file=file)

        print("\nCommands:", file=file)
        commands = dict(sorted(self._subparsers._group_actions[0].choices.items()))
        for key, value in commands.items():
            print(f"  {key:<20}{value.description}")

        print("\nOptions:", file=file)

        actions = {}

        for index, action in enumerate(self._actions):
            if not isinstance(action, argparse._SubParsersAction):
                actions[action.option_strings[0]] = action

        for key, value in dict(sorted(actions.items())).items():
            helpstr = value.help or "NO HELP AVAILABLE!!"
            if len(value.option_strings) == 1:
                print(f"{' ':<6}{value.option_strings[0]:<16}{helpstr}", file=file)
            else:
                print(
                    f"{' ':<2}{', '.join(value.option_strings):<20}{helpstr}", file=file
                )

        print(
            '\nUse "itential-mcp <COMMAND> --help" for more information about a command.\n',
            file=file,
        )

    def print_help(self, file: IO | None = None) -> None:
        """
        Print hep for an application command

        This method will print the help message for an application command
        such as `run` or `call`.   The help message is printed to stdout
        by default

        Args:
            file (IO): The file to print the ouptut to.  The default is stdout

        Returns:
            None

        Raises:
            None
        """
        print(self.description, file=file)

        actions = {}
        positional = list()

        for index, action in enumerate(self._actions):
            if not isinstance(action, argparse._SubParsersAction):
                if action.option_strings:
                    if action.container.title not in actions:
                        actions[action.container.title] = {}
                    actions[action.container.title][action.option_strings[0]] = action
                else:
                    positional.append(action.dest)

        args = list()
        for item in positional:
            args.append(f"<{item}>")

        args = " ".join(args)

        print(f"\nUsage:\n  {self.prog} {args} [OPTIONS]\n", file=file)

        options = actions.pop("options")

        for key, value in dict(sorted(actions.items())).items():
            print(f"{key}")

            for k, v in value.items():
                helpstr = v.help or "NO HELP AVAILABLE!!"

                if len(v.option_strings) == 1:
                    if v.metavar is not None:
                        option = f"{v.option_strings[0]} {v.metavar.upper()}"
                    else:
                        option = v.option_strings[0]

                    if len(option) > 21:
                        n = getcols()
                        helpstr = [
                            helpstr[i : i + n] for i in range(0, len(helpstr), n)
                        ]
                        print(f"{' ':6}{option:<22}", file=file)
                        for s in helpstr:
                            print(f"{' ':28}{s}", file=file)
                    else:
                        print(f"{' ':6}{option:<22}{helpstr}", file=file)

                else:
                    if v.metavar is not None:
                        option = f"{', '.join(v.option_strings)} {v.metavar.upper()}"
                    else:
                        option = ", ".join(v.option_strings)

                    if len(option) > 15:
                        n = getcols()
                        helpstr = [
                            helpstr[i : i + n] for i in range(0, len(helpstr), n)
                        ]
                        print(f"{' ':<6}{option:<22}", file=file)
                        for s in helpstr:
                            print(f"{' ':28}{s}", file=file)
                    else:
                        print(f"{' ':<6}{option:<22}{helpstr}", file=file)

        print("\nOptions", file=file)

        for key, value in dict(sorted(options.items())).items():
            helpstr = value.help or "NO HELP AVAILABLE!!"

            if len(value.option_strings) == 1:
                if value.metavar is not None:
                    option = f"{value.option_strings[0]} {value.metavar.upper()}"
                else:
                    option = value.option_strings[0]

                if len(option) > 15:
                    n = getcols()
                    helpstr = [helpstr[i : i + n] for i in range(0, len(helpstr), n)]
                    print(f"{' ':6}{option:<22}", file=file)
                    for s in helpstr:
                        print(f"{' ':28}{s}", file=file)
                else:
                    print(f"{' ':10}{option:<18}{helpstr}", file=file)

            else:
                if value.metavar is not None:
                    option = (
                        f"{', '.join(value.option_strings)} {value.metavar.upper()}"
                    )
                else:
                    option = ", ".join(value.option_strings)

                if len(option) > 15:
                    n = getcols()
                    helpstr = [helpstr[i : i + n] for i in range(0, len(helpstr), n)]
                    print(f"{' ':6}{option:<22}", file=file)
                    for s in helpstr:
                        print(f"{' ':28}{s}", file=file)
                else:
                    print(f"{' ':6}{option:<22}{helpstr}", file=file)

        print(
            '\nUse "itential-mcp <COMMAND> --help" for more information about a command.\n',
            file=file,
        )
