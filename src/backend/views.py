from datetime import datetime, timedelta
import string
import hashlib
import random
import typing as _t

from flask import render_template, send_file, send_from_directory

from src.emailsender import send_verification_code

from ..ahfakit.simplecrypto.dh import DH
from ..ahfakit.datautil.form import DictForm, Field
from ..gconfig import Dirs, Files
from .webapp import app, db
from .require import RequireJsonData, require_ensure_response, require_login, require_session
from .models import RecordRegistry, RecordResetPwd, Session, User, DataAccount
from .status import *
from .require import require
from .util import generate_veri_code, cvt_pwd_md5, len_limit, validator_email, validator_password


@app.route('/favicon.ico')
def favicon():
    return send_file(Files.icon)


@app.route('/<path:name>')
def anyurl(name: str):
    response = send_from_directory(Dirs.webroot, name)
    if '.' in name and name.rsplit('.', 1)[-1] in ('js', 'ts'):
        response.headers['Content-Type'] = 'text/javascript;charset=utf-8'
    if response.status_code != 404:
        response.status_code = 200
    return response


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route('/session/status', methods=['POST'])
@require_ensure_response
@RequireJsonData(DictForm({'id': Field(str)}))
def app_session_status(data: dict):
    """获取session状态"""
    session: Session = Session.query.filter(
        Session.id == data['id'],
        Session.validity < datetime.now(),
    ).first()
    if not session:
        return S_SESSION_ERROR
    return {**S_SUCCESS_200, "logined": session.user_uid is not None}


@app.route('/session/create', methods=['POST'])
@require_ensure_response
@RequireJsonData(DictForm({
    'p': Field((str, int), validator=len_limit(500)),
    'g': Field((str, int), validator=len_limit(500)),
    'key': Field((str, int), validator=len_limit(500)),
}))
def session_create(json_data: dict):
    """创建session"""
    p = int(json_data['p'])
    g = int(json_data['g'])
    key = int(json_data['key'])
    while True:
        dh = DH(p, g, DH.randint(p >> 1, p - 1))
        shared_key = str(dh.step2(key)).encode()
        shared_key = hashlib.sha256(shared_key).hexdigest()[:32].encode()
        session_id = hashlib.sha256(shared_key).hexdigest()
        if Session.query.filter(Session.id == session_id).first():
            continue
        t = datetime.now() + timedelta(0, 1800)
        session = Session(id=session_id, aes_key=shared_key, validity=t)
        db.session.add(session)
        db.session.commit()
        break
    return {**S_SUCCESS_200, 'key': str(dh.step1())}


@app.route('/user/login', methods=['POST'])
@require_session
@RequireJsonData(DictForm({
    'email': Field(str, validator=validator_email),
    'password': Field(str, validator=validator_password),
    'veriCode': Field(str, '', validator=len_limit(50)),
}))
def login(json_data: dict):
    """登录和注册"""
    email: str = json_data['email']
    password: str = json_data['password']
    veri_code: str = json_data['veriCode']
    # 登录
    user: User = User.query.filter(User.email == email).first()
    if user:
        solt: str = user.solt
        password = hashlib.md5((password + solt).encode()).hexdigest()
        if password == user.password:
            require.session.user_uid = user.uid
            return S_SUCCESS_200
        return S_PASSWORD_ERROR
    # 注册
    registry: RecordRegistry = RecordRegistry.query.filter(
        RecordRegistry.email == email,
        RecordRegistry.validity < datetime.now(),
    ).first()
    if registry:
        if veri_code.upper() != registry.veri_code:
            return S_VERIFICATION_ERROR
        solt = "".join(random.choices(string.hexdigits, k=16))
        password = cvt_pwd_md5(password, solt)
        t = datetime.now() + timedelta(0, 1800)
        db.session.add(User(
            email=email, password=password, solt=solt, creation_time=t,
        ))
        user = User.query.filter(
            User.email == email
        ).order_by(User.uid.desc()).first()
        user.name = f'uid{user.uid}'
        db.session.add(user)
        return S_SUCCESS_200
    # 生成验证码, 发送邮件
    veri_code = generate_veri_code()
    status = send_verification_code([email], veri_code)
    if status != S_SUCCESS_200:
        return status

    t = datetime.now() + timedelta(0, 180)
    registry = RecordRegistry(email=email, veri_code=veri_code, validity=t)
    db.session.add(registry)
    db.session.commit()
    return S_WAIT_VERIFY


@app.route('/user/had', methods=['POST'])
@require_session
@RequireJsonData(DictForm({
    'uid': Field(int, nullable=True, validator=len_limit(50)),
    'email': Field(str, nullable=True, validator=len_limit(50)),
}))
def had_user(json_data: dict):
    """判断用户是否存在"""
    uid: _t.Union[int, None] = json_data['uid']
    email: _t.Union[str, None] = json_data['email']
    had_user = False
    if uid:
        had_user = bool(User.query.filter(User.uid == uid).first())
    elif email:
        had_user = bool(User.query.filter(User.email == email).first())
    return {**S_SUCCESS_200, 'hadUser': had_user}


@app.route('/user/resetpassword', methods=['POST'])
@require_session
@RequireJsonData(DictForm({
    'email': Field(str, validator=validator_email),
    'password': Field(str, nullable=True, validator=validator_password),
    'veriCode': Field(str, nullable=True, validator=len_limit(50)),
}))
def user_reset_password(json_data: dict):
    """重置密码"""
    email: str = json_data['email']
    resetpwd: RecordResetPwd = RecordResetPwd.query.filter(
        RecordResetPwd.email == email,
        RecordResetPwd.validity < datetime.now(),
    ).fisrt()
    if not resetpwd:
        veri_code = generate_veri_code()
        status = send_verification_code([email], veri_code)
        if status != S_SUCCESS_200:
            return status
        t = datetime.now() + timedelta(0, 180)
        db.session.add(RecordResetPwd(
            email=email, veri_code=veri_code, validity=t
        ))
        db.session.commit()
        return S_WAIT_VERIFY

    veri_code: _t.Union[str, None] = json_data['veriCode']
    password: _t.Union[str, None] = json_data['password']
    if veri_code is None:
        return S_WAIT_VERIFY
    if veri_code.upper() != resetpwd.veri_code:
        return S_VERIFICATION_ERROR
    if password is None:
        return S_PASSWORD_ERROR

    user = require.user
    user.password = cvt_pwd_md5(user.password, user.solt)
    db.session.add(user)
    db.session.commit()
    return S_SUCCESS_200


@app.route('/user/logout', methods=['POST'])
@require_session
@require_login
def logout(*_):
    """退出登录"""
    require.session.user_uid = None
    db.session.add(require.session)
    db.session.commit()
    return S_SUCCESS_200


@app.route('/user/info', methods=['POST'])
@require_session
@require_login
def user_info(*_):
    """获取用户信息"""
    user = require.user
    return {
        **S_SUCCESS_200,
        'data': {
            'uid': user.uid,
            'email': user.email,
            'name': user.name,
            'avatar': user.avatar,
        },
    }


@app.route('/user/updateinfo', methods=['POST'])
@require_session
@require_login
@RequireJsonData(DictForm({
    'name': Field(str, nullable=True, validator=len_limit(32)),
}))
def user_update_info(json_data: dict):
    """更新用户信息"""
    name: _t.Union[str, None] = json_data['name']
    if name is not None:
        require.user.name = name
    db.session.add(require.user)
    db.session.commit()
    return S_SUCCESS_200


@app.route('/user/accounts', methods=['POST'])
@require_session
@require_login
def user_data_accounts(*_):
    """获取全部账号数据"""
    lst: list[DataAccount] = DataAccount.query.filter(
        DataAccount.user_uid == require.user.uid
    ).all()
    accounts = [
        {
            'id': account.id,
            'platform': account.platform,
            'account': account.account,
            'password': account.password,
            'note': account.note,
        }
        for account in lst
    ]
    return {**S_SUCCESS_200, 'data': accounts}


@app.route('/user/accounts/create', methods=['POST'])
@require_session
@require_login
@RequireJsonData(DictForm({
    'platform': Field(str, nullable=True, validator=len_limit(50)),
    'account': Field(str, nullable=True, validator=len_limit(50)),
    'password': Field(str, nullable=True, validator=len_limit(100)),
    'note': Field(str, nullable=True, validator=len_limit(200)),
}))
def user_data_account_create(json_data: dict):
    """添加账号数据"""
    user = require.user
    account = DataAccount(
        user_uid=user.uid,
        platform=json_data['platform'] or '',
        account=json_data['account'] or '',
        password=json_data['password'] or '',
        note=json_data['note'] or '',
    )
    db.session.add(account)
    db.session.commit()
    return {
        **S_SUCCESS_200,
        'id': DataAccount.query.filter(
            DataAccount.user_uid == user.uid
        ).order_by(
            DataAccount.id.desc()
        ).first().id,
    }


@app.route('/user/accounts/update', methods=['POST'])
@require_session
@require_login
@RequireJsonData(DictForm({
    'id': Field(int),
    'platform': Field(str, nullable=True, validator=len_limit(50)),
    'account': Field(str, nullable=True, validator=len_limit(50)),
    'password': Field(str, nullable=True, validator=len_limit(100)),
    'note': Field(str, nullable=True, validator=len_limit(200)),
}))
def user_data_accounts_update(json_data: dict):
    """更新账号数据"""
    data_account: DataAccount = DataAccount.query.filter(
        DataAccount.id == json_data['id'],
        DataAccount.user_uid == require.user.uid,
    ).first()
    if not data_account:
        return S_PARAM_ERROR
    platform = json_data['platform']
    account = json_data['account']
    password = json_data['password']
    note = json_data['note']
    if platform is not None:
        data_account.platform = platform
    if account is not None:
        data_account.account = account
    if password is not None:
        data_account.password = password
    if note is not None:
        data_account.note = note
    db.session.add(data_account)
    db.session.commit()
    return S_SUCCESS_200


@app.route('/user/accounts/delete', methods=['POST'])
@require_session
@require_login
@RequireJsonData(DictForm({
    'id': Field(int),
}))
def user_data_account_delete(json_data: dict):
    """删除账号数据"""
    DataAccount.query.filter(
        DataAccount.id == json_data['id'],
        DataAccount.user_uid == require.user.uid,
    ).delete()
    return S_SUCCESS_200
