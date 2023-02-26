import typing as _t

from src.database.dbapi import DBApi, set_dbapi
from .event import EventType, emit
from . import gconfig


def init(dbapi: _t.Type[DBApi]):
    # gconfig.AppCfg.debug = True
    gconfig.init()
    set_dbapi(dbapi)
    emit(EventType.INITED)
