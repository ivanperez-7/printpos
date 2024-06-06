from functools import partial
import inspect

from PySide6 import QtWidgets
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import QDate, Qt

from .CrearVenta import Base_VisualizarProductos
from utils import Moneda
from utils.mywidgets import VentanaPrincipal


class App_Home(QtWidgets.QWidget):
    """ Backend para la pantalla principal. """
    
    def __init__(self, parent: VentanaPrincipal):
        from ui.Ui_Home import Ui_Home
        
        super().__init__()
        
        self.ui = Ui_Home()
        self.ui.setupUi(self)
        
        user = parent.user
        conn = parent.conn
        
        # foto de perfil del usuario
        if user.foto_perfil:
            qp = QPixmap()
            qp.loadFromData(user.foto_perfil)
        else:
            qp = QPixmap(":/img/resources/images/user.png")
        
        self.ui.btFotoPerfil.setIcon(qp)
        
        # ocultar lista y proporcionar eventos
        self.ui.listaNotificaciones.setVisible(False)
        self.ui.btFotoPerfil.clicked.connect(self.ui.listaNotificaciones.alternarNotificaciones)
        self.ui.listaNotificaciones.agregarNotificaciones(conn, user)
        
        # configurar texto dinámico
        self.ui.fechaHoy.setDate(QDate.currentDate())
        self.ui.usuario.setText(user.nombre)
        self.ui.tipo_usuario.setText(user.rol.capitalize())
        
        # deshabilita eventos del mouse para los textos en los botones
        for name, item in vars(self.ui).items():
            if 'label_' in name:
                item.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        # deshabilitar funciones para usuarios normales
        if user.rol != 'ADMINISTRADOR':
            for w in [self.ui.frameInventario,
                      self.ui.frameCaja,
                      self.ui.frameUsuarios,
                      self.ui.frameProductos,
                      self.ui.frameReportes]:
                w.setEnabled(False)
        
        if not self.ui.listaNotificaciones.sinNotificaciones:
            lab = QtWidgets.QLabel(self.ui.frame_5)
            lab.setPixmap(_create_pixmap(self.ui.listaNotificaciones.count()))
            lab.setGeometry(392, 5, 26, 26)
        
        self.conectar_botones()
    
    def conectar_botones(self):
        from .AdministrarVentas import App_AdministrarVentas
        from .AdministrarInventario import App_AdministrarInventario
        from .AdministrarProductos import App_AdministrarProductos
        from .AdministrarClientes import App_AdministrarClientes
        from .AdministrarUsuarios import App_AdministrarUsuarios
        from .Ajustes import App_Ajustes
        from .Caja import App_Caja
        from .Reportes import App_Reportes
        
        # create a dictionary to map buttons to their corresponding classes
        button_class_mapping = {
            self.ui.btCrearVenta: self.iniciarVenta,
            self.ui.btProductos: App_AdministrarProductos,
            self.ui.btInventario: App_AdministrarInventario,
            self.ui.btVentas: App_AdministrarVentas,
            self.ui.btCaja: App_Caja,
            self.ui.btClientes: App_AdministrarClientes,
            self.ui.btUsuarios: App_AdministrarUsuarios,
            self.ui.btReportes: App_Reportes,
            self.ui.btAjustes: App_Ajustes,
            self.ui.btSalir: lambda: self.parentWidget().close()
        }

        # connect buttons to their corresponding functions or classes
        for button, action in button_class_mapping.items():
            if inspect.isclass(action):
                handle = partial(self.crearVentana, action)
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
            from .CrearVenta import App_CrearVenta
            self.crearVentana(App_CrearVenta)
    
    def crearVentana(self, modulo):
        parent = self.parentWidget()  # QMainWindow
        new = modulo(parent)
        parent.setCentralWidget(new)


def _create_pixmap(point: int):
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


##################################
# VENTANA PARA CONSULTAR PRECIOS #
##################################
class App_ConsultarPrecios(Base_VisualizarProductos):
    """ Backend para el módulo de consultar precios.
        No se puede cerrar hasta cerrar por completo el sistema. """
    def __init__(self, first):
        super().__init__(first, extern=True)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint)
        self.setWindowTitle('Consultar precios')
        self.setWindowIcon(QIcon(':img/icon.ico'))
        
        self.warnings = False
        
        self.ui.label.setText('Consultar precios')
        self.ui.btRegresar.setCursor(Qt.CursorShape.ArrowCursor)
        self.ui.btRegresar.setIcon(QIcon(':/img/resources/images/package.png'))
        
        self.ui.btAgregar.hide()
        self.ui.groupBoxEspecGran.hide()
        self.ui.groupBoxEspecSimple.hide()
        
        # eventos para tabla de productos simples
        self.ui.tabla_seleccionar.itemClicked.connect(self.mostrarSimple)
        self.ui.txtCantidad.textChanged.connect(self.mostrarSimple)
        self.ui.checkDuplex.toggled.connect(self.mostrarSimple)
        
        # eventos para tabla de gran formato
        self.ui.tabla_granformato.itemClicked.connect(self.medidasHandle)
        self.ui.txtAnchoMaterial.textChanged.connect(self.medidasHandle)
        self.ui.txtAltoMaterial.textChanged.connect(self.medidasHandle)
        # lo demás está en la superclase :p
        
        self.showMinimized()
    
    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def mostrarSimple(self):
        if item := self.generarSimple():
            self.ui.lbTotalSimple.setText(f'Total: ${Moneda(item.importe)}')
        else:
            self.ui.lbTotalSimple.setText('Total: ...')
    
    def medidasHandle(self):
        if item := self.generarGranFormato():
            self.ui.lbTotalGran.setText(f'Total: ${Moneda(item.importe)}')
        else:
            self.ui.lbTotalGran.setText('Total: ...')
