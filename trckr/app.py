# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import datetime
from itertools import groupby
from operator import attrgetter
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


def add_entry(db, start, stop, note=None):
    db.add(start, stop, note)
    db.commit()


def start_timer(db, time, note=None):
    db.start(time, note)
    db.commit()


def stop_timer(db, time, note=None):
    db.stop(time)
    db.commit()


def list_entries(db, from_time=None, to_time=None, format="list"):
    entries = db.select(
        from_time=from_time,
        to_time=to_time
    )

    def _hours_and_minutes(td):
        return (
            td.days * 24 + td.seconds // 3600,
            td.seconds // 60 % 60
        )

    grouped_entries = groupby(entries, key=attrgetter("contextid"))
    timeformat = "%02dh %02dm"
    for contextid, group_entries in grouped_entries:
        entry_list = list(group_entries)
        groupsum = sum(
            [entry.stop - entry.start for entry in entry_list],
            datetime.timedelta()
        )
        print(f"{contextid}: {timeformat % _hours_and_minutes(groupsum)}")
        for entry in entry_list:
            difference = entry.stop - entry.start
            print(
                f"  {entry.start.date()}: "
                f"{timeformat % _hours_and_minutes(difference)} "
                f"# {entry.note}"
            )


def init_tracker(config_path, userid=None, contextid=None):
    with writable_config(config_path) as config:
        if userid is not None:
            config["userid"] = userid
        if contextid is not None:
            config["contextid"] = contextid


def set_context(config_path, contextid):
    with writable_config(config_path) as config:
        config["contextid"] = contextid


def set_user(config_path, userid):
    with writable_config(config_path) as config:
        config["userid"] = userid


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


def database_from_config(config_path, loader, contextid=None, userid=None):
    overrides = {
        "contextid": contextid,
        "userid": userid,
    }
    config_data = config_from_json(
        config_path,
        **{
            key: value
            for key, value in overrides.items()
            if value is not None
        }
    )
    return loader(config_data)


def main(
    command,
    config_path,
    contextid=None,
    userid=None,
    database_loader=first_database(database_loaders),
    **kargs
):
    try:
        tracker_cmds = {
            "add": add_entry,
            "start": start_timer,
            "stop": stop_timer,
            "list": list_entries
        }
        root_cmds = {
            "init": lambda: init_tracker(config_path, contextid, userid),
            "context": lambda: set_context(config_path, contextid),
            "user": lambda: set_user(config_path, userid)
        }
        if command in tracker_cmds:
            db = database_from_config(
                config_path,
                database_loader,
                contextid=contextid,
                userid=userid
            )
            tracker_cmds[command](db=db, **kargs)
        elif command in root_cmds:
            root_cmds[command]()
    except TrckrError as e:
        print("Error:", str(e))
