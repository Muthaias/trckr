# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import getpass
import json
from contextlib import contextmanager
from datetime import datetime
from contextlib import suppress
from .readwrite import JsonFileRW
from .database import StructDatabase
from .exceptions import TrckrError


def parse_path(path_template, config):
    config_path = config["_path"]
    contextid = config["contextid"]
    userid = config["userid"]
    config_dir = os.path.dirname(config_path)
    home = os.path.expanduser("~")
    user = getpass.getuser()
    data = {
        "CONFIG_DIR": config_dir,
        "CONFIG_PATH": config_path,
        "USERID": userid,
        "CONTEXTID": contextid,
        "HOME": home,
        "USER": user,
    }
    try:
        return path_template % data
    except (ValueError, KeyError) as e:
        raise TrckrError(
            f"Failed to parse path template: {str(e)}: in '{path_template}'"
        )


def struct_database(config):
    if config["type"] == "struct":
        path = config["path"]
        data_type = config["data_type"]
        contextid = config["contextid"]
        userid = config["userid"]
        if data_type == "json":
            return StructDatabase(
                rw=JsonFileRW(path),
                userid=userid,
                contextid=contextid
            )
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


def config_from_json(path, **kargs):
    with open(path, "r") as f:
        data = {
            **json.load(f),
            **kargs,
            "_path": path
        }

        return {
            **data,
            "path": parse_path(data["path"], data)
        }


@contextmanager
def writable_config(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {
            "contextid": "default",
            "data_type": "json",
            "path": "%(CONFIG_PATH)s",
            "type": "struct",
            "userid": getpass.getuser()
        }

    yield data
    serialized = json.dumps(data, indent=4, sort_keys=True)

    with open(path, "w") as f:
        f.write(serialized)


database_loaders = [
    struct_database
]
