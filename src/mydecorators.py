"""
Módulo para implementar decoradores útiles varios.
"""
from PyQt5.QtWidgets import QMessageBox, QDialog
from PyQt5.QtCore import QThread, pyqtSignal

from functools import wraps
import fdb


##############################################
# <DECORADOR PARA SOLICITAR CUENTA DE ADMIN> #
##############################################
class Dialog_ObtenerAdmin(QDialog):
    success = pyqtSignal()
    
    def __init__(self, parent):
        from PyQt5 import QtCore, QtGui, QtWidgets
        
        super().__init__(parent)
        
        self.resize(370, 116)
        self.setMinimumSize(QtCore.QSize(370, 116))
        self.setMaximumSize(QtCore.QSize(370, 116))
        self.setWindowTitle("Atención")
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.formLayout = QtWidgets.QFormLayout(self)
        self.formLayout.setHorizontalSpacing(15)
        self.formLayout.setVerticalSpacing(6)
        self.label = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setText("Esta acción requiere de una cuenta de administrador.")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.label)
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setFont(font)
        self.label_2.setText("Usuario:")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.txtUsuario = QtWidgets.QLineEdit(self)
        self.txtUsuario.setFont(font)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.txtUsuario)
        self.label_3 = QtWidgets.QLabel(self)
        self.label_3.setFont(font)
        self.label_3.setText("Contraseña:")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.txtPsswd = QtWidgets.QLineEdit(self)
        self.txtPsswd.setFont(font)
        self.txtPsswd.setEchoMode(QtWidgets.QLineEdit.Password)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.txtPsswd)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.SpanningRole, self.buttonBox)

        self.buttonBox.accepted.connect(self.accept) # type: ignore
        self.buttonBox.rejected.connect(self.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.show()

def requiere_admin(func):
    def accept_handle():
        global dialog
        global parent
        
        from Login.App_Login import crear_conexion
        
        usuario = dialog.txtUsuario.text().upper()
        psswd = dialog.txtPsswd.text()
        
        if not (usuario and psswd):
            return
        
        conn = crear_conexion(usuario, psswd, 'ADMINISTRADOR')
        
        if not conn:
            dialog.close()
            QMessageBox.warning(parent, 'Error', 
                                'Las credenciales no son válidas para una cuenta de administrador.')
            return
        
        try:
            crsr = conn.cursor()
            crsr.execute('SELECT permisos FROM Usuarios WHERE usuario = ?;', (usuario,))
        except fdb.Error as err:
            print(str(err))
            
            dialog.close()
            QMessageBox.warning(parent, 'Error', 
                                'Las credenciales no son válidas para una cuenta de administrador.')
        else:
            dialog.success.emit()
            dialog.close()
            conn.close()
    
    @wraps(func)
    def wrapper_decorator(*args, **kwargs):
        global dialog
        global parent
        
        parent = args[0]    # QMainWindow (módulo) actual
        
        if parent.session['user'].administrador:
            func(*args, **kwargs)
            return
        
        dialog = Dialog_ObtenerAdmin(parent)
        dialog.accept = accept_handle
        dialog.success.connect(lambda: func(*args, **kwargs))
        
        dialog.show()
        
    return wrapper_decorator
###############################################
# </DECORADOR PARA SOLICITAR CUENTA DE ADMIN> #
###############################################


########################################
# <DECORADOR PARA EEJCUTAR EN QTHREAD> #
########################################
class Runner(QThread):
    success = pyqtSignal()

    def __init__(self, target, *args, **kwargs):
        super().__init__()
        self._target = target
        self._args = args
        self._kwargs = kwargs

    def run(self):
        self._target(*self._args, **self._kwargs)
        self.success.emit()

def run_in_thread(func):
    @wraps(func)
    def async_func(*args, **kwargs):
        runner = Runner(func, *args, **kwargs)
        runner.success.connect(runner.quit)
        runner.success.connect(runner.deleteLater)
        # Keep the runner somewhere or it will be destroyed
        func.__runner = runner
        runner.start()

    return async_func
#########################################
# </DECORADOR PARA EEJCUTAR EN QTHREAD> #
#########################################


def con_fondo(modulo):
    """
    Decorador para crear un fondo oscurecedor en la ventana principal.
    """
    orig_init = modulo.__init__

    def __init__(self, *args, **kws):
        from mywidgets import DimBackground
        
        orig_init(self, *args, **kws)
        
        parent = args[0]   # QMainWindow, parent widget
        parent.bg = DimBackground(parent)
    
    def closeEvent(self, event):
        self.parentWidget().bg.close()
        self.close()

    modulo.__init__ = __init__
    modulo.closeEvent = closeEvent
    
    return modulo
