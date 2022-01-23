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
from .commands import Commands


DEFAULT_CONFIG_PATH = os.environ.get("TRCKR_CONFIG", ".trckr.json")
commands = Commands()
configs = Commands()


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
        "config_path": args.config,
        "props": unknown_argv,
    }


def parse_add(argv):
    parser = ArgumentParser(
        description="Add an interval",
        prog="add"
    )
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
    parser = ArgumentParser(
        description="Start the timer",
        prog="start"
    )
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
    parser = ArgumentParser(
        description="Stop the timer",
        prog="stop"
    )
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


def parse_ordered(description, *argids, prog=None):
    def _parse(argv):
        parser = ArgumentParser(
            description=description,
            prog=prog
        )
        for arg in argids:
            parser.add_argument(
                arg,
                type=str
            )
        args = vars(parser.parse_args(argv))
        return {
            arg: args[arg]
            for arg in argids
        }
    return _parse


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


@configs.alias(
    "init",
    parse_ordered(
        "initialize trckr",
        "userid",
        "contextid",
        prog="init"
    )
)
def init(config_path, userid=None, contextid=None):
    with writable_config(config_path) as config:
        if userid is not None:
            config["userid"] = userid
        if contextid is not None:
            config["contextid"] = contextid


@configs.alias(
    "context",
    parse_ordered("set active context", "contextid", prog="context")
)
def context(config_path, contextid):
    with writable_config(config_path) as config:
        config["contextid"] = contextid


@configs.alias(
    "user",
    parse_ordered("set active user", "userid", prog="user")
)
def user(config_path, userid):
    with writable_config(config_path) as config:
        config["userid"] = userid


def main(
    command,
    config_path,
    context=None,
    props=None,
    database_loader=first_database(database_loaders)
):
    if command in configs.commands:
        configs.exec(command, props, config_path=config_path)
    else:
        contextid = (
            {"contextid": context}
            if context is not None
            else {}
        )
        with config_from_json(config_path, **contextid) as config_data:
            database = database_loader(config_data)
            try:
                commands.exec(command, props, db=database)
            except TrckrError as e:
                print("Error:", str(e))
