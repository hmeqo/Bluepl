import typing as _t

from flask import Flask
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, model

from ..gconfig import Dirs, FlaskConfig


class Model(model.Model):

    def __init__(self, *args, **kwds) -> None:
        super().__init__(*args, **kwds)


class SQLAlchemy(_SQLAlchemy):

    Model: _t.Type[Model]


app = Flask(
    __name__,
    template_folder=str(Dirs.webroot),
    root_path=str(Dirs.base),
)
app.config.from_object(FlaskConfig)

db = SQLAlchemy(app)
