import ctypes
import sys
from typing import Literal


def is_admin() -> Literal[0, 1]:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except WindowsError:
        return 0


def runas(fp) -> int:
    """以管理员身份运行.
    返回42为成功, 5为失败
    """
    return ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, fp, None, 1)
