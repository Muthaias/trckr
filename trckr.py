# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import json
from trckr import app, cli, utils


if __name__ == "__main__":
    args = cli.parse_args(sys.argv[1:])
    config = app.load_config(args["config_path"])
    database = app.load_database(config)
    app.main(
        config=config,
        database=database,
        **args
    )
