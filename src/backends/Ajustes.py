from PySide6 import QtWidgets
from PySide6 import QtPrintSupport

from config import INI
from interfaces import IModuloPrincipal


#####################
# VENTANA PRINCIPAL #
#####################

class App_Ajustes(QtWidgets.QWidget, IModuloPrincipal):
    """ Backend para la ventana de administración de ventas. """

    def crear(self, conn, user):
        from ui.Ui_Ajustes import Ui_Ajustes

        self.ui = Ui_Ajustes()
        self.ui.setupUi(self)

        self.conn = conn
        self.user = user

        self.ui.boxImpresoras.addItems(QtPrintSupport.QPrinterInfo.availablePrinterNames())
        self.ui.boxImpresoras.setCurrentText(INI.IMPRESORA)

        self.ui.txtCalle1.setText(INI.CALLE_1)
        self.ui.txtCalle2.setText(INI.CALLE_2)
        self.ui.txtTelefono.setText(INI.TELEFONO)

        # crear eventos para los botones
        self.ui.btRegresar.clicked.connect(self._salir)
        #self.ui.btRespaldar.clicked.connect(self.respaldar_db)

    def _salir(self, _):
        """ Cierra la ventana y regresa a Home. """
        INI.IMPRESORA = self.ui.boxImpresoras.currentText()
        INI.CALLE_1 = self.ui.txtCalle1.text()
        INI.CALLE_2 = self.ui.txtCalle2.text()
        INI.TELEFONO = self.ui.txtTelefono.text()
        INI.guardar()

        self.go_back.emit()
