import webview

from .. import gconfig, server, database
from ..database import pydb
from ..event import EventType, emit

database.set_db(pydb.create_db())


class App(object):

    def __init__(self):
        self.window = webview.create_window(gconfig.App.name, url=server.app)
        self.window.events.closing += self.on_closing  # type: ignore
        self.window.events.closed += self.on_closed  # type: ignore
        self.gui = "gtk"

    def run(self):
        webview.start(self.on_start, gui=self.gui)

    def on_start(self):
        emit(EventType.START)

    def on_closing(self):
        emit(EventType.CLOSING)

    def on_closed(self):
        emit(EventType.CLOSED)


def main():
    app = App()
    app.run()
