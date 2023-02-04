import hashlib
import json
import random
import string
import traceback
import typing as _t

from flask import Flask, render_template, send_file, send_from_directory, request, Response

from ..ahfakit.simplecrypto import DH
from ..ahfakit.datautil.form import Field, Form
from .. import gconfig
from ..collections import collections, sessions, users, registrys
from ..sender.smtp import send_veri_code
from .status import *

app = Flask(
    __name__,
    template_folder=str(gconfig.Dirs.webroot),
    root_path=str(gconfig.Dirs.root),
)
app.config["JSON_AS_ASCII"] = False

user_form = Form(email=Field(str), password=Field(str))


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


def veri_session(json_data: _t.Optional[_t.Dict[str, _t.Any]]):
    """验证session"""
    # 验证是否提供了session信息和data
    if not json_data or {"sessionId", "digest", "data"}.difference(json_data):
        return app.make_response(status_10)
    # 获取session并判断session是否正常
    session_id = json_data["sessionId"]
    digest = json_data["digest"]
    session = sessions.get(session_id)
    if not session or not session.is_available():
        return app.make_response({**status_10, "expired": True})
    # 验证摘要
    data: bytes = json_data["data"].encode()
    if digest != hashlib.sha256(session.key + data).hexdigest():
        return app.make_response(status_10)
    try:
        # 解密并返回数据
        decrypted = session.decrypt_base64(data)
        result: _t.Dict = json.loads(decrypted)
    except Exception:
        traceback.print_exc()
        return app.make_response(status_10)
    else:
        return result


@app.route("/", methods=["GET", "POST"])
def index():
    """主页面和登录注册"""
    if request.method == "GET":
        return render_template("index.html")
    json_data = request.get_json()
    # 验证 session 并判断必要信息
    data = veri_session(json_data)
    if isinstance(data, Response):
        return data
    if {"email", "password"}.difference(data):
        return app.make_response(status_400)

    email: str = data["email"]
    password: str = data["password"]
    user = users.get(email)

    # 判断用户是否存在
    if user:
        # 判断密码是否正确
        print(hashlib.md5((password + user.solt).encode()).hexdigest())
        print(user.password)
        if hashlib.md5((password + user.solt).encode()).hexdigest() == user.password:
            return app.make_response(status_200)
        return app.make_response(status_101)

    # 判断邮箱是否正在注册
    if email in registrys:
        registry = registrys.get(email)
        # 验证是否有效
        if not registry or not registry.is_available():
            return app.make_response(status_601)
        # 获取并判断验证码
        veri_code = data.get("veriCode")
        if veri_code is None:
            # 没有提供验证码, 返回status信息
            return app.make_response(status_102)
        if data.get("veriCode", "").upper() == registry.veri_code:
            # 验证成功后注册
            solt = "".join(random.choices(string.hexdigits, k=16))
            password = hashlib.md5((password + solt).encode()).hexdigest()
            registry.registry(password, solt)
            return app.make_response(status_200)
        return app.make_response(status_102)

    # 注册
    veri_code = "".join(random.choices(string.hexdigits, k=5)).upper()
    registrys.create(email=email, veri_code=veri_code)
    # 发送验证码
    send_veri_code([email], veri_code)
    return app.make_response(status_102)


@app.route("/session", methods=["POST"])
def app_session():
    """创建与验证会话"""
    data = request.get_json()
    if data:
        # 判断 session id 是否可用
        if "id" in data:
            session = sessions.get(data["id"])
            if session:
                available = session.is_available()
            else:
                available = False
            return app.make_response({"available": available})       
        # 创建会话
        if not {"p", "g", "key"}.difference(data):
            p, g, key = int(data["p"]), int(data["g"]), int(data["key"])
            while True:
                dh = DH(p, g, DH.randint(p >> 1, p - 1))
                session_key = str(dh.step2(key)).encode()
                session_key = hashlib.sha256(session_key).hexdigest()
                session_key = session_key[:32].encode()
                session_id = hashlib.sha256(session_key).hexdigest()
                session = sessions.get(session_id)
                # 判断 session 是否不存在不可用
                if session is None or not session.is_available():
                    sessions.create(id=session_id, key=session_key)
                    collections.save()
                    break
            return app.make_response({"key": str(dh.step1())})
    return app.make_response(b"")
