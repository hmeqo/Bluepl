"""全局配置"""

import os as _os
from pathlib import Path as _Path
import sys as _sys

from ..ahfakit.datautil import datamb as _datamb
from .config import Smtp, Socket  # type: ignore


class Dirs(object):
    """目录路径"""

    root = _Path(_sys.argv[0]).parent
    webroot = _Path("resources/app")
    webassets = _Path("resources/app/assets")
    data = _Path("data")


class Files(object):
    """文件路径"""

    icon = Dirs.webroot.joinpath("favicon.ico")
    database = Dirs.data.joinpath("bluepl.db")


class App(object):
    """应用信息"""

    name = "Bluepl"
    debug = False
    port = 27640


config = _datamb.ArgMapTree({})


def init():
    for path in (i for i in Dirs.__dict__.values() if isinstance(i, _Path)):
        if path.exists():
            continue
        _os.makedirs(path)
