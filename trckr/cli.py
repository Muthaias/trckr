# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from argparse import ArgumentParser


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
        "from",
        type=str,
        help="start of interval"
    )
    add_parse.add_argument(
        "to",
        type=str,
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
        "from",
        type=str,
        help="start of interval"
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
        "to",
        type=str,
        help="end of interval"
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
        type=str,
        help="start of interval"
    )
    list_parse.add_argument(
        "--to",
        type=str,
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
    init_parse.set_defaults(
        command="init"
    )

    context_parse = subparsers.add_parser(
        "set",
        help="set a value"
    )
    context_parse.add_argument(
        "property",
        type=str,
        help="value id"
    )
    context_parse.add_argument(
        "value",
        type=str,
        help="value"
    )
    context_parse.set_defaults(
        command="set"
    )

    args = parser.parse_args(argv)

    if args.command == "main":
        parser.print_help()

    return vars(args)
