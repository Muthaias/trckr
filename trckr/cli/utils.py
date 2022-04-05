# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import os
from ..utils import (
    parse_time,
    parse_interval,
)


DEFAULT_CONFIG_PATH = os.environ.get("TRCKR_CONFIG", ".trckr.json")


class CLIParseError(Exception):
    pass


def parse_meta(metalist, defaults=None):
    defaults = {} if defaults is None else defaults
    note = {"note": " ".join(metalist)} if len(metalist) > 0 else {}
    return {
        **defaults,
        **note
    }


def parse_start(timestr, metalist, defaults={}):
    t = parse_time(timestr)
    meta = parse_meta(metalist, defaults)
    return {
        "type": "start",
        "time": t,
        "meta": meta
    }


def parse_stop(timestr):
    t = parse_time(timestr)
    return {
        "type": "stop",
        "time": t
    }


def parse_add(intervalstr, metalist, defaults={}):
    [s, t] = parse_interval(intervalstr)
    meta = parse_meta(metalist, defaults)
    return {
        "type": "add",
        "interval": [s, t],
        "meta": meta
    }


def parse_list(intervalstr):
    [s, t] = parse_interval(intervalstr)
    return {
        "type": "list",
        "interval": [s, t],
    }


def parse_config_property(path, property, value):
    return {
        "type": "config",
        "path": path,
        "property": property,
        "value": value
    }