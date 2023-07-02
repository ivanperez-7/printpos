from dataclasses import dataclass

import fdb

from PyQt5 import QtWidgets
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp, pyqtSignal

from mydecorators import run_in_thread


##################
# CLASE AUXILIAR #
##################
@dataclass
class Usuario:
    """
    Clase para mantener registro de un usuario.
    """
    id: int
    usuario: str
    nombre: str
    permisos: str
    foto_perfil: bytes

    @property
    def administrador(self) -> bool:
        """
        Regresa un booleano que dice si el usuario es administrador.
        """
        return self.permisos == 'Administrador'

#####################
# VENTANA PRINCIPAL #
#####################
class App_Login(QtWidgets.QMainWindow):
    """
    Backend para la pantalla de inicio de sesión.
    """
    validated = pyqtSignal(object, object)
    
    def __init__(self):
        from Login.Ui_Login import Ui_Login
        
        super().__init__()

        self.ui = Ui_Login()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        
        self.lock = False
        
        # validador para nombre de usuario
        regexp = QRegExp(r'[a-zA-Z0-9_$]+')
        validador = QRegExpValidator(regexp)
        self.ui.inputUsuario.setValidator(validador)
        
        self.ui.btIngresar.clicked.connect(lambda: self.verificar_info() if not self.lock else None)
        self.validated.connect(self.crearVentanaPrincipal)

        self.show()
    
    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() in {Qt.Key_Return, Qt.Key_Enter} and not self.lock: 
            self.verificar_info()
    
    @run_in_thread
    def verificar_info(self):
        """
        Verifica datos ingresados consultando la tabla Usuarios.
        """
        self.lock = True
            
        usuario = self.ui.inputUsuario.text().upper()
        psswd = self.ui.inputContrasenia.text()

        if not (usuario and psswd):
            self.ui.lbEstado.clear()
            self.lock = False
            return
        
        self.ui.lbEstado.setStyleSheet('color: rgb(0, 0, 0);')
        self.ui.lbEstado.setText('Conectando a la base de datos...')
        
        conn_a = crear_conexion(usuario, psswd, 'ADMINISTRADOR')
        
        if conn_a:
            conn_v = crear_conexion(usuario, psswd, 'VENDEDOR')
        else:
            self.ui.lbEstado.setStyleSheet('color: rgb(255, 0, 0);')
            self.ui.lbEstado.setText('¡El usuario y contraseña no son válidos!')
            self.lock = False
            return
        
        try:
            conn = conn_a
            crsr = conn.cursor()
            crsr.execute('SELECT * FROM Usuarios WHERE usuario = ?;', (usuario,))
        except fdb.Error as err:
            print(str(err))
            
            conn = conn_v
            crsr = conn.cursor()
            crsr.execute('SELECT * FROM Usuarios WHERE usuario = ?;', (usuario,))
        
        result = crsr.fetchone()
        user = Usuario(*result)
        
        self.validated.emit(conn, user)

    def crearVentanaPrincipal(self, conn, user):
        """
        En método separado para regresar al hilo principal.
        """
        from mywidgets import VentanaPrincipal
        
        self.close()
        self.mainWindow = VentanaPrincipal(conn, user)

########################
# FUNCIONES DEL MÓDULO #
########################
def crear_conexion(usuario: str, psswd: str, rol: str):
    from configparser import ConfigParser
    
    # leer datos de config.ini
    config = ConfigParser(inline_comment_prefixes=';')
    config.read('config.ini')

    red_local = config['DEFAULT']['red_local']
    
    try:
        conn = fdb.connect(
                    dsn=red_local + ':pensiones.fdb',
                    user=usuario,
                    password=psswd,
                    charset='UTF8',
                    role=rol)
        return conn
    except fdb.Error as err:
        print(f'Cannot open connection to database: {str(err)}')
        return None
