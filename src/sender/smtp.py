from smtplib import SMTP
from email.header import Header
from email.mime.text import MIMEText
import typing as _t

from .. import gconfig
from .sender import host, port, sender, password

smtp = SMTP(host, port)

veri_html = """
<h1>验证码 {veri_code}</h1>
"""


def send_verification_code(receivers: _t.List[str], veri_code: str):
    smtp.login(sender, password)
    message = MIMEText(veri_html.format(veri_code=veri_code), "html", "UTF-8")
    message["From"] = Header(gconfig.App.name, "UTF-8")
    message["To"] = Header("", "UTF-8")
    message["Subject"] = Header("Verification link", "UTF-8")
    smtp.sendmail(sender, receivers, message.as_string())
    smtp.quit()
