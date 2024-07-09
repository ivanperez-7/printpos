from typing import TYPE_CHECKING

from haps import base
from PySide6.QtCore import Signal as _Signal, SignalInstance as _SignalInstance

if TYPE_CHECKING:
    from utils import mydataclasses


@base
class IDatabaseConnection:
    pass


@base
class IControllerWindow:
    def crear(self, conn: IDatabaseConnection, user: 'mydataclasses.Usuario') -> None:
        raise NotImplementedError
    
    def go_home(self) -> None:
        raise NotImplementedError
    
    def go_to(self, modulo: str) -> None:
        raise NotImplementedError


@base
class IModuloPrincipal:
    go_back: _SignalInstance = _Signal()
    
    def crear(self, conn: IDatabaseConnection, user: 'mydataclasses.Usuario') -> None:
        raise NotImplementedError


@base
class IWarningLogger:
    def display(self, title: str, body: str) -> None:
        raise NotImplementedError
