from src.database import set_dbapi, pydbapi
from src.event import EventType, emit
from src.server import app

set_dbapi(pydbapi.PyDBApi)
emit(EventType.START)
