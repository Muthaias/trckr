# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

from .utils import (
    CLIParseError,
    parse_start,
    parse_stop,
    parse_add,
    parse_list
)


def cmd_start(argv):
    parse_start(
        timestr=argv[0] if len(argv) > 0 else None,
        metalist=argv[1:]
    )


def cmd_stop(argv):
    parse_stop(
        timestr=argv[0] if len(argv) > 0 else None,
    )


def cmd_add(argv):
    return parse_add(
        intervalstr=argv[0],
        metalist=argv[1:]
    )


def cmd_list(argv):
    return parse_list(
        intervalstr=argv[0] if len(argv) > 0 else None,
    )


def parse_args(argv):
    commands = {
        "t": cmd_start,
        "a": cmd_add,
        "s": cmd_stop,
        "l": cmd_list,
    }
    try:
        command_id = argv[0]
        command = commands[command_id]
        return command(argv[1:])
    except (IndexError, KeyError):
        raise CLIParseError(
            f"""
This script aims to be an efficient way to track time.
Usage: tracker.py <command> [options]
- command: {", ".join(commands.keys())}
""".strip()
        )
