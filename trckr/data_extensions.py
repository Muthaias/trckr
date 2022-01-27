# SPDX-FileCopyrightText: 2022 Mattias Nyberg
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import subprocess
import getpass
from datetime import datetime


def extensions(*exts):
    def _extenstions(data):
        ext_data = {}
        for ext in exts:
            ext_data.update(ext(data))
        return ext_data

    return _extenstions


def config(data):
    config_path = data["_path"]
    config_dir = os.path.dirname(config_path)
    return {
        "CONFIG_DIR": config_dir,
        "CONFIG_PATH": config_path,
    }


def userspace(data):
    return {
        "HOME": os.path.expanduser("~"),
        "USER": getpass.getuser()
    }


def time(data):
    return {
        "NOW": str(datetime.now()),
        "TODAY": str(datetime.today())
    }


def git(data):
    config_dir = os.path.dirname(data["_path"])
    gitdir = data.get(
        "gitdir",
        os.path.join(config_dir, ".git")
    )

    def _git_command(*cmd):
        try:
            cmd_list = ["git", "--git-dir", gitdir, *cmd]
            return subprocess.check_output(cmd_list).decode("utf-8").strip()
        except subprocess.CalledProcessError:
            return None

    return {
        "GITBRANCH": _git_command("branch", "--show-current"),
        "GITHASH": _git_command("rev-parse", "--short", "HEAD"),
        "GITHASHLONG": _git_command("rev-parse", "HEAD"),
        "GITNAME": os.path.basename(
            _git_command("rev-parse", "--show-toplevel")
        )
    }


standard_extensions = extensions(
    config,
    userspace,
    git,
    time,
)
