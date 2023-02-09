"""
数据库, 内置多种数据库实现, 应按照 `.dbapi.py` 中所规定的接口配置数据库接口
需要调用数据库实现模块中 `init` 函数初始化数据
使用 set_dbapi 设置数据库接口
使用 get_dbapi 获取数据库接口
"""

from .dbapi import set_dbapi, get_dbapi
