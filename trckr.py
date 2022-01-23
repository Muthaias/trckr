# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
from trckr import app


if __name__ == "__main__":
    app.main(
        app.parse_args(
            sys.argv[1:]
        )
    )
