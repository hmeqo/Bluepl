from .androidwebview import BrowserApp

from .. import gconfig


def main(debug=False):
    if debug:
        gconfig.App.debug = True
    BrowserApp().run()
