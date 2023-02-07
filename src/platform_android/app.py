from .androidwebview import BrowserApp

from .. import gconfig
from ..database import set_dbapi, pydbapi

set_dbapi(pydbapi.PyDBApi)


def main(debug=False):
    if debug:
        gconfig.App.debug = True
    BrowserApp().run()
