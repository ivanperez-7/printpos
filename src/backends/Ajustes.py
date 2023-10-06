from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import QDate, QDateTime, QModelIndex, QRegularExpression, Qt


#####################
# VENTANA PRINCIPAL #
#####################

class App_Ajustes(QtWidgets.QWidget):
    """
    Backend para la ventana de administración de ventas.
    """
    
    def __init__(self, parent):
        from ui.Ui_Ajustes import Ui_Ajustes
        
        super().__init__()
        
        self.ui = Ui_Ajustes()
        self.ui.setupUi(self)
        
        self.session = parent.session  # conexión a la base de datos y usuario actual
        
        # crear eventos para los botones
        self.ui.lbRegresar.mousePressEvent = self.goHome
    
    def goHome(self, _):
        """
        Cierra la ventana y regresa a Home.
        """
        from backends.Home import App_Home
        
        parent = self.parentWidget()  # QMainWindow
        new = App_Home(parent)
        parent.setCentralWidget(new)
