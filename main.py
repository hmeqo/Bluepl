from src.platform_android.androidwebview import BrowserApp

from src import gconfig
from src.database import set_dbapi, pydbapi

set_dbapi(pydbapi.PyDBApi)


def main():
    BrowserApp().run()
