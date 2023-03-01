import typing as _t

from ..ahfakit.simplecrypto.aes import AES


def create_aes(aes_key: _t.Union[bytes, _t.Any]):
    aes = AES(aes_key, AES.modes.CBC(b"0102030405060708"))
    return aes


def encrypt(aes_key: _t.Union[bytes, _t.Any], b: bytes):
    return create_aes(aes_key).encrypt(b)


def decrypt(aes_key: _t.Union[bytes, _t.Any], b: bytes):
    return create_aes(aes_key).decrypt(b)
