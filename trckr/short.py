# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import json
import datetime
from .exceptions import TrckrError
from .utils import (
    parse_time,
    parse_interval,
)


def parse_meta(argv, defaults=None):
    defaults = {} if defaults is None else defaults
    note = " ".join(argv)
    return {
        **defaults,
        "note": note
    }


def cmd_start(argv):
    timestr = argv[0] if len(argv) > 0 else None
    t = parse_time(timestr)
    meta = parse_meta(argv[1:])
    return {
        "type": "start",
        "time": t,
        "meta": meta
    }


def cmd_stop(argv):
    timestr = argv[0] if len(argv) > 0 else None
    t = parse_time(timestr)
    return {
        "type": "stop",
        "time": t
    }


def cmd_add(argv):
    [s, t] = parse_interval(argv[0])
    meta = parse_meta(argv[1:])
    return {
        "type": "add",
        "interval": [s, t],
        "meta": meta
    }


def cmd_list(argv):
    intervalstr = argv[0] if len(argv) > 0 else None
    [s, t] = parse_interval(intervalstr)
    return {
        "type": "list",
        "interval": [s, t],
    }


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
        raise TrckrError(
f"""
This script aims to be an efficient way to track time.
Usage: tracker.py <command> [options]
- command: {", ".join(commands.keys())}
"""
        )


