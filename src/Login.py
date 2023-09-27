from dataclasses import dataclass

from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt, Signal
import PySide6.QtGui

from utils.mydecorators import run_in_thread
from utils.myutils import FabricaValidadores
from utils import sql


##################
# CLASE AUXILIAR #
##################
@dataclass
class Usuario:
    """ Clase para mantener registro de un usuario. """
    id: int
    usuario: str
    nombre: str
    permisos: str = 'Vendedor'
    foto_perfil: bytes = None
    rol: str = 'Vendedor'
    
    @property
    def administrador(self):
        """ Regresa un booleano que dice si el usuario es administrador. """
        return self.permisos.upper() == 'ADMINISTRADOR'
    
    @classmethod
    def generarUsuarioActivo(cls, conn: sql.Connection):
        """ Genera clase Usuario dada una conexión válida a la DB. """
        manejador = sql.ManejadorUsuarios(conn)
        usuario = manejador.identificadorUsuarioActivo
        result = manejador.obtenerUsuario(usuario)
        
        return cls(*result, manejador.rolActivo)


#####################
# VENTANA PRINCIPAL #
#####################
class App_Login(QtWidgets.QWidget):
    """ Backend para la pantalla de inicio de sesión. """
    validated = Signal(sql.Connection)
    
    def __init__(self):
        from ui.Ui_Login import Ui_Login
        
        super().__init__()
        
        self.ui = Ui_Login()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        
        self.lock = False
        
        # validador para nombre de usuario
        self.ui.inputUsuario.setValidator(FabricaValidadores.IdFirebird)
        
        self.ui.btIngresar.clicked.connect(
            lambda: self.verificar_info() if not self.lock else None)
        self.validated.connect(self.crearVentanaPrincipal)
        
        self.show()
    
    def keyPressEvent(self, event):
        if event.key() in {Qt.Key_Return, Qt.Key_Enter} and not self.lock:
            self.verificar_info()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @run_in_thread
    def verificar_info(self):
        """ Verifica datos ingresados consultando la tabla Usuarios. """
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
        conn = sql.conectar_db(usuario, psswd, rol)
        
        try:
            manejador = sql.ManejadorUsuarios(conn, handle_exceptions=False)
            manejador.obtenerUsuario(usuario)
        except sql.Error as err:
            print(err.args[0])
            self.ui.lbEstado.setStyleSheet('color: rgb(255, 0, 0);')
            self.ui.lbEstado.setText('¡El usuario y contraseña no son válidos!')
            self.lock = False
            return
        
        self.validated.emit(conn)
    
    def crearVentanaPrincipal(self, conn):
        """ En método separado para regresar al hilo principal."""
        from utils.mywidgets import VentanaPrincipal
        
        self.close()
        self.mainWindow = VentanaPrincipal(conn)


########################
# WIDGET PERSONALIZADO #
########################
class LoginButton(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.color1 = QtGui.QColor(240, 53, 218)
        self.color2 = QtGui.QColor(61, 217, 245)

        self._animation = QtCore.QVariantAnimation(
            self,
            valueChanged=self._animate,
            startValue=0.00001,
            endValue=0.9999,
            duration=250
        )

    def _animate(self, value):
        qss = """
            font: 75 10pt "Segoe UI";
            font-weight: bold;
            color: rgb(255, 255, 255);
            border-style: solid;
            border-radius: 15px;
            outline: 0px;
        """
        grad = """
            background-color: qlineargradient(
                spread:pad, x1:0, y1:0, x2:1, y2:0,
                stop:0 {color1}, stop:{value} {color2}, stop: 1.0 {color1});
        """.format(color1=self.color1.name(), color2=self.color2.name(), value=value)
        
        self.setStyleSheet(qss + grad)

    def enterEvent(self, event):
        self._animation.setDirection(QtCore.QAbstractAnimation.Forward)
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animation.setDirection(QtCore.QAbstractAnimation.Backward)
        self._animation.start()
        super().leaveEvent(event)
