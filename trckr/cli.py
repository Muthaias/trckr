# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from argparse import ArgumentParser
from .utils import (
    parse_date_input,
)


DEFAULT_CONFIG_PATH = os.environ.get("TRCKR_CONFIG", ".trckr.json")


def parse_args(
    argv
):
    parser = ArgumentParser(
        description="Trckr is a simple time tracking tool."
    )
    parser.add_argument(
        "--config",
        type=str,
        dest="config_path",
        default=DEFAULT_CONFIG_PATH,
        help="path to config file"
    )
    parser.add_argument(
        "--context",
        dest="contextid",
        type=str,
        help="use a temporary context id"
    )
    parser.add_argument(
        "--user",
        dest="userid",
        type=str,
        help="use a temporary user id"
    )

    def _show_help(*args, **kargs):
        parser.print_help()

    def _noprop(*args, **kargs):
        return {}

    parser.set_defaults(
        command="main"
    )

    subparsers = parser.add_subparsers()

    add_parse = subparsers.add_parser(
        "add",
        help="add an interval with a note"
    )
    add_parse.add_argument(
        "start",
        type=parse_date_input,
        help="start of interval"
    )
    add_parse.add_argument(
        "stop",
        type=parse_date_input,
        help="end of interval"
    )
    add_parse.add_argument(
        "note",
        type=str,
        help="a note for the interval"
    )
    add_parse.set_defaults(
        command="add",
    )

    start_parse = subparsers.add_parser(
        "start",
        help="start the timer with a note"
    )
    start_parse.add_argument(
        "time",
        type=parse_date_input,
        help="the time to start at"
    )
    start_parse.add_argument(
        "note",
        type=str,
        help="a note for the interval"
    )
    start_parse.set_defaults(
        command="start",
    )

    stop_parse = subparsers.add_parser(
        "stop",
        help="stop the current timer"
    )
    stop_parse.add_argument(
        "time",
        type=parse_date_input,
        help="the time to stop at"
    )
    stop_parse.set_defaults(
        command="stop"
    )

    list_parse = subparsers.add_parser(
        "list",
        help="list entries"
    )
    list_parse.add_argument(
        "--from",
        dest="from_time",
        type=parse_date_input,
        help="start of interval"
    )
    list_parse.add_argument(
        "--to",
        dest="to_time",
        type=parse_date_input,
        help="end of interval"
    )
    list_parse.add_argument(
        "--format",
        type=str,
        help="output format"
    )
    list_parse.set_defaults(
        command="list"
    )

    init_parse = subparsers.add_parser(
        "init",
        help="initialize a new trckr"
    )
    init_parse.add_argument(
        "--user",
        dest="userid",
        type=str,
        help="the default user for the trckr"
    )
    init_parse.add_argument(
        "--context",
        dest="contextid",
        type=str,
        help="the default context for the trckr"
    )
    init_parse.set_defaults(
        command="init"
    )

    context_parse = subparsers.add_parser(
        "context",
        help="set active context id"
    )
    context_parse.add_argument(
        "contextid",
        type=str,
        help="a context id or alias"
    )
    context_parse.set_defaults(
        command="context"
    )

    user_parse = subparsers.add_parser(
        "user",
        help="set active user id"
    )
    user_parse.add_argument(
        "userid",
        type=str,
        help="a user id or alias"
    )
    user_parse.set_defaults(
        command="user"
    )

    args = parser.parse_args(argv)

    if args.command == "main":
        parser.print_help()

    return vars(args)
