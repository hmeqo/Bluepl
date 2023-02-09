from src.database import pydb
from src.server import app
from src.event import EventType, emit
from src import gconfig

pydb.init()

gconfig.init()
emit(EventType.START)
