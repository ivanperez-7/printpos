from functools import partial
import inspect

from PySide6 import QtWidgets
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtCore import QDate, Qt, QRect, QPropertyAnimation, QEasingCurve, Signal

from .AdministrarVentas import App_AdministrarVentas
from .AdministrarInventario import App_AdministrarInventario
from .AdministrarProductos import App_AdministrarProductos
from .AdministrarClientes import App_AdministrarClientes
from .AdministrarUsuarios import App_AdministrarUsuarios
from .Ajustes import App_Ajustes
from .Caja import App_Caja
from .CrearVenta import App_CrearVenta
from protocols import ModuloPrincipal
from .Reportes import App_Reportes
import sql


class App_Home(ModuloPrincipal):
    """ Backend para la pantalla principal. """
    new_module = Signal(object)
    
    def __init__(self, conn, user):
        from ui.Ui_Home import Ui_Home

        super().__init__()
        self.ui = Ui_Home()
        self.ui.setupUi(self)

        self.conn = conn
        self.user = user

        # foto de perfil del usuario
        if self.user.foto_perfil:
            qp = QPixmap()
            qp.loadFromData(self.user.foto_perfil)
        else:
            qp = QPixmap(":/img/resources/images/user.png")

        self.ui.btFotoPerfil.setIcon(qp)

        # ocultar lista y proporcionar eventos
        self.ui.listaNotificaciones.setVisible(False)
        self.ui.btFotoPerfil.clicked.connect(self.ui.listaNotificaciones.alternarNotificaciones)
        self.ui.listaNotificaciones.agregarNotificaciones(conn, user)

        # configurar texto dinámico
        self.ui.fechaHoy.setDate(QDate.currentDate())
        self.ui.usuario.setText(self.user.nombre)
        self.ui.tipo_usuario.setText(self.user.rol.capitalize())

        # deshabilita eventos del mouse para los textos en los botones
        for name, item in vars(self.ui).items():
            if 'label_' in name:
                item.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # deshabilitar funciones para usuarios normales
        if self.user.rol != 'ADMINISTRADOR':
            for w in [self.ui.frameInventario,
                      self.ui.frameCaja,
                      self.ui.frameUsuarios,
                      self.ui.frameProductos,
                      self.ui.frameReportes]:
                w.setEnabled(False)

        if not self.ui.listaNotificaciones.sinNotificaciones:
            lab = QtWidgets.QLabel(self.ui.frame_5)
            lab.setPixmap(self._create_pixmap(self.ui.listaNotificaciones.count()))
            lab.setGeometry(392, 5, 26, 26)

        # mapeo de botones con sus acciones
        button_class_mapping = {
            self.ui.btClientes: App_AdministrarClientes,
            self.ui.btInventario: App_AdministrarInventario,
            self.ui.btProductos: App_AdministrarProductos,
            self.ui.btUsuarios: App_AdministrarUsuarios,
            self.ui.btVentas: App_AdministrarVentas,
            self.ui.btAjustes: App_Ajustes,
            self.ui.btCaja: App_Caja,
            self.ui.btCrearVenta: self.iniciarVenta,
            self.ui.btReportes: App_Reportes,
            self.ui.btSalir: self.go_back.emit
        }

        # conectar botones con acciones
        for button, action in button_class_mapping.items():
            if inspect.isclass(action):
                handle = partial(self.new_module.emit, action) # action = clase de módulo
                button.clicked.connect(handle)
            else:
                button.clicked.connect(action)

    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def iniciarVenta(self):
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Iniciar venta',
                          '¿Desea iniciar una nueva venta?')
        if ret == qm.Yes:
            self.new_module.emit(App_CrearVenta)

    def _create_pixmap(self, point: int):
        from PySide6 import QtCore, QtGui

        rect = QtCore.QRect(QtCore.QPoint(), 23 * QtCore.QSize(1, 1))
        pixmap = QtGui.QPixmap(rect.size())
        rect.adjust(1, 1, -1, -1)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHints(
            QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing
        )

        pen = painter.pen()
        pen.setColor(QtCore.Qt.white)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(250, 62, 62)))
        painter.drawEllipse(rect)
        painter.setPen(pen)
        painter.drawText(rect, QtCore.Qt.AlignCenter, str(point))
        painter.end()
        return pixmap


########################
# WIDGET PERSONALIZADO #
########################
class ListaNotificaciones(QtWidgets.QListWidget):
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
        ''' % QColor(225, 225, 225).name())

    def agregarNotificaciones(self, conn, user):
        """ Llena la caja de notificaciones. """
        items = []
        manejador = sql.ManejadorVentas(conn)

        numPendientes, = manejador.obtenerNumPendientes(user.id)

        if numPendientes:
            items.append(f'Tiene {numPendientes} pedidos pendientes.')

        manejador = sql.ManejadorInventario(conn)

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
        hiddenGeom = QRect(0, 0, 400, 0)
        shownGeom = QRect(0, 0, 400, 120)
        
        if not self.isVisible():
            # Create an animation to gradually change the height of the widget
            self.setVisible(True)
            self.show_animation = QPropertyAnimation(self, b'geometry')
            self.show_animation.setDuration(200)
            self.show_animation.setStartValue(hiddenGeom)
            self.show_animation.setEndValue(shownGeom)
            self.show_animation.setEasingCurve(QEasingCurve.OutSine)
            self.show_animation.start()
        else:
            # Hide the widget
            self.hide_animation = QPropertyAnimation(self, b'geometry')
            self.hide_animation.setDuration(200)
            self.hide_animation.setStartValue(shownGeom)
            self.hide_animation.setEndValue(hiddenGeom)
            self.hide_animation.setEasingCurve(QEasingCurve.InSine)
            self.hide_animation.finished.connect(lambda: self.setVisible(False))
            self.hide_animation.start()

    @property
    def sinNotificaciones(self):
        return self.item(0).text().startswith('¡No hay nuevas')
