def pad(b: bytes, block_size: int):
    """padding bytes"""
    a = block_size - len(b) % block_size
    return b + a*chr(a).encode()


def unpad(b: bytes):
    """unpadding bytes"""
    return b[:-ord(b[-1:])]
