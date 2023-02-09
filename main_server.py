from src.database import pydb
from src.event import EventType, emit
from src.server import app

pydb.init()

emit(EventType.START)
