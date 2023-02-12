import webview

from src import gconfig, server
from src.event import EventType, emit
from src.database import pydb

pydb.init()


class App(object):

    def __init__(self):
        self.window = webview.create_window(gconfig.App.name, server.app)
        self.window._http_port = gconfig.App.port

    def run(self):
        webview.start(self.on_start, gui="gtk", debug=gconfig.App.debug)

    def on_start(self):
        emit(EventType.START)


if __name__ == "__main__":
    # gconfig.App.debug = True
    gconfig.init()
    app = App()
    app.run()
