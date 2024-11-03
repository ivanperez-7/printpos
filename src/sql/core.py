""" Módulo con manejadores para tablas en la base de datos. """

import fdb
from haps import egg

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
