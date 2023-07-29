from dataclasses import dataclass

from PySide6 import QtWidgets
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import Qt, QRegularExpression, Signal

from utils.mydecorators import run_in_thread


##################
# CLASE AUXILIAR #
##################
@dataclass
class Usuario:
    """ Clase para mantener registro de un usuario. """
    id: int
    usuario: str
    nombre: str
    permisos: str
    foto_perfil: bytes
    rol: str

    @property
    def administrador(self) -> bool:
        """ Regresa un booleano que dice si el usuario es administrador. """
        return self.permisos == 'Administrador'


#####################
# VENTANA PRINCIPAL #
#####################
class App_Login(QtWidgets.QMainWindow):
    """ Backend para la pantalla de inicio de sesión. """
    validated = Signal(object, object)

    def __init__(self):
        from ui.Ui_Login import Ui_Login

        super().__init__()

        self.ui = Ui_Login()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())

        self.lock = False

        # validador para nombre de usuario
        regexp = QRegularExpression(r'[a-zA-Z0-9_$]+')
        validador = QRegularExpressionValidator(regexp)
        self.ui.inputUsuario.setValidator(validador)

        self.ui.btIngresar.clicked.connect(
            lambda: self.verificar_info() if not self.lock else None)
        self.validated.connect(self.crearVentanaPrincipal)

        self.show()

    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() in {Qt.Key_Return, Qt.Key_Enter} and not self.lock:
            self.verificar_info()

    @run_in_thread
    def verificar_info(self):
        """ Verifica datos ingresados consultando la tabla Usuarios. """
        from utils.databasemanagers import crear_conexion, ManejadorUsuarios

        self.lock = True

        usuario = self.ui.inputUsuario.text().upper()
        psswd = self.ui.inputContrasenia.text()

        if not (usuario and psswd):
            self.ui.lbEstado.clear()
            self.lock = False
            return

        self.ui.lbEstado.setStyleSheet('color: rgb(0, 0, 0);')
        self.ui.lbEstado.setText('Conectando a la base de datos...')

        rol = self.ui.groupRol.checkedButton().text()
        conn = crear_conexion(usuario, psswd, rol)

        if not conn:
            self.errorLogin()
            return

        try:
            manejador = ManejadorUsuarios(conn, handle_exceptions=False)
            result = manejador.obtenerUsuario(usuario)
        except Exception as err:
            print(str(err))
            self.errorLogin()
            return

        user = Usuario(*result, rol)
        self.validated.emit(conn, user)

    def errorLogin(self):
        """ Error al iniciar sesión. """
        self.ui.lbEstado.setStyleSheet('color: rgb(255, 0, 0);')
        self.ui.lbEstado.setText('¡El usuario y contraseña no son válidos!')
        self.lock = False

    def crearVentanaPrincipal(self, conn, user):
        """ En método separado para regresar al hilo principal."""
        from utils.mywidgets import VentanaPrincipal

        self.close()
        self.mainWindow = VentanaPrincipal(conn, user)
