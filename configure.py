import inspect
from pathlib import Path


class Smtp:

    # Email services provider host url
    host = ""
    # Port
    port = 0
    # Sender email
    sender = ""
    # Smtp password
    password = ""


class Socket:

    # This program use dynamic ip or static ip, if is server, recommended True
    static_ip = False


if __name__ == "__main__":
    code = "".join(inspect.getsource(i) for i in (Smtp, Socket))
    Path("./src/gconfig/config.py").write_text(code)
