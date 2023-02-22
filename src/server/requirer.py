import json
import hashlib
import traceback
import typing as _t

from flask import Response, request

from ..ahfakit.datautil.form import DictForm, Field, Form
from ..database.dbapi import Session, User
from ..database import get_dbapi
from .app import app
from .status import *

current_session: _t.Union[Session, None] = None

current_user: _t.Union[User, None] = None


def get_session():
    """获取 current session, 只能在 `require_aes_parser` 之后调用"""
    if current_session is None:
        raise ValueError(current_session)
    return current_session


def set_session(session: Session):
    global current_session
    current_session = session


def get_user():
    """获取 current user, 只能在 `require_login` 之后调用"""
    if current_user is None:
        raise ValueError(current_user)
    return current_user


def set_user(user: User):
    global current_user
    current_user = user


def require_json_data(form: Form):
    """装饰器, 获取并验证dict, 返回无误的dict或错误response"""
    def get_func(func: _t.Callable[[_t.Any], dict]):
        def wrapper(data: _t.Union[dict, list, None] = None):
            data = request.get_json() if data is None else data
            if data is None or not isinstance(data, (dict, list)):
                return S_PARAM_ERROR
            try:
                d = form.parse(data)
            except ValueError:
                return S_PARAM_ERROR
            return func(d)
        wrapper.__name__ = func.__name__
        return wrapper
    return get_func


def require_aes_parser(func: _t.Callable[[_t.Any], _t.Union[dict, Response]]):
    """装饰器, 解析aes会话获取数据, 返回值为 Response"""
    def wrapper() -> Response:
        veri_result = veri_session()

        data = veri_result["data"]
        if veri_result["error"]:
            response = app.make_response(data)
            # response.data = session.encrypt(response.data)
            return response
        session = get_session()

        response = func(data)
        if not isinstance(response, Response):
            response = app.make_response(response)
        response.data = session.encrypt(response.data)
        return response
    wrapper.__name__ = func.__name__
    return wrapper


def require_login(func: _t.Callable[[_t.Any], _t.Union[dict, Response]]):
    """装饰器, 解析aes并判断登录状态"""
    def wrapper(data: _t.Any):
        dbapi = get_dbapi()
        session = get_session()
        uid = session.user_uid
        if uid is None:
            return S_NOT_LOGIN
        user = dbapi.get_user(uid=uid)
        if not user:
            return S_NOT_LOGIN
        set_user(user)
        return func(data)
    wrapper.__name__ = func.__name__
    return require_aes_parser(wrapper)


def require_ensure_response(func: _t.Callable[..., _t.Union[Response, dict]]):
    """装饰器, 确保返回值为 Response"""
    def wrapper(*args, **kwargs) -> Response:
        response = func(*args, **kwargs)
        if isinstance(response, Response):
            return response
        return app.make_response(response)
    wrapper.__name__ = func.__name__
    return wrapper


@require_json_data(DictForm({
    "sessionId": Field(str),
    "digest": Field(str),
    "data": Field(str)
}))
def veri_session(json_data: _t.Dict[str, _t.Any]):
    """验证session"""
    # 获取session并判断session是否正常
    session_id = json_data["sessionId"]
    digest = json_data["digest"]
    session = get_dbapi().get_available_session(session_id)
    if not session:
        return {"error": True, "data": {**S_SESSION_ERROR, "expired": True}}
    set_session(session)
    # 验证摘要
    data: bytes = json_data["data"].encode()
    if digest != hashlib.sha256(session.key + data).hexdigest():
        return {"error": True, "data": S_SESSION_ERROR}
    try:
        decrypted = session.decrypt(data)
        result = json.loads(decrypted)
    except Exception:
        traceback.print_exc()
        return {"error": True, "data": S_SESSION_ERROR}
    else:
        return {"error": False, "data": result}
