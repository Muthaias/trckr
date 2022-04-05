# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
from itertools import groupby
from .data_extensions import standard_extensions
from .utils import (
    first_database,
    database_loaders,
    config_from_json,
    writable_config,
    insert_into_struct,
)
from .database import Meta
from .exceptions import TrckrError


def add_entry(db, interval, note=None):
    [from_time, to_time] = interval
    db.add(from_time, to_time, note)
    db.commit()


def start_timer(db, time, note=None):
    db.start(time, note)
    db.commit()


def stop_timer(db, time):
    db.stop(time)
    db.commit()


def list_entries(db, interval=[None, None], format="list"):
    [from_time, to_time] = interval
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


def exec(config, database, command):
    defaults = config.get("defaults", {})
    meta = Meta.from_data({
        **defaults,
        **command.get("meta", {})
    })
    tracker_cmds = {
        "add": lambda db: add_entry(db, command["interval"], meta),
        "start": lambda db: start_timer(db, command["time"], meta),
        "stop": lambda db: stop_timer(db, command["time"]),
        "list": lambda db: list_entries(db, command["interval"]),
        "config": lambda db: set_property(
            command["path"],
            command["property"],
            command["value"]
        ),
    }
    try:
        command_type = command["type"]
        tracker_cmds[command_type](database)
    except KeyError:
        raise TrckrError(f"Command type not found: {command_type}")
