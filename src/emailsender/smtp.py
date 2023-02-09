from smtplib import SMTP
from email.header import Header
from email.mime.text import MIMEText
import typing as _t

from src.server.status import *

from .. import gconfig
from ..gconfig import Smtp

veri_html = """
<h1>验证码 {veri_code}</h1>
"""


def send_verification_code(receivers: _t.List[str], veri_code: str):
    message = MIMEText(veri_html.format(veri_code=veri_code), "html", "UTF-8")
    message["From"] = Header(gconfig.App.name, "UTF-8")
    message["To"] = Header("", "UTF-8")
    message["Subject"] = Header("Verification link", "UTF-8")
    try:
        with SMTP(Smtp.host, Smtp.port) as smtp:
            smtp.login(Smtp.sender, Smtp.password)
            smtp.sendmail(Smtp.sender, receivers, message.as_string())
    except Exception:
        return S_NOT_INTERNET_ERROR
    return S_SUCCESS_200
