"""
数据库相关的接口
实现在另外的文件
"""

from __future__ import annotations
import datetime
import typing as _t

from ..event import EventType, subscribe
from ..ahfakit.datautil.recordcollection import NONE_TYPE, AutoincProperty, RecordProperty, Record, RecordCollection
from ..ahfakit.simplecrypto.aes import AES

api: _t.Type[DBApi] = None  # type: ignore


def set_dbapi(__api: _t.Type[DBApi]):
    global api
    api = __api


def get_dbapi():
    return api


@subscribe(EventType.DATABASE_OPENED)
def on_db_opened():
    user = api.create_user("test", "267763")
    if user:
        api.create_data_account(
            user, "QQ", "MyQQAccount", "MyQQPassword", "我的QQ账号"
        )
        api.create_data_account(
            user, "微信", "13344455667", "12345678", "我的微信账号"
        )


class DBApi(object):

    @staticmethod
    def login(session: Session, user: User):
        """登录"""
        raise NotImplementedError

    @staticmethod
    def logout(session: Session):
        """退出登录"""
        raise NotImplementedError

    @staticmethod
    def get_available_session(session_id: str) -> _t.Union[Session, None]:
        """获取一个有效的 session"""
        raise NotImplementedError

    @staticmethod
    def create_session(id: str, key: bytes) -> None:
        """创建一个 session"""
        raise NotImplementedError

    @staticmethod
    def get_user(uid: _t.Optional[int] = None, email: _t.Optional[str] = None) -> _t.Union[User, None]:
        """获取一个用户"""
        raise NotImplementedError

    @staticmethod
    def create_user(email: str, password: str) -> _t.Union[User, None]:
        """创建一个用户, 如果用户已存在返回 None"""
        raise NotImplementedError

    @staticmethod
    def reset_password(email: str, password: str) -> bool:
        """重置密码"""
        raise NotImplementedError

    @staticmethod
    def update_user_info(user: User, name: str) -> bool:
        """修改用户信息"""
        raise NotImplementedError

    @staticmethod
    def get_data_accounts(user: User) -> _t.Tuple[Account, ...]:
        """获取某个用户的 account 数据"""
        raise NotImplementedError

    @staticmethod
    def create_data_account(user: User, platform="", account="", password="", note="") -> Account:
        """创建 account 数据, 返回 account_id"""
        raise NotImplementedError

    @staticmethod
    def update_data_account(user: User, account_dict: dict):
        """更新 account 数据"""
        raise NotImplementedError

    @staticmethod
    def delete_data_account(user: User, account_id: int):
        """删除 account 数据"""
        raise NotImplementedError

    @staticmethod
    def get_available_registry(email: str):
        """获取有效的 registry"""
        registry = registries.get(email)
        if registry:
            if registry.is_available():
                return registry
            del registries[email]
        return None

    @staticmethod
    def create_registry(email: str, veri_code: str) -> _t.Union[Registry, None]:
        """创建一个 registry"""
        if email not in registries:
            registry = Registry(email=email, veri_code=veri_code)
            registries.add(registry)
            return registry
        return None

    @staticmethod
    def delete_registry(email: str):
        """删除一个 registry"""
        del registries[email]

    @staticmethod
    def get_available_resetrecord(email: str) -> _t.Union[ResetRecord, None]:
        """获取有效的 resetrecord"""
        resetrecord = resetrecords.get(email)
        if resetrecord:
            if resetrecord.is_available():
                return resetrecord
            del registries[email]
        return None

    @staticmethod
    def create_resetrecord(email: str, veri_code: str) -> _t.Union[ResetRecord, None]:
        """创建一个 resetrecord"""
        if email not in resetrecords:
            resetrecord = ResetRecord(email=email, veri_code=veri_code)
            resetrecords.add(resetrecord)
            return resetrecord
        return None

    @staticmethod
    def delete_resetrecord(email: str):
        """删除一个 resetrecord"""
        del resetrecords[email]


class Session(Record):

    id = RecordProperty("id", str)
    time = RecordProperty("time", datetime.datetime, lambda: datetime.datetime.now())
    age = RecordProperty("age", int, 1800)
    key = RecordProperty("key", bytes)
    user_uid = RecordProperty("user_uid", (int, NONE_TYPE))

    def __init__(self, properties: _t.Optional[_t.Dict[str, _t.Any]] = None, **kwds):
        super().__init__(properties, **kwds)
        self.aes = AES(self.key, AES.modes.CBC(b"0102030405060708"))

    def is_available(self):
        return time_not_expired(self.time, self.age)

    def encrypt(self, b: bytes):
        return self.aes.encrypt(b)

    def decrypt(self, b: bytes):
        return self.aes.decrypt(b)


class User(Record):

    uid = id = AutoincProperty("uid")
    email = RecordProperty("email", str)
    password = RecordProperty("password", str)
    name = RecordProperty("name", str, default="")
    solt = RecordProperty("solt", str, "")
    time = RecordProperty("time", datetime.datetime, lambda: datetime.datetime.now())
    avatar = RecordProperty("avatar", str, "")


class Account(Record):

    id = AutoincProperty("id")
    user_uid = RecordProperty("user_uid", int)
    platform = RecordProperty("platform", str, "")
    account = RecordProperty("account", str, "")
    password = RecordProperty("password", str, "")
    note = RecordProperty("note", str, "")


class Registry(Record):

    email = id = RecordProperty("email", str)
    veri_code = RecordProperty("veri_code", str)
    time = RecordProperty("time", datetime.datetime, lambda: datetime.datetime.now())
    age = RecordProperty("age", int, 180)

    def is_available(self):
        return time_not_expired(self.time, self.age)


class ResetRecord(Registry):
    pass


def time_not_expired(time_: datetime.datetime, age: int) -> bool:
    """
    Args:
        t (int): time ms
        age (int): age seconds
    """
    if (datetime.datetime.now() - time_).seconds < age:
        return True
    return False


def generate_user(email: str, password: str, uid: _t.Optional[int] = None) -> User:
    """生成一个用户实例"""
    import random
    import string
    import hashlib

    solt = "".join(random.choices(string.hexdigits, k=16))
    password = hashlib.md5((password + solt).encode()).hexdigest()
    return User(uid=uid, email=email, password=password, solt=solt)


registries = RecordCollection(Registry)
resetrecords = RecordCollection(ResetRecord)
