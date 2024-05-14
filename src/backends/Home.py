from functools import partial
import inspect

from PySide6 import QtWidgets
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QDate, Qt, Signal

from utils.mywidgets import LabelAdvertencia, VentanaPrincipal
from utils.myutils import Runner, son_similar


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
            self.ui.btSalir: self.exitApp
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
        from .CrearVenta import App_CrearVenta
        
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Iniciar venta',
                          '¿Desea iniciar una nueva venta?')
        if ret == qm.Yes:
            self.crearVentana(App_CrearVenta)
    
    def crearVentana(self, modulo):
        parent: VentanaPrincipal = self.parentWidget()  # QMainWindow
        new = modulo(parent)
        parent.setCentralWidget(new)
    
    def exitApp(self):
        self.parentWidget().close()


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
class App_ConsultarPrecios(QtWidgets.QWidget):
    """ Backend para el módulo de consultar precios.
        No se puede cerrar hasta cerrar por completo el sistema. """
    dataChanged = Signal()  # señal para actualizar tabla en hilo principal
    
    def __init__(self, principal: VentanaPrincipal):
        from ui.Ui_ConsultarPrecios import Ui_ConsultarPrecios
        
        super().__init__()
        
        self.ui = Ui_ConsultarPrecios()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        
        LabelAdvertencia(self.ui.tabla_seleccionar, '¡No se encontró ningún producto!')
        LabelAdvertencia(self.ui.tabla_granformato, '¡No se encontró ningún producto!')
        
        self.conn = principal.conn
        
        # manejador de DB, en tabla productos
        from utils.sql import ManejadorProductos
        self.manejador = ManejadorProductos(principal.conn)
        
        # eventos para widgets
        self.ui.searchBar.textChanged.connect(lambda: self.update_display(False))
        self.ui.groupButtonFiltro.buttonClicked.connect(lambda: self.update_display(False))
        self.ui.tabWidget.currentChanged.connect(
            lambda: self.tabla_actual.resizeRowsToContents())
        
        self.ui.tabla_seleccionar.itemClicked.connect(self.calcularPrecio)
        self.ui.txtCantidad.textChanged.connect(self.calcularPrecio)
        self.ui.checkDuplex.toggled.connect(self.calcularPrecio)
        
        self.ui.tabla_granformato.itemClicked.connect(self.calcularPrecio)
        self.ui.txtAncho.textChanged.connect(self.calcularPrecio)
        self.ui.txtAlto.textChanged.connect(self.calcularPrecio)
        self.ui.groupButtonAlto.buttonClicked.connect(self.calcularPrecio)
        self.ui.groupButtonAncho.buttonClicked.connect(self.calcularPrecio)
        
        self.dataChanged.connect(lambda: self.update_display(True))
        
        self.ui.tabla_seleccionar.configurarCabecera(lambda col: col != 1)
        self.ui.tabla_granformato.configurarCabecera(lambda col: col != 1)
        
        self.eventReader = Runner(self.startEvents)
        self.eventReader.start()
        self.showMinimized()
    
    def showEvent(self, event):
        self.update_display(True)
    
    def closeEvent(self, event):
        if event.spontaneous():
            event.ignore()
        else:
            # no recomendado generalmente para terminar hilos, sin embargo,
            # esta vez se puede hacer así al no ser una función crítica.
            self.eventReader.stop()
            self.events.close()
            event.accept()
    
    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @property
    def tabla_actual(self):
        return [self.ui.tabla_seleccionar, self.ui.tabla_granformato][self.ui.tabWidget.currentIndex()]
    
    def startEvents(self):
        # eventos de Firebird para escuchar cambios en tabla productos
        self.events = self.conn.event_conduit(['cambio_productos'])
        self.events.begin()
        
        while True:
            self.events.wait()
            self.dataChanged.emit()
            self.events.flush()
    
    def update_display(self, rescan: bool = False):
        """ Actualiza la tabla y el contador de clientes.
            Acepta una cadena de texto para la búsqueda de clientes.
            También lee de nuevo la tabla de clientes, si se desea. """
        if rescan:
            self.all_prod = self.manejador.obtenerVista('View_Productos_Simples')
            self.all_gran = self.manejador.obtenerVista('View_Gran_Formato')
        
        filtro = self.ui.btDescripcion.isChecked()
        txt_busqueda = self.ui.searchBar.text()
        
        # <tabla de productos normales>
        tabla = self.ui.tabla_seleccionar
        tabla.setRowCount(0)
        
        found = self.all_prod if not txt_busqueda else \
            filter(lambda prod: prod[filtro]
                                and son_similar(txt_busqueda, prod[filtro]),
                   self.all_prod)
        
        tabla.llenar(found)
        # </tabla de productos normales>
        
        # <tabla de gran formato>
        tabla = self.ui.tabla_granformato
        tabla.setRowCount(0)
        
        found = self.all_gran if not txt_busqueda else \
            filter(lambda prod: prod[filtro]
                                and son_similar(txt_busqueda, prod[filtro]),
                   self.all_gran)
        
        tabla.llenar(found)
        # </tabla de gran formato>
        
        self.tabla_actual.resizeRowsToContents()
    
    def calcularPrecio(self):
        if self.ui.tabWidget.currentIndex() == 0:
            self.calcularSimple()
        else:
            self.calcularGranFormato()
    
    def calcularSimple(self):
        if not (selected := self.ui.tabla_seleccionar.selectedItems()):
            return
        
        idProducto = self.manejador.obtenerIdProducto(selected[0].text())
        
        try:
            cantidad = float(self.ui.txtCantidad.text())
            precio = self.manejador.obtenerPrecioSimple(idProducto, cantidad,
                                                        self.ui.checkDuplex.isChecked())
            
            txt = f'Total: ${precio * cantidad:,.2f}'
        except ValueError:
            txt = 'Total: $0.00'
        
        self.ui.lbTotalSimple.setText(txt)
    
    def calcularGranFormato(self):
        if not (selected := self.ui.tabla_granformato.selectedItems()):
            return
        
        modificador_alto = 100 if self.ui.btAltoCm.isChecked() else 1
        modificador_ancho = 100 if self.ui.btAnchoCm.isChecked() else 1
        
        idProducto = self.manejador.obtenerIdProducto(selected[0].text())
        
        try:
            alto = float(self.ui.txtAlto.text()) / modificador_alto
            ancho = float(self.ui.txtAncho.text()) / modificador_ancho
            
            precio = self.manejador.obtenerPrecioGranFormato(idProducto, alto, ancho)
            
            txt = f'Total: ${precio:,.2f}'
        except ValueError:
            txt = 'Total: $0.00'
        
        self.ui.lbTotalGranFormato.setText(txt)
