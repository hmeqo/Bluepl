import typing as _t

from ..database.dbapi import Session

current_session: _t.Union[Session, None] = None


def get_current_session():
    if current_session is None:
        raise ValueError(current_session)
    return current_session


def set_current_session(session: Session):
    global current_session
    current_session = session
