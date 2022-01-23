# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from argparse import ArgumentParser
from .utils import (
    first_database,
    parse_date_input,
    database_loaders,
    config_from_json,
    writable_config
)
from .exceptions import TrckrError


DEFAULT_CONFIG_PATH = os.environ.get("TRCKR_CONFIG", ".trckr.json")


def add(db, start, stop, note=None):
    db.add(start, stop, note)
    db.commit()


def start(db, time, note=None):
    db.start(time, note)
    db.commit()


def stop(db, time, note=None):
    db.stop(time)
    db.commit()


def list(db):
    for entry in db.entries:
        print(entry.note, entry.start, entry.stop)


def init(config_path, userid=None, contextid=None):
    with writable_config(config_path) as config:
        if userid is not None:
            config["userid"] = userid
        if contextid is not None:
            config["contextid"] = contextid


def context(config_path, contextid):
    with writable_config(config_path) as config:
        config["contextid"] = contextid


def user(config_path, userid):
    with writable_config(config_path) as config:
        config["userid"] = userid


def database_prop(database_loader):
    def _prop(args):
        contextid = (
            {"contextid": args.contextid}
            if args.contextid is not None
            else {}
        )
        userid = (
            {"userid": args.userid}
            if args.userid is not None
            else {}
        )
        config_data = config_from_json(
            args.config,
            **contextid,
            **userid
        )
        return {
            "db": database_loader(config_data)
        }
    return _prop


def config_path_prop(args):
    return {
        "config_path": args.config
    }


def select_args(*argids):
    def _select(args):
        argdict = vars(args)
        return {
            argid: argdict[argid]
            for argid in argids
            if argid in argdict
        }
    return _select


def parse_args(
    argv,
    database_prop_func=database_prop(first_database(database_loaders)),
    config_path_prop_func=config_path_prop
):
    parser = ArgumentParser(
        description="Trckr is a simple time tracking tool."
    )
    parser.add_argument(
        "--config",
        type=str,
        default=DEFAULT_CONFIG_PATH,
        help="path to config file"
    )
    parser.add_argument(
        "--contextid",
        type=str,
        default=None,
        help="use a temporary context id"
    )
    parser.add_argument(
        "--userid",
        type=str,
        help="use a temporary user id"
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
        func=add,
        props=database_prop_func,
        select=select_args("start", "stop", "note")
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
        func=start,
        props=database_prop_func,
        select=select_args("time", "note")
    )

    stop_parse = subparsers.add_parser(
        "stop",
        help="stop the curren timer"
    )
    stop_parse.add_argument(
        "time",
        type=parse_date_input,
        help="the time to stop at"
    )
    stop_parse.set_defaults(
        func=stop,
        props=database_prop_func,
        select=select_args("time")
    )

    init_parse = subparsers.add_parser(
        "init",
        help="initialize a new trckr"
    )
    init_parse.add_argument(
        "--userid",
        type=str,
        help="the default user for the trckr"
    )
    init_parse.add_argument(
        "--contextid",
        type=str,
        help="the default context for the trckr"
    )
    init_parse.set_defaults(
        func=init,
        props=config_path_prop_func,
        select=select_args("userid", "contextid")
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
        func=context,
        props=config_path_prop_func,
        select=select_args("contextid")
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
        func=user,
        props=config_path_prop_func,
        select=select_args("userid")
    )

    args = parser.parse_args(argv)
    return args


def main(args):
    try:
        args.func(
            **args.select(args),
            **args.props(args)
        )
    except TrckrError as e:
        print("Error:", str(e))
