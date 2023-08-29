from dataclasses import dataclass

from PySide6 import QtWidgets
from PySide6.QtCore import Qt, Signal

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
    def administrador(self) -> bool:
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
    
    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() in {Qt.Key_Return, Qt.Key_Enter} and not self.lock:
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
