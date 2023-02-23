import sqlite3
import typing as _t

from ..ahfakit.apckit.taskrunner import TaskRunner
from .. import gconfig
from ..event import EventType, subscribe
from .dbapi import *

connection: sqlite3.Connection = None  # type: ignore
cursor: sqlite3.Cursor = None  # type: ignore

tr = TaskRunner()
tr.start()


def init():
    set_dbapi(SqliteDBApi)


@subscribe(EventType.START)
@tr.proxy()
def db_open():
    global connection, cursor
    connection = sqlite3.connect(gconfig.Files.database)
    cursor = connection.cursor()
    cursor.execute("""
CREATE TABLE if not exists Session (
    Id      varchar(64)  PRIMARY KEY NOT NULL UNIQUE,
    Time    datetime     NOT NULL DEFAULT (datetime('now', 'localtime')),
    Age     int          NOT NULL DEFAULT 1800,
    Key     varchar(512) NOT NULL,
    UserUid INTEGER
)""")
    cursor.execute("""
CREATE TABLE if not exists User (
    Uid      INTEGER       PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    Email    nvarchar(50)  NOT NULL DEFAULT '',
    Password varchar(64)   NOT NULL DEFAULT '',
    Name     nvarchar(32)  NOT NULL DEFAULT '',
    Solt     char(16)      NOT NULL,
    Time     datetime      NOT NULL DEFAULT (datetime('now', 'localtime')),
    Avatar   nvarchar(200) NOT NULL DEFAULT ''
)""")
    cursor.execute("""
CREATE TABLE if not exists Account (
    Id       INTEGER       PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    UserUid  INTEGER       NOT NULL,
    Platform nvarchar(50)  NOT NULL DEFAULT '',
    Account  nvarchar(50)  NOT NULL DEFAULT '',
    Password nvarchar(100) NOT NULL DEFAULT '',
    Note     nvarchar(200) NOT NULL DEFAULT ''
)""")
    user = _SqliteDBApi.create_user("test", "267763")
    if user:
        _SqliteDBApi.create_data_account(
            user, "QQ", "MyQQAccount", "MyQQPassword", "我的QQ账号"
        )
        _SqliteDBApi.create_data_account(
            user, "微信", "13344455667", "12345678", "我的微信账号"
        )


@subscribe(EventType.EXIT)
@tr.proxy()
def db_close():
    connection.commit()
    connection.close()


class _SqliteDBApi(DBApi):

    @staticmethod
    def login(session: Session, user: User):
        cursor.execute(
            f"UPDATE Session SET UserUid={user.uid} WHERE Id='{session.id}'")
        connection.commit()

    @staticmethod
    def logout(session: Session):
        cursor.execute(
            f"UPDATE Session SET UserUid=null WHERE Id='{session.id}'")
        connection.commit()

    @staticmethod
    def get_available_session(session_id: str) -> _t.Union[Session, None]:
        cursor.execute(f"SELECT * FROM Session WHERE id='{session_id}'")
        session = cursor.fetchone()
        if session:
            session = Session(
                id=session[0],
                time=str2datetime(session[1]),
                age=session[2],
                key=session[3].encode(),
                user_uid=session[4],
            )
            if session.is_available():
                return session
            cursor.execute(f"DELETE FROM Session WHERE id='{session_id}'")
            connection.commit()
        return None

    @staticmethod
    def create_session(id: str, key: bytes) -> None:
        time = datetime2str(datetime.datetime.now())
        cursor.execute(
            f"INSERT INTO Session (id, Time, key) VALUES ('{id}', '{time}', '{key.decode()}')")
        connection.commit()

    @staticmethod
    def get_user(uid: _t.Optional[int] = None, email: _t.Optional[str] = None) -> _t.Union[User, None]:
        condition = f"Uid='{uid}'" if email is None else f"Email='{email}'"
        cursor.execute("SELECT * FROM User WHERE " + condition)
        user = cursor.fetchone()
        if user is None:
            return None
        return User(
            uid=user[0],
            email=user[1],
            password=user[2],
            name=user[3],
            solt=user[4],
            time=str2datetime(user[5]),
            avatar=user[6],
        )

    @staticmethod
    def create_user(email: str, password: str) -> _t.Union[User, None]:
        if _SqliteDBApi.get_user(email=email) is not None:
            return None
        user = generate_user(email, password)
        email = user.email
        password = user.password
        solt = user.solt
        time = datetime2str(user.time)
        cursor.execute(
            f"INSERT INTO User (Email, Password, Solt, Time) VALUES ('{email}', '{password}', '{solt}', '{time}')")
        connection.commit()
        return user

    @staticmethod
    def reset_password(email: str, password: str) -> bool:
        new_user = generate_user(email, password)
        cursor.execute(
            f"UPDATE User SET Password='{new_user.password}', Solt='{new_user.solt}' WHERE Email='{email}'")
        if cursor.rowcount == 0:
            return False
        connection.commit()
        return True

    @staticmethod
    def update_user_info(user: User, name: _t.Optional[str]) -> bool:
        if name is None:
            return False
        cursor.execute(f"UPDATE User SET Name='{name}' WHERE Uid={user.uid}")
        return cursor.rowcount == 1

    @staticmethod
    def get_data_accounts(user: User) -> _t.Tuple[Account, ...]:
        cursor.execute(
            f"SELECT * FROM Account WHERE Account.UserUid={user.uid}")
        return tuple(Account(
            id=i[0],
            user_uid=i[1],
            platform=i[2],
            account=i[3],
            password=i[4],
            note=i[5]
        ) for i in cursor.fetchall())

    @staticmethod
    def create_data_account(user: User, platform="", account="", password="", note="") -> Account:
        uid = user.uid
        cursor.execute(
            f"INSERT INTO Account (UserUid, Platform, Account, Password, Note) VALUES ('{uid}', '{platform}', '{account}', '{password}', '{note}')")
        connection.commit()
        account = Account(
            user_uid=uid,
            platform=platform,
            account=account,
            password=password,
            note=note,
        )
        cursor.execute(
            f"SELECT Id FROM Account WHERE UserUid={uid} ORDER BY Id DESC LIMIT 1")
        account.id = cursor.fetchone()[0]
        return account

    @staticmethod
    def update_data_accounts(user: User, account_list: _t.Iterable[dict]):
        uid = user.uid
        for account_params in account_list:
            id = account_params.get("id")
            if id is None:
                continue
            sets = []
            if "platform" in account_params:
                sets.append(f"Platform='{account_params['platform']}'")
            if "account" in account_params:
                sets.append(f"Account='{account_params['account']}'")
            if "password" in account_params:
                sets.append(f"Password='{account_params['password']}'")
            if "note" in account_params:
                sets.append(f"Note='{account_params['note']}'")
            if not sets:
                continue
            cursor.execute(
                f"UPDATE Account SET {', '.join(sets)} WHERE id={id} AND UserUid={uid}")
        connection.commit()

    @staticmethod
    def delete_data_accounts(user: User, account_ids: _t.Iterable[int]):
        for account_id in account_ids:
            cursor.execute(
                f"DELETE FROM Account WHERE Id={account_id} AND UserUid={user.uid}")
        connection.commit()


class SqliteDBApi(_SqliteDBApi):

    @staticmethod
    @tr.proxy()
    def login(session: Session, user: User):
        return _SqliteDBApi.login(session, user)

    @staticmethod
    @tr.proxy()
    def logout(session: Session):
        return _SqliteDBApi.logout(session)

    @staticmethod
    @tr.proxy()
    def get_available_session(session_id: str) -> _t.Union[Session, None]:
        return _SqliteDBApi.get_available_session(session_id)

    @staticmethod
    @tr.proxy()
    def create_session(id: str, key: bytes) -> None:
        return _SqliteDBApi.create_session(id, key)

    @staticmethod
    @tr.proxy()
    def get_user(uid: _t.Optional[int] = None, email: _t.Optional[str] = None) -> _t.Union[User, None]:
        return _SqliteDBApi.get_user(uid, email)

    @staticmethod
    @tr.proxy()
    def create_user(email: str, password: str) -> _t.Union[User, None]:
        return _SqliteDBApi.create_user(email, password)

    @staticmethod
    @tr.proxy()
    def reset_password(email: str, password: str) -> bool:
        return _SqliteDBApi.reset_password(email, password)

    @staticmethod
    @tr.proxy()
    def update_user_info(user: User, name: _t.Optional[str]) -> bool:
        return _SqliteDBApi.update_user_info(user, name)

    @staticmethod
    @tr.proxy()
    def get_data_accounts(user: User) -> _t.Tuple[Account, ...]:
        return _SqliteDBApi.get_data_accounts(user)

    @staticmethod
    @tr.proxy()
    def create_data_account(user: User, platform="", account="", password="", note="") -> Account:
        return _SqliteDBApi.create_data_account(user, platform, account, password, note)

    @staticmethod
    @tr.proxy()
    def update_data_accounts(user: User, account_list: _t.Iterable[dict]):
        return _SqliteDBApi.update_data_accounts(user, account_list)

    @staticmethod
    @tr.proxy()
    def delete_data_accounts(user: User, account_ids: _t.Iterable[int]):
        return _SqliteDBApi.delete_data_accounts(user, account_ids)


def str2datetime(s: str):
    return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def datetime2str(dt: datetime.datetime):
    return dt.strftime("%Y-%m-%d %H:%M:%S")
