from dataclasses import dataclass
import socket

from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt, QMutex, Signal

from config import INI
import licensing
import sql
from utils.mydecorators import run_in_thread
from utils.myutils import FabricaValidadores

from PrintPOS import app


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

    def __post_init__(self):
        self.rol = self.rol.upper()

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
    validated = Signal()
    failure = Signal(licensing.Errores)

    logged = Signal(sql.Connection)
    warning = Signal(str)

    def __init__(self):
        from ui.Ui_Login import Ui_Login

        super().__init__()

        self.ui = Ui_Login()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())

        self.mutex = QMutex()

        # validador para nombre de usuario
        self.ui.inputUsuario.setValidator(FabricaValidadores.IdFirebird)

        self.logged.connect(self.crearVentanaPrincipal)
        self.warning.connect(self.crearWarningDialog)
        self.validated.connect(self.exito_verificacion)
        self.failure.connect(self.error_verificacion)

        self.ui.btAjustes.clicked.connect(lambda: AjustesDB(self))

        self.show()
        self.ui.inputUsuario.setFocus()

        if not app.licencia_validada:
            self.validar_licencia()
        else:
            self.exito_verificacion()

    def keyPressEvent(self, event):
        if event.key() in {Qt.Key_Return, Qt.Key_Enter}:
            self.ui.btIngresar.click()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @run_in_thread
    def validar_licencia(self):
        self.ui.lbEstado.setText('Verificando licencia...')

        activado, error = licensing.validar_licencia()
        if activado:
            self.validated.emit()
        else:
            self.failure.emit(error)

        self.ui.lbEstado.clear()
        app.licencia_validada = activado

    def exito_verificacion(self):
        """ En método separado para regresar al hilo principal."""
        self.ui.btIngresar.clicked.connect(self.verificar_info)
        print("exito_verificacion()")

    def error_verificacion(self, error):
        """ En método separado para regresar al hilo principal."""
        match error:
            case licensing.Errores.LICENCIA_NO_EXISTENTE:
                self.ui.btIngresar.clicked.connect(lambda: self._crear_dialogo(error))

            case licensing.Errores.LICENCIA_NO_VALIDA:
                self.ui.btIngresar.clicked.connect(lambda: self._crear_dialogo(error))

            case licensing.Errores.VERIFICACION_FALLIDA:
                QtWidgets.QMessageBox.warning(
                    self, 'Error al validar licencia',
                    'Ha ocurrido un error al validar su licencia en línea.\n'
                    'Por favor, verifique su acceso a internet e intente nuevamente.')

    def _crear_dialogo(self, error):
        wdg = DialogoActivacion(self)
        wdg.success.connect(lambda: (self.ui.btIngresar.clicked.disconnect(),
                                     self.exito_verificacion()))

        if error == licensing.Errores.LICENCIA_NO_VALIDA:
            wdg.ui.label.setText('¡Su licencia ha expirado!')

    @run_in_thread
    def verificar_info(self):
        """ Verifica datos ingresados consultando la tabla Usuarios. """
        if not self.mutex.try_lock():
            return

        # verificar que se ingresaron datos
        usuario = self.ui.inputUsuario.text().upper()
        psswd = self.ui.inputContrasenia.text()
        rol = self.ui.groupRol.checkedButton().text()

        if not (usuario and psswd):
            self.ui.lbEstado.clear()
            self.mutex.unlock()
            return

        self.ui.lbEstado.setStyleSheet('color: black;')
        self.ui.lbEstado.setText('Conectando a la base de datos...')

        try:
            conn = sql.conectar_db(usuario, psswd, rol)
            manejador = sql.ManejadorUsuarios(conn, handle_exceptions=False)
            manejador.obtenerUsuario(usuario)
        except sql.Error as err:
            txt, sqlcode, gdscode = err.args
            if gdscode in [335544472, 335544352]:
                self.ui.lbEstado.setStyleSheet('color: red;')
                self.ui.lbEstado.setText('¡El usuario y contraseña no son válidos!')
            else:
                self.warning.emit(txt)
        except Exception as err:  # arrojado por fdb al no encontrarse librería Firebird
            self.warning.emit(str(err))
        else:
            self.logged.emit(conn)
        finally:
            self.mutex.unlock()

    def crearWarningDialog(self, txt):
        from utils.mywidgets import WarningDialog
        self.ui.lbEstado.clear()
        wdg = WarningDialog('No se pudo acceder al servidor.', txt)

    def crearVentanaPrincipal(self, conn):
        """ En método separado para regresar al hilo principal."""
        from utils.mywidgets import VentanaPrincipal
        user = Usuario.generarUsuarioActivo(conn)
        self.mainWindow = VentanaPrincipal(conn, user)
        self.close()


########################
# WIDGET PERSONALIZADO #
########################
class AjustesDB(QtWidgets.QWidget):
    def __init__(self, parent=None):
        from ui.Ui_AjustesDB import Ui_AjustesDB

        super().__init__(parent)

        self.ui = Ui_AjustesDB()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)

        self.ui.lineNombre.setText(hn := socket.gethostname())
        self.ui.lineDireccion.setText(socket.gethostbyname(hn))
        self.ui.lineNombreServ.setText(INI.NOMBRE_SERVIDOR)

        self.ui.btAceptar.clicked.connect(self.done)
        self.ui.btRegresar.clicked.connect(self.close)

        self.show()

    def done(self):
        INI.NOMBRE_SERVIDOR = self.ui.lineNombreServ.text()
        INI.guardar()
        self.close()


class DialogoActivacion(QtWidgets.QWidget):
    success = Signal()
    failed = Signal(licensing.Errores)

    def __init__(self, parent=None):
        from ui.Ui_Activacion import Ui_Activacion

        super().__init__(parent)

        self.mutex = QMutex()

        self.ui = Ui_Activacion()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)

        self.ui.btActivar.clicked.connect(self.accept)
        self.ui.btCerrar.clicked.connect(self.close)

        self.success.connect(self.exito_verificacion)
        self.failed.connect(self.error_verificacion)

        self.show()

    @run_in_thread
    def accept(self):
        licencia = self.ui.lineLicencia.text().strip()
        if not (licencia and self.mutex.try_lock()):
            return

        activado, error = licensing.activar_licencia(licencia)
        if activado:
            self.success.emit()
        else:
            self.failed.emit(error)
        self.mutex.unlock()

    def exito_verificacion(self):
        """ En método separado para regresar al hilo principal."""
        self.close()
        QtWidgets.QMessageBox.information(
            self, 'Licencia activada',
            '¡Muchas gracias por adquirir PrintPOS!\n'
            'Su licencia ha sido activada con éxito.'
        )

    def error_verificacion(self, error):
        """ En método separado para regresar al hilo principal."""
        match error:
            case licensing.Errores.ACTIVACION_FALLIDA:
                txt = ('Ha ocurrido un error al activar su licencia en línea.\n'
                       'Por favor, verifique su acceso a internet e intente nuevamente.')

            case licensing.Errores.ACTIVACION_NO_VALIDA:
                txt = ('La clave ingresada no es válida. Por favor, verifique este dato.\n'
                       'Si el problema persiste, será necesario que contacte a soporte.')
        QtWidgets.QMessageBox.warning(self, 'Activación fallida', txt)


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
            color: #fff;
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
