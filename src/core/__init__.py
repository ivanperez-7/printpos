""" Paquete con módulos de utilidades varias (widgets, interfaces, 
    manejadores SQL, etc.) para uso en diversas partes del sistema. """

from PySide6.QtGui import QRegularExpressionValidator as _QRegExpVal

from .daterange import DateRange
from .moneda import Moneda
from .runner import Runner


# validadores
IdFirebird = _QRegExpVal(r"[a-zA-Z0-9_$]+")
NumeroDecimal = _QRegExpVal(r"(\d*\.\d+|\d+\.\d*|\d+)")

# colores para GUI
VERDE = 0xB2FFAE
AMARILLO = 0xFDFDA9
ROJO = 0xFFB2AE
