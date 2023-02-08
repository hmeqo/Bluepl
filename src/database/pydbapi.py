"""py版本的数据库实现"""

from ..ahfakit.datautil.recordcollection import RecordCollectionsIO, RecordCollection, registry_type
from ..event import EventType, subscribe
from .. import gconfig
from .dbapi import *

registry_type(Session)
registry_type(User)
registry_type(Account)

collections = RecordCollectionsIO()

sessions = collections.get(Session)
users = collections.get(User)
accounts = collections.get(Account)
registries = RecordCollection(Registry)


@subscribe(EventType.START)
def db_open():
    collections.open(gconfig.Dirs.data.joinpath("session.db"))

    if "test" not in users:
        user = PyDBApi.generate_user("test", "1234")
        PyDBApi.add_user(user)
        PyDBApi.add_data_account(user, "QQ", "1875557990", "1234", "我的QQ账号")
        PyDBApi.add_data_account(user, "微信", "15859262656", "5678", "我的微信账号")


@subscribe(EventType.EXIT)
def db_close():
    collections.close()


class PyDBApi(DBApi):

    @staticmethod
    def get_available_session(session_id: str):
        session = sessions.get(session_id)
        if session:
            if session.is_available():
                return session
            del sessions[session_id]
        return None

    @staticmethod
    def create_session(id: str, key: bytes):
        sessions.create(id=id, key=key)
        collections.save()

    @staticmethod
    def get_available_registry(email: str):
        registry = registries.get(email)
        if registry:
            if registry.is_available():
                return registry
            del registries[email]
        return None

    @staticmethod
    def create_registry(email: str, veri_code: str):
        if email not in registries:
            registries.create(email=email, veri_code=veri_code)

    @staticmethod
    def delete_registry(email: str):
        del registries[email]

    @staticmethod
    def get_user(email: str):
        for user in users.values():
            if user.email == email:
                return user
        return None

    @staticmethod
    def add_user(user: User):
        users.add(user)
        collections.save()

    @staticmethod
    def get_data_accounts(user: User):
        return tuple(filter(lambda x: x.uid == user.uid, accounts.values()))

    @staticmethod
    def add_data_account(
        user: User,
        platform="",
        account="",
        password="",
        note="",
    ) -> None:
        accounts.create(
            uid=user.uid,
            platform=platform,
            account=account,
            password=password,
            note=note
        )
