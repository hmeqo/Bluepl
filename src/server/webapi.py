import hashlib
import json
import random
import string
import traceback
import typing as _t

from flask import Flask, render_template, send_file, send_from_directory, request, Response

from ..ahfakit.simplecrypto.dh import DH
from ..ahfakit.datautil.form import Form, Field
from .. import gconfig
from ..database import get_dbapi
from ..sender.smtp import send_verification_code
from .status import *
from . import currequest

app = Flask(
    __name__,
    template_folder=str(gconfig.Dirs.webroot),
    root_path=str(gconfig.Dirs.root),
)
app.config["JSON_AS_ASCII"] = False


def require_json_dict(form: _t.Optional[Form] = None):
    """装饰器, 获取并验证dict, 返回无误的dict或错误response"""
    def get_func(func: _t.Callable[[dict], _t.Any]):
        def wrapper(data: _t.Optional[_t.Union[Response, dict]] = None) -> Response:
            if isinstance(data, Response):
                return data
            data = request.get_json() if data is None else data
            if not data or not isinstance(data, dict):
                return app.make_response(S_PARAM_ERROR)
            if form:
                data = form.parse(data)
                if data is None:
                    return app.make_response(S_PARAM_ERROR)
            return func(data)
        wrapper.__name__ = func.__name__
        return wrapper
    return get_func


def require_aes_parser(func: _t.Callable[..., Response]):
    """装饰器, 解析aes会话获取数据或错误response"""
    def wrapper() -> Response:
        response = func(veri_session())
        session = currequest.get_current_session()
        response.data = session.encrypt(response.data)
        return response
    wrapper.__name__ = func.__name__
    return wrapper


@require_json_dict(Form({
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
        return app.make_response({**S_SESSION_ERROR, "expired": True})
    currequest.set_current_session(session)
    # 验证摘要
    data: bytes = json_data["data"].encode()
    if digest != hashlib.sha256(session.key + data).hexdigest():
        return app.make_response(S_SESSION_ERROR)
    try:
        decrypted = session.decrypt(data)
        result = json.loads(decrypted)
    except Exception:
        traceback.print_exc()
        return app.make_response(S_SESSION_ERROR)
    else:
        return result


@app.route("/favicon.ico")
def app_favicon():
    return send_file(gconfig.Files.icon)


@app.route("/<path:name>")
def app_anyurl(name: str):
    # 发送静态文件
    response = send_from_directory(gconfig.Dirs.webroot, name)
    # 如果是 js 文件, 则更改 Content-Type
    if "." in name and name.rsplit(".", 1)[-1] in ("js", "ts"):
        response.headers["Content-Type"] = "text/javascript;charset=utf-8"
    return response


@app.route("/", methods=["GET", "POST"])
def app_index():
    """主页面和登录注册"""
    return render_template("index.html")


@app.route("/login", methods=["POST"])
@require_aes_parser
@require_json_dict(Form({
    "email": Field(str),
    "password": Field(str),
    "veriCode": Field(str, ""),
}))
def app_login(json_data: dict):
    """登录和注册"""
    dbapi = get_dbapi()
    email: str = json_data["email"]
    password: str = json_data["password"]
    veri_code: str = json_data["veriCode"]
    # 登录
    user = dbapi.get_user(email)
    if user:
        if user.password == hashlib.md5((password + user.solt).encode()).hexdigest():
            currequest.get_current_session().user_email = email
            return app.make_response(S_SUCCESS_200)
        return app.make_response(S_PASSWORD_ERROR)
    # 注册
    registry = dbapi.get_available_registry(email)
    if registry:
        # 验证是否有效
        if not registry or not registry.is_available():
            return app.make_response(S_EXPIRED_ERROR)
        # 获取并判断验证码
        if veri_code is None:
            # 没有提供验证码, 返回status信息
            return app.make_response(S_WAIT_VERIFY)
        if veri_code.upper() == registry.veri_code:
            # 验证成功后注册
            solt = "".join(random.choices(string.hexdigits, k=16))
            password = hashlib.md5((password + solt).encode()).hexdigest()
            dbapi.registry_user(registry, password, solt)
            return app.make_response(S_SUCCESS_200)
        return app.make_response(S_WAIT_VERIFY)
    veri_code = "".join(random.choices(string.hexdigits, k=5)).upper()
    status = send_verification_code([email], veri_code)
    if status == S_NOT_INTERNET_ERROR:
        return app.make_response(S_NOT_INTERNET_ERROR)
    dbapi.create_registry(email, veri_code)
    return app.make_response(S_WAIT_VERIFY)


@app.route("/session/info", methods=["POST"])
@require_json_dict(Form({"id": Field(str)}))
def app_session_info(data: dict):
    session = get_dbapi().get_available_session(data["id"])
    if session:
        return {**S_SUCCESS_200, "logined": bool(session.user_email), "available": True}
    return {**S_SUCCESS_200, "logined": False, "available": False}


@app.route("/session/create", methods=["POST"])
@require_json_dict(Form({
    "p": Field((str, int)),
    "g": Field((str, int)),
    "key": Field((str, int)),
}))
def app_session_create(data: dict):
    dbapi = get_dbapi()
    p, g, key = int(data["p"]), int(data["g"]), int(data["key"])
    while True:
        dh = DH(p, g, DH.randint(p >> 1, p - 1))
        shared_key = str(dh.step2(key)).encode()
        shared_key = hashlib.sha256(shared_key).hexdigest()[:32].encode()
        session_id = hashlib.sha256(shared_key).hexdigest()
        session = dbapi.get_available_session(session_id)
        if session is None:
            dbapi.create_session(session_id, shared_key)
            break
    return app.make_response({**S_SUCCESS_200, "key": str(dh.step1())})
