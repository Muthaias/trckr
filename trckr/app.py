# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import os
from argparse import ArgumentParser
from .utils import (
    first_database,
    parse_date_input,
    database_loaders
)
from .exceptions import TrckrError
from .commands import Commands


DEFAULT_CONFIG_PATH = os.environ.get("TRCKR_CONFIG", ".trckr.json")
commands = Commands()


def parse_main(argv):
    parser = ArgumentParser(
        description="Trckr is a simple time tracking tool."
    )
    parser.add_argument(
        "command",
        type=str,
        help="the command to be issued"
    )
    parser.add_argument(
        "--context",
        type=str,
        default=None,
        help="the tracking context"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=DEFAULT_CONFIG_PATH,
        help="path to config file"
    )

    args, unknown_argv = parser.parse_known_args(argv)

    return {
        "command": args.command,
        "context": args.context,
        "config": args.config,
        "props": unknown_argv,
    }


def parse_add(argv):
    parser = ArgumentParser(description="Add an interval")
    parser.add_argument(
        "start",
        type=str,
        help="start of interval"
    )
    parser.add_argument(
        "stop",
        type=str,
        help="end of interval"
    )
    parser.add_argument(
        "note",
        type=str,
        default=None,
        help="a note for the interval"
    )
    args = parser.parse_args(argv)

    return {
        "start": parse_date_input(args.start),
        "stop": parse_date_input(args.stop),
        "note": args.note
    }


def parse_start(argv):
    parser = ArgumentParser(description="Start the timer")
    parser.add_argument(
        "note",
        type=str,
        default=None,
        help="a note for the interval"
    )
    parser.add_argument(
        "--when",
        type=str,
        default=None,
        help="start of interval"
    )
    args = parser.parse_args(argv)

    return {
        "time": parse_date_input(args.when),
        "note": args.note
    }


def parse_stop(argv):
    parser = ArgumentParser(description="Stop the timer")
    parser.add_argument(
        "--when",
        type=str,
        default=None,
        help="start of interval"
    )
    args = parser.parse_args(argv)

    return {
        "time": parse_date_input(args.when)
    }


def parse_none(argv):
    return {}


@commands.alias("add", parse_add)
def add(db, start, stop, note=None):
    db.add(start, stop, note)
    db.commit()


@commands.alias("start", parse_start)
def start(db, time, note=None):
    db.start(time, note)
    db.commit()


@commands.alias("stop", parse_stop)
def stop(db, time, note=None):
    db.stop(time)
    db.commit()


@commands.alias("list", parse_none)
def list(db):
    for entry in db.entries:
        print(entry.note, entry.start, entry.stop)


def main(
    command,
    config,
    context=None,
    props=None,
    database_loader=first_database(database_loaders)
):
    with open(config, "r") as f:
        config_data = json.load(f)
        contextid = (
            {"contextid": context}
            if context is not None
            else {}
        )
        database = database_loader(
            {
                **config_data,
                **contextid
            },
        )
        try:
            commands.exec(command, props, db=database)
        except TrckrError as e:
            print("Error:", str(e))
