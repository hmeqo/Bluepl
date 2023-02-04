"""事件中心

`EventType` 为事件类型, 此类可以分布在各个模块中, 也可以动态的添加事件
`subscribe` 订阅事件, callback 可以没有参数或带一个event参数 (传入该事件的`Event`实例)
`unsubscribe` 取消订阅
`emit` 发送事件
"""

from __future__ import annotations
from collections import defaultdict as _defaultdict
from enum import Enum as _Enum, EnumMeta as _EnumMeta
import inspect as _inspect
import typing as _t
import atexit as _atexit


class Event(object):

    def __init__(self, args, kwds):
        self.args = args
        self.kwds = kwds

    def __str__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            ", ".join("%s=%r" % (k, v) for k, v in self.__dict__.items())
        )

    __repr__ = __str__


class ExceptionEvent(Event):

    @property
    def exc(self):
        return self.args[0]


class EventTypeWrapper(object):

    def __init__(self, type: _t.Type[Event]):
        self.type = type

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return super().__hash__()


class EventTypeMeta(_EnumMeta):

    def __getattribute__(cls, name) -> EventType:
        return super().__getattribute__(name)

    def __setattr__(cls, name, value):
        super().__setattr__(name, value)

    def __registry__(cls, name, event: _t.Type[Event]):
        """注册一个事件"""
        setattr(cls, name, EventTypeWrapper(event))


class EventType(_Enum, metaclass=EventTypeMeta):
    """Event type"""

    value: EventTypeWrapper

    # On the application start
    START = EventTypeWrapper(Event)
    # On the application close
    CLOSING = EventTypeWrapper(Event)
    CLOSED = EventTypeWrapper(Event)
    EXIT = EventTypeWrapper(Event)

    ERROR = EventTypeWrapper(ExceptionEvent)


class Subscriber(object):
    """订阅者"""

    def __new__(cls, subscriber: ExpectCallable):
        if isinstance(subscriber, Subscriber):
            return subscriber
        return object.__new__(cls)

    def __init__(self, subscriber: ExpectCallable):
        self.func: _t.Callable = subscriber
        try:
            _inspect.getcallargs(subscriber)  # type: ignore
            self.event_flag = False
        except Exception:
            self.event_flag = True

    def __call__(self, event: Event):
        if self.event_flag:
            self.func(event)
        else:
            self.func()

    def __eq__(self, other):
        if isinstance(other, Subscriber):
            return self.func == other.func
        return self.func == other


ExpectCallable = _t.Union[_t.Callable[[Event], _t.Any], _t.Callable[[], _t.Any], Subscriber]
ExpectCallback = _t.TypeVar("ExpectCallback", ExpectCallable, ExpectCallable)

subscribers: _t.DefaultDict[EventType, _t.List[Subscriber]] = _defaultdict(list)


@_t.overload
def subscribe(eventtype: EventType, callback: ExpectCallback) -> None:
    ...


@_t.overload
def subscribe(eventtype: EventType) -> _t.Callable[[ExpectCallback], ExpectCallback]:
    ...


def subscribe(
    eventtype: EventType,
    callback: _t.Optional[ExpectCallback] = None,
) -> _t.Union[_t.Callable[[ExpectCallback], ExpectCallback], None]:
    """订阅一个事件

    Args:
        eventtype (ET): 事件类型
        callback (_t.Optional[ExpectFunc], optional): 回调函数. Defaults to None.

    Returns:
        _t.Union[_t.Callable[[ExpectFunc], ExpectFunc], None]: _description_
    """
    if callback is None:
        def wrapper(callback):
            subscribers[eventtype].append(Subscriber(callback))
            return callback
        return wrapper
    return subscribers[eventtype].append(Subscriber(callback))


def unsubscribe(eventtype, callback: ExpectCallable):
    """取消订阅

    Args:
        eventtype (_type_): 事件类型
        callback (_t.Callable): 回调函数
    """
    try:
        subscribers[eventtype].remove(callback)  # type: ignore
    except ValueError:
        pass


def emit(eventtype: EventType, *args, **kwds):
    """发送事件

    Args:
        eventtype (ET): 事件类型
        *args: Event.args
        **kwds: Event.kwds
    """
    __event = eventtype.value.type(args, kwds)
    for func in subscribers[eventtype]:
        func(__event)
    if eventtype in (
            EventType.START,
            EventType.CLOSING,
            EventType.CLOSED,
            EventType.EXIT):
        del subscribers[eventtype]


@_atexit.register
def emit_exit():
    """发送退出事件 (会在Python退出时自动执行)"""
    emit(EventType.EXIT)


# alias
ev_subscribers = subscribers
ev_subscribe = subscribe
ev_unsubscribe = unsubscribe
ev_emit = emit
