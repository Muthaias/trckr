# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
from trckr import app, cli
from trckr.exceptions import TrckrError
from trckr.cli.utils import CLIParseError


if __name__ == "__main__":
    try:
        args = cli.cli.parse_args(
            sys.argv[1:],
            cli.utils.DEFAULT_CONFIG_PATH
        )
        config = app.load_config(args["config_path"])
        command = cli.cli.args_to_command(config, **args)
        database = app.load_database(config)
        app.exec(
            config,
            database,
            command
        )
    except (CLIParseError, TrckrError) as e:
        print(str(e))
