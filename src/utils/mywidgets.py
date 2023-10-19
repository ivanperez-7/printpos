""" Módulo con widgets personalizados varios. """
from datetime import datetime
from enum import Enum, auto
from typing import Callable, Iterator

from PySide6 import QtWidgets
from PySide6.QtGui import *
from PySide6.QtCore import *
import PySide6.QtGui

from backends.Login import Usuario
from utils.myutils import formatDate
from utils import Moneda, sql


__all__ = ['VentanaPrincipal', 'DimBackground', 'WidgetPago', 
           'StackPagos', 'TablaDatos', 'NumberEdit', 'LabelAdvertencia', 
           'WarningDialog', 'SpeechBubble', 'ListaNotificaciones']

alternate_bg = QColor(225, 225, 225)

class VentanaPrincipal(QtWidgets.QMainWindow):
    def __init__(self, conn: sql.Connection):
        super().__init__()
        
        self.resize(1540, 800)
        self.setWindowTitle('PrintPOS')
        
        self.conn = conn
        self.user = Usuario.generarUsuarioActivo(conn)
        self.en_venta = False  # bandera levantada al entrar en CrearVenta
        
        icon = QIcon()
        icon.addFile(':img/icon.ico', QSize(), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        
        from backends.Home import App_ConsultarPrecios
        self.consultarPrecios = App_ConsultarPrecios(self)
        self.goHome()
        
        self.show()
    
    def goHome(self):
        """ Regresar al menú principal.
            Crea módulo Home y establece como widget principal. """
        from backends.Home import App_Home
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


class ClickableIcon(QtWidgets.QPushButton):
    """ QPushButton con un stylesheet apropiado para eliminar bordes. """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet('''
            /* Normal state */
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0px;
            }
            /* Hover state */
            QPushButton:hover {
                border: none;
            }
            /* Focus state */
            QPushButton:focus {
                border: none;
                outline: none; /* Remove the dotted focus outline */
            }
        ''')
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)


class DimBackground(QtWidgets.QFrame):
    """ Crea un QFrame que ocupa la ventana entera, para poner énfasis en las ventanas nuevas. """
    
    def __init__(self, window: QtWidgets.QWidget):
        super().__init__(window)
        
        self.setFixedSize(window.size())
        self.setStyleSheet('background: rgba(64, 64, 64, 64);')
        self.show()


class WidgetPago(QtWidgets.QFrame):
    def __init__(self, parent=None):
        from ui.Ui_WidgetPago import Ui_WidgetPago
        
        super().__init__(parent)
        
        self.ui = Ui_WidgetPago()
        self.ui.setupUi(self)
        
    def calcularCambio(self, para_pagar):
        """ Recalcular cambio a entregar. Notar que sólo se ejecuta
            cuando el método de pago actual es efectivo. """
        if self.metodoSeleccionado != 'Efectivo':
            self.ui.lbCambio.setText(f'{Moneda.cero}')
            return
        
        pago = self.ui.txtPago.cantidad
        cambio = max(Moneda.cero, pago - para_pagar)
        self.ui.lbCambio.setText(f'{cambio}')
    
    @property
    def montoPagado(self):
        return self.ui.txtPago.cantidad
    
    @property
    def metodoSeleccionado(self):
        return self.ui.buttonGroup.checkedButton().text()
    
    @property
    def grupoBotones(self):
        return self.ui.buttonGroup


class StackPagos(QtWidgets.QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMaximumHeight(139)
        self.total = Moneda()
    
    def retroceder(self):
        self.setCurrentIndex(self.currentIndex() - 1)
    
    def avanzar(self):
        self.setCurrentIndex(self.currentIndex() + 1)
    
    def agregarPago(self):
        """ Agrega widget de pago a la lista y regresa el widget. """
        wdg = WidgetPago()
        wdg.ui.txtPago.textChanged.connect(lambda: wdg.calcularCambio(self.totalEnEfectivo))
        wdg.grupoBotones.buttonClicked.connect(lambda: wdg.calcularCambio(self.totalEnEfectivo))
        
        self.currentChanged.connect(lambda: wdg.calcularCambio(self.totalEnEfectivo))
        self.addWidget(wdg)
        self.setCurrentWidget(wdg)
        return wdg
    
    def quitarPago(self):
        """ Quitar el widget de pago actual. """
        if self.count() > 1:
            self.removeWidget(self.currentWidget())
    
    @property
    def widgetsPago(self) -> Iterator[WidgetPago]:
        for i in range(self.count()):
            yield self.widget(i)
    
    @property
    def totalEnEfectivo(self):
        """ Residuo del total menos lo ya pagado con moneda electrónico. """
        return self.total - sum(wdg.montoPagado for wdg in self.widgetsPago
                                if wdg.metodoSeleccionado != 'Efectivo')
    
    @property
    def pagosValidos(self):
        montoPagado = sum(wdg.montoPagado for wdg in self.widgetsPago)
        n_efec = [wdg.metodoSeleccionado for wdg in self.widgetsPago].count('Efectivo')
        
        if n_efec == 0:
            sumaCorrecta = montoPagado == self.total
        elif n_efec == 1:
            sumaCorrecta = montoPagado >= self.total
        else:
            return False
        return all(wdg.montoPagado for wdg in self.widgetsPago) and sumaCorrecta


class TablaDatos(QtWidgets.QTableWidget):
    class Modelos(Enum):
        DEFAULT = auto()
        CREAR_VENTA = auto()
        
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.modelo = self.Modelos.DEFAULT
        
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
                alternate-background-color: %s;
            }

            QTableView {
                selection-background-color: rgb(85, 85, 255);
                selection-color: rgb(255, 255, 255);
            }
            QTableView:active {
                selection-background-color: rgb(85, 85, 255);
                selection-color: rgb(255, 255, 255);
            }
        """%alternate_bg.name())
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
    
    def llenar(self, data):
        funcs = {
            self.Modelos.DEFAULT: self._llenar_default,
            self.Modelos.CREAR_VENTA: self._llenar_crear_venta
        }
        funcs[self.modelo](data)
    
    def tamanoCabecera(self, pt: int):
        qs = self.styleSheet()
        header = 'QHeaderView::section {font: bold %dpt;}'%pt
        self.setStyleSheet(qs + header)
    
    def quitarBordeCabecera(self):
        qs = self.styleSheet()
        borde = 'QHeaderView::section {border: 0px;}'
        self.setStyleSheet(qs + borde)
    
    def cambiarColorCabecera(self, color):
        qs = self.styleSheet()
        color = QColor(color)
        color_qs = 'QHeaderView::section {{ background-color: {} }};'.format(color.name())
        self.setStyleSheet(qs + color_qs)
    
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
    
    # ************************************* #
    def _llenar_default(self, data):
        self.setRowCount(0)
        
        for row, prod in enumerate(data):
            self.insertRow(row)
            
            for col, dato in enumerate(prod):
                if isinstance(dato, float):
                    cell = f'{dato:,.2f}'
                elif isinstance(dato, datetime):
                    cell = formatDate(dato)
                else:
                    cell = str(dato or '')
                tableItem = QtWidgets.QTableWidgetItem(cell)
                self.setItem(row, col, tableItem)
    
    def _llenar_crear_venta(self, data):
        self.setRowCount(0)
        
        for row, prod in enumerate(data):
            self.insertRow(row)
            
            for col, dato in enumerate(prod):
                if isinstance(dato, float):
                    if col == 4 and not dato:
                        cell = ''
                    else:
                        cell = f'{dato:,.2f}'
                else:
                    cell = str(dato or '')
                
                tableItem = QtWidgets.QTableWidgetItem(cell)
                flags = tableItem.flags()
                if col != 2:
                    flags &= ~Qt.ItemFlag.ItemIsEditable
                tableItem.setFlags(flags)
                
                self.setItem(row, col, tableItem)
        self.resizeRowsToContents()


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
            QRegularExpressionValidator(r'\d{1,15}\.?\d{0,2}'))
    
    def bloquear(self, monto):
        self.cantidad = monto
        self.setReadOnly(True)
    
    def desbloquear(self):
        self.setReadOnly(False)
    
    @property
    def cantidad(self):
        try:
            return Moneda(self.text())
        except ValueError:
            return Moneda()
    
    @cantidad.setter
    def cantidad(self, val):
        self.setText(f'{Moneda(val)}')


class LabelAdvertencia(QtWidgets.QLabel):
    """ Crea un label de advertencia para las tablas, ya que en Qt Designer no se puede.

        Añade método `resizeEvent` al padre para posicionar el label en el centro.
        
        Añade método al padre para actualizar el texto, que verifica si hay items o no en la tabla. """
    
    def __init__(self, parent: QtWidgets.QTableWidget, msj: str):
        super().__init__(parent)
        
        self.parent = parent
        self.msj = msj
        
        font = QFont()
        font.setPointSize(14)
        self.setMinimumSize(282, 52)
        self.setFont(font)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        self.actualizarLabel()
        
        parent.resizeEvent = self.relocate
        parent.model().rowsInserted.connect(self.actualizarLabel)
        parent.model().rowsRemoved.connect(self.actualizarLabel)
    
    def relocate(self, event):
        w_t, h_t = self.parent.width(), self.parent.height()
        pm_x = (w_t - self.width()) // 2
        pm_y = (h_t - self.height()) // 2
        
        self.move(pm_x, pm_y)
        QtWidgets.QTableWidget.resizeEvent(self.parent, event)
    
    def actualizarLabel(self):
        self.setText(self.msj if not self.parent.rowCount() else '')


class WarningDialog(QtWidgets.QMessageBox):
    """ Crea un widget simple con un ícono de advertencia. """
    
    def __init__(self, body: str, error: str = None):
        super().__init__()
        
        icon = QIcon()
        icon.addFile(':img/icon.ico', QSize(), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        
        self.setWindowTitle('Atención')
        self.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        self.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        self.setText(body)
        if error:
            self.setDetailedText(error)
        self.exec()


class SpeechBubble(QtWidgets.QWidget):
    hiddenGeom = QRect(610, 28, 0, 165)
    shownGeom = QRect(610, 28, 345, 165)
    
    def __init__(self, parent, txt = ''):
        super().__init__(parent)
        
        self.setGeometry(self.shownGeom)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(17, 17, 17, 17)
        
        self.text_browser = QtWidgets.QTextBrowser()
        self.text_browser.setStyleSheet('''
            QTextBrowser { 
                border: none;
                background-color: transparent;
            }
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
        self.text_browser.setPlainText(txt)
        font = QFont()
        font.setPointSize(11)
        self.text_browser.setFont(font)
        self.text_browser.setLineWrapMode(QtWidgets.QTextBrowser.LineWrapMode.FixedPixelWidth)
        self.text_browser.setLineWrapColumnOrWidth(295)
        self.text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        layout.addWidget(self.text_browser)
    
    def setText(self, txt):
        self.text_browser.setPlainText(txt)
    
    def paintEvent(self, event):
        painter_path = QPainterPath()
        
        # Draw the speech bubble background with added padding
        bubble_rect = self.rect().adjusted(10, 10, -10, -10)
        painter_path.addRoundedRect(bubble_rect, 10, 10)
        
        # Draw the triangle at the top middle
        triangle_path = QPolygon()
        triangle_center = bubble_rect.center().y()
        triangle_path << QPoint(bubble_rect.left(), triangle_center - 10)
        triangle_path << QPoint(bubble_rect.left(), triangle_center + 10)
        triangle_path << QPoint(bubble_rect.left() - 10, triangle_center)
        
        painter_path.addPolygon(triangle_path)
        
        # Set the painter properties
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(Qt.GlobalColor.white)
        
        painter.drawPath(painter_path.simplified())
    
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


class ListaNotificaciones(QtWidgets.QListWidget):
    hiddenGeom = QRect(0, 0, 400, 0)
    shownGeom = QRect(0, 0, 400, 120)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet('''
            QListWidget {
                alternate-background-color: %s;
            }
            QListWidget::item { 
                margin: 5px;
            }
            QFrame {
                border: 2px solid;
            }
        '''%alternate_bg.name())
    
    def agregarNotificaciones(self, conn, user):
        """ Llena la caja de notificaciones. """
        from utils.sql import ManejadorInventario, ManejadorVentas
        
        items = []
        manejador = ManejadorVentas(conn)
        
        numPendientes, = manejador.obtenerNumPendientes(user.id)
        
        if numPendientes:
            items.append(f'Tiene {numPendientes} pedidos pendientes.')
        
        manejador = ManejadorInventario(conn)
        
        for nombre, stock, minimo in manejador.obtenerInventarioFaltante():
            items.append(
                f'¡Hay que surtir el material {nombre}! ' +
                f'Faltan {minimo - stock} lotes para cubrir el mínimo.'
            )
        items = items or ['¡No hay nuevas notificaciones!']
        
        for item in items:
            self.addItem(item)
    
    def alternarNotificaciones(self):
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
    
    @property
    def sinNotificaciones(self):
        return self.item(0).text().startswith('¡No hay nuevas')
