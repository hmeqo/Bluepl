import json
import hashlib
import traceback
import typing as _t

from flask import Response, request

from ..ahfakit.datautil.form import DictForm, Field, Form
from .webapp import app
from .status import *
from .models import Session, User
from .aes import decrypt, encrypt


class Requirement(object):

    _session: _t.Union[Session, None] = None
    _user: _t.Union[User, None] = None

    @property
    def session(self):
        if self._session is None:
            raise AttributeError
        return self._session

    @session.setter
    def session(self, value: Session):
        self._session = value

    @property
    def user(self):
        if self._user is None:
            raise AttributeError
        return self._user

    @user.setter
    def user(self, value: User):
        self._user = value


require = Requirement()


class RequireJsonData(object):
    """装饰器, 获取并验证dict, 返回无误的dict或错误response"""

    def __init__(self, form: Form) -> None:
        self.form = form

    def __call__(self, func: _t.Callable[[_t.Any], dict]):
        def wrapper(data: _t.Union[dict, list, None] = None) -> dict:
            data = request.get_json() if data is None else data
            if data is None or not isinstance(data, (dict, list)):
                return S_PARAM_ERROR
            success, d = self.form.parse(data)
            if not success:
                return S_PARAM_ERROR
            return func(d)
        wrapper.__name__ = func.__name__
        return wrapper


session_form = DictForm({
    'sessionId': Field(str),
    'digest': Field(str),
    'data': Field(str)
})


def parse_session_data():
    """验证session并解析数据"""
    # 验证参数
    success, json_data = session_form.parse(request.get_json())
    if not success:
        return False, S_PARAM_ERROR

    # 获取session并判断session是否正常
    session_id: str = json_data['sessionId']
    session: Session = Session.query.filter(Session.id == session_id).first()
    if not session:
        return False, S_SESSION_ERROR
    aes_key: bytes = session.aes_key
    # 验证摘要
    digest: str = json_data['digest']
    data: bytes = json_data['data'].encode()
    if digest != hashlib.sha256(aes_key + data).hexdigest():
        return False, S_SESSION_ERROR

    try:
        decrypted = decrypt(session.aes_key, data)
        result = json.loads(decrypted)
    except Exception:
        traceback.print_exc()
        return False, S_SESSION_ERROR
    require.session = session
    return True, result


def require_session(func: _t.Callable[[_t.Any], _t.Union[dict, Response]]):
    """装饰器, 解析aes会话获取数据, 返回值为 Response"""
    def wrapper() -> Response:
        success, data = parse_session_data()
        if not success:
            return app.make_response(data)
        response = func(data)
        if not isinstance(response, Response):
            response = app.make_response(response)
        aes_key: bytes = require.session.aes_key
        response.data = encrypt(aes_key, response.data)
        return response
    wrapper.__name__ = func.__name__
    return wrapper


def require_login(func: _t.Callable[[_t.Any], _t.Union[dict, Response]]):
    """装饰器, 解析aes并判断登录状态"""
    def wrapper(data: _t.Any):
        uid = require.session.user_uid
        if uid is None:
            return S_NOT_LOGIN
        user: User = User.query.filter(User.uid == uid).first()
        if not user:
            return S_NOT_LOGIN
        require.user = user
        return func(data)
    wrapper.__name__ = func.__name__
    return wrapper


def require_ensure_response(func: _t.Callable[..., _t.Union[Response, dict]]):
    """装饰器, 确保返回值为 Response"""
    def wrapper(*args, **kwargs) -> Response:
        response = func(*args, **kwargs)
        if isinstance(response, Response):
            return response
        return app.make_response(response)
    wrapper.__name__ = func.__name__
    return wrapper
