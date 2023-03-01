import random
import string
import re
import hashlib

pattern_email = re.compile(r"^(\d+@\w+\.\w+){1,50}|test$")
pattern_password = re.compile(
    r"^[\w `~!@#$%^&*()_+-=\[\]{}|\\;:'\",<.>/?]{4,32}$")


def generate_veri_code(k=8):
    """获取随机大写验证码"""
    return ''.join(random.choices(string.hexdigits, k=k)).upper()


def validator_email(s: str):
    return bool(pattern_email.fullmatch(s))


def validator_password(s: str):
    return bool(pattern_password.fullmatch(s))


def cvt_pwd_md5(s: str, solt: str):
    return hashlib.md5((s + solt).encode()).hexdigest()
