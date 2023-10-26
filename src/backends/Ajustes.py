from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import QDate, QDateTime, QModelIndex, QRegularExpression, Qt
from PySide6 import QtPrintSupport

from config import INI
from utils.mywidgets import VentanaPrincipal


#####################
# VENTANA PRINCIPAL #
#####################

class App_Ajustes(QtWidgets.QWidget):
    """ Backend para la ventana de administración de ventas. """
    
    def __init__(self, parent: VentanaPrincipal):
        from ui.Ui_Ajustes import Ui_Ajustes
        
        super().__init__()
        
        self.ui = Ui_Ajustes()
        self.ui.setupUi(self)
        
        self.conn = parent.conn
        self.user = parent.user
        
        self.ui.boxImpresoras.addItems(QtPrintSupport.QPrinterInfo.availablePrinterNames())
        self.ui.boxImpresoras.setCurrentText(INI.IMPRESORA)
        
        # crear eventos para los botones
        self.ui.btRegresar.clicked.connect(self.goHome)
    
    def goHome(self, _):
        """ Cierra la ventana y regresa a Home. """
        INI.IMPRESORA = self.ui.boxImpresoras.currentText()
        INI.guardar()
        
        parent = self.parentWidget()
        parent.goHome()
