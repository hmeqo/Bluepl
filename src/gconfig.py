"""全局配置"""

from datetime import datetime
import os as _os
from pathlib import Path as _Path
import sys as _sys

from .ahfakit.apckit.versioninfo import VersionInfo
from .ahfakit.datautil import datamb as _datamb
from .settings import Smtp, Socket


class Dirs(object):
    """目录路径"""

    base = _Path(_sys.argv[0]).parent
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
    template_veri_code = Dirs.templates.joinpath("veri_code.html")
    template_veri_link = Dirs.templates.joinpath("veri_link.html")


class AppConfig(object):
    """应用信息"""

    debug = False
    name = "Bluepl"
    port = 27640


class FlaskConfig(object):

    JSON_AS_ASCII = False
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{Files.database.absolute()}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True


# _sys._MEIPASS = Dirs.base  # type: ignore

gconfig = _datamb.ArgMapTree({})

versioninfo = VersionInfo(0, 0, 4, 0, 'Alpha', date=datetime.now().date())


def init():
    print(Dirs.base)
    for path in (i for i in Dirs.__dict__.values() if isinstance(i, _Path)):
        if path.exists():
            continue
        _os.makedirs(path)
