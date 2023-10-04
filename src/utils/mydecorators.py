""" Módulo para implementar decoradores útiles varios. """
from functools import wraps

from PySide6.QtWidgets import QMessageBox, QDialog
from PySide6.QtCore import QThreadPool, QRunnable, Signal


__all__ = ['requiere_admin', 'run_in_thread', 'con_fondo']


##############################################
# <DECORADOR PARA SOLICITAR CUENTA DE ADMIN> #
##############################################
class Dialog_ObtenerAdmin(QDialog):
    success = Signal(object)
    
    def __init__(self, parent=None):
        from PySide6 import QtCore, QtGui, QtWidgets
        
        super().__init__(parent)
        
        self.resize(370, 116)
        self.setFixedSize(QtCore.QSize(370, 116))
        self.setWindowTitle("Atención")
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.formLayout = QtWidgets.QFormLayout(self)
        self.formLayout.setHorizontalSpacing(15)
        self.formLayout.setVerticalSpacing(6)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label = QtWidgets.QLabel("Esta acción requiere de una cuenta de administrador.", self)
        self.label.setFont(font)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.label)
        self.label_2 = QtWidgets.QLabel("Usuario:", self)
        self.label_2.setFont(font)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.txtUsuario = QtWidgets.QLineEdit(self)
        self.txtUsuario.setFont(font)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.txtUsuario)
        self.label_3 = QtWidgets.QLabel("Contraseña:", self)
        self.label_3.setFont(font)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.txtPsswd = QtWidgets.QLineEdit(self)
        self.txtPsswd.setFont(font)
        self.txtPsswd.setEchoMode(QtWidgets.QLineEdit.Password)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.txtPsswd)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.SpanningRole, self.buttonBox)
        
        self.buttonBox.accepted.connect(self.accept)  # type: ignore
        self.buttonBox.rejected.connect(self.reject)  # type: ignore
        QtCore.QMetaObject.connectSlotsByName(self)

    def accept(self):
        from utils import sql
        
        usuario = self.txtUsuario.text().upper()
        psswd = self.txtPsswd.text()
        
        if not (usuario and psswd):
            return
        
        conn = sql.conectar_db(usuario, psswd, 'ADMINISTRADOR')
        try:
            manejador = sql.ManejadorUsuarios(conn, handle_exceptions=False)
            manejador.obtenerUsuario(usuario)
        except sql.Error:
            self.close()
            QMessageBox.warning(self.parentWidget(), 'Error',
                                'Las credenciales no son válidas para una cuenta de administrador.')
        else:
            self.close()
            self.success.emit(conn)
            conn.close()

def requiere_admin(func):
    """ Decorador para solicitar contraseña de administrador
        antes de ejecutar alguna función dada.
        
        Añadir parámetro nombrado `conn` al final de la función, ya que
        es devuelto por el decorador para extraer información que se requiera
        de la conexión de administrador, por ejemplo, nombre del administrador. """
    @wraps(func)
    def wrapper_decorator(*args, **kwargs):
        parent = args[0]  # QWidget (módulo actual)
        
        if parent.user.administrador:
            func(*args, **kwargs, conn=parent.conn)
        else:
            dialog = Dialog_ObtenerAdmin(parent)
            dialog.success.connect(lambda conn: func(*args, **kwargs, conn=conn))
            dialog.show()
    
    return wrapper_decorator
###############################################
# </DECORADOR PARA SOLICITAR CUENTA DE ADMIN> #
###############################################


########################################
# <DECORADOR PARA EEJCUTAR EN QTHREAD> #
########################################
class Runner(QRunnable):
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self._func = func
        self._args = args
        self._kwargs = kwargs
    
    def run(self):
        self._func(*self._args, **self._kwargs)
    
def run_in_thread(func):
    """ Decorador para ejecutar alguna función dada en otro hilo. """
    @wraps(func)
    def async_func(*args, **kwargs):
        task = Runner(func, *args, **kwargs)
        QThreadPool.globalInstance().start(task)
    return async_func
#########################################
# </DECORADOR PARA EEJCUTAR EN QTHREAD> #
#########################################


def con_fondo(modulo):
    """ Decorador para crear un fondo oscurecedor en la ventana principal. """
    orig_init = modulo.__init__
    
    def __init__(self, *args, **kwargs):
        from utils.mywidgets import DimBackground
        
        orig_init(self, *args, **kwargs)
        
        parent = args[0]  # QMainWindow, parent widget
        parent.bg = DimBackground(parent)
    
    def closeEvent(self, event):
        self.parentWidget().bg.close()
        event.accept()
    
    modulo.__init__ = __init__
    modulo.closeEvent = closeEvent
    
    return modulo
