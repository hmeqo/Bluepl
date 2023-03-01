from smtplib import SMTP
from email.header import Header
from email.mime.text import MIMEText

from . import sockutil
from .gconfig import AppConfig, Files, Smtp
from .backend.status import *

with open(Files.template_veri_code, "r", encoding="UTF-8") as file:
    veri_html = file.read()

with open(Files.template_veri_link, "r", encoding="UTF-8") as file:
    veri_link_html = file.read()


def send_verification_code(receivers: list[str], veri_code: str):
    text = veri_html.format(veri_code=veri_code)
    return send_text(receivers, text, "Verification code")


def send_verification_link(receivers: list[str], link: str):
    link = f"http://{sockutil.get_current_ip()}:{AppConfig.port}/{link}"
    text = veri_link_html.format(veri_link=link)
    return send_text(receivers, text, "Verification link")


def send_text(receivers: list[str], text: str, subject: str):
    message = MIMEText(text, "html", "UTF-8")
    message["From"] = Header(AppConfig.name, "UTF-8")
    message["To"] = Header("", "UTF-8")
    message["Subject"] = Header(subject, "UTF-8")
    try:
        smtp = SMTP(Smtp.host, Smtp.port)
        smtp.login(Smtp.sender, Smtp.password)
    except Exception as exc:
        print(exc)
        return S_NOT_INTERNET_ERROR
    try:
        smtp.sendmail(Smtp.sender, receivers, message.as_string())
    except Exception as exc:
        print(exc)
        return S_EMAIL_ERROR
    return S_SUCCESS_200
