import typing as _t

from src.database.dbapi import DBApi, set_dbapi
from .event import EventType, emit
from . import gconfig


def init(dbapi: _t.Type[DBApi]):
    set_dbapi(dbapi)
    gconfig.init()
    emit(EventType.INITED)
