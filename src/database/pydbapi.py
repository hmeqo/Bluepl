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
        import hashlib
        import random
        import string

        password = "1234"
        solt = "".join(random.choices(string.hexdigits, k=16))
        password = hashlib.md5((password + solt).encode()).hexdigest()
        PyDBApi.create_user(email="test", password=password, solt=solt)


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
    def get_available_registry(email: str):
        registry = registries.get(email)
        if registry and registry.is_available():
            return registry
        del registries[email]
        return None

    @staticmethod
    def get_user(email: str):
        return users.get(email)

    @staticmethod
    def create_registry(email: str, veri_code: str):
        if email in registries:
            return None
        registries.create(email=email, veri_code=veri_code)
        return None

    @staticmethod
    def create_session(id: str, key: bytes):
        sessions.create(id=id, key=key)
        collections.save()

    @staticmethod
    def create_user(email: str, password: str, solt: str):
        users.create(email=email, password=password, solt=solt)
        collections.save()

    @staticmethod
    def registry_user(registry, password, solt):
        users.create(email=registry.email, password=password, solt=solt)
        collections.save()
        del registries[registry.id]
