"""py版本的数据库实现"""

import typing as _t

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


def init():
    set_dbapi(PyDBApi)


@subscribe(EventType.START)
def db_open():
    collections.open(gconfig.Dirs.data.joinpath("session.db"))
    # 添加测试账号
    user = PyDBApi.create_user("test", "267763")
    if not user:
        return None
    PyDBApi.create_data_account(
        user, "QQ", "1875557990", "MyQQPassword", "我的QQ账号")
    PyDBApi.create_data_account(
        user, "微信", "15859262656", "12345678", "我的微信账号")
    return None


@subscribe(EventType.EXIT)
def db_close():
    collections.close()


class PyDBApi(DBApi):

    @staticmethod
    def get_available_session(session_id):
        session = sessions.get(session_id)
        if session:
            if session.is_available():
                return session
            del sessions[session_id]
        return None

    @staticmethod
    def create_session(id, key):
        sessions.create(id=id, key=key)
        collections.save()

    @staticmethod
    def get_available_registry(email):
        registry = registries.get(email)
        if registry:
            if registry.is_available():
                return registry
            del registries[email]
        return None

    @staticmethod
    def create_registry(email, veri_code) -> _t.Union[Registry, None]:
        if email not in registries:
            registry = Registry(email=email, veri_code=veri_code)
            registries.add(registry)
            return registry
        return None

    @staticmethod
    def delete_registry(email):
        del registries[email]

    @staticmethod
    def get_user(email):
        for user in users.values():
            if user.email == email:
                return user
        return None

    @staticmethod
    def create_user(email, password) -> _t.Union[User, None]:
        if PyDBApi.get_user(email):
            return None
        user = generate_user(email, password)
        users.add(user)
        collections.save()
        return user

    @staticmethod
    def get_data_accounts(user):
        return tuple(filter(lambda x: x.uid == user.uid, accounts.values()))

    @staticmethod
    def create_data_account(user, platform="", account="", password="", note="") -> Account:
        account = Account(
            uid=user.uid,
            platform=platform,
            account=account,
            password=password,
            note=note,
        )
        accounts.add(account)
        collections.save()
        return account

    @staticmethod
    def update_data_accounts(user, account_list):
        uid = user.uid
        for account_params in account_list:
            account = accounts[account_params["id"]]
            if account.uid != uid:
                continue
            account.platform = account_params.get("platform")
            account.account = account_params.get("account")
            account.password = account_params.get("password")
            account.note = account_params.get("note")
        collections.save()

    @staticmethod
    def delete_data_accounts(user, account_ids):
        for account_id in account_ids:
            account = accounts.get(account_id)
            if account and account.uid == user.uid:
                del accounts[account_id]
        collections.save()
