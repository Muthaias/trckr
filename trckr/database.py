# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Entry:
    start: datetime
    stop: datetime
    contextid: str
    userid: str
    note: str
    id: str

    @staticmethod
    def from_data(data):
        return Entry(
            start=datetime.fromisoformat(data["start"]),
            stop=datetime.fromisoformat(data["stop"]),
            userid=data["userid"],
            contextid=data["contextid"],
            note=data["note"],
            id=data["id"]
        )


class DatabaseInterface:
    def start(self, time: datetime, note: str = None):
        raise NotImplementedError()

    def stop(self, time: datetime):
        raise NotImplementedError()

    def add(self, start: datetime, stop: datetime, note: str = None):
        raise NotImplementedError()

    def commit(self):
        raise NotImplementedError()

    @property
    def entries(self) -> list[Entry]:
        raise NotImplementedError()


class StructDatabase(DatabaseInterface):
    def __init__(self, rw, userid=None, contextid=None):
        self._rw = rw
        self._userid = userid
        self._contextid = contextid
        self._data = self._rw.read(
            {
                "intervals": [],
                "timer": None
            }
        )

    def _generate_id(self):
        return str(uuid.uuid4())

    def _entry(self, start: datetime, stop: datetime = None, note: str = None):
        return {
            "id": self._generate_id(),
            "contextid": self._contextid,
            "userid": self._userid,
            "start": str(start),
            "stop": str(stop),
            "note": note
        }

    def start(self, time: datetime, note: str = None):
        self.stop(time)
        self._data["timer"] = self._entry(time, note=note)

    def stop(self, time: datetime):
        timer = self._data["timer"]
        if timer is not None:
            old_timer = {
                **timer,
                "stop": str(time)
            }
            self._data["timer"] = None
            self._data["intervals"].append(old_timer)

    def add(self, start: datetime, stop: datetime, note: str = None):
        self._data["intervals"].append(
            self._entry(start, stop, note)
        )

    def commit(self):
        self._rw.write(self._data)

    @property
    def entries(self) -> list[Entry]:
        return [
            Entry.from_data(entry)
            for entry
            in self._data["intervals"]
            if entry["contextid"] == self._contextid
            and entry["userid"] == self._userid
            or (self._contextid is None and self._userid is None)
        ]
