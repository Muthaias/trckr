# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid
from datetime import datetime
from dataclasses import dataclass, asdict
from collections import ChainMap
from .exceptions import TrckrError


@dataclass
class Meta:
    userid: str
    contextid: str
    note: str

    @staticmethod
    def from_data(data):
        return Meta(
            userid=data["userid"],
            contextid=data["contextid"],
            note=data["note"],
        )


@dataclass
class Entry:
    start: datetime
    stop: datetime
    meta: Meta
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
                meta=self.meta,
                id=self.id
            )
        else:
            return None

    @staticmethod
    def from_data(data):
        return Entry(
            start=datetime.fromisoformat(data["start"]),
            stop=datetime.fromisoformat(data["stop"]),
            meta=Meta.from_data(data["meta"]),
            id=data["id"]
        )


class DatabaseInterface:
    def start(self, time: datetime, meta: Meta = None):
        raise NotImplementedError()

    def stop(self, time: datetime):
        raise NotImplementedError()

    def add(self, start: datetime, stop: datetime, meta: Meta = None):
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
    def __init__(self, rw):
        self._rw = rw
        self._data = ChainMap(
            self._rw.read({}),
            {
                "entries": [],
                "timer": None
            },
        )

    def _generate_id(self):
        return str(uuid.uuid4())

    def _entry(
        self,
        start: datetime,
        stop: datetime = None,
        meta: Meta = None
    ):
        return {
            "id": self._generate_id(),
            "start": str(start),
            "stop": str(stop),
            "meta": asdict(meta)
        }

    def _entries(self):
        return (
            Entry.from_data(entry)
            for entry
            in self._data["entries"]
        )

    def _stop(self, time: datetime):
        timer = self._data["timer"]
        if timer is not None:
            old_timer = {
                **timer,
                "stop": str(time)
            }
            self._data["timer"] = None
            self._data["entries"].append(old_timer)

    def start(self, time: datetime, meta: Meta = None):
        self._stop(time)
        self._data["timer"] = self._entry(time, meta=meta)

    def stop(self, time: datetime):
        timer = self._data["timer"]
        if timer is not None:
            self._stop(time)
        else:
            raise TrckrError("No existing timer to stop.")

    def add(self, start: datetime, stop: datetime, meta: Meta = None):
        self._data["entries"].append(
            self._entry(start, stop, meta)
        )

    def commit(self):
        self._rw.write(dict(self._data))

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
