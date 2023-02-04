import webview

from .. import gconfig, server
from ..event import EventType, emit


class App(object):

    def __init__(self):
        self.window = webview.create_window(gconfig.App.name, url=server.app)
        self.window.events.closing += self.on_closing  # type: ignore
        self.window.events.closed += self.on_closed  # type: ignore

    def run(self):
        webview.start(self.on_start, gui="gtk", debug=gconfig.App.debug)

    def on_start(self):
        emit(EventType.START)

    def on_closing(self):
        emit(EventType.CLOSING)

    def on_closed(self):
        emit(EventType.CLOSED)


def main():
    app = App()
    app.run()
