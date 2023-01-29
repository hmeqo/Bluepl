from .androidwebview import BrowserApp

from .. import database
from ..database import pydb

database.set_db(pydb.create_db())


def main():
    BrowserApp().run()
