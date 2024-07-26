from PySide6.QtCore import QThread


class Runner(QThread):
    """Clase derivada de QThread para manejar manualmente cuándo un hilo comienza y termina.
    Para manejo automático, usar decorador `run_in_thread`."""

    def __init__(self, target, *args, **kwargs):
        super().__init__()
        self._target = target
        self._args = args
        self._kwargs = kwargs

    def run(self):
        self._target(*self._args, **self._kwargs)
