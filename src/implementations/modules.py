import glob
import os

from haps import egg
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QIcon

from context import user_context
from backends.ConsultarPrecios import App_ConsultarPrecios
from factorias import crear_modulo
from interfaces import IControllerWindow


@egg
class VentanaPrincipal(QMainWindow, IControllerWindow):  # TODO: clase App -> Inject()
    en_venta = False

    def crear(self):
        self.resize(1500, 800)
        self.setWindowTitle('PrintPOS')
        self.setWindowIcon(QIcon(':img/icon.ico'))

        self.conn = user_context.conn
        self.user = user_context.user

        self.consultarPrecios = App_ConsultarPrecios()

        self.go_home()
        self.show()

    def go_home(self):
        """ Regresar al menú principal.
        Crea módulo Home y establece como widget principal. """
        home = crear_modulo('App_Home')

        home.crear()
        home.go_back.connect(self.close)
        home.new_module.connect(self.go_to)

        self.setCentralWidget(home)
        self.en_venta = False

    def go_to(self, modulo: str):
        new = crear_modulo(modulo)
        new.crear()
        new.go_back.connect(self.go_home)

        self.setCentralWidget(new)
        self.en_venta = modulo == 'App_CrearVenta'

    def closeEvent(self, event):
        """ En eventos específicos, restringimos el cerrado del sistema. """
        if self.en_venta and not self.user.administrador:
            event.ignore()
            return

        for j in glob.glob('auto-*'):
            os.remove(j)
        self.conn.close()

        if self.consultarPrecios:
            self.consultarPrecios.close()
        login = crear_modulo('App_Login')
