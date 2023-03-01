from src.gconfig import FlaskConfig
from src.initialize import init
from src.event import EventType, emit
from src.backend.webapp import app

# FlaskConfig.SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/bluepl'
init()
emit(EventType.START)
