# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

class Commands:
    def __init__(self):
        self._commands = {}
        self._parsers = {}

    def alias(self, alias, parser):
        def _alias(func):
            self._commands[alias] = func
            self._parsers[alias] = parser

            return func
        return _alias

    @property
    def commands(self):
        return self._commands.keys()

    def exec(self, command, argv, **kargs):
        args = self._parsers[command](argv)
        return self._commands[command](**args, **kargs)
