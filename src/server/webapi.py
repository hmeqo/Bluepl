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
from ..collections import collections, sessions, users, registries
from ..sender.smtp import send_verification_code
from .status import *

app = Flask(
    __name__,
    template_folder=str(gconfig.Dirs.webroot),
    root_path=str(gconfig.Dirs.root),
)
app.config["JSON_AS_ASCII"] = False

ParseResponse = _t.Union[Response, dict]


def get_available_session(session_id: str):
    session = sessions.get(session_id)
    if session and session.is_available():
        return session
    return None


def require_json_dict(form: _t.Optional[Form] = None):
    """装饰器, 获取并验证dict, 返回无误的dict或错误response"""
    def get_func(func: _t.Callable[[dict], _t.Any]):
        def wrapper(data: _t.Optional[ParseResponse] = None) -> ParseResponse:
            if isinstance(data, Response):
                return data
            data = request.get_json() if data is None else data
            if not data or not isinstance(data, dict):
                return app.make_response(E_param_error)
            if form:
                data = form.parse(data)
                if data is None:
                    return app.make_response(E_param_error)
            return func(data)
        wrapper.__name__ = func.__name__
        return wrapper
    return get_func


def require_parse_aes_data(func: _t.Callable[[ParseResponse], _t.Any]):
    """装饰器, 解析aes会话获取数据或错误response"""
    def wrapper():
        return func(veri_session())
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
    session = sessions.get(session_id)
    if not session or not session.is_available():
        return app.make_response({**F_session_error, "expired": True})
    # 验证摘要
    data: bytes = json_data["data"].encode()
    if digest != hashlib.sha256(session.key + data).hexdigest():
        return app.make_response(F_session_error)
    try:
        decrypted = session.decrypt(data)
        result = json.loads(decrypted)
    except Exception:
        traceback.print_exc()
        return app.make_response(F_session_error)
    else:
        return result


@app.route("/favicon.ico")
def favicon():
    return send_file(gconfig.Files.icon)


@app.route("/<path:name>")
def anyurl(name: str):
    # 发送静态文件
    response = send_from_directory(gconfig.Dirs.webroot, name)
    # 如果是 js 文件, 则更改 Content-Type
    if "." in name and name.rsplit(".", 1)[-1] in ("js", "ts"):
        response.headers["Content-Type"] = "text/javascript;charset=utf-8"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    """主页面和登录注册"""
    return render_template("index.html")


@app.route("/login", methods=["POST"])
@require_parse_aes_data
@require_json_dict(Form({
    "email": Field(str),
    "password": Field(str),
    "veriCode": Field(str, ""),
}))
def app_login(json_data: dict):
    """登录和注册"""
    email: str = json_data["email"]
    password: str = json_data["password"]
    veri_code: str = json_data["veriCode"]
    # 登录
    user = users.get(email)
    if user:
        if user.password == hashlib.md5((password + user.solt).encode()).hexdigest():
            return app.make_response(Success_200)
        return app.make_response(L_password_error)
    # 注册
    if email in registries:
        registry = registries.get(email)
        # 验证是否有效
        if not registry or not registry.is_available():
            return app.make_response(F_expired)
        # 获取并判断验证码
        if veri_code is None:
            # 没有提供验证码, 返回status信息
            return app.make_response(L_wait_verify)
        if json_data.get("veriCode", "").upper() == registry.veri_code:
            # 验证成功后注册
            solt = "".join(random.choices(string.hexdigits, k=16))
            password = hashlib.md5((password + solt).encode()).hexdigest()
            registry.registry(password, solt)
            collections.save()
            return app.make_response(Success_200)
        return app.make_response(L_wait_verify)
    veri_code = "".join(random.choices(string.hexdigits, k=5)).upper()
    registries.create(email=email, veri_code=veri_code)
    send_verification_code([email], veri_code)
    return app.make_response(L_wait_verify)


@app.route("/session/validate", methods=["POST"])
@require_json_dict(Form(id=Field(str)))
def app_check_validate(data: dict):
    return {**Success_200, "available": bool(get_available_session(data["id"]))}


@app.route("/session/create", methods=["POST"])
@require_json_dict(Form({
    "p": Field((str, int)),
    "g": Field((str, int)),
    "key": Field((str, int)),
}))
def app_session_create(data: dict):
    p, g, key = int(data["p"]), int(data["g"]), int(data["key"])
    while True:
        dh = DH(p, g, DH.randint(p >> 1, p - 1))
        shared_key = str(dh.step2(key)).encode()
        shared_key = hashlib.sha256(shared_key).hexdigest()[:32].encode()
        session_id = hashlib.sha256(shared_key).hexdigest()
        session = sessions.get(session_id)
        if session is None or not session.is_available():
            sessions.create(id=session_id, key=shared_key)
            collections.save()
            break
    return app.make_response({**Success_200, "key": str(dh.step1())})
