import webview
import psutil

from src.initialize import init
from src import gconfig, server
from src.event import EventType, emit
from src.database.pydb import PyDBApi


class App(object):

    def __init__(self):
        self.window = webview.create_window(gconfig.App.name, server.app)
        self.window._http_port = gconfig.App.port

    def run(self):
        webview.start(self.on_start, gui="gtk", debug=gconfig.App.debug)

    def on_start(self):
        emit(EventType.START)


def main():
    # gconfig.App.debug = True
    init(PyDBApi)

    with open(gconfig.Files.pidlock, "a+") as file:
        file.seek(0)
        try:
            pid = int(file.read())
            if psutil.pid_exists(pid):
                return None
        except ValueError:
            pass
        file.seek(0)
        file.truncate()
        file.write(str(psutil.Process().pid))

    app = App()
    app.run()
    return None


if __name__ == "__main__":
    main()
