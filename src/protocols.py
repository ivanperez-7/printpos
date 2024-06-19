""" Módulo para proveedores de type hinting. """
from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal

if TYPE_CHECKING:
    import sql
    from utils.mydataclasses import Usuario


class _ModuloProtocol(Protocol):
    """ Protocolo para módulo principal, con atributos persistentes
        `conn`, `user` y señal `go_back`. """
    conn: sql.Connection
    user: Usuario
    go_back: Signal = Signal()

_ProtocolMeta = type(_ModuloProtocol)
_WidgetMeta = type(QWidget)

class _CustomMeta(_WidgetMeta, _ProtocolMeta):
    pass

class ModuloPrincipal(QWidget, _ModuloProtocol, metaclass=_CustomMeta):
    """ Subclase de QWidget para módulo principal, con atributos persistentes
        `conn`, `user` y señal `go_back`. """
    pass


__all__ = ['ModuloPrincipal']
