import typing as _t

from .event import EventType, emit
from . import gconfig


def init():
    # gconfig.AppConfig.debug = True
    gconfig.init()
    emit(EventType.INITED)
