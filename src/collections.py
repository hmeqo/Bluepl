import time
import typing as _t

from .ahfakit.datautil.objcollection import AutoincObjProperty, Collection, CollectionsIO, Obj, ObjProperty, registry_type
from . import gconfig
from .event import EventType, subscribe
from .ahfakit.simplecrypto import AES

collections = CollectionsIO()


@subscribe(EventType.START)
def db_open():
    collections.open(gconfig.Dirs.data.joinpath("session.db"))


@subscribe(EventType.EXIT)
def db_close():
    collections.close()


class Session(Obj):

    id = ObjProperty("id", str)
    time = ObjProperty("time", int, lambda: int(time.time() * 1000))
    age = ObjProperty("age", int, 1800)
    key = ObjProperty("key", bytes)

    def __init__(self, properties: _t.Optional[_t.Dict[str, _t.Any]] = None, **kwds):
        super().__init__(properties, **kwds)
        self.aes = AES(self.key, AES.modes.ECB())

    def is_available(self):
        """判断是否过期, 如果过期则自动删除, 未过期返回 True"""
        if time.time() - self.time/1000 < self.age:
            return True
        del sessions[self.id]
        return False

    def flash_time(self):
        self.time = int(time.time() * 1000)

    def encrypt_base64(self, b: bytes):
        return self.aes.encrypt(b)

    def decrypt_base64(self, b: bytes):
        return self.aes.decrypt(b)


class User(Obj):

    email = id = ObjProperty("email", str)
    password = ObjProperty("password", str)
    uid = AutoincObjProperty("id")
    name = ObjProperty("name", str, default="")
    solt = ObjProperty("solt", str, "")
    time = ObjProperty("time", int, lambda: int(time.time() * 1000))


class Registry(Obj):

    email = id = ObjProperty("email", str)
    veri_code = ObjProperty("veri_code", str)
    time = ObjProperty("time", int, lambda: int(time.time() * 1000))
    age = ObjProperty("age", int, 180)

    def registry(self, password: str, solt=""):
        """注册该用户"""
        users.create(email=self.email, password=password, solt=solt)

    def is_available(self):
        """判断是否过期, 如果过期则自动删除, 未过期返回 True"""
        if time.time() - self.time/1000 < self.age:
            return True
        del registrys[self.id]
        return False


registry_pool = Collection(Registry)

sessions = collections.get(Session)
users = collections.get(User)
# accounts = collections.get(Account)

registrys = Collection(Registry)

registry_type(Session)
registry_type(User)
# registry_type(Account)
