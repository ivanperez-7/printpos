""" Módulo con manejadores para tablas en la base de datos. """

import fdb
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from config import INI


class FirebirdError(fdb.Error):
    pass


def conectar_firebird(usuario: str, psswd: str, rol: str = None):
    """ Crea conexión a base de datos y regresa conexión a DB.
    Levanta sql.FirebirdError, por lo que siempre se debe usar en un bloque `try-except`.
    """
    connection_string = f"firebird+fdb://{usuario}:{psswd}@{INI.NOMBRE_SERVIDOR}:3050/PrintPOS.fdb?charset=UTF8&role={rol}"
    engine = create_engine(connection_string)
    Session = sessionmaker(bind=engine)
    return Session()
