# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime
from .readwrite import JsonFileRW
from .database import StructDatabase
from contextlib import suppress


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
        time = current
        with suppress(ValueError):
            time = datetime.strptime(date_input, "%H:%M")
        with suppress(ValueError):
            time = datetime.strptime(date_input, "%H:%M:%S")

        return current.replace(
            hour=time.hour,
            minute=time.minute,
            second=time.second
        )
