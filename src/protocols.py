""" Módulo para proveedores de type hinting. """
from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtCore import Signal

if TYPE_CHECKING:
    import sql
    from utils.mydataclasses import Usuario


class _ModuloProtocol(Protocol):
    conn: sql.Connection
    user: Usuario

_ProtocolMeta = type(_ModuloProtocol)
_WidgetMeta = type(QWidget)

class _CustomWidgetMeta(_WidgetMeta, _ProtocolMeta):
    pass

class ModuloPrincipal(QWidget, _ModuloProtocol, metaclass=_CustomWidgetMeta):
    """ Subclase de QWidget para módulo principal, con atributos persistentes
        `conn`, `user` y señal `go_back`. """
    go_back: Signal = Signal()

class HasConnUser(QMainWindow, _ModuloProtocol, metaclass=_CustomWidgetMeta):
    """ Subclase de QMainWindow con atributos persistentes `conn` y `user`. """
    ...


__all__ = ['ModuloPrincipal', 'HasConnUser']
