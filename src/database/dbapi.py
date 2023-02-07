from __future__ import annotations
import time
import typing as _t

from ..ahfakit.datautil.recordcollection import AutoincProperty, RecordProperty, Record
from ..ahfakit.simplecrypto.aes import AES

api: _t.Type[DBApi]


def set_dbapi(__api: _t.Type[DBApi]):
    global api
    api = __api


def get_dbapi():
    return api


class DBApi(object):

    @staticmethod
    def get_available_session(session_id: str) -> Session:
        raise NotImplementedError

    @staticmethod
    def get_available_registry(email: str) -> Registry:
        raise NotImplementedError

    @staticmethod
    def get_user(email: str) -> User:
        raise NotImplementedError

    @staticmethod
    def create_registry(email: str, veri_code: str) -> None:
        raise NotImplementedError

    @staticmethod
    def create_session(id: str, key: bytes) -> None:
        raise NotImplementedError

    @staticmethod
    def create_user(email: str, password: str, solt: str) -> None:
        raise NotImplementedError

    @staticmethod
    def registry_user(registry: Registry, password: str, solt: str) -> None:
        raise NotImplementedError


class Session(Record):

    id = RecordProperty("id", str)
    time = RecordProperty("time", int, lambda: int(time.time() * 1000))
    age = RecordProperty("age", int, 1800)
    key = RecordProperty("key", bytes)
    user_email = RecordProperty("user", str, "")

    def __init__(self, properties: _t.Optional[_t.Dict[str, _t.Any]] = None, **kwds):
        super().__init__(properties, **kwds)
        self.aes = AES(self.key, AES.modes.ECB())

    def is_available(self):
        return time_not_expired(self.time, self.age)

    def encrypt(self, b: bytes):
        return self.aes.encrypt(b)

    def decrypt(self, b: bytes):
        return self.aes.decrypt(b)


class User(Record):

    email = id = RecordProperty("email", str)
    password = RecordProperty("password", str)
    uid = AutoincProperty("uid")
    name = RecordProperty("name", str, default="")
    solt = RecordProperty("solt", str, "")
    time = RecordProperty("time", int, lambda: int(time.time() * 1000))


class Account(Record):

    id = AutoincProperty("id")
    uid = RecordProperty("uid", int)
    platform = RecordProperty("platform", str, "")
    account = RecordProperty("platform", str, "")
    password = RecordProperty("password", str, "")
    note = RecordProperty("note", str, "")


class Registry(Record):

    email = id = RecordProperty("email", str)
    veri_code = RecordProperty("veri_code", str)
    time = RecordProperty("time", int, lambda: int(time.time() * 1000))
    age = RecordProperty("age", int, 180)

    def is_available(self):
        return time_not_expired(self.time, self.age)


def time_not_expired(time_: int, age: int) -> bool:
    """
    Args:
        t (int): time ms
        age (int): age seconds
    """
    if time.time() - time_/1000 < age:
        return True
    return False
