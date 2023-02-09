import inspect
from pathlib import Path


class Smtp:

    host = ""
    port = 0
    sender = ""
    password = ""


if __name__ == "__main__":
    code = inspect.getsource(Smtp)
    Path("./src/gconfig/config.py").write_text(code)
