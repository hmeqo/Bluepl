"""服务器, 绑定url地址以及处理socket"""

from datetime import datetime

from ..event import EventType, subscribe
from .webapp import app, db
from .models import User
from .util import cvt_pwd_md5
from . import views


@subscribe(EventType.INITED)
def on_inited():
    with app.app_context():
        db.create_all()
        if not User.query.filter(User.email == 'test').first():
            solt = '1234'
            user = User(
                email='test',
                password=cvt_pwd_md5('267763', '1234'),
                solt=solt,
                creation_time=datetime.now(),
            )
            db.session.add(user)
