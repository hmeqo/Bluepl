from src.platform_android import BrowserApp
from src.database import pydb
from src import gconfig
from src.event import EventType, emit

pydb.init()


def main():
    gconfig.init()
    emit(EventType.START)
    BrowserApp().run()


if __name__ == "__main__":
    main()
