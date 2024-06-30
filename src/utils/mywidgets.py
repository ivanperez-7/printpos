""" Módulo con widgets personalizados varios. """
from datetime import datetime
from enum import Enum, auto
import glob
import os
from typing import Callable, Iterator, Type

from PySide6 import QtWidgets
from PySide6.QtGui import *
from PySide6.QtCore import *

from core import Moneda, ROJO, VERDE, AMARILLO
from mixins import ModuloPrincipal, HasConnUser
from .myutils import unidecode, formatdate

__all__ = ['VentanaPrincipal', 'WidgetPago', 'StackPagos', 
           'TablaDatos', 'NumberEdit', 'LabelAdvertencia',
           'WarningDialog', 'SpeechBubble', 'ListaNotificaciones']


class VentanaPrincipal(QtWidgets.QMainWindow, HasConnUser):
    def __init__(self, conn, user):
        super().__init__()

        self.resize(1500, 800)
        self.setWindowTitle('PrintPOS')
        self.setWindowIcon(QIcon(':img/icon.ico'))

        self.conn = conn
        self.user = user

        from backends.AdministrarProductos import App_ConsultarPrecios
        self.consultarPrecios = App_ConsultarPrecios(conn)

        self.go_home()
        self.show()

    def go_home(self):
        """ Regresar al menú principal.
            Crea módulo Home y establece como widget principal. """
        from backends.Home import App_Home

        home = App_Home(self.conn, self.user)
        home.go_back.connect(self.close)
        home.new_module.connect(self.go_to)

        self.setCentralWidget(home)
    
    def go_to(self, modulo: Type[ModuloPrincipal]):
        new = modulo(self.conn, self.user)
        new.go_back.connect(self.go_home)
        self.setCentralWidget(new)

    @property
    def en_venta(self):
        from backends.CrearVenta import App_CrearVenta
        return isinstance(self.centralWidget(), App_CrearVenta)

    def closeEvent(self, event):
        """ En eventos específicos, restringimos el cerrado del sistema. """
        if self.en_venta and not self.user.administrador:
            event.ignore()
            return

        for j in glob.glob('*.jpg'):
            os.remove(j)
        self.conn.close()
        self.consultarPrecios.close()
        
        from backends.Login import App_Login
        login = App_Login(self.__class__)


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


class WidgetPago(QtWidgets.QFrame):
    def __init__(self, parent=None):
        from ui.Ui_WidgetPago import Ui_WidgetPago

        super().__init__(parent)

        self.ui = Ui_WidgetPago()
        self.ui.setupUi(self)

    @property
    def montoPagado(self):
        return self.ui.txtPago.cantidad

    @property
    def metodoSeleccionado(self):
        return self.ui.buttonGroup.checkedButton().text()

    @metodoSeleccionado.setter
    def metodoSeleccionado(self, val):
        for bt in self.ui.buttonGroup.buttons():
            bt.setChecked(val == bt.text())


class StackPagos(QtWidgets.QStackedWidget):
    cambio_pagos = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMaximumHeight(139)
        self.total = Moneda()  # monto debido
        self.permitir_nulo = False

    def retroceder(self):
        self.setCurrentIndex(self.currentIndex() - 1)

    def avanzar(self):
        self.setCurrentIndex(self.currentIndex() + 1)

    def agregarPago(self):
        """ Agrega widget de pago a la lista y regresa el widget. """
        wdg = WidgetPago()
        wdg.ui.txtPago.textChanged.connect(lambda: self.cambio_pagos.emit())
        wdg.ui.buttonGroup.buttonClicked.connect(lambda: self.cambio_pagos.emit())

        self.addWidget(wdg)
        self.setCurrentWidget(wdg)
        self.cambio_pagos.emit()
        return wdg

    def quitarPago(self):
        """ Quitar el widget de pago actual. """
        if self.count() > 1:
            self.removeWidget(self.currentWidget())
            self.cambio_pagos.emit()

    @property
    def restanteEnEfectivo(self):
        """ Residuo del total menos lo ya pagado con moneda electrónica. """
        return self.total - sum(wdg.montoPagado for wdg in self
                                if wdg.metodoSeleccionado != 'Efectivo')

    @property
    def pagosValidos(self):
        """ Determinar que los pagos introducidos cumplan varios requisitos.
            1. Si el monto debido es de cero, nunca aceptar. 
            2. No puede haber pagos de cero pesos.
            3. No puede haber más de un pago en efectivo.
            4. Al haber uno de estos, verificar que sea necesario
               y que lo pagado sea igual o mayor que lo debido (es decir,
               permitir que el efectivo exceda lo necesario)
            5. Al no haber efectivo, verificar que lo pagado sea exactamente lo debido. """
        montoPagado = sum(wdg.montoPagado for wdg in self)
        if self.permitir_nulo and self.total == montoPagado == 0. and self.count() == 1:
            return True

        n_efec = [wdg.metodoSeleccionado for wdg in self].count('Efectivo')

        if n_efec == 0:
            sumaCorrecta = montoPagado == self.total
        elif n_efec == 1:
            sumaCorrecta = self.restanteEnEfectivo > 0. and montoPagado >= self.total
        else:
            return False
        return sumaCorrecta and all(wdg.montoPagado for wdg in self)

    def __len__(self):
        return self.count()

    def __iter__(self) -> Iterator[WidgetPago]:
        for i in range(self.count()):
            yield self.widget(i)

    def __getitem__(self, i: int) -> WidgetPago:
        return self.widget(i)


class MyTableItem(QtWidgets.QTableWidgetItem):
    def __init__(self, text, sort_key=None):
        super().__init__(text)
        self.sort_key = sort_key

    def __lt__(self, other):
        if not isinstance(other, MyTableItem) or self.sort_key is None:
            return unidecode(self.text()) < unidecode(other.text())
        else:
            return self.sort_key < other.sort_key


class TablaDatos(QtWidgets.QTableWidget):
    class Modelos(Enum):
        DEFAULT = auto()
        RESALTAR_SEGUNDA = auto()
        CREAR_VENTA = auto()
        TABLA_VENTAS_DIRECTAS = auto()
        TABLA_PEDIDOS = auto()

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
        """ % QColor(225, 225, 225).name())
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
        if not isinstance(data, list):
            data = list(data)

        sort = self.isSortingEnabled()
        self.setSortingEnabled(False)
        self.setRowCount(0)
        self.setRowCount(len(data))

        funcs = {
            self.Modelos.DEFAULT: self._llenar_default,
            self.Modelos.RESALTAR_SEGUNDA: self._llenar_resaltar_segunda,
            self.Modelos.CREAR_VENTA: self._llenar_crear_venta,
            self.Modelos.TABLA_VENTAS_DIRECTAS: self._llenar_tabla_ventas_directas,
            self.Modelos.TABLA_PEDIDOS: self._llenar_tabla_pedidos
        }
        funcs[self.modelo](data)

        self.setSortingEnabled(sort)

    def tamanoCabecera(self, pt: int):
        qs = self.styleSheet()
        header = 'QHeaderView::section {font: bold %dpt;}' % pt
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
        for row, prod in enumerate(data):
            for col, dato in enumerate(prod):
                sort_key = None
                if isinstance(dato, float):
                    cell = f'${dato:,.2f}'
                    sort_key = Moneda(dato)
                elif isinstance(dato, datetime):
                    cell = formatdate(dato)
                    sort_key = dato
                else:
                    cell = str(dato or '')
                tableItem = MyTableItem(cell, sort_key)
                self.setItem(row, col, tableItem)

    def _llenar_resaltar_segunda(self, data):
        self._llenar_default(data)

        bold = QFont()
        bold.setBold(True)

        for row in range(self.rowCount()):
            self.item(row, 1).setFont(bold)

    def _llenar_crear_venta(self, data):
        for row, prod in enumerate(data):
            for col, dato in enumerate(prod):
                if isinstance(dato, float):
                    if col == 4 and not dato:
                        cell = ''
                    else:
                        cell = f'{dato:,.2f}'
                else:
                    cell = str(dato or '')

                tableItem = MyTableItem(cell)
                flags = tableItem.flags()
                if col != 2:
                    flags &= ~Qt.ItemFlag.ItemIsEditable
                tableItem.setFlags(flags)

                self.setItem(row, col, tableItem)
        self.resizeRowsToContents()

    def _llenar_tabla_ventas_directas(self, data):
        bold = QFont()
        bold.setBold(True)

        for row, compra in enumerate(data):
            for col, dato in enumerate(compra):
                if isinstance(dato, datetime):
                    cell = formatdate(dato)
                elif isinstance(dato, float):
                    cell = f'${dato:,.2f}'
                else:
                    cell = str(dato or '')
                self.setItem(row, col, MyTableItem(cell))

            self.item(row, 4).setFont(bold)
            self.item(row, 5).setTextAlignment(Qt.AlignCenter)

            estado = self.item(row, 5).text()

            if estado.startswith('Cancelada'):
                self.item(row, 5).setBackground(QColor(ROJO))
            elif estado.startswith('Terminada'):
                self.item(row, 5).setBackground(QColor(VERDE))

    def _llenar_tabla_pedidos(self, data):
        bold = QFont()
        bold.setBold(True)
        icon = QIcon(":/img/resources/images/whatsapp.png")

        for row, compra in enumerate(data):
            for col, dato in enumerate(compra):
                if isinstance(dato, datetime):
                    cell = formatdate(dato)
                elif isinstance(dato, float):
                    cell = f'${dato:,.2f}'
                else:
                    cell = str(dato or '')
                self.setItem(row, col, MyTableItem(cell))

            self.item(row, 5).setFont(bold)
            self.item(row, 6).setTextAlignment(Qt.AlignCenter)

            estado_cell = self.item(row, 6)
            estado = estado_cell.text()

            if estado.startswith('Cancelada'):
                estado_cell.setBackground(QColor(ROJO))
            elif estado.startswith('Entregado') or estado.startswith('Terminada'):
                estado_cell.setBackground(QColor(VERDE))
            elif estado.startswith('Recibido'):
                estado_cell.setBackground(QColor(AMARILLO))

                button_cell = QtWidgets.QPushButton(' Enviar recordatorio')
                button_cell.setIcon(icon)
                button_cell.setFlat(True)

                self.setCellWidget(row, 8, button_cell)

                # resaltar pedidos con fechas de entrega ya pasadas
                if QDateTime.currentDateTime() > compra[4]:
                    self.item(row, 4).setBackground(QColor(ROJO))


class NumberEdit(QtWidgets.QLineEdit):
    """ Widget QLineEdit para manejar cantidad monetarias de forma más fácil. """

    def __init__(self, parent=None):
        super().__init__(parent)

        font = QFont()
        font.setPointSize(14)
        self.setFont(font)
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # validadores para datos numéricos
        self.setValidator(QRegularExpressionValidator(r'\d{1,15}\.?\d{0,2}'))

    @property
    def cantidad(self):
        try:
            return Moneda(self.text())
        except ValueError:
            return Moneda.cero

    @cantidad.setter
    def cantidad(self, val):
        self.setText(f'{Moneda(val)}')


class LabelAdvertencia(QtWidgets.QLabel):
    """ Crea un label de advertencia para las tablas, ya que en Qt Designer no se puede.

        Añade método `resizeEvent` al padre para posicionar el label en el centro.
        
        Añade método al padre para actualizar el texto, que verifica si hay items o no en la tabla. """

    def __init__(self, parent: QtWidgets.QTableWidget, msj: str):
        super().__init__(parent)

        self.parent_ = parent
        self.msj = msj

        font = QFont()
        font.setPointSize(14)
        self.setMinimumSize(282, 52)
        self.setFont(font)
        self.setAlignment(Qt.AlignCenter)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.actualizarLabel()

        parent.resizeEvent = self.relocate
        parent.model().rowsInserted.connect(self.actualizarLabel)
        parent.model().rowsRemoved.connect(self.actualizarLabel)

    def relocate(self, event):
        pm_x = (self.parent_.width() - self.width()) // 2
        pm_y = (self.parent_.height() - self.height()) // 2

        self.move(pm_x, pm_y)
        QtWidgets.QTableWidget.resizeEvent(self.parent_, event)

    def actualizarLabel(self):
        self.setText(self.msj if not self.parent_.rowCount() else '')


class WarningDialog(QtWidgets.QMessageBox):
    """ Crea un widget simple con un ícono de advertencia. """

    def __init__(self, body: str, error: str = None):
        super().__init__()

        self.setWindowTitle('Atención')
        self.setWindowIcon(QIcon(':img/icon.ico'))
        self.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        self.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        self.setText(body)
        if error:
            self.setDetailedText(error)
        self.exec()


class SpeechBubble(QtWidgets.QWidget):
    hiddenGeom = QRect(610, 28, 0, 165)
    shownGeom = QRect(610, 28, 345, 165)

    def __init__(self, parent, txt=''):
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
