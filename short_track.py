# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import os
import json
from trckr import app, short, utils
from trckr.exceptions import TrckrError


CONFIG_PATH = os.environ.get("TRCKR_CONFIG", ".trckr.json")


if __name__ == "__main__":
    try:
        config = app.load_config(CONFIG_PATH)
        database = app.load_database(config)
        command = short.parse_args(sys.argv[1:])
        app.exec(
            config,
            database,
            command
        )
    except TrckrError as e:
        print(str(e))
