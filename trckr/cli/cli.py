# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import ArgumentParser
from .utils import (
    CLIParseError,
    parse_config_property,
    parse_start,
    parse_stop,
    parse_add,
    parse_list,
    parse_time
)


def parse_args(
    argv,
    default_config_path=None
):
    parser = ArgumentParser(
        description="Trckr is a simple time tracking tool."
    )
    parser.add_argument(
        "--config",
        type=str,
        dest="config_path",
        default=default_config_path,
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
        "interval",
        type=str,
        help="interval to list"
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


def args_to_command(config, command, **kargs):
    args = {
        **config.get("defaults", {}),
        **{
            key: value
            for key, value in kargs.items()
            if value is not None
            and value != "-"
        }
    }
    config_path = config["_path"]
    meta = {
        metaid: args.get(metaid)
        for metaid in ["userid", "contextid", "note"]
        if metaid in args
    }
    if command == "add":
        return parse_add(
            "-".join([args["from"], args["to"]]),
            [],
            meta
        )
    elif command == "start":
        return parse_start(
            args.get("from"),
            [],
            meta
        )
    elif command == "stop":
        return parse_stop(args.get("to"))
    elif command == "list":
        return parse_list(
            args.get("interval", "-"),
            args.get("format", "list")
        )
    elif command == "init":
        return parse_config_property(
            path=config_path,
            property="created",
            value=str(parse_time("now"))
        )
    elif command == "set":
        return parse_config_property(
            path=config_path,
            property=args["property"],
            value=args["value"]
        )

    raise CLIParseError(f"Command not found: {command}")
