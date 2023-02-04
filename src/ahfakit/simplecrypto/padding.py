def pad(b: bytes, block_size: int):
    """padding bytes"""
    a = block_size - len(b) % block_size
    return b + a*chr(a).encode()
    # div, mod = divmod(len(b), block_size)
    # return b.ljust(block_size * (div+1), chr(block_size - mod).encode())


def unpad(b: bytes):
    """unpadding bytes"""
    return b[:-ord(b[-1:])]
