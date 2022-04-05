# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

from .utils import (
    CLIParseError,
    parse_start,
    parse_stop,
    parse_add,
    parse_list,
    parse_config_property,
    parse_time
)


def cmd_start(argv):
    """Start timer: (time|now) ([...note...])"""
    return parse_start(
        timestr=argv[0] if len(argv) > 0 else None,
        metalist=argv[1:]
    )


def cmd_stop(argv):
    """Stop current timer: (time|now)"""
    return parse_stop(
        timestr=argv[0] if len(argv) > 0 else None,
    )


def cmd_add(argv):
    """Add an interval: <interval> ([...note...])"""
    return parse_add(
        intervalstr=argv[0],
        metalist=argv[1:]
    )


def cmd_list(argv):
    """List the time entries in interval: (interval)"""
    return parse_list(
        intervalstr=argv[0] if len(argv) > 0 else None,
    )


def cmd_config_property(argv):
    """Set configuration property: <property.path> <value>"""
    return parse_config_property(
        property=argv[0],
        value=argv[1]
    )


def cmd_config_init(argv):
    """Initialize the tracker in current direcotry: No arguments"""
    return parse_config_property(
        property="created",
        value=str(parse_time("now"))
    )


def parse_args(argv):
    commands = {
        "t": cmd_start,
        "a": cmd_add,
        "s": cmd_stop,
        "l": cmd_list,
        "cs": cmd_config_property,
        "ci": cmd_config_init
    }
    try:
        command_id = argv[0]
        command = commands[command_id]
        return command(argv[1:])
    except (IndexError, KeyError):
        command_help = "\n".join(
            [f"  - {k}: {c.__doc__}" for k, c in commands.items()]
        )
        raise CLIParseError(
            f"""
This script aims to be an efficient way to track time.
Usage: tracker.py <command> [options]
- command: {", ".join(commands.keys())}
{command_help}
""".strip()
        )
