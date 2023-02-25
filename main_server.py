from src.initialize import init
from src.event import EventType, emit
from src.database.pydb import PyDBApi
from src.server import app

init(PyDBApi)
emit(EventType.START)
