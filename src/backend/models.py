from .webapp import db
from sqlalchemy import Column, BINARY, INTEGER, DateTime, ForeignKey, CHAR, String


class Session(db.Model):

    __tablename__ = 'session'

    id = db.Column(CHAR(64), primary_key=True)
    aes_key = db.Column(BINARY(512))
    validity = db.Column(DateTime)
    user_uid = db.Column(INTEGER, ForeignKey('user.uid'))


class User(db.Model):

    __tablename__ = 'user'

    uid = db.Column(INTEGER, primary_key=True, autoincrement=True)
    email = db.Column(String(50))
    password = db.Column(String(64))
    solt = db.Column(CHAR(16))
    creation_time = db.Column(DateTime)
    name = db.Column(String(32), default='')
    avatar = db.Column(String(200), default='')


class DataAccount(db.Model):

    __tablename__ = 'data_account'

    id = db.Column(INTEGER, primary_key=True, autoincrement=True)
    user_uid = db.Column(INTEGER, ForeignKey('user.uid'))
    platform = db.Column(String(50), default='')
    account = db.Column(String(50), default='')
    password = db.Column(String(100), default='')
    note = db.Column(String(200), default='')


class RecordRegistry(db.Model):

    __tablename__ = 'record_registry'

    email = db.Column(String(50), primary_key=True)
    veri_code = db.Column(String(16))
    validity = db.Column(DateTime)


class RecordResetPwd(db.Model):

    __tablename__ = 'record_resetpassword'

    email = db.Column(String(50), primary_key=True)
    veri_code = db.Column(String(16))
    validity = db.Column(DateTime)
