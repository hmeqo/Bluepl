import sys
import webview
import psutil

from src.ahfakit.stdlibtools import tlos, tlctypes
from src.initialize import init
from src.backend import webapp
from src.gconfig import AppConfig, Files
from src.event import EventType, emit


class App(object):

    def __init__(self):
        self.window = webview.create_window(AppConfig.name, webapp.app)
        self.window._http_port = AppConfig.port

    def run(self):
        webview.start(self.on_start, gui="gtk", debug=AppConfig.debug)

    def on_start(self):
        emit(EventType.START)


def main():
    # 当前非可写入文件夹 以管理员权限打开
    if not tlctypes.is_admin() and not tlos.writable("."):
        tlctypes.runas(sys.argv[0])
        return None

    init()

    # 互斥锁 防止重复打开
    with open(Files.pidlock, "a+") as file:
        file.seek(0)
        pid = file.read()
        if pid.isdecimal() and psutil.pid_exists(int(pid)):
            return None
        file.seek(0)
        file.truncate()
        file.write(str(psutil.Process().pid))

    app = App()
    app.run()
    return None


if __name__ == "__main__":
    main()
