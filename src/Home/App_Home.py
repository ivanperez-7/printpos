from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import (QDate, Qt, QPropertyAnimation,
                          QRect, QEasingCurve, pyqtSignal)

from mydecorators import run_in_thread
from mywidgets import VentanaPrincipal


class App_Home(QtWidgets.QMainWindow):
    """
    Backend para la pantalla principal.
    """
    def __init__(self, parent: VentanaPrincipal):
        from Home.Ui_Home import Ui_Home
        
        super().__init__()

        self.ui = Ui_Home()
        self.ui.setupUi(self)
        
        user = parent.user
        
        # guardar conexión y usuarios como atributos
        self.conn = parent.conn
        self.user = parent.user
        
        # foto de perfil del usuario
        if user.foto_perfil:
            qp = QPixmap()
            qp.loadFromData(user.foto_perfil)
        else:
            qp = QPixmap("resources/images/user.png")
            
        self.ui.fotoPerfil.setPixmap(qp)

        # ocultar lista y proporcionar eventos
        self.ui.listaNotificaciones.setVisible(False)
        self.ui.fotoPerfil.mousePressEvent = self.alternarNotificaciones
        self.agregarNotificaciones()

        # configurar texto dinámico
        self.ui.fechaHoy.setDate(QDate.currentDate())
        self.ui.usuario.setText(user.nombre)
        self.ui.tipo_usuario.setText(user.permisos)

        # deshabilita eventos del mouse para los textos en los botones
        items = vars(self.ui)
        items = [items[name] for name in items if 'label_' in name]

        for w in items:
            w.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        # crear eventos para los botones
        from AdministrarVentas import App_AdministrarVentas
        from AdministrarInventario import App_AdministrarInventario
        from AdministrarProductos import App_AdministrarProductos
        from AdministrarClientes import App_AdministrarClientes
        from AdministrarUsuarios import App_AdministrarUsuarios
        from Ajustes import App_Ajustes
        from Caja import App_Caja
        from Reportes import App_Reportes

        self.ui.btCrearVenta.clicked.connect(self.iniciarVenta)
        self.ui.btProductos.clicked.connect(lambda: self.crearVentana(App_AdministrarProductos))
        self.ui.btInventario.clicked.connect(lambda: self.crearVentana(App_AdministrarInventario))
        self.ui.btVentas.clicked.connect(lambda: self.crearVentana(App_AdministrarVentas))
        self.ui.btCaja.clicked.connect(lambda: self.crearVentana(App_Caja))
        self.ui.btClientes.clicked.connect(lambda: self.crearVentana(App_AdministrarClientes))
        self.ui.btUsuarios.clicked.connect(lambda: self.crearVentana(App_AdministrarUsuarios))
        self.ui.btReportes.clicked.connect(lambda: self.crearVentana(App_Reportes))
        self.ui.btAjustes.clicked.connect(lambda: self.crearVentana(App_Ajustes))
        self.ui.btSalir.clicked.connect(self.exitApp)

        # deshabilitar funciones para usuarios normales
        if not user.administrador:
            for w in [self.ui.frameInventario,
                      self.ui.frameCaja,
                      self.ui.frameUsuarios,
                      self.ui.frameProductos,
                      self.ui.frameReportes]:
                w.setEnabled(False)
    
    def showEvent(self, event):
        self.parentWidget().en_venta = False
        event.accept()
    
    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def alternarNotificaciones(self, _):
        """
        Se llama a esta función al hacer click en la foto de perfil
        del usuario. Anima el tamaño de la caja de notificaciones.
        """
        hiddenGeom = QRect(9, 76, 400, 0)
        shownGeom = QRect(9, 76, 400, 120)

        if not self.ui.listaNotificaciones.isVisible():
            # Create an animation to gradually change the height of the widget
            self.ui.listaNotificaciones.setVisible(True)
            self.show_animation = QPropertyAnimation(self.ui.listaNotificaciones, b'geometry')
            self.show_animation.setDuration(200)
            self.show_animation.setStartValue(hiddenGeom)
            self.show_animation.setEndValue(shownGeom)
            self.show_animation.setEasingCurve(QEasingCurve.OutSine)
            self.show_animation.start()
        else:
            # Hide the widget
            self.hide_animation = QPropertyAnimation(self.ui.listaNotificaciones, b'geometry')
            self.hide_animation.setDuration(200)
            self.hide_animation.setStartValue(shownGeom)
            self.hide_animation.setEndValue(hiddenGeom)
            self.hide_animation.setEasingCurve(QEasingCurve.InSine)
            self.hide_animation.finished.connect(lambda: self.ui.listaNotificaciones.setVisible(False))
            self.hide_animation.start()
    
    def agregarNotificaciones(self):
        """
        Llena la caja de notificaciones.
        """
        items = []
        crsr = self.conn.cursor()

        crsr.execute('''
        SELECT	COUNT(*)
        FROM	Ventas
        WHERE	fecha_hora_creacion != fecha_hora_entrega
                AND estado LIKE 'Recibido%'
                AND id_usuarios = ?;
        ''', (self.user.id,))
        
        numPendientes, = crsr.fetchone()

        if numPendientes:
            items.append(f'Tiene {numPendientes} pedidos pendientes.')

        crsr.execute('''
        SELECT  nombre,
                lotes_restantes,
                minimo_lotes
        FROM    Inventario 
        WHERE   lotes_restantes < minimo_lotes;
        ''')

        for nombre, stock, minimo in crsr:
            items.append(
                f'¡Hay que surtir el material {nombre}! ' +
                f'Faltan {minimo-stock} lotes para cubrir el mínimo.'
            )
        
        items = items or ['¡No hay nuevas notificaciones!']
        
        for item in items:
            self.ui.listaNotificaciones.addItem(item)

    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def iniciarVenta(self):
        from CrearVenta import App_CrearVenta
        
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Iniciar venta',
                          '¿Desea iniciar una nueva venta?', qm.Yes | qm.No)
        
        if ret == qm.Yes:
            self.crearVentana(App_CrearVenta)
        
    def crearVentana(self, modulo):
        parent = self.parentWidget()       # QMainWindow
        new = modulo(parent)
        parent.setCentralWidget(new)
    
    def exitApp(self):
        from Login import App_Login

        self.login = App_Login()
        self.parentWidget().close()


##################################
# VENTANA PARA CONSULTAR PRECIOS #
##################################
from myutils import son_similar
from mywidgets import LabelAdvertencia

class App_ConsultarPrecios(QtWidgets.QMainWindow):
    """
    Backend para el módulo de consultar precios.
    No se puede cerrar hasta cerrar por completo el sistema.
    """
    dataChanged = pyqtSignal()  # señal para actualizar tabla en hilo principal
    
    def __init__(self, principal: VentanaPrincipal):
        from Home.Ui_ConsultarPrecios import Ui_ConsultarPrecios
        
        super().__init__()
        
        self.ui = Ui_ConsultarPrecios()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        
        LabelAdvertencia(self.ui.tabla_seleccionar, '¡No se encontró ningún producto!')
        LabelAdvertencia(self.ui.tabla_granformato, '¡No se encontró ningún producto!')
        
        # guardar conexión y usuarios como atributos
        self.conn = principal.conn
        self.user = principal.user

        # dar formato a las tablas
        header = self.ui.tabla_seleccionar.horizontalHeader()

        for col in range(self.ui.tabla_seleccionar.columnCount()):
            if col == 1:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
        
        header = self.ui.tabla_granformato.horizontalHeader()

        for col in range(self.ui.tabla_granformato.columnCount()):
            if col == 1:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
        
        # eventos para widgets
        self.ui.searchBar.textChanged.connect(
            lambda: self.update_display(False))
        self.ui.groupButtonFiltro.buttonClicked.connect(
            lambda: self.update_display(False))
        self.ui.tabWidget.currentChanged.connect(
            lambda: self.tabla_actual.resizeRowsToContents())
        
        self.ui.tabla_seleccionar.itemClicked.connect(self.calcularPrecio)
        self.ui.txtCantidad.textChanged.connect(self.calcularPrecio)
        
        self.ui.tabla_granformato.itemClicked.connect(self.calcularPrecio)
        self.ui.txtAncho.textChanged.connect(self.calcularPrecio)
        self.ui.txtAlto.textChanged.connect(self.calcularPrecio)
        self.ui.groupButtonAlto.buttonClicked.connect(self.calcularPrecio)
        self.ui.groupButtonAncho.buttonClicked.connect(self.calcularPrecio)
        
        self.dataChanged.connect(
            lambda: self.update_display(True))
        
        # evento de Firebird para escuchar cambios en productos
        self.events = principal.conn.event_conduit(['cambio_productos'])
        self.events.begin()
        
        self.showMinimized()
        self.listenEvents()
    
    def showEvent(self, event):
        self.update_display(True)
    
    def closeEvent(self, event):
        if event.spontaneous():
            event.ignore()
        else:
            self.events.close()
            event.accept()
    
    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @property
    def tabla_actual(self):
        return [self.ui.tabla_seleccionar, self.ui.tabla_granformato][self.ui.tabWidget.currentIndex()]
    
    @run_in_thread
    def listenEvents(self):
        """
        Escucha trigger 'cambio_productos' en la base de datos.
        Al suceder, se actualizan las tablas de productos.
        """
        while True:
            if self.events.wait():
                self.dataChanged.emit()
                self.events.flush()
    
    def update_display(self, rescan: bool = False):
        """
        Actualiza la tabla y el contador de clientes.
        Acepta una cadena de texto para la búsqueda de clientes.
        También lee de nuevo la tabla de clientes, si se desea.
        """
        if rescan:
            crsr = self.conn.cursor()
            
            crsr.execute('SELECT * FROM View_Productos_Simples;')
            self.all_prod = crsr.fetchall()
            
            crsr.execute('SELECT * FROM View_Gran_Formato;')
            self.all_gran = crsr.fetchall()
        
        filtro = int(self.ui.btDescripcion.isChecked())
        txt_busqueda = self.ui.searchBar.text()
        
        # <tabla de productos normales>
        tabla = self.ui.tabla_seleccionar
        tabla.setRowCount(0)

        found = self.all_prod if not txt_busqueda else \
                filter(lambda prod: prod[filtro] 
                                    and son_similar(txt_busqueda, prod[filtro]), 
                       self.all_prod)

        for row, prod in enumerate(found):
            tabla.insertRow(row)

            for col, cell in enumerate(prod):
                if isinstance(cell, float):
                    cell = f'{cell:,.2f}'
                else:
                    cell = str(cell or '')
                tabla.setItem(row, col, QtWidgets.QTableWidgetItem(cell))
        # </tabla de productos normales>
        
        # <tabla de gran formato>
        tabla = self.ui.tabla_granformato
        tabla.setRowCount(0)

        found = self.all_gran if not txt_busqueda else \
                filter(lambda prod: prod[filtro] 
                                    and son_similar(txt_busqueda, prod[filtro]), 
                       self.all_gran)

        for row, prod in enumerate(found):
            tabla.insertRow(row)

            for col, cell in enumerate(prod):
                if isinstance(cell, float):
                    cell = f'{cell:,.2f}'
                else:
                    cell = str(cell or '')
                tabla.setItem(row, col, QtWidgets.QTableWidgetItem(cell))
        # </tabla de gran formato>
        
        self.tabla_actual.resizeRowsToContents()
    
    def calcularPrecio(self):
        if self.ui.tabWidget.currentIndex() == 0:
            self.calcularSimple()
        else:
            self.calcularGranFormato()
    
    def calcularSimple(self):
        selected = self.ui.tabla_seleccionar.selectedItems()
        
        try:
            precio = float(selected[2].text().replace(',',''))
            cantidad = float(self.ui.txtCantidad.text())
            
            self.ui.lbTotalSimple.setText(f'Total: ${precio * cantidad:,.2f}')
        except (ValueError, IndexError):
            self.ui.lbTotalSimple.setText('Total: $0.00')
    
    def calcularGranFormato(self):
        selected = self.ui.tabla_granformato.selectedItems()
        
        alto = self.ui.txtAlto.text()
        modificador_alto = 100 if self.ui.btAltoCm.isChecked() else 1
        
        ancho = self.ui.txtAncho.text()
        modificador_ancho = 100 if self.ui.btAnchoCm.isChecked() else 1
        
        try:
            precio = float(selected[4].text().replace(',',''))
            alto = float(alto) / modificador_alto
            ancho = float(ancho) / modificador_ancho
            
            self.ui.lbTotalGranFormato.setText(f'Total: ${precio * alto * ancho:,.2f}')
        except (ValueError, IndexError):
            self.ui.lbTotalGranFormato.setText('Total: $0.00')
