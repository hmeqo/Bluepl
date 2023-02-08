import webview

from src import gconfig, server
from src.event import EventType, emit
from src.database import set_dbapi, pydbapi

set_dbapi(pydbapi.PyDBApi)


class App(object):

    def __init__(self):
        self.window = webview.create_window(gconfig.App.name, server.app)
        self.window._http_port = 27640

    def run(self):
        webview.start(self.on_start, gui="gtk", debug=gconfig.App.debug)

    def on_start(self):
        emit(EventType.START)


def main():
    app = App()
    app.run()
