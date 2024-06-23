import glob
import os

from injector import inject
from PySide6.QtGui import QIcon

#from backends.AdministrarProductos import App_ConsultarPrecios
from backends.CrearVenta import App_CrearVenta
#from backends.Login import App_Login
from factoriamodulos import FactoriaModulosPrincipales
from protocols import ModuloPrincipal, VentanaPrincipal


class MyMainWindow(VentanaPrincipal):
    
    @inject
    def __init__(self, conn, user):
        super().__init__()

        self.resize(1500, 800)
        self.setWindowTitle('PrintPOS')
        self.setWindowIcon(QIcon(':img/icon.ico'))

        self.conn = conn
        self.user = user
        self.factoria = FactoriaModulosPrincipales()

        #self.consultarPrecios = App_ConsultarPrecios(conn)

        self.go_home()
        self.show()

    def go_home(self):
        """ Regresar al menú principal.
            Crea módulo Home y establece como widget principal. """
        home: ModuloPrincipal = self.factoria.crear_modulo('App_Home')
        home.go_back.connect(self.close)
        home.new_module.connect(self.go_to)
        self.setCentralWidget(home)
    
    def go_to(self, modulo: str):
        new: ModuloPrincipal = self.factoria.crear_modulo(modulo)
        new.go_back.connect(self.go_home)
        self.setCentralWidget(new)

    @property
    def en_venta(self):
        return isinstance(self.centralWidget(), App_CrearVenta)

    def closeEvent(self, event):
        """ En eventos específicos, restringimos el cerrado del sistema. """
        if self.en_venta and not self.user.administrador:
            event.ignore()
            return

        for j in glob.glob('*.jpg'):
            os.remove(j)
        self.conn.close()
        #self.consultarPrecios.close()
        
        from backends.Login import App_Login
        login = App_Login()
