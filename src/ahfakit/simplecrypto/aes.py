"""
Usage:

```
key = b"1234567890123456"
# key = AES.generate_key()
aes = AES(key, AES.modes.ECB())
a = aes.encrypt(b"123")
b = aes.decrypt(a)
print(a, b)
```
"""

import base64
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from .padding import *


class AES(Cipher):

    block_size = 16

    modes = modes

    def __init__(self, key: bytes, mode: modes.Mode):
        super().__init__(algorithms.AES(key), mode, default_backend())

    @classmethod
    def generate_key(cls):
        return os.urandom(cls.block_size)

    @classmethod
    def pad(cls, b: bytes):
        """padding bytes"""
        return pad(b, cls.block_size)

    @staticmethod
    def unpad(b: bytes):
        """unpadding bytes"""
        return unpad(b)

    def encrypt(self, data: bytes):
        """Encrypt bytes, automatic padding data"""
        encryptor = self.encryptor()
        encrypted = encryptor.update(self.pad(data)) + encryptor.finalize()
        return base64.b64encode(encrypted)

    def decrypt(self, data: bytes):
        """Decrypt bytes, automatic unpadding data"""
        a = base64.b64decode(data)
        decryptor = self.decryptor()
        decrypted = decryptor.update(a) + decryptor.finalize()
        return self.unpad(decrypted)
