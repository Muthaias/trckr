# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import os
import json
from trckr import app, cli, utils
from trckr.exceptions import TrckrError
from trckr.cli.utils import CLIParseError


if __name__ == "__main__":
    try:
        config = app.load_config(cli.utils.DEFAULT_CONFIG_PATH)
        database = app.load_database(config)
        command = cli.short.parse_args(sys.argv[1:])
        app.exec(
            config,
            database,
            command
        )
    except (CLIParseError, TrckrError) as e:
        print(str(e))
