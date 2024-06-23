from injector import Injector

from .core import conectar_db, Connection, DatabaseManager
from protocols import IDatabaseHandler


def configure(binder):
    binder.bind(IDatabaseHandler, to=DatabaseManager)
    binder.bind(Connection, to=conectar_db('ivanperez', '123', 'administrador'))

db_injector = Injector(configure)
