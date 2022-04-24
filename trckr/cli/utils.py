# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import calendar
from datetime import datetime, timedelta
from contextlib import suppress


DEFAULT_CONFIG_PATH = os.environ.get("TRCKR_CONFIG", ".trckr.json")
BASE_TIME = datetime.now()


class CLIParseError(Exception):
    pass


def parse_time(date_input):
    current = BASE_TIME
    if (
        date_input == "-"
        or date_input == "now"
        or date_input is None
        or date_input == ""
    ):
        return current
    else:
        with suppress(UnboundLocalError):
            with suppress(ValueError):
                time = datetime.strptime(date_input, "%H:%M")
                return current.replace(
                    hour=time.hour,
                    minute=time.minute,
                    second=time.second,
                )
            with suppress(ValueError):
                time = datetime.strptime(date_input, "%H:%M:%S")
                return current.replace(
                    hour=time.hour,
                    minute=time.minute,
                    second=time.second,
                )
            with suppress(ValueError):
                time = datetime.strptime(date_input, "%m/%d")
                return current.replace(
                    hour=time.hour,
                    minute=time.minute,
                    second=time.second,
                    day=time.day,
                    month=time.month
                )
    raise CLIParseError(f"Failed to parse date input: {date_input}")


def parse_interval(interval):
    if interval is None or interval == "-":
        return (None, None)

    current = BASE_TIME
    if (
        interval == "today"
        or interval == "day"
    ):
        return (
            current.replace(
                hour=0,
                minute=0,
                second=0
            ),
            current.replace(
                hour=23,
                minute=59,
                second=59
            )
        )
    if interval == "week":
        days = calendar.weekday(current.year, current.month, current.day)
        delta_back = timedelta(days=days)
        delta_forward = timedelta(days=6-days)
        return (
            current.replace(
                hour=0,
                minute=0,
                second=0
            ) - delta_back,
            current.replace(
                hour=23,
                minute=59,
                second=59
            ) + delta_forward
        )
    elif interval == "month":
        (start, end) = calendar.monthrange(current.year, current.month)
        return (
            current.replace(
                day=start,
                hour=0,
                minute=0,
                second=0
            ),
            current.replace(
                day=end,
                hour=23,
                minute=0,
                second=0
            )
        )
    else:
        with suppress(ValueError):
            [a, b] = interval.split("-")
            return (
                parse_time(a),
                parse_time(b)
            )

    raise CLIParseError(f"Unable to parse interval: '{interval}'")


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


def parse_list(intervalstr, list_format="list"):
    [s, t] = parse_interval(intervalstr)
    return {
        "type": "list",
        "format": list_format,
        "interval": [s, t],
    }


def parse_config_property(property, value, path=None):
    return {
        "type": "config",
        "property": property,
        "value": value,
        **(
            {}
            if path is None
            else {"path": path}
        )
    }
