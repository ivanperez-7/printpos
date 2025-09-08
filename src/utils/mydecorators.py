""" Módulo para implementar decoradores útiles varios. """

from functools import wraps

from PySide6.QtWidgets import QWidget, QMessageBox, QDialog
from PySide6.QtGui import QIcon
from PySide6.QtCore import QThreadPool, QRunnable, Signal

from sql import DatabaseManager
from sql.core import conectar_firebird, FirebirdError

__all__ = ['requiere_admin', 'run_in_thread', 'fondo_oscuro', 'function_details']


def function_details(func):
    # argument names of the called function
    argnames = func.__code__.co_varnames[: func.__code__.co_argcount]
    # function name of the called function
    fname = func.__name__

    def inner_func(*args, **kwargs):
        print(f'{fname}(', end='')
        # printing the function arguments
        print(
            *('{} = {}'.format(name, val) for name, val in zip(argnames, args)), sep=', ', end=', ',
        )
        # printing the variable length Arguments
        print('args =', list(args[len(argnames) :]), end=', ')
        # printing the variable length keyword arguments
        print(f'kwargs = {kwargs})')
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
        self.setWindowTitle('Requiere administrador')
        self.setWindowIcon(QIcon(':img/icon.ico'))
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.formLayout = QtWidgets.QFormLayout(self)
        self.formLayout.setObjectName('formLayout')
        self.label = QtWidgets.QLabel(self)
        self.label.setObjectName('label')
        self.label.setText('Esta acción requiere de una cuenta de administrador.')
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.label)
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setObjectName('label_2')
        self.label_2.setText('Usuario:')
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.txtUsuario = QtWidgets.QLineEdit(self)
        self.txtUsuario.setObjectName('txtUsuario')
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.txtUsuario)
        self.label_3 = QtWidgets.QLabel(self)
        self.label_3.setObjectName('label_3')
        self.label_3.setText('Contraseña:')
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.txtPsswd = QtWidgets.QLineEdit(self)
        self.txtPsswd.setObjectName('txtPsswd')
        self.txtPsswd.setEchoMode(QtWidgets.QLineEdit.Password)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.txtPsswd)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setObjectName('buttonBox')
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.SpanningRole, self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def accept(self):
        usuario = self.txtUsuario.text()
        psswd = self.txtPsswd.text()

        if not (usuario and psswd):
            return
        try:
            conn = conectar_firebird(usuario, psswd, 'ADMINISTRADOR')
            manejador = DatabaseManager(conn)
        except (FirebirdError, AssertionError):
            self.close()
            wdg = QMessageBox(
                QMessageBox.Warning,
                'Permiso denegado',
                'Las credenciales no son válidas para una cuenta de administrador.',
            )
            wdg.setWindowIcon(QIcon(':img/icon.ico'))
            wdg.exec()
        else:
            self.close()
            self.success.emit(conn)
            conn.close()


def requiere_admin(func):
    """ Decorador para solicitar contraseña de administrador
    antes de ejecutar alguna función. Requiere que el parent tenga atributos
    `conn` y `user`, donde `user` debe tener atributo `administrador`.

    >>> @requiere_admin
    ... def abortar_venta():
    ...     print("función secreta!")

    Se puede añadir parámetro nombrado `conn` al final de la función envuelta,
    ya que es devuelto por el decorador para extraer información que se requiera
    de la conexión de administrador, por ejemplo, nombre del administrador.

    >>> @requiere_admin
    ... def abortar_venta(conn):
    ...     man = sql.ManejadorVentas(conn)
    ...     print(man.nombreUsuarioActivo)

    Por el momento, no se puede usar un return en una función envuelta. """

    @wraps(func)
    def wrapper_decorator(*args, **kwargs):
        def admin_func(conn):
            try:
                func(*args, **kwargs, conn=conn)
            except TypeError:
                func(*args, **kwargs)

        try:
            parent = args[0]  # QWidget (módulo actual)
            assert parent.conn and parent.user

            if parent.user.administrador:
                admin_func(parent.conn)
            else:
                raise AttributeError
        except (IndexError, AttributeError):
            dialog = Dialog_ObtenerAdmin()
            dialog.success.connect(admin_func)
            dialog.exec()

    return wrapper_decorator


###############################################
# </DECORADOR PARA SOLICITAR CUENTA DE ADMIN> #
###############################################


########################################
# <DECORADOR PARA EEJCUTAR EN QTHREAD> #
########################################
class _Runnable(QRunnable):
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
        task = _Runnable(func, *args, **kwargs)
        QThreadPool.globalInstance().start(task)

    return async_func


#########################################
# </DECORADOR PARA EEJCUTAR EN QTHREAD> #
#########################################


def fondo_oscuro(widget):
    """ Decorador para crear un fondo oscurecedor en la ventana principal.
    Requiere widget padre que, por convención para este proyecto, al ser requerido
    en el constructor, siempre se pasa como último parámetro del widget hijo. """
    orig_init = widget.__init__
    orig_show = widget.showEvent
    orig_close = widget.closeEvent

    def __init__(self, *args, **kwargs):
        self.bg_parent = args[-1]
        orig_init(self, *args, **kwargs)

    def showEvent(self, event):
        try:
            orig_show(self, event)
            if self.bg_parent:
                wdg = QWidget(self.bg_parent)  # widget padre (módulo actual)
                wdg.setFixedSize(self.bg_parent.size())
                wdg.setStyleSheet('background: rgba(64, 64, 64, 64);')
                wdg.show()
                self.bg = wdg
        except TypeError as err:
            print('fondo_oscuro error !!\n', str(err))
            self.bg = None

    def closeEvent(self, event):
        try:
            orig_close(self, event)
            if event.isAccepted():
                self.bg.close()
        except AttributeError:
            pass

    widget.__init__ = __init__
    widget.showEvent = showEvent
    widget.closeEvent = closeEvent

    return widget
