from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QRegExp

from dataclasses import dataclass
from mywidgets import VentanaPrincipal

import fdb

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
    def __init__(self):
        from Login.Ui_Login import Ui_Login
        
        super().__init__()

        self.ui = Ui_Login()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        
        # validador para nombre de usuario
        regexp = QRegExp(r'[a-zA-Z0-9_$]+')
        validador = QtGui.QRegExpValidator(regexp)
        self.ui.inputUsuario.setValidator(validador)
        
        self.ui.btIngresar.clicked.connect(self.verificar_info)

        self.show()
    
    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() in {Qt.Key_Return, Qt.Key_Enter}: 
            self.verificar_info()
    
    def verificar_info(self):
        """
        Verifica datos ingresados consultando la tabla Usuarios.
        """
        usuario = self.ui.inputUsuario.text().upper()
        psswd = self.ui.inputContrasenia.text()

        if not (usuario and psswd):
            self.ui.lbAdvertencia.setText('')
            return
        
        conn_a = crear_conexion(usuario, psswd, 'ADMINISTRADOR')
        conn_v = crear_conexion(usuario, psswd, 'VENDEDOR')
        
        if not conn_a and not conn_v:
            self.ui.lbAdvertencia.setText('¡El usuario y contraseña no son válidos!')
            return
        
        try:
            conn = conn_a
            crsr = conn.cursor()
            crsr.execute('SELECT * FROM Usuarios WHERE usuario = ?;', (usuario,))
        except Exception as err:
            print(str(err))
            
            conn = conn_v
            crsr = conn.cursor()
            crsr.execute('SELECT * FROM Usuarios WHERE usuario = ?;', (usuario,))
        
        result = crsr.fetchone()
        user = Usuario(*result)
        
        self.close()

        # crear ventana principal del sistema
        from Home import App_Home
        
        session = {'conn': conn, 'user': user}
        self.mainWindow = VentanaPrincipal(session, App_Home)
        
        self.conn = conn

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
