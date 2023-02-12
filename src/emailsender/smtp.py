import socket
from smtplib import SMTP
from email.header import Header
from email.mime.text import MIMEText
import typing as _t

from src.server.status import *

from .. import gconfig, sockutil
from ..gconfig import Smtp

veri_html = """
<h1>验证码 {veri_code}</h1>
"""

veri_link_html = """
<a href="{veri_link}">验证链接</a>
"""


def send_verification_code(receivers: _t.List[str], veri_code: str):
    text = veri_html.format(veri_code=veri_code)
    return send_text(receivers, text, "Verification code")


def send_verification_link(receivers: _t.List[str], link: str):
    link = f"http://{sockutil.get_current_ip()}:{gconfig.App.port}/{link}"
    text = veri_link_html.format(veri_link=link)
    send_text(receivers, text, "Verification link")


def send_text(receivers: _t.List[str], text: str, subject: str):
    message = MIMEText(text, "html", "UTF-8")
    message["From"] = Header(gconfig.App.name, "UTF-8")
    message["To"] = Header("", "UTF-8")
    message["Subject"] = Header(subject, "UTF-8")
    try:
        with SMTP(Smtp.host, Smtp.port) as smtp:
            smtp.login(Smtp.sender, Smtp.password)
            smtp.sendmail(Smtp.sender, receivers, message.as_string())
    except Exception:
        return S_NOT_INTERNET_ERROR
    return S_SUCCESS_200
