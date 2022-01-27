# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from contextlib import contextmanager
from datetime import datetime
from contextlib import suppress
from .readwrite import JsonFileRW
from .database import StructDatabase
from .exceptions import TrckrError


def default_config():
    return {
        "database": {
            "data_type": "json",
            "path": "%(HOME)s/.trckr-%(GITNAME)s",
            "type": "struct",
        },
        "defaults": {
            "contextid": "%(GITNAME)s",
            "userid": "%(USER)s",
            "note": "%(GITNAME)s-%(GITBRANCH)s",
        }
    }


def parse_path(path_template, data):
    try:
        return path_template % {
            key: str(value)
            for key, value in data.items()
        }
    except (ValueError, KeyError) as e:
        raise TrckrError(
            f"Failed to parse path template: {str(e)}: in '{path_template}'"
        )


def parse_id(id):
    return None if id == "-" else id


def struct_database(config):
    try:
        dbconf = config["database"]
        if dbconf["type"] == "struct":
            path = dbconf["path"]
            data_type = dbconf["data_type"]
            if data_type == "json":
                return StructDatabase(
                    rw=JsonFileRW(path),
                )
    except KeyError:
        pass
    return None


def parse_date_input(date_input):
    current = datetime.now()
    if date_input == "-":
        return current
    elif date_input is None:
        return current
    else:
        with suppress(UnboundLocalError):
            with suppress(ValueError):
                time = datetime.strptime(date_input, "%H:%M")
            with suppress(ValueError):
                time = datetime.strptime(date_input, "%H:%M:%S")

            return current.replace(
                hour=time.hour,
                minute=time.minute,
                second=time.second
            )
    raise TrckrError(f"Failed to parse date input: {date_input}")


def first_database(loaders):
    def _loader(config):
        dbs = (loader(config) for loader in loaders)
        return next(db for db in dbs if db is not None)

    return _loader


def config_from_json(path, extensions=None):
    try:
        with open(path, "r") as f:
            base_data = json.load(f)
    except FileNotFoundError:
        base_data = default_config()

    data = {
        **base_data,
        "_path": path
    }
    ext_data = (
        {}
        if extensions is None
        else extensions(data)
    )

    defaults = {
        key: parse_path(value, ext_data)
        for key, value in data.get("defaults", {}).items()
    }

    return {
        **data,
        "database": {
            **data["database"],
            "path": parse_path(data["database"]["path"], ext_data),
        },
        "defaults": defaults
    }


def insert_into_struct(struct, path, value):
    try:
        current = struct
        for p in path[0:-1]:
            current[p] = current.get(p, {})
            current = current[p]
        p = path[-1]
        if (
            isinstance(current.get(p), dict)
            or isinstance(current.get(p), list)
        ):
            raise TrckrError(f"Cannot replace object with value: {property}")
        else:
            current[p] = value
    except KeyError:
        raise TrckrError(f"Propery path not accessable: '{property}'")


@contextmanager
def writable_config(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = default_config()

    if data.get("locked") is True:
        raise TrckrError("Configuration changes not allowed in locked config.")

    yield data
    serialized = json.dumps(data, indent=4, sort_keys=True)

    with open(path, "w") as f:
        f.write(serialized)


database_loaders = [
    struct_database
]
