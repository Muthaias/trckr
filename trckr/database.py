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

    def intersection(self, start, stop):
        start = (
            start
            if start is not None and start > self.start
            else self.start
        )
        stop = (
            stop
            if stop is not None and stop < self.stop
            else self.stop
        )
        if start < stop:
            return Entry(
                start=start,
                stop=stop,
                userid=self.userid,
                contextid=self.contextid,
                note=self.note,
                id=self.id
            )
        else:
            return None

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

    def select(
        from_time: datetime = None,
        to_time: datetime = None
    ) -> list[Entry]:
        raise NotImplementedError()

    @property
    def entries(self) -> list[Entry]:
        raise NotImplementedError()


class StructDatabase(DatabaseInterface):
    def __init__(self, rw, userid: str = None, contextid: str = None):
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

    def _entries(self):
        return (
            Entry.from_data(entry)
            for entry
            in self._data["intervals"]
            if (
                self._contextid is None
                or entry["contextid"] == self._contextid
            )
            and (
                self._userid is None
                or entry["userid"] == self._userid
            )
        )

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

    def select(
        self,
        from_time: datetime = None,
        to_time: datetime = None
    ) -> list[Entry]:
        entries = (
            entry.intersection(from_time, to_time)
            for entry in self._entries()
        )
        return [
            entry
            for entry in entries
            if entry is not None
        ]

    @property
    def entries(self) -> list[Entry]:
        return list(self._entries())
