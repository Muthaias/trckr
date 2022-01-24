# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
from itertools import groupby
from operator import attrgetter
from .utils import (
    first_database,
    database_loaders,
    config_from_json,
    writable_config
)
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


def database_from_config(config_path, loader, contextid=None, userid=None):
    overrides = {
        key: value
        for key, value in {
            "contextid": contextid,
            "userid": userid,
        }.items()
        if value is not None
    }
    config_data = config_from_json(
        config_path,
        overrides
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
