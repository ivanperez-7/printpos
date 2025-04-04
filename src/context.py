from sqlalchemy.orm import Session

from sql.core import FirebirdConnection
from sql.models import Usuario


class UserContext:
    """ Clase para almacenar el contexto del usuario. """
    conn: FirebirdConnection = None
    user: Usuario = None
    session: Session = None
    rol: str = None

    def __str__(self):
        return f'UserContext(conn={self.conn}, user={self.user}, session={self.session}, rol={self.rol})'


user_context = UserContext()

user_context.conn = None
user_context.user = None
user_context.session = None
user_context.rol = None
