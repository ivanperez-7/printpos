import threading as _threading

from sqlalchemy.orm import Session

from sql.models import Usuario


class UserContext:
    session: Session
    user: Usuario
    active_role: str

user_context: UserContext = _threading.local()
""" Contexto de objeto Session y objeto Usuario. """
