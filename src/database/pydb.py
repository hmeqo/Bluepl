"""py版本的数据库实现"""

import typing as _t

from ..ahfakit.datautil.recordcollection import RecordCollectionsIO, registry_type
from ..event import EventType, emit, subscribe
from ..gconfig import Files
from .dbapi import *

registry_type(Session)
registry_type(User)
registry_type(Account)
registry_type(datetime)

collections = RecordCollectionsIO()

sessions = collections.get(Session)
users = collections.get(User)
accounts = collections.get(Account)


@subscribe(EventType.INITED)
def db_open():
    collections.open(Files.database)
    emit(EventType.DATABASE_OPENED)


@subscribe(EventType.EXIT)
def db_close():
    collections.close()


class PyDBApi(DBApi):

    @staticmethod
    def login(session: Session, user: User):
        session.user_uid = user.uid
        collections.save()

    @staticmethod
    def logout(session: Session):
        session.user_uid = None
        collections.save()

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
    def get_user(uid: _t.Optional[int] = None, email: _t.Optional[str] = None) -> _t.Union[User, None]:
        if uid is not None:
            return users.get(uid)
        for user in users.values():
            if user.email == email:
                return user
        return None

    @staticmethod
    def create_user(email, password) -> _t.Union[User, None]:
        if PyDBApi.get_user(email=email):
            return None
        user = generate_user(email, password)
        user.name = f"uid{user.uid}"
        users.add(user)
        collections.save()
        return user

    @staticmethod
    def reset_password(email: str, password: str) -> bool:
        user = PyDBApi.get_user(email=email)
        if user is None:
            return False
        new_user = generate_user(email, password, uid=user.uid)
        user.password = new_user.password
        user.solt = new_user.solt
        return True

    @staticmethod
    def update_user_info(user: User, name: _t.Optional[str]) -> bool:
        if name is None:
            return False
        user.name = name
        return True

    @staticmethod
    def get_data_accounts(user):
        return tuple(filter(lambda x: x.user_uid == user.uid, accounts.values()))

    @staticmethod
    def create_data_account(user, platform="", account="", password="", note="") -> Account:
        account = Account(
            user_uid=user.uid,
            platform=platform,
            account=account,
            password=password,
            note=note,
        )
        accounts.add(account)
        collections.save()
        return account

    @staticmethod
    def update_data_account(user, account_dict: dict):
        uid = user.uid
        account = accounts[account_dict["id"]]
        if account.user_uid == uid:
            if "platform" in account_dict:
                account.platform = account_dict["platform"]
            if "account" in account_dict:
                account.account = account_dict["account"]
            if "password" in account_dict:
                account.password = account_dict["password"]
            if "note" in account_dict:
                account.note = account_dict["note"]
            collections.save()

    @staticmethod
    def delete_data_account(user, account_id):
        account = accounts.get(account_id)
        if account and account.user_uid == user.uid:
            del accounts[account_id]
            collections.save()
