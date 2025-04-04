""" Módulo con manejadores para tablas en la base de datos. """

import fdb
from haps import egg
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from config import INI
from interfaces import IDatabaseConnection


################## CLASES DE CONEXIÓN A DB ##################
class FirebirdConnection(fdb.Connection, IDatabaseConnection):
    pass


################## CLASES DE ERRORES ##################
FirebirdError = fdb.Error


################## FACTORÍAS DE CONEXIÓN ##################
@egg
def conectar_firebird(usuario: str, psswd: str, rol: str = None) -> FirebirdConnection:
    """ Crea conexión a base de datos y regresa conexión a DB.
    Levanta sql.FirebirdError, por lo que siempre se debe usar en un bloque `try-except`.
    """
    try:
        return fdb.connect(
            dsn='{}/3050:PrintPOS.fdb'.format(INI.NOMBRE_SERVIDOR),
            user=usuario,
            password=psswd,
            charset='UTF8',
            role=rol,
            connection_class=FirebirdConnection,
        )
    except FirebirdError as err:
        txt, sqlcode, gdscode = err.args
        print('\nconectar_db() {\n', sqlcode, gdscode, '\n' + txt + '\n}')
        raise err


def conectar_firebird_sqlalchemy(usuario: str, psswd: str, rol: str = None):
    """ Crea conexión a base de datos y regresa conexión a DB.
    Levanta sql.FirebirdError, por lo que siempre se debe usar en un bloque `try-except`.
    """
    connection_string = f'firebird+fdb://{usuario}:{psswd}@{INI.NOMBRE_SERVIDOR}:3050/PrintPOS.fdb?charset=UTF8&role={rol}'
    engine = create_engine(connection_string)
    Session = sessionmaker(bind=engine)
    return Session()
