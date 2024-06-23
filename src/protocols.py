""" Módulo para proveedores de type hinting. """
from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtCore import Signal

if TYPE_CHECKING:
    from sql.core import Connection
    from utils.mydataclasses import Usuario


class HasConnUser:
    """ Clase para type-hinting de atributos persistentes `conn` y `user`. """
    conn: Connection
    user: Usuario


class ModuloPrincipal(QWidget, HasConnUser):
    """ Subclase de QWidget para módulo principal, con atributos persistentes
        `conn`, `user` y señal `go_back`. """
    go_back: Signal = Signal()


class VentanaPrincipal(QMainWindow, HasConnUser):
    """ Subclase de QMainWindow para ventana principal (anfitriona),
        con atributos persistentes `conn` y `user`. """
    pass


class IDatabaseHandler(Protocol):
    """ Protocolo para manejador de base de datos, con métodos fetch y execute. """
    
    def execute(self, query: str, params: tuple = None, commit: bool = False) -> bool:
        pass
    
    def executemany(self, query: str, params: list[tuple] = None, commit: bool = False) -> bool:
        pass
    
    def fetchall(self, query: str, params: tuple = None) -> list[tuple]:
        pass
    
    def fetchone(self, query: str, params: tuple = None) -> tuple:
        pass
