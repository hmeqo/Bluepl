from src.platform_android.androidwebview import BrowserApp

from src.database import pydb

pydb.init()


def main():
    BrowserApp().run()


if __name__ == "__main__":
    main()
