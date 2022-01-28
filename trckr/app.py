# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
from itertools import groupby
from operator import attrgetter
from .data_extensions import standard_extensions
from .utils import (
    first_database,
    database_loaders,
    config_from_json,
    writable_config,
    parse_date_input,
    insert_into_struct,
)
from .database import Meta
from .exceptions import TrckrError


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

    grouped_entries = groupby(
        entries,
        key=lambda e: e.meta.contextid
    )
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
                f"# {entry.meta.note}"
            )


def set_property(config_path, property, value):
    path = property.split(".")
    with writable_config(config_path) as config:
        insert_into_struct(config, path, value)


def load_config(config_path):
    return config_from_json(
        config_path,
        standard_extensions
    )


def load_database(
    config,
    database_loader=first_database(database_loaders)
):
    return database_loader(config)


def main(
    config,
    database,
    command,
    **kargs
):
    args = {
        **config.get("defaults", {}),
        **{
            key: value
            for key, value in kargs.items()
            if value is not None
            and value != "-"
        }
    }
    try:
        config_path = config["_path"]
        from_time = parse_date_input(args.get("from"))
        to_time = parse_date_input(args.get("to"))
        meta = Meta.from_data(args)
        tracker_cmds = {
            "add": lambda db: add_entry(db, from_time, to_time, meta),
            "start": lambda db: start_timer(db, from_time, meta),
            "stop": lambda db: stop_timer(db, to_time),
            "list": lambda db: list_entries(db)
        }
        root_cmds = {
            "init": lambda: set_property(
                config_path,
                "created",
                str(datetime.datetime.now())
            ),
            "set": lambda: set_property(
                config_path,
                args["property"],
                args["value"]
            ),
        }
        if command in tracker_cmds:
            tracker_cmds[command](database)

        elif command in root_cmds:
            root_cmds[command]()
    except TrckrError as e:
        print("Error:", str(e))
