# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import json


class JsonFileRW:
    def __init__(self, path):
        self._path = path

    def read(self, default=None):
        try:
            with open(self._path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return default

    def write(self, data):
        serialized = json.dumps(data, indent=4, sort_keys=True)
        with open(self._path, "w") as f:
            f.write(serialized)
