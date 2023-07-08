"""
Módulo con widgets personalizados varios.
"""
import fdb

from PySide6.QtWidgets import QMainWindow, QMessageBox, QWidget, QLabel, QTableWidget
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtCore import Qt, QSize

from Login.App_Login import Usuario


class VentanaPrincipal(QMainWindow):
    def __init__(self, conn: fdb.Connection, user: Usuario):
        super().__init__()
        
        self.resize(1540, 800)
        self.setWindowTitle('PrintPOS')
        
        self.conn = conn
        self.user = user
        self.en_venta = False   # bandera levantada al entrar en CrearVenta
        
        icon = QIcon()
        icon.addPixmap(QPixmap(':/img/icon.ico'), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        
        from Home import App_ConsultarPrecios, App_Home
        
        central_widget = App_Home(self)
        self.setCentralWidget(central_widget)
        self.consultarPrecios = App_ConsultarPrecios(self)
        self.show()
    
    def closeEvent(self, event):
        """ En eventos específicos, restringimos el cerrado del sistema. """
        if self.en_venta and not self.user.administrador:
            event.ignore()
        else:
            import shutil
            
            shutil.rmtree('./tmp/', ignore_errors=True)
            
            self.conn.close()
            self.consultarPrecios.close()
            event.accept()


def DimBackground(window: QMainWindow):
    """ Crea un widget que ocupa la ventana entera, para poner énfasis en las ventanas nuevas. """
    bg = QWidget(parent=window)
    bg.setFixedSize(window.size())
    bg.setStyleSheet('background: rgba(64, 64, 64, 64);')
    bg.show()

    return bg


class LabelAdvertencia(QLabel):
    """ Crea un label de advertencia para las tablas, ya que en Qt Designer no se puede.
    
        Añade método `resizeEvent` al padre para posicionar el label en el centro.
        
        Añade método al padre para actualizar el texto, que verifica si hay items o no en la tabla. """    
    def __init__(self, parent: QTableWidget, msj: str):
        super().__init__(parent)
        
        self._parent = parent
        self.msj = msj
        
        self.setMinimumSize(QSize(282, 52))
        
        font = QFont()
        font.setPointSize(14)

        self.setFont(font)
        self.setAlignment(Qt.AlignCenter)
        self.setText(msj)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        
        parent.resizeEvent = self.relocate
        parent.model().rowsInserted.connect(self.actualizarLabel)
        parent.model().rowsRemoved.connect(self.actualizarLabel)
    
    def relocate(self, event):
        w_t, h_t = self._parent.width(), self._parent.height()
        pm_x = (w_t - self.width()) // 2
        pm_y = (h_t - self.height()) // 2

        self.move(pm_x, pm_y)
        QTableWidget.resizeEvent(self._parent, event)
    
    def actualizarLabel(self):
        self.setText(self.msj if not self._parent.rowCount() else '')


class WarningDialog(QMessageBox):
    """ Crea un widget simple con un ícono de advertencia. """
    def __init__(self, body: str, error: str):
        super().__init__()

        icon = QIcon()
        icon.addPixmap(QPixmap(':/img/icon.ico'), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)

        self.setWindowTitle('Atención')
        self.setIcon(QMessageBox.Icon.Warning)
        self.setStandardButtons(QMessageBox.Ok)
        self.setText(body)
        self.setDetailedText(error)

        self.exec()
