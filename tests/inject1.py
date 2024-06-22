from dataclasses import dataclass

from config import INI
import fdb
from injector import Module, provider, Injector, inject

Connection = fdb.Connection
Cursor = fdb.Cursor
Error = fdb.Error


class RequestHandler:
    @inject
    def __init__(self, db: Connection):
        self._db = db

    def get(self):
        cursor = self._db.cursor()
        cursor.execute('SELECT usuario FROM usuarios;')
        return cursor.fetchall()

@dataclass
class FdbConfig:
    connection_string: str
    user: str
    psswd: str
    role: str = None

class DatabaseModule(Module):
    def configure(self, binder):
        config = FdbConfig(
            '{}/3050:PrintPOS.fdb'.format(INI.NOMBRE_SERVIDOR),
            'ivanperez',
            '123',
            'vendedor')
        binder.bind(FdbConfig, to=config)

    @provider
    def provide_fdb_connection(self, config: FdbConfig) -> Connection:
        try:
            return fdb.connect(
                dsn=config.connection_string,
                user=config.user,
                password=config.psswd,
                role=config.role,
                charset='UTF8')
        except Error as err:
            txt, sqlcode, gdscode = err.args
            print('\nconectar_db() {\n', sqlcode, gdscode, '\n' + txt + '\n}')
            raise err


injector = Injector(DatabaseModule)
handler = injector.get(RequestHandler)
print(handler.get())
