"""数据库"""

from .impl import *

# 数据库单例, 需要在 platform 中定义此 db 单例
db: Database


def set_db(__db: Database):
    """设置 db, 传入该包下的db接口实现"""
    global db
    db = __db


def get_db():
    """获取数据库单例"""
    return db


def get_api():
    """获取数据库单例的接口"""
    return db.api
