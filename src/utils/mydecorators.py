""" Módulo para implementar decoradores útiles varios. """
from functools import wraps

from PySide6.QtWidgets import QMessageBox, QDialog
from PySide6.QtCore import QThreadPool, QRunnable, Signal

import sql
from .mywidgets import DimBackground

__all__ = ['requiere_admin', 'run_in_thread', 'fondo_oscuro', 'function_details']


def function_details(func): 
    # argument names of the called function 
    argnames = func.__code__.co_varnames[:func.__code__.co_argcount] 
    # function name of the called function 
    fname = func.__name__ 

    def inner_func(*args, **kwargs): 
        print(fname, "(", end = "") 
        # printing the function arguments 
        print(', '.join( '% s = % r' % entry 
                        for entry in zip(argnames, args[:len(argnames)])), end = ", ") 
        # printing the variable length Arguments 
        print("args =", list(args[len(argnames):]), end = ", ") 
        # printing the variable length keyword arguments
        print("kwargs =", kwargs, end = "")
        print(")")
        return func(*args, **kwargs)

    return inner_func 


##############################################
# <DECORADOR PARA SOLICITAR CUENTA DE ADMIN> #
##############################################
class Dialog_ObtenerAdmin(QDialog):
    success = Signal(object)

    def __init__(self, parent=None):  # código GUI
        from PySide6 import QtCore, QtWidgets

        super().__init__(parent)

        self.setFixedSize(380, 120)
        self.setWindowTitle("Requiere administrador")
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.formLayout = QtWidgets.QFormLayout(self)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QtWidgets.QLabel(self)
        self.label.setObjectName(u"label")
        self.label.setText("Esta acción requiere de una cuenta de administrador.")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.label)
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setText("Usuario:")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.txtUsuario = QtWidgets.QLineEdit(self)
        self.txtUsuario.setObjectName(u"txtUsuario")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.txtUsuario)
        self.label_3 = QtWidgets.QLabel(self)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setText("Contraseña:")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.txtPsswd = QtWidgets.QLineEdit(self)
        self.txtPsswd.setObjectName(u"txtPsswd")
        self.txtPsswd.setEchoMode(QtWidgets.QLineEdit.Password)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.txtPsswd)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.SpanningRole, self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def accept(self):
        usuario = self.txtUsuario.text().upper()
        psswd = self.txtPsswd.text()

        if not (usuario and psswd):
            return
        try:
            conn = sql.conectar_db(usuario, psswd, 'ADMINISTRADOR')
            manejador = sql.ManejadorUsuarios(conn, handle_exceptions=False)
            manejador.obtenerUsuario(usuario)
        except sql.Error:
            self.close()
            QMessageBox.warning(self.parentWidget(), 'Permiso denegado',
                                'Las credenciales no son válidas para una cuenta de administrador.')
        else:
            self.close()
            self.success.emit(conn)
            conn.close()


def requiere_admin(func):
    """ Decorador para solicitar contraseña de administrador
        antes de ejecutar alguna función envuelta.
        
        Añadir parámetro nombrado `conn` al final de la función envuelta, ya que
        es devuelto por el decorador para extraer información que se requiera
        de la conexión de administrador, por ejemplo, nombre del administrador.
        
        Requiere que QWidget tenga atributo `user` (objeto mydataclasses.Usuario actual)
        y atributo `conn` (objeto sql.Connection actual). """

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
class _Runner(QRunnable):
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
        task = _Runner(func, *args, **kwargs)
        QThreadPool.globalInstance().start(task)

    return async_func


#########################################
# </DECORADOR PARA EEJCUTAR EN QTHREAD> #
#########################################


def fondo_oscuro(modulo):
    """ Decorador para crear un fondo oscurecedor en la ventana principal.
        NOTA: Modifica método closeEvent para cerrar fondo automáticamente. """
    orig_init = modulo.__init__
    orig_close = modulo.closeEvent

    def __init__(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        self.bg = DimBackground(args[0]) # args[0] = widget padre (módulo actual)

    def closeEvent(self, event):
        orig_close(self, event)
        self.bg.close()

    modulo.__init__ = __init__
    modulo.closeEvent = closeEvent

    return modulo
