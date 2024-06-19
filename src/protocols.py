""" Módulo para proveedores de type hinting. """
from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal

if TYPE_CHECKING:
    import sql
    from utils.mydataclasses import Usuario


class HasConnUser:
    """ Clase para type-hinting de atributos persistentes `conn` y `user`. """
    conn: sql.Connection
    user: Usuario
    

class ModuloPrincipal(QWidget, HasConnUser):
    """ Subclase de QWidget para módulo principal, con atributos persistentes
        `conn`, `user` y señal `go_back`. """
    go_back: Signal = Signal()


__all__ = ['ModuloPrincipal', 'HasConnUser']
