""" Módulo con manejadores para tablas en la base de datos. """
from functools import partialmethod
from pathlib import Path

import fdb
from injector import inject

from config import INI
from utils.mywidgets import WarningDialog

Connection = fdb.Connection
Cursor = fdb.Cursor
Error = fdb.Error


def conectar_db(usuario: str, psswd: str, rol: str = None) -> Connection:
    """ Crea conexión a base de datos y regresa objeto Connection.
        Levanta sql.Error, por lo que siempre se debe usar en un bloque `try-except`. """
    try:
        return fdb.connect(
            dsn='{}/3050:PrintPOS.fdb'.format(INI.NOMBRE_SERVIDOR),
            user=usuario,
            password=psswd,
            charset='UTF8',
            role=rol)
    except Error as err:
        txt, sqlcode, gdscode = err.args
        print('\nconectar_db() {\n', sqlcode, gdscode, '\n' + txt + '\n}')
        raise err


def respaldar_db(user: str, psswd: str):
        p = Path('./resources/db/printpos.fbk').absolute()
        conn = fdb.services.connect(INI.NOMBRE_SERVIDOR, user, psswd)
        conn.backup('PrintPOS.fdb', str(p))
        return conn.readlines()


class DatabaseManager:
    """ Clase general de un administrador de bases de datos.
        Permite ejecutar consultas varias y manejar las excepciones.
    
        Todas las operaciones realizadas en esta clase y en clases derivadas
        pueden regresar `False` o `None` al ocurrir un error, por lo que siempre se 
        debe verificar el resultado obtenido para asegurar una correcta funcionalidad. """

    @inject
    def __init__(self, conn: Connection,
                 error_txt: str = None,
                 *, handle_exceptions: bool = True):
        assert isinstance(conn, Connection), "Conexión a DB no válida."

        self._conn = conn
        self._error_txt = error_txt or 'Operación fallida en base de datos.'
        self._handle_exceptions = handle_exceptions

        self._crsr = conn.cursor()
        self._crsr.execute("SET TIME ZONE '-06:00';")  # <- tiempo local en UTC

    def _partial_execute(self, func, query: str, parameters=None, commit=False):
        try:
            getattr(self._crsr, func)(query, parameters)
            if commit:
                self._conn.commit()
            return True
        except Error as err:
            self.__handle_err(err)  # <- levanta sql.Error si se solicita
            return False

    def _partial_fetch(self, func, query: str, parameters=None):
        try:
            self._crsr.execute(query, parameters)
            return getattr(self._crsr, func)()
        except Error as err:
            self.__handle_err(err)  # <- levanta sql.Error si se solicita
            return None

    def __handle_err(self, err: Error):
        if not self._handle_exceptions:
            raise err

        txt, sqlcode, gdscode = err.args
        body = [self.__class__.__name__ + ' {',
                f'{gdscode=}',
                txt,
                '}']
        WarningDialog(self._error_txt, '\n'.join(body))
        self._conn.rollback()

    execute = partialmethod(_partial_execute, 'execute')
    executemany = partialmethod(_partial_execute, 'executemany')
    fetchall: partialmethod[list] = partialmethod(_partial_fetch, 'fetchall')
    fetchone: partialmethod[tuple] = partialmethod(_partial_fetch, 'fetchone')

    def obtener_vista(self, vista: str):
        """ Atajo de sentencia SELECT para obtener una vista. """
        return self.fetchall(f'SELECT * FROM {vista};')

    @property
    def nombreUsuarioActivo(self) -> str:
        """ Obtiene nombre/apellido del usuario de la conexión activa. """
        if result := self.fetchone('''
            SELECT  nombre
            FROM    usuarios
            WHERE   usuario = ?;
        ''', (self.usuarioActivo,)):
            return result[0]

    @property
    def idUsuarioActivo(self) -> int:
        """ Obtiene identificador numérico de la conexión activa, de la tabla Usuarios. """
        if result := self.fetchone('''
            SELECT  id_usuarios
            FROM    usuarios 
            WHERE   usuario = ?;
        ''', (self.usuarioActivo,)):
            return result[0]

    @property
    def usuarioActivo(self) -> str:
        """ Obtiene usuario (username) de la conexión activa. """
        if result := self.fetchone('SELECT USER FROM RDB$DATABASE;'):
            return result[0]

    @property
    def rolActivo(self) -> str:
        """ Obtiene rol de la conexión activa. """
        if result := self.fetchone('SELECT CURRENT_ROLE FROM RDB$DATABASE;'):
            return result[0]
