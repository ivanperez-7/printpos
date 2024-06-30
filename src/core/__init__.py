""" Paquete con módulos de utilidades varias (widgets, interfaces, 
    manejadores SQL, etc.) para uso en diversas partes del sistema. """
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QThread

from .moneda import Moneda


# validadores
IdFirebird = QRegularExpressionValidator(r'[a-zA-Z0-9_$]+')
NumeroDecimal = QRegularExpressionValidator(r'(\d*\.\d+|\d+\.\d*|\d+)')

# colores para GUI
VERDE = 0xB2FFAE
AMARILLO = 0xFDFDA9
ROJO = 0xFFB2AE

# subclase de QThread para async
class Runner(QThread):
    """ Clase derivada de QThread para manejar manualmente cuándo un hilo comienza y termina.
        Para manejo automático, usar decorador `run_in_thread`. """

    def __init__(self, target, *args, **kwargs):
        super().__init__()
        self._target = target
        self._args = args
        self._kwargs = kwargs

    def run(self):
        self._target(*self._args, **self._kwargs)
