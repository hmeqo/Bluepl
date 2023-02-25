"""全局配置"""

import os as _os
from pathlib import Path as _Path
import sys as _sys

from ..ahfakit.apckit.versioninfo import VersionInfo
from ..ahfakit.datautil import datamb as _datamb
from .config import Smtp, Socket  # type: ignore


class Dirs(object):
    """目录路径"""

    root = _Path(_sys.argv[0]).parent
    data = _Path("data")
    resources = _Path("resources")
    webroot = resources.joinpath("app")
    webassets = webroot.joinpath("assets")
    templates = resources.joinpath("templates")


class Files(object):
    """文件路径"""

    pidlock = Dirs.data.joinpath("lock.pid")
    icon = Dirs.webroot.joinpath("favicon.ico")
    database = Dirs.data.joinpath("bluepl.db")


class App(object):
    """应用信息"""

    name = "Bluepl"
    debug = False
    port = 27640


config = _datamb.ArgMapTree({})

versioninfo = VersionInfo(0, 0, 1, "dev", 0)


def init():
    for path in (i for i in Dirs.__dict__.values() if isinstance(i, _Path)):
        if path.exists():
            continue
        _os.makedirs(path)
