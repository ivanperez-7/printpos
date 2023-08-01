""" Módulo con widgets personalizados varios. """
from typing import Callable

import fdb

from PySide6.QtWidgets import (QMainWindow, QMessageBox, QWidget,
                               QLabel, QTableWidget, QLineEdit)
from PySide6.QtGui import QFont, QIcon, QPixmap, QRegularExpressionValidator
from PySide6.QtCore import Qt, QSize, QRegularExpression

from Login import Usuario


class VentanaPrincipal(QMainWindow):
    def __init__(self, conn: fdb.Connection, user: Usuario):
        super().__init__()
        
        self.resize(1540, 800)
        self.setWindowTitle('PrintPOS')
        
        self.conn = conn
        self.user = user
        self.en_venta = False  # bandera levantada al entrar en CrearVenta
        
        icon = QIcon()
        icon.addPixmap(QPixmap(':/img/icon.ico'), QIcon.Mode.Normal, QIcon.State.Off)
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


class TablaDatos(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
        QHeaderView::section {
            font: bold 10pt;
            color: rgb(255, 255, 255);
            background-color: rgb(52, 172, 224);
            padding: 7px;
        }

        QTableView::item{
            padding: 5px;
        }
        
        QTableWidget {
            alternate-background-color: rgb(240, 240, 240);
        }

        QTableView {
            selection-background-color: rgb(85, 85, 255);
            selection-color: rgb(255, 255, 255);
        }
        QTableView:active {
            selection-background-color: rgb(85, 85, 255);
            selection-color: rgb(255, 255, 255);
        }""")
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setWordWrap(True)
        self.verticalHeader().hide()
        self.horizontalHeader().setMinimumSectionSize(50)
    
    def quitarBordeCabecera(self):
        self.setStyleSheet(self.styleSheet() + '\nQHeaderView::section {border: 0px;}')
    
    def cambiarColorCabecera(self, color: str):
        self.setStyleSheet(self.styleSheet() + '\nQHeaderView::section {background-color:' + color + ';}')
    
    def configurarCabecera(self, resize_cols: Callable[[int], bool] = None,
                           align_flags=None):
        """ Configurar tamaño de cabeceras de tabla. En particular, 
            establece `ResizeToContents` en las columnas especificadas.
            
            También se añaden banderas de alineación, si se desea. """
        from PySide6.QtWidgets import QHeaderView
        
        header = self.horizontalHeader()
        
        if not resize_cols:
            resize_cols = lambda _: True
        if align_flags:
            header.setDefaultAlignment(align_flags)
        
        for col in range(self.columnCount()):
            if resize_cols(col):
                mode = QHeaderView.ResizeMode.ResizeToContents
            else:
                mode = QHeaderView.ResizeMode.Stretch
            
            header.setSectionResizeMode(col, mode)


class NumberEdit(QLineEdit):
    """ Widget QLineEdit para manejar cantidad monetarias de forma más fácil. """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        font = QFont()
        font.setPointSize(14)
        self.setFont(font)
        self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # validadores para datos numéricos
        regexp_numero = QRegularExpression(r'\d*\.?\d{0,2}')
        validador = QRegularExpressionValidator(regexp_numero)
        self.setValidator(validador)
    
    @property
    def cantidad(self):
        try:
            return float(self.text())
        except ValueError:
            return 0.
    
    @cantidad.setter
    def cantidad(self, val: float):
        self.setText(f'{val:.2f}')


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
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.actualizarLabel()
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
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
    
    def __init__(self, body: str, error: str = None):
        super().__init__()
        
        icon = QIcon()
        icon.addPixmap(QPixmap(':/img/icon.ico'), QIcon.Mode.Normal, QIcon.State.Off)
        self.setWindowIcon(icon)
        
        self.setWindowTitle('Atención')
        self.setIcon(QMessageBox.Icon.Warning)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.setText(body)
        if error: self.setDetailedText(error)
        self.exec()
