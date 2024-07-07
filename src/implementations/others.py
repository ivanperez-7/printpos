from functools import wraps as _wraps

from haps import egg
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QObject as _QObject, Slot as _Slot, Signal as _Signal
from PySide6.QtGui import QIcon, QGuiApplication as _QGuiApplication

from interfaces import IWarningLogger


class _InvokeMethod(_QObject):
    called = _Signal()
    def __init__(self, method):
        """ Invokes a method on the main thread. Taking care of garbage collection "bugs". """
        super().__init__()

        main_thread = _QGuiApplication.instance().thread()
        self.moveToThread(main_thread)
        self.setParent(_QGuiApplication.instance())
        self.method = method
        self.called.connect(self.execute)
        self.called.emit()

    @_Slot()
    def execute(self):
        self.method()
        # trigger garbage collector
        self.setParent(None)

def _back_to_main(func):
    """ Función para forzar función en hilo principal. """

    @_wraps(func)
    def wrapper(*args, **kwargs):
        _InvokeMethod(lambda: func(*args, **kwargs))

    return wrapper


@egg
class WarningWidget(QMessageBox, IWarningLogger):
    def __init__(self):
        super().__init__()
    
    @_back_to_main
    def display(self, title: str, body: str = '') -> None:
        self.setWindowTitle('Atención')
        self.setWindowIcon(QIcon(':img/icon.ico'))
        self.setIcon(QMessageBox.Icon.Warning)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.setText(title)
        if body:
            self.setDetailedText(body)
        self.exec()
