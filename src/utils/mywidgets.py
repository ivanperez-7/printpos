""" Módulo con widgets personalizados varios. """
from typing import Callable

from PySide6 import QtWidgets
from PySide6.QtGui import (QFont, QIcon, QPixmap, QRegularExpressionValidator, 
                           QPainter, QColor, QPolygon, QPainterPath)
from PySide6.QtCore import Qt, QSize, QRectF, QPoint, QPropertyAnimation, QRect, QEasingCurve

from Login import Usuario
from utils.sql import Connection


class VentanaPrincipal(QtWidgets.QMainWindow):
    def __init__(self, conn: Connection, user: Usuario):
        super().__init__()
        
        self.resize(1540, 800)
        self.setWindowTitle('PrintPOS')
        
        self.conn = conn
        self.user = user
        self.en_venta = False  # bandera levantada al entrar en CrearVenta
        
        icon = QIcon()
        icon.addPixmap(QPixmap(':/img/icon.ico'), QIcon.Mode.Normal, QIcon.State.Off)
        self.setWindowIcon(icon)
        
        from Home import App_ConsultarPrecios
        self.consultarPrecios = App_ConsultarPrecios(self)
        self.goHome()
        
        self.show()
    
    def goHome(self):
        """ Regresar al menú principal.
            Crea módulo Home y establece como widget principal. """
        from Home import App_Home
        new = App_Home(self)
        self.setCentralWidget(new)
    
    def closeEvent(self, event):
        """ En eventos específicos, restringimos el cerrado del sistema. """
        if self.en_venta and not self.user.administrador:
            event.ignore()
        else:
            self.conn.close()
            self.consultarPrecios.close()
            event.accept()


def DimBackground(window: QtWidgets.QMainWindow):
    """ Crea un widget que ocupa la ventana entera, para poner énfasis en las ventanas nuevas. """
    bg = QtWidgets.QWidget(parent=window)
    bg.setFixedSize(window.size())
    bg.setStyleSheet('background: rgba(64, 64, 64, 64);')
    bg.show()
    
    return bg


class TablaDatos(QtWidgets.QTableWidget):
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
        self.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
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
        header = self.horizontalHeader()
        
        if not resize_cols:
            resize_cols = lambda _: True
        if align_flags:
            header.setDefaultAlignment(align_flags)
        
        for col in range(self.columnCount()):
            if resize_cols(col):
                mode = QtWidgets.QHeaderView.ResizeMode.ResizeToContents
            else:
                mode = QtWidgets.QHeaderView.ResizeMode.Stretch
            
            header.setSectionResizeMode(col, mode)


class NumberEdit(QtWidgets.QLineEdit):
    """ Widget QLineEdit para manejar cantidad monetarias de forma más fácil. """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        font = QFont()
        font.setPointSize(14)
        self.setFont(font)
        self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # validadores para datos numéricos
        self.setValidator(
            QRegularExpressionValidator(r'\d*\.?\d{0,2}'))
    
    @property
    def cantidad(self):
        try:
            return float(self.text())
        except ValueError:
            return 0.
    
    @cantidad.setter
    def cantidad(self, val: float):
        self.setText(f'{val:.2f}')


class LabelAdvertencia(QtWidgets.QLabel):
    """ Crea un label de advertencia para las tablas, ya que en Qt Designer no se puede.
    
        Añade método `resizeEvent` al padre para posicionar el label en el centro.
        
        Añade método al padre para actualizar el texto, que verifica si hay items o no en la tabla. """
    
    def __init__(self, parent: QtWidgets.QTableWidget, msj: str):
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
        QtWidgets.QTableWidget.resizeEvent(self._parent, event)
    
    def actualizarLabel(self):
        self.setText(self.msj if not self._parent.rowCount() else '')


class WarningDialog(QtWidgets.QMessageBox):
    """ Crea un widget simple con un ícono de advertencia. """
    
    def __init__(self, body: str, error: str = None):
        super().__init__()
        
        icon = QIcon()
        icon.addPixmap(QPixmap(':/img/icon.ico'), QIcon.Mode.Normal, QIcon.State.Off)
        self.setWindowIcon(icon)
        
        self.setWindowTitle('Atención')
        self.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        self.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        self.setText(body)
        if error: self.setDetailedText(error)
        self.exec()


class SpeechBubble(QtWidgets.QWidget):
    def __init__(self, parent, text=''):
        super().__init__(parent)
        
        # Create the layout and QTextBrowser
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(17, 17, 17, 17)
        
        self.text_browser = QtWidgets.QTextBrowser()
        self.text_browser.setStyleSheet('''
            QTextBrowser { border: none; background-color: transparent; }
            QScrollBar:vertical {
                border: 0px solid;
                background: #c0c0c0;
                width:10px;    
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {         
        
                min-height: 0px;
                border: 0px solid red;
                border-radius: 4px;
                background-color: #1e3085;
            }
            QScrollBar::add-line:vertical {       
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:vertical {
                height: 0 px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }

            QScrollBar::add-page:vertical {
            background: none;
            }
        ''')
        self.text_browser.setPlainText(text)
        font = QFont()
        font.setPointSize(11)
        self.text_browser.setFont(font)
        self.text_browser.setLineWrapMode(QtWidgets.QTextBrowser.LineWrapMode.FixedPixelWidth)
        self.text_browser.setLineWrapColumnOrWidth(295)
        self.text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.hiddenGeom = QRect(610, 28, 0, 165)
        self.shownGeom = QRect(610, 28, 345, 165)
        self.setGeometry(self.shownGeom)
        
        layout.addWidget(self.text_browser)
    
    def setText(self, txt):
        self.text_browser.setPlainText(txt)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw the speech bubble background
        bubble_rect = self.rect().adjusted(10, 10, -10, -10)  # Add padding to the bubble
        
        # Draw the bubble shape
        bubble_path = QPainterPath()
        bubble_path.addRoundedRect(QRectF(bubble_rect), 10, 10)
        
        # Draw the triangle at the top middle
        triangle_path = QPolygon()
        triangle_center = bubble_rect.center().y()
        triangle_path << QPoint(bubble_rect.left(), triangle_center - 10)
        triangle_path << QPoint(bubble_rect.left(), triangle_center + 10)
        triangle_path << QPoint(bubble_rect.left() - 10, triangle_center)
        
        # Set the painter properties
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 255))
        
        # Draw the bubble and triangle
        painter.drawPath(bubble_path.simplified())
        painter.drawPolygon(triangle_path)
    
    def alternarDescuentos(self):
        """ Se llama a esta función al hacer click en la foto de perfil
        del usuario. Anima el tamaño de la caja de notificaciones. """
        if not self.isVisible():
            # Create an animation to gradually change the height of the widget
            self.setVisible(True)
            self.show_animation = QPropertyAnimation(self, b'geometry')
            self.show_animation.setDuration(200)
            self.show_animation.setStartValue(self.hiddenGeom)
            self.show_animation.setEndValue(self.shownGeom)
            self.show_animation.setEasingCurve(QEasingCurve.OutSine)
            self.show_animation.start()
        else:
            # Hide the widget
            self.hide_animation = QPropertyAnimation(self, b'geometry')
            self.hide_animation.setDuration(200)
            self.hide_animation.setStartValue(self.shownGeom)
            self.hide_animation.setEndValue(self.hiddenGeom)
            self.hide_animation.setEasingCurve(QEasingCurve.InSine)
            self.hide_animation.finished.connect(lambda: self.setVisible(False))
            self.hide_animation.start()
