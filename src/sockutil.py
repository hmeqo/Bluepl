import socket
import typing as _t

from . import gconfig

current_ip: _t.Union[str, None] = None


def get_current_ip() -> str:
    global current_ip
    if gconfig.Socket.static_ip and current_ip is not None:
        return current_ip
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ip: str = sock.getsockname()[0]
    current_ip = ip
    return ip
