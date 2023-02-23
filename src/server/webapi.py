import hashlib
import re
import typing as _t

from flask import render_template, send_file, send_from_directory, request

from src.ahfakit.datautil.recordcollection import NONE_TYPE

from ..ahfakit.simplecrypto.dh import DH
from ..ahfakit.datautil.form import DictForm, Field, ListForm
from .. import gconfig
from ..emailsender.smtp import send_verification_code
from .status import *
from .app import app
from . import requirer
from .requirer import get_dbapi

pattern_email = re.compile(r"^\d+@\w+\.\w+|test$")
pattern_password = re.compile(
    r"^[\w `~!@#$%^&*()_+-=\[\]{}|\\;:'\",<.>/?]{4,32}$")


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
    if response.status_code != 404:
        response.status_code = 200
    return response


@app.route("/", methods=["GET", "POST"])
def app_index():
    return render_template("index.html")


@app.route("/session/info", methods=["POST"])
@requirer.require_ensure_response
@requirer.require_json_data(DictForm({"id": Field(str)}))
def app_session_info(data: dict):
    session = get_dbapi().get_available_session(data["id"])
    if session is None:
        return S_SESSION_ERROR
    return {**S_SUCCESS_200, "logined": session.user_uid is not None}


@app.route("/session/create", methods=["POST"])
@requirer.require_ensure_response
@requirer.require_json_data(DictForm({
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
    return {**S_SUCCESS_200, "key": str(dh.step1())}


@app.route("/login", methods=["POST"])
@requirer.require_aes_parser
@requirer.require_json_data(DictForm({
    "email": Field(str, validator=lambda x: bool(pattern_email.match(x)) and len(x) <= 50),
    "password": Field(str, validator=lambda x: bool(pattern_password.match(x))),
    "veriCode": Field(str, ""),
}))
def app_login(json_data: dict):
    """登录和注册"""
    dbapi = get_dbapi()
    email: str = json_data["email"]
    password: str = json_data["password"]
    veri_code: str = json_data["veriCode"]
    # 登录
    user = dbapi.get_user(email=email)
    if user:
        password = hashlib.md5((password + user.solt).encode()).hexdigest()
        if password == user.password:
            dbapi.login(requirer.get_session(), user)
            return S_SUCCESS_200
        return S_PASSWORD_ERROR
    # 注册
    registry = dbapi.get_available_registry(email)
    if registry:
        # 验证是否有效
        if not registry or not registry.is_available():
            return S_EXPIRED_ERROR
        # 获取并判断验证码
        if veri_code is None:
            # 没有提供验证码, 返回status信息
            return S_WAIT_VERIFY
        if veri_code.upper() == registry.veri_code:
            # 验证成功后注册
            user = dbapi.create_user(email, password)
            if user is None:
                return S_USER_ALREADY_EXISTS
            dbapi.delete_registry(email)
            dbapi.login(requirer.get_session(), user)
            return S_SUCCESS_200
        return S_WAIT_VERIFY
    # 生成验证码, 发送邮件
    veri_code = requirer.get_random_veri_code()
    status = send_verification_code([email], veri_code)
    if status == S_NOT_INTERNET_ERROR:
        return S_NOT_INTERNET_ERROR
    dbapi.create_registry(email, veri_code)
    return S_WAIT_VERIFY


@app.route("/user/had", methods=["POST"])
@requirer.require_ensure_response
@requirer.require_json_data(DictForm({
    "uid": Field(int, nullable=True),
    "email": Field(str, ""),
}))
def app_had_user(json_data: dict):
    dbapi = get_dbapi()
    uid: _t.Union[int, None] = json_data["uid"]
    email: str = json_data["email"]
    had_user = False
    if uid is not None:
        had_user = dbapi.get_user(uid=uid) is not None
    elif email:
        had_user = dbapi.get_user(email=email) is not None
    return {**S_SUCCESS_200, "hadUser": had_user}


@app.route("/user/resetpassword", methods=["POST"])
@requirer.require_ensure_response
@requirer.require_json_data(DictForm({
    "email": Field(str),
    "password": Field((str, NONE_TYPE), validator=lambda x: bool(pattern_password.match(x))),
    "veriCode": Field((str, NONE_TYPE)),
}))
def app_user_reset_password(json_data: dict):
    dbapi = get_dbapi()
    email: str = json_data["email"]
    resetrecord = dbapi.get_available_resetrecord(email)
    if not resetrecord:
        veri_code = requirer.get_random_veri_code()
        dbapi.create_resetrecord(email, veri_code)
        return S_WAIT_VERIFY

    veri_code: _t.Union[str, None] = json_data["veriCode"]
    password: _t.Union[str, None] = json_data["password"]
    if veri_code is None:
        return S_WAIT_VERIFY
    if veri_code != resetrecord.veri_code:
        return S_VERIFICATION_ERROR
    if password is None:
        return S_PASSWORD_ERROR

    dbapi.reset_password(email, password)
    return S_SUCCESS_200


@app.route("/logout", methods=["POST"])
@requirer.require_login
def app_logout(*_):
    dbapi = get_dbapi()
    dbapi.logout(requirer.get_session())
    return S_SUCCESS_200


@app.route("/user/updateinfo", methods=["POST"])
@requirer.require_login
@requirer.require_json_data(DictForm({
    "name": Field((str, NONE_TYPE)),
}))
def app_user_update_info(json_data: dict):
    dbapi = get_dbapi()
    dbapi.update_user_info(requirer.get_user(), name=json_data["name"])
    return S_SUCCESS_200


@app.route("/user/info", methods=["POST"])
@requirer.require_login
def app_user_info(*_):
    user = requirer.get_user()
    return {**S_SUCCESS_200, "data": {
        "uid": user.uid,
        "email": user.email,
        "name": user.name,
        "avatar": user.avatar,
    }}


@app.route("/user/accounts", methods=["POST"])
@requirer.require_login
def app_user_data_accounts(*_):
    dbapi = get_dbapi()
    accounts = [
        {
            "id": account.id,
            "platform": account.platform,
            "account": account.account,
            "password": account.password,
            "note": account.note,
        }
        for account in dbapi.get_data_accounts(requirer.get_user())
    ]
    return {**S_SUCCESS_200, "data": accounts}


@app.route("/user/accounts/create", methods=["POST"])
@requirer.require_login
@requirer.require_json_data(DictForm({
    "platform": Field(str, "", validator=lambda x: len(x) < 50),
    "account": Field(str, "", validator=lambda x: len(x) < 50),
    "password": Field(str, "", validator=lambda x: len(x) < 100),
    "note": Field(str, "", validator=lambda x: len(x) < 200),
}))
def app_user_data_create_account(json_data: dict):
    dbapi = get_dbapi()
    user = requirer.get_user()
    return {**S_SUCCESS_200, "id": dbapi.create_data_account(
        user, json_data["platform"], json_data["account"],
        json_data["password"], json_data["note"],
    ).id}


@app.route("/user/accounts/update", methods=["POST"])
@requirer.require_login
@requirer.require_json_data(ListForm(
    DictForm({
        "id": Field(int),
        "platform": Field(str, "", validator=lambda x: len(x) < 50),
        "account": Field(str, "", validator=lambda x: len(x) < 50),
        "password": Field(str, "", validator=lambda x: len(x) < 100),
        "note": Field(str, "", validator=lambda x: len(x) < 200),
    })
))
def app_user_data_update_accounts(json_data: _t.List[dict]):
    dbapi = get_dbapi()
    dbapi.update_data_accounts(requirer.get_user(), json_data)
    return S_SUCCESS_200


@app.route("/user/accounts/delete", methods=["POST"])
@requirer.require_login
@requirer.require_json_data(ListForm(Field(int)))
def app_user_data_delete_account(json_data: _t.List[int]):
    dbapi = get_dbapi()
    dbapi.delete_data_accounts(requirer.get_user(), json_data)
    return S_SUCCESS_200
