"""全局配置"""

from pathlib import Path as _Path
import sys as _sys

from .ahfakit.datamb import datamb as _datamb


class Dirs(object):
    """目录路径"""

    root = _Path(_sys.argv[0]).parent
    webroot = _Path("src/web")
    webassets = _Path("src/web/assets")
    data = _Path("data")


class Files(object):
    """文件路径"""

    icon = Dirs.webroot.joinpath("favicon.ico")
    db = Dirs.data.joinpath("data.db")


class App(object):
    """应用信息"""

    name = "Bluepl"


config = _datamb.ArgMapTree({})
