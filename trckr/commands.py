# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

from .exceptions import TrckrError


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
        if command in self._commands:
            args = self._parsers[command](argv)
            return self._commands[command](**args, **kargs)
        else:
            raise TrckrError(f"Command not found: {command}")
