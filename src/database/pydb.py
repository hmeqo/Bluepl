from .impl import Database
from src.ahfakit.datamb import pysqldb
from src.database import get_api
from src.event import EventType, subscribe, unsubscribe
from src import gconfig


@subscribe(EventType.START)
def _open():
    db: pysqldb.Database = get_api()
    db.open(gconfig.Files.db)
    # 判断数据表是否存在
    if "user" not in db.tables:
        db.tables.user = pysqldb.Table(
            id=pysqldb.Field(int, unique=True, autoincrement=True),
            email=pysqldb.Field(str, nullable=False, unique=True),
            password=pysqldb.Field(str, nullable=False),
        )
        db.tables.user.check_constrains.append("4 <= len(password) <= 16")
    if "account" not in db.tables:
        db.tables.account = pysqldb.Table(
            id=pysqldb.Field(int, unique=True, autoincrement=True),
            userId=pysqldb.Field(int, nullable=False, unique=True),
            platform=pysqldb.Field(str),
            account=pysqldb.Field(str),
            password=pysqldb.Field(str),
            note=pysqldb.Field(str),
        )
    if "session" not in db.tables:
        db.tables.session = pysqldb.Table(
            id=pysqldb.Field(int, nullable=False, unique=True),
            userId=pysqldb.Field(int, nullable=False, unique=True),
            key=pysqldb.Field(str, nullable=False),
            age=pysqldb.Field(int, nullable=False)
        )
        db.tables.session.check_constrains.append("0 < age <= 86400")
    unsubscribe(EventType.START, _open)


@subscribe(EventType.CLOSED)
def _close():
    db: pysqldb.Database = get_api()
    db.close()
    unsubscribe(EventType.CLOSED, _close)


def on_error(exc):
    print(exc)


def create_db():
    """获取Py版本的数据库api"""
    db = pysqldb.Database()
    db.on_error = on_error
    return PyDatabase(db)


class PyDatabase(Database):
    """Py版本的数据库接口"""
    pass
