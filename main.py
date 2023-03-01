from src.platform_android import BrowserApp
from src.initialize import init
from src.event import EventType, emit


def main():
    init()
    emit(EventType.START)
    BrowserApp().run()


if __name__ == "__main__":
    main()
