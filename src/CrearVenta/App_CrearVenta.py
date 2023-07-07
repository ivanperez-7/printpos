from dataclasses import dataclass, field

from PySide6 import QtWidgets
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import (QDate, QDateTime, QRegularExpression, Qt,
                          QPropertyAnimation, QRect, QEasingCurve)

from databasemanagers import (ManejadorCaja, ManejadorClientes,
                              ManejadorProductos, ManejadorVentas)
from mydecorators import con_fondo, requiere_admin
from myutils import (clamp, enviarWhatsApp, formatDate,
                     generarOrdenCompra, generarTicketCompra,
                     generarTicketPresupuesto, son_similar)
from mywidgets import DimBackground, LabelAdvertencia, VentanaPrincipal


##################
# CLASE AUXILIAR #
##################
@dataclass
class ItemVenta:
    """ Clase para mantener registro de un producto de la venta. """
    id: int               # identificador interno en la base de datos
    codigo: str           # nombre del producto
    precio_unit: float    # precio por unidad
    descuento_unit: float # cantidad a descontar por unidad
    cantidad: int         # cantidad solicitada por el cliente
    notas: str            # especificaciones del producto
    duplex: bool          # dicta si el producto es duplex

    @property
    def importe(self) -> float:
        """ Costo total del producto. """
        return (self.precio_unit - self.descuento_unit) * self.cantidad
    
    def __iter__(self) -> tuple:
        """ Regresa iterable para alimentar las tablas de productos.
            Cantidad | Código | Especificaciones | Precio | Descuento | Importe """
        return iter((self.cantidad,
                    self.codigo + (' (a doble cara)' if self.duplex else ''), 
                    self.notas, 
                    self.precio_unit, 
                    self.descuento_unit, 
                    self.importe))


@dataclass
class Venta:
    """ Clase para mantener registro de una venta. """
    productos: list[ItemVenta] = field(default_factory=list)
    fechaCreacion: QDateTime = QDateTime.currentDateTime()
    fechaEntrega: QDateTime = QDateTime(fechaCreacion)
    metodoPago: str = 'Efectivo'
    requiereFactura: bool = False
    comentarios: str = ''
    idCliente: int = 1
        
    @property
    def total(self) -> float:
        if self.productos:
            temp = sum(prod.importe for prod in self.productos)
            return round(temp, 2)
        else:
            return 0.0
    
    @property
    def total_descuentos(self) -> float:
        return sum(prod.descuento_unit * prod.cantidad for prod in self.productos)
    
    @property
    def esVentaDirecta(self) -> bool:
        """ Compara fechas de creación y entrega para determinar si la venta será un pedido. """
        return self.fechaCreacion == self.fechaEntrega
    
    def obtenerProductosExistentes(self, codigo: str):
        return [p for p in self.productos if p.codigo == codigo]
    
    def __contains__(self, item: ItemVenta) -> bool:
        """ Indica si un item se halla en la venta. """
        return item.codigo in {p.codigo for p in self.productos}


#####################
# VENTANA PRINCIPAL #
#####################
class App_CrearVenta(QtWidgets.QMainWindow):
    """ Backend para la función de crear ventas.
        TODO:
            - mandar ticket por whatsapp o imprimir, sí o sí """
    def __init__(self, parent: VentanaPrincipal):
        from CrearVenta.Ui_CrearVenta import Ui_CrearVenta
        
        super().__init__()

        self.ui = Ui_CrearVenta()
        self.ui.setupUi(self)
        
        LabelAdvertencia(self.ui.tabla_productos, '¡Aún no hay productos!')

        # VARIABLE DE LA VENTA ACTIVA ACTUAL
        self.ventaDatos = Venta()
        
        # guardar conexión y usuarios como atributos
        self.conn = parent.conn
        self.user = parent.user
        
        # cuadro de texto para los descuentos del cliente
        self.dialogoDescuentos = SpeechBubble(self)
        self.dialogoDescuentos.setGeometry(610, 28, 0, 165)
        self.dialogoDescuentos.setVisible(False)

        # datos por defecto
        self.ui.txtVendedor.setText(self.user.nombre)
        self.ui.lbFecha.setText(formatDate(self.ventaDatos.fechaEntrega))

        # dar formato a la tabla principal
        header = self.ui.tabla_productos.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        for col in range(self.ui.tabla_productos.columnCount()):
            if col == 2:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)

        # deshabilita eventos del mouse para los textos en los botones
        items = vars(self.ui)
        items = [items[name] for name in items if 'label_' in name]

        for w in items:
            w.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # crear eventos para los botones
        self.ui.btCalendario.clicked.connect(self.cambiarFecha)
        self.ui.btAgregar.clicked.connect(self.agregarProducto)
        self.ui.btEliminar.clicked.connect(self.quitarProducto)
        self.ui.btRegresar.clicked.connect(self.goHome)
        
        ocultar_boton = lambda: self.ui.btDescuentosCliente.setVisible(False) \
                                or self.dialogoDescuentos.setVisible(False)
        
        self.ui.txtCliente.textChanged.connect(ocultar_boton)
        self.ui.txtCorreo.textChanged.connect(ocultar_boton)
        self.ui.txtTelefono.textChanged.connect(ocultar_boton)
        
        self.ui.tabla_productos.itemChanged.connect(self.itemChanged_handle)
        self.ui.btRegistrar.clicked.connect(self.insertarCliente)
        self.ui.btSeleccionar.clicked.connect(self.seleccionarCliente)
        self.ui.btDescuento.clicked.connect(self.agregarDescuento)
        self.ui.btDescuentosCliente.clicked.connect(self.alternarDescuentos)
        self.ui.btCotizacion.clicked.connect(self.generarCotizacion)
        self.ui.btListo.clicked.connect(self.confirmarVenta)
        
        self.ui.btDescuentosCliente.hide()
    
    def showEvent(self, event):
        self.parentWidget().en_venta = True
        event.accept()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def itemChanged_handle(self, item: QtWidgets.QTableWidgetItem):
        if item.column() == 2:
            self.ventaDatos.productos[item.row()].notas = item.text()
    
    @requiere_admin
    def goHome(self):
        from Home import App_Home
        
        parent = self.parentWidget()    # QMainWindow
        new = App_Home(parent)
        parent.setCentralWidget(new)
        
    def colorearActualizar(self):
        """ Llenar tabla con los productos seleccionados,
            luego calcular precios y actualizar los QLabel. """       
        # <llenar tabla>
        tabla = self.ui.tabla_productos
        tabla.setRowCount(0)

        for row, prod in enumerate(self.ventaDatos.productos):
            tabla.insertRow(row)

            for col, dato in enumerate(prod):
                if isinstance(dato, float):
                    if col == 4 and not dato: cell = ''
                    else: cell = f'{dato:,.2f}'
                else:
                    cell = str(dato or '')
                
                tableItem = QtWidgets.QTableWidgetItem(cell)
                flags = tableItem.flags()
                
                if col == 2:
                    flags |= Qt.ItemFlag.ItemIsEditable
                else:
                    flags &= ~Qt.ItemFlag.ItemIsEditable
                
                tableItem.setFlags(flags)
                tabla.setItem(row, col, tableItem)
        # </llenar tabla>
        
        # <calcular precios y mostrar>
        preciosConIVA = self.ventaDatos.total
        preciosSinIVA = preciosConIVA / 1.16
        impuestos = preciosConIVA - preciosSinIVA
        
        descuentos = self.ventaDatos.total_descuentos

        self.ui.lbTotal.setText(f'{preciosConIVA:,.2f}')
        self.ui.lbSubtotal.setText(f'{preciosSinIVA:,.2f}')
        self.ui.lbImpuestos.setText(f'{impuestos:,.2f}')
        self.ui.lbDescuento.setText(f'{descuentos:,.2f}')
        # </calcular precios y mostrar>
        
        tabla.resizeRowsToContents()
    
    def alternarDescuentos(self):
        """ Se llama a esta función al hacer click en la foto de perfil
        del usuario. Anima el tamaño de la caja de notificaciones. """
        hiddenGeom = QRect(610, 28, 0, 165)
        shownGeom = QRect(610, 28, 345, 165)

        if not self.dialogoDescuentos.isVisible():
            # Create an animation to gradually change the height of the widget
            self.dialogoDescuentos.setVisible(True)
            self.show_animation = QPropertyAnimation(self.dialogoDescuentos, b'geometry')
            self.show_animation.setDuration(200)
            self.show_animation.setStartValue(hiddenGeom)
            self.show_animation.setEndValue(shownGeom)
            self.show_animation.setEasingCurve(QEasingCurve.OutSine)
            self.show_animation.start()
        else:
            # Hide the widget
            self.hide_animation = QPropertyAnimation(self.dialogoDescuentos, b'geometry')
            self.hide_animation.setDuration(200)
            self.hide_animation.setStartValue(shownGeom)
            self.hide_animation.setEndValue(hiddenGeom)
            self.hide_animation.setEasingCurve(QEasingCurve.InSine)
            self.hide_animation.finished.connect(lambda: self.dialogoDescuentos.setVisible(False))
            self.hide_animation.start()

    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def cambiarFecha(self):
        """ Abre ventana para cambiar la fecha de entrega. """
        self.new = App_FechaEntrega(self)

    def seleccionarCliente(self):
        """ Abre ventana para seleccionar un cliente de la base de datos. """
        self.new = App_SeleccionarCliente(self)

    def insertarCliente(self):
        """ Abre ventana para registrar un cliente. """
        from AdministrarClientes import App_RegistrarCliente

        self.new = App_RegistrarCliente(
            self,
            nombre = self.ui.txtCliente.text(),
            celular = self.ui.txtTelefono.text(),
            correo = self.ui.txtCorreo.text()
        )
        self.new.success.connect(
            lambda nombre, tel, correo: 
                       self.ui.txtCliente.setText(nombre)
                    or self.ui.txtTelefono.setText(tel)
                    or self.ui.txtCorreo.setText(correo))

    def agregarProducto(self):
        """ Abre ventana para agregar un producto a la orden. """
        self.new = App_AgregarProducto(self)
        
    def quitarProducto(self):
        """ Pide confirmación para eliminar un producto de la tabla. """
        @requiere_admin
        def accion(parent, selected):
            for row in sorted(selected, reverse=True):
                self.ventaDatos.productos.pop(row)
            self.colorearActualizar()
            
        selected = {i.row() for i in self.ui.tabla_productos.selectedIndexes()}
        
        if not selected:
            return
        
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Atención',
                          '¿Desea descartar de la venta los productos seleccionados?',
                          qm.Yes | qm.No)
        
        if ret == qm.Yes:
            accion(self, selected)
    
    def agregarDescuento(self):
        """ Abre ventana para agregar un descuento a la orden si el cliente es especial. """
        @requiere_admin
        def accion(parent):
            self.new = App_AgregarDescuento(self)
        
        if self.ui.tabla_productos.rowCount():
            accion(self)
    
    def generarCotizacion(self):
        """ Genera PDF con cotización de la orden actual. """
        if not self.ui.tabla_productos.rowCount():
            return
        
        self.new = App_EnviarCotizacion(self)

    def confirmarVenta(self):
        """ Abre ventana para confirmar y terminar la venta. """
        if not self.ui.tabla_productos.rowCount():
            return
        
        qm = QtWidgets.QMessageBox

        # se confirma si existe el cliente en la base de datos
        manejador = ManejadorClientes(self.conn)
        
        nombre = self.ui.txtCliente.text().strip()
        telefono = self.ui.txtTelefono.text().strip()

        cliente = manejador.verificarCliente(nombre, telefono)

        if not cliente:
            qm.warning(self, '¡Atención!', 
                       'No se encontró el cliente en la base de datos.\n'
                       'Por favor, regístrelo como un nuevo cliente o seleccione "Público general".')
            return

        # indices para acceder a la tupla `cliente`
        id, nombre, telefono, correo, direccion, rfc, _, _ = range(8)
        
        if not self.ventaDatos.esVentaDirecta \
           and cliente[nombre] == 'Público general':
                qm.warning(self, '¡Atención!', 
                           'No se puede generar un pedido a nombre de "Público general".\n'
                           'Por favor, seleccione un cliente y/o regístrelo.')
                return

        if self.ui.tickFacturaSi.isChecked():
            if cliente[nombre] == 'Público general':
                qm.warning(self, '¡Atención!', 
                           'No se puede generar una factura a nombre de "Público general".\n'
                           'Por favor, verifique que los datos del cliente sean correctos.')
                return

            if not (cliente[correo] and cliente[direccion] and cliente[rfc]):
                from AdministrarClientes import App_EditarCliente
                
                self.new = App_EditarCliente(self, cliente[id])
                self.new.success.connect(
                    lambda nombre, tel, correo: 
                            self.ui.txtCliente.setText(nombre)
                            or self.ui.txtTelefono.setText(tel)
                            or self.ui.txtCorreo.setText(correo))
                
                qm.warning(self, '¡Atención!', 
                           'El cliente no tiene completos sus datos para la factura.\n'
                           'Por favor, llene los datos como corresponde.')
                return
        
        # todos los datos del cliente y fecha de entrega son correctos,
        # ahora se checa el monto total de la venta
        ret = qm.question(self, 'Concluir venta',
                          'Verifique todos los datos ingresados.\n'
                          '¿Desea concluir la venta?',
                          qm.Yes | qm.No)

        if ret == qm.Yes:    
            self.ventaDatos.idCliente = cliente[id]
            self.ventaDatos.metodoPago = self.ui.btMetodoGrupo.checkedButton().text()
            self.ventaDatos.requiereFactura = self.ui.boxFactura.isChecked()
            self.ventaDatos.comentarios = self.ui.txtComentarios.toPlainText()
            
            bg = DimBackground(self)
            self.new = App_ConfirmarVenta(self, self.ventaDatos)


#################################
# VENTANAS PARA EDITAR LA VENTA #
#################################
@con_fondo
class App_AgregarProducto(QtWidgets.QMainWindow):
    """ Backend para la función de agregar un producto a la venta. """
    def __init__(self, first: App_CrearVenta):
        from CrearVenta.Ui_AgregarProducto import Ui_AgregarProducto
        
        super().__init__(first)

        self.ui = Ui_AgregarProducto()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)

        LabelAdvertencia(self.ui.tabla_seleccionar, '¡No se encontró ningún producto!')
        LabelAdvertencia(self.ui.tabla_granformato, '¡No se encontró ningún producto!')
        
        # referencia a widget padre
        self.first = first
        
        # guardar conexión y usuarios como atributos
        self.conn = first.conn
        self.user = first.user

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

        manejador = ManejadorProductos(self.conn)
        
        # llena la tabla de productos no gran formato        
        self.all_prod = manejador.fetchall('SELECT * FROM View_Productos_Simples;')
        # llena la tabla de productos gran formato
        self.all_gran = manejador.fetchall('SELECT * FROM View_Gran_Formato;')

        # añade eventos para los botones
        self.ui.btRegresar.clicked.connect(self.close)
        self.ui.btAgregar.clicked.connect(self.done)
        self.ui.searchBar.textChanged.connect(self.update_display)
        self.ui.tabla_seleccionar.itemDoubleClicked.connect(self.done)
        self.ui.tabla_granformato.itemDoubleClicked.connect(self.done)
        self.ui.tabWidget.currentChanged.connect(lambda: self.tabla_actual.resizeRowsToContents())
        
        self.ui.groupFiltro.buttonClicked.connect(
            lambda: self.update_display(self.ui.searchBar.text()))
        
        # validadores para datos numéricos
        regexp_numero = QRegularExpression(r'\d*\.?\d*')
        validador = QRegularExpressionValidator(regexp_numero)
        self.ui.txtCantidad.setValidator(validador)

        self.show()
    
    def showEvent(self, event):
        self.update_display()

    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() in {Qt.Key_Return, Qt.Key_Enter}:
            self.done()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @property
    def tabla_actual(self):
        return [self.ui.tabla_seleccionar, self.ui.tabla_granformato][self.ui.tabWidget.currentIndex()]
    
    def update_display(self, txt_busqueda: str = ''):
        """ Actualiza la tabla y el contador de clientes.
            Acepta una cadena de texto para la búsqueda de clientes.
            También lee de nuevo la tabla de clientes, si se desea. """
        filtro = int(self.ui.btDescripcion.isChecked())
        
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

    def done(self):
        """ Determina la rutina a ejecutar basándose en la pestaña actual. """
        current = self.ui.tabWidget.currentIndex()
        
        if current == 0:
            item = self.agregarSimple()
        elif current == 1:
            item = self.agregarGranFormato()
        
        if item:
            self.first.ventaDatos.productos.append(item)
            self.first.colorearActualizar()
            self.close()
    
    def agregarSimple(self):
        selected = self.ui.tabla_seleccionar.selectedItems()
        
        if not selected:
            return
        
        try:
            cantidad = int(float(self.ui.txtCantidad.text() or 1))
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self, 'Atención',
                '¡Algo anda mal! La cantidad debe ser un número.')
            return
        
        if cantidad <= 0:
            return
        
        # obtener información del producto
        codigo = selected[0].text()
        manejador = ManejadorProductos(self.conn)
        
        idProducto, = manejador.obtenerIdProducto(codigo)
        
        # obtener precio basado en cantidad
        duplex = self.ui.checkDuplex.isChecked()
        
        try:
            precio, = manejador.obtenerPrecioSimple(idProducto, cantidad, duplex)
        except TypeError:
            QtWidgets.QMessageBox.warning(
                self, 'Atención',
                'No existe ningún precio de este producto '
                'asociado a la cantidad proporcionada.')
            return

        # insertar información del producto con cantidad y especificaciones        
        return ItemVenta(
                idProducto, codigo, precio, 0.0, cantidad, 
                self.ui.txtNotas.text().strip(), self.ui.checkDuplex.isChecked())
        
    def agregarGranFormato(self):
        selected = self.ui.tabla_granformato.selectedItems()
        
        try:
            codigo = selected[0].text()
        except IndexError:
            return
        
        ancho = self.ui.txtAncho.text()
        modificador_ancho = 100 if self.ui.btAnchoCm.isChecked() else 1
        
        alto = self.ui.txtAlto.text()
        modificador_alto = 100 if self.ui.btAltoCm.isChecked() else 1
        
        try:
            # determinar metros cuadrados
            ancho = float(ancho) / modificador_ancho
            alto = float(alto) / modificador_alto
            
            cantidad = ancho * alto
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self, 'Atención',
                '¡Algo anda mal! Las medidas deben ser números.')
            return
        
        if cantidad <= 0:
            return
        
        # obtener información del producto
        manejador = ManejadorProductos(self.conn)
        idProducto, = manejador.obtenerIdProducto(codigo)
        
        try:
            min_ancho, min_alto, precio = manejador.obtenerGranFormato(idProducto)
        except TypeError:
            QtWidgets.QMessageBox.warning(
                self, 'Atención',
                'No existe ningún precio de este producto.')
            return
        
        if ancho < min_ancho or alto < min_alto:
            QtWidgets.QMessageBox.warning(
                self, 'Atención',
                'Asegúrese de que las medidas satisfagan los mínimos.')
            return

        # insertar información del producto con cantidad y especificaciones
        return ItemVenta(
                idProducto, codigo, precio, 0.0, cantidad, 
                self.ui.txtNotas_2.text().strip(), False)


@con_fondo
class App_SeleccionarCliente(QtWidgets.QMainWindow):
    """ Backend para la función de seleccionar un cliente de la base de datos. """
    def __init__(self, first: App_CrearVenta):
        from CrearVenta.Ui_SeleccionarCliente import Ui_SeleccionarCliente
        
        super().__init__(first)

        self.ui = Ui_SeleccionarCliente()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)
        
        LabelAdvertencia(self.ui.tabla_seleccionar, '¡No se encontró ningún cliente!')

        # otras variables importantes
        self.first = first
        
        # guardar conexión y usuarios como atributos
        self.conn = first.conn
        self.user = first.user

        # dar formato a la tabla principal
        header = self.ui.tabla_seleccionar.horizontalHeader()

        for col in range(self.ui.tabla_seleccionar.columnCount()):
            if col == 3:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)

        # llena la tabla con todos los clientes existentes
        manejador = ManejadorClientes(self.conn)
        
        self.all = [datos for (id, *datos) in manejador.obtenerTablaPrincipal()]

        # añade eventos para los botones
        self.ui.btRegresar.clicked.connect(self.close)
        self.ui.btAgregar.clicked.connect(self.done)
        self.ui.searchBar.textChanged.connect(self.update_display)
        self.ui.tabla_seleccionar.itemDoubleClicked.connect(self.done)

        self.show()
    
    def showEvent(self, event):
        self.update_display()
    
    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() in {Qt.Key_Return, Qt.Key_Enter}:
            self.done()
        
    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def update_display(self, txt_busqueda: str = ''):
        """ Actualiza la tabla y el contador de clientes.
            Acepta una cadena de texto para la búsqueda de clientes.
            También lee de nuevo la tabla de clientes, si se desea. """
        tabla = self.ui.tabla_seleccionar
        tabla.setRowCount(0)

        found = self.all if not txt_busqueda else \
                filter(lambda cliente: cliente[0] 
                                       and son_similar(txt_busqueda, cliente[0]), 
                       self.all)

        for row, item in enumerate(found):
            tabla.insertRow(row)

            for col, dato in enumerate(item):
                cell = str(dato or '')
                tabla.setItem(row, col, QtWidgets.QTableWidgetItem(cell))

        tabla.resizeRowsToContents()

    def done(self):
        """ Modifica datos de cliente en la ventana principal (CrearVenta). """
        selected = self.ui.tabla_seleccionar.selectedItems()

        if not selected:
            return

        # recuérdese que Clientes(Nombre, Teléfono, Correo, Dirección, RFC)
        nombre = selected[0].text()
        telefono = selected[1].text()
        correo = selected[2].text()

        self.first.ui.txtCliente.setText(nombre)
        self.first.ui.txtTelefono.setText(telefono)
        self.first.ui.txtCorreo.setText(correo)

        # checar si el cliente es especial
        manejador = ManejadorClientes(self.conn)
        
        especial, descuentos = manejador.obtenerDescuentosCliente(nombre, telefono)
        self.first.ui.btDescuentosCliente.setVisible(especial)
        
        if descuentos:
            txt = descuentos.strip() or 'El cliente aún no tiene descuentos.'
        else:
            txt = 'El cliente aún no tiene descuentos.'
        self.first.dialogoDescuentos.setText(txt)

        self.close()


@con_fondo
class App_FechaEntrega(QtWidgets.QMainWindow):
    """ Backend para la función de cambiar fecha de entrega. """
    def __init__(self, first: App_CrearVenta):
        from CrearVenta.Ui_FechaEntrega import Ui_FechaEntrega
        
        super().__init__(first)

        self.ui = Ui_FechaEntrega()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)

        self.first = first
        
        # datos por defecto
        fechaEntrega = first.ventaDatos.fechaEntrega
        self.ui.calendario.setSelectedDate(fechaEntrega.date())
        self.ui.horaEdit.setTime(fechaEntrega.time())
        
        hoy = QDate.currentDate()
        self.ui.calendario.setMinimumDate(hoy)
        self.ui.calendario.setMaximumDate(hoy.addYears(1))

        # añade eventos para los botones
        self.ui.btRegresar.clicked.connect(self.close)
        self.ui.btListo.clicked.connect(self.done)

        self.show()
    
    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() in {Qt.Key_Return, Qt.Key_Enter}:
            self.done()

    def done(self):
        """ Acepta los cambios y modifica la fecha seleccionada 
            en la ventana principal (CrearVenta). """
        dateTime = QDateTime(
            self.ui.calendario.selectedDate(), 
            self.ui.horaEdit.time())

        self.first.ventaDatos.fechaEntrega = dateTime
        self.first.ui.lbFecha.setText(formatDate(dateTime))

        self.close()


@con_fondo
class App_AgregarDescuento(QtWidgets.QMainWindow):
    """ Backend para agregar descuento a la orden. """
    def __init__(self, first: App_CrearVenta):
        from CrearVenta.Ui_AgregarDescuento import Ui_AgregarDescuento
        
        super().__init__(first)

        self.ui = Ui_AgregarDescuento()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)

        self.first = first
        
        # dar formato a la tabla principal
        header = self.ui.tabla_productos.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        for col in range(self.ui.tabla_productos.columnCount()):
            if col == 2:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
                
        # insertar productos a la tabla
        tabla = self.ui.tabla_productos
        tabla.setRowCount(0)
        
        self.productosVenta = first.ventaDatos.productos

        for row, prod in enumerate(self.productosVenta):
            tabla.insertRow(row)

            for col, dato in enumerate(prod):
                if isinstance(dato, float):
                    cell = f'{dato:,.2f}'
                else:
                    cell = str(dato or '')
                    
                cell = QtWidgets.QTableWidgetItem(cell)
                tabla.setItem(row, col, cell)

        # añade eventos para los botones
        self.ui.btRegresar.clicked.connect(self.close)
        self.ui.btListo.clicked.connect(self.done)
        
        # validadores numéricos
        regexp_numero = QRegularExpression(r'\d*\.?\d*')
        validador = QRegularExpressionValidator(regexp_numero)
        self.ui.txtPrecio.setValidator(validador)
        
        self.show()
    
    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() in {Qt.Key_Return, Qt.Key_Enter}:
            self.done()
        
    # ================ #
    # FUNCIONES ÚTILES #
    # ================ #
    def done(self):
        """ Acepta los cambios e inserta descuento en la lista de productos. """
        selected = self.ui.tabla_productos.selectedItems()
        
        if not selected:
            return
        
        prod = self.productosVenta[selected[0].row()]
   
        try:
            nuevo_precio = float(self.ui.txtPrecio.text())
        except ValueError:
            return
        
        prod.descuento_unit = clamp(prod.precio_unit - nuevo_precio, 0, prod.precio_unit)
        
        self.first.ui.btSeleccionar.setEnabled(False) 
        self.first.ui.txtCliente.setReadOnly(True)
        self.first.ui.txtCorreo.setReadOnly(True)
        self.first.ui.txtTelefono.setReadOnly(True)
        
        self.first.colorearActualizar()
        self.close()


@con_fondo
class App_EnviarCotizacion(QtWidgets.QMainWindow):
    """ Backend para agregar descuento a la orden. """
    def __init__(self, first: App_CrearVenta):
        from CrearVenta.Ui_Cotizacion import Ui_EnviarCotizacion
        
        super().__init__(first)

        self.ui = Ui_EnviarCotizacion()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)

        self.first = first

        # añade eventos para los botones
        self.ui.btRegresar.clicked.connect(self.close)
        self.ui.btTicket.clicked.connect(self.imprimirTicket)
        self.ui.btWhatsapp.clicked.connect(self.enviarWhatsApp)
        
        # deshabilita eventos del mouse para los textos en los botones
        items = vars(self.ui)
        items = [items[name] for name in items if 'label_' in name]

        for w in items:
            w.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.show()

    # ================ #
    # FUNCIONES ÚTILES #
    # ================ #
    def enviarWhatsApp(self):
        mensaje = [
            '*COTIZACIÓN DE VENTA*',
            f'Cliente: *{self.first.ui.txtCliente.text()}*',
            '-------------------------------------------',
            f'Fecha: *{formatDate(QDateTime.currentDateTime())}*',
            '-------------------------------------------'
        ]
        
        for prod in self.first.ventaDatos.productos:
            mensaje.extend([
                f'{prod.codigo} ({prod.cantidad:,.2f} unidades)',
                f'Importe: {prod.importe: ,.2f}',
                ''
            ])
        
        mensaje.append(f'*Total a pagar: {self.first.ui.lbTotal.text()}*')
        
        mensaje = '\n'.join(mensaje)
        celular = self.first.ui.txtTelefono.text()
        
        enviarWhatsApp(celular, mensaje)
        self.close()
        
    def imprimirTicket(self):             
        productos = [(prod.cantidad, prod.codigo, prod.precio_unit, 
                      prod.descuento_unit, prod.importe)
                     for prod in self.first.ventaDatos.productos]
        
        vendedor = self.first.ui.txtVendedor.text()
        
        generarTicketPresupuesto(productos, vendedor)
        self.close()


class App_ConfirmarVenta(QtWidgets.QMainWindow):
    """ Backend para la ventana de finalización de venta. """
    def __init__(self, first: App_CrearVenta, ventaDatos: Venta):
        from CrearVenta.Ui_ConfirmarVenta import Ui_ConfirmarVenta
        
        super().__init__(first)

        self.ui = Ui_ConfirmarVenta()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)

        esDirecta = ventaDatos.esVentaDirecta
        ventaDatos.fechaCreacion = QDateTime.currentDateTime()
        
        # guardar conexión y usuarios como atributos
        self.conn = first.conn
        self.user = first.user
        
        self.ventaDatos = ventaDatos

        # total de la compra y precio a pagarse ahora mismo
        self.total = ventaDatos.total
        self.paraPagar = self.total if esDirecta else round(self.total/2, 2)

        # dar formato a la tabla principal
        header = self.ui.tabla_productos.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        for col in range(self.ui.tabla_productos.columnCount()):
            if col == 2:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)

        # si la venta es directa, ocultar los widgets para apartados
        if esDirecta:
            for w in [self.ui.boxFechaEntrega,
                      self.ui.lbAnticipo1,
                      self.ui.lbAnticipo2,
                      self.ui.txtAnticipo]:
                w.hide()
            
            ventaDatos.fechaEntrega = ventaDatos.fechaCreacion

        #### registrar venta en tablas ####
        manejadorVentas = ManejadorVentas(self.conn)
        ventas_db_parametros = self.obtenerParametrosVentas()
        ventas_detallado_db_parametros = self.obtenerParametrosVentasDetallado()

        # ejecuta internamente un fetchone, por lo que se desempaca luego
        result = manejadorVentas.insertarVenta(ventas_db_parametros)
        if not result:
            return

        self.idVentas, = result
        manejadorVentas.insertarDetallesVenta(self.idVentas,
                                              ventas_detallado_db_parametros)
        
        # mostrar datos del cliente, fechas, etc.
        manejadorClientes = ManejadorClientes(self.conn)
        _, nombre, telefono, correo, *_ = manejadorClientes.obtenerCliente(ventaDatos.idCliente)

        self.ui.txtCliente.setText(nombre)
        self.ui.txtCorreo.setText(correo)
        self.ui.txtTelefono.setText(telefono)
        self.ui.txtCreacion.setText(formatDate(ventaDatos.fechaCreacion))
        self.ui.txtEntrega.setText(formatDate(ventaDatos.fechaEntrega))
        self.ui.lbTotal.setText(f'{ventaDatos.total:,.2f}')
        self.ui.txtAnticipo.setText(f'{self.paraPagar:.2f}')
        self.ui.lbFolio.setText(f'{self.idVentas}')
        
        # validadores para datos numéricos
        regexp_numero = QRegularExpression(r'\d*\.?\d*')
        validador = QRegularExpressionValidator(regexp_numero)
        
        self.ui.txtAnticipo.setValidator(validador)
        self.ui.txtPago.setValidator(validador)

        # añade eventos para los botones
        self.ui.btListo.clicked.connect(self.done)
        self.ui.btCancelar.clicked.connect(self.abortar)
        self.ui.txtPago.textChanged.connect(self.calcularCambio)
        self.ui.txtAnticipo.textChanged.connect(self.cambiarAnticipo)

        self.show()
        
        # brincar el proceso si el pago es de cero
        if self.paraPagar <= 0:
            self.done()
    
    def showEvent(self, event):
        self.update_display()
        event.accept()
    
    def closeEvent(self, event):
        event.ignore()
    
    # ================
    # FUNCIONES ÚTILES
    # ================
    def update_display(self):
        """ Llenar tabla de productos. """
        tabla = self.ui.tabla_productos
        tabla.setRowCount(0)

        for row, prod in enumerate(self.ventaDatos.productos):
            tabla.insertRow(row)

            for col, dato in enumerate(prod):
                if isinstance(dato, float):
                    if col == 4 and not dato: cell = ''
                    else: cell = f'{dato:,.2f}'
                else:
                    cell = str(dato or '')
                    
                cell = QtWidgets.QTableWidgetItem(cell)
                tabla.setItem(row, col, cell)
                
        tabla.resizeRowsToContents()
        
    def obtenerParametrosVentas(self):
        """ Parámetros para tabla ventas (datos generales). """
        return (self.ventaDatos.idCliente,
                self.user.id,
                self.ventaDatos.fechaCreacion.toPython(),
                self.ventaDatos.fechaEntrega.toPython(),
                self.ventaDatos.comentarios.strip(),
                self.ventaDatos.metodoPago,
                int(self.ventaDatos.requiereFactura),
                'No terminada')
    
    def obtenerParametrosVentasDetallado(self):
        """ Parámetros para tabla ventas_detallado (datos de productos). """
        return [(int(prod.id),
                 float(prod.cantidad),
                 float(prod.precio_unit),
                 float(prod.descuento_unit),
                 prod.notas,
                 prod.duplex) 
                for prod in self.ventaDatos.productos]
    
    def calcularCambio(self, txt):
        """ Recalcular cambio a entregar. """
        try:
            pago = float(txt)
        except ValueError:
            pago = 0.
        
        cambio = max(0., pago - self.paraPagar)
        self.ui.lbCambio.setText(f'{cambio:,.2f}')
    
    def cambiarAnticipo(self, txt):
        """ Cambiar el anticipo pagado por el cliente. """
        try:
            self.paraPagar = float(txt)
        except ValueError:
            self.paraPagar = round(self.total/2, 2)  # regresar al 50%
            self.ui.txtAnticipo.setText(f'{self.paraPagar:.2f}')
        
        self.calcularCambio(self.ui.txtPago.text())
    
    def done(self):
        """ Intenta finalizar la compra o pedido, actualizando el estado
            e insertando los correspondientes movimientos en la tabla Caja. """
        esDirecta = not self.ui.boxFechaEntrega.isVisible()
        
        try:
            pago = float(self.ui.txtPago.text())
        except ValueError:
            pago = 0.
            
        metodo = self.ventaDatos.metodoPago
        
        pagoAceptado = pago >= self.paraPagar if metodo == 'Efectivo' \
                       else pago == self.paraPagar
        minimoCincuentaPorCiento = round(self.total/2, 2) <= self.paraPagar <= self.total
        
        if not pagoAceptado or not minimoCincuentaPorCiento:
            return

        if pago >= 0.:
            manejadorCaja = ManejadorCaja(self.conn)
            hoy = QDateTime.currentDateTime().toPython()
            
            # registrar ingreso (sin cambio) en caja
            ingreso_db_parametros = (
                hoy,
                pago,
                f'Pago de venta con folio {self.idVentas}',
                metodo,
                self.user.id
            )
            
            if not manejadorCaja.insertarMovimiento(ingreso_db_parametros,
                                                     commit=False):
                return
            
            # registrar egreso (cambio) en caja
            if (cambio := pago - self.paraPagar):
                egreso_db_parametros = (
                    hoy,
                    -cambio,
                    f'Cambio de venta con folio {self.idVentas}',
                    metodo,
                    self.user.id
                )
                if not manejadorCaja.insertarMovimiento(egreso_db_parametros,
                                                         commit=False):
                    return
        
        # cambiar el estado de la venta a 'Terminada' o 'Recibido xx.xx'
        manejadorVentas = ManejadorVentas(self.conn)
        estado = 'Terminada' if esDirecta else f'Recibido {self.paraPagar:.2f}'
        
        if not manejadorVentas.actualizarEstadoVenta(self.idVentas, estado, commit=True):
            return

        # abrir pregunta
        qm = QtWidgets.QMessageBox

        if not esDirecta:
            qm.information(self, 'Éxito', 'Venta terminada. Se imprimirá ahora la orden de compra.')
            generarOrdenCompra(self.conn, self.idVentas)
        else:
            ret = qm.question(self, 'Éxito',
                              'Venta terminada. ¡Recuerde ofrecer el ticket de compra! '
                              '¿Desea imprimirlo?',
                              qm.Yes | qm.No)
            if ret == qm.Yes:
                generarTicketCompra(self.conn, self.idVentas)
        
        self.goHome()
    
    def abortar(self):
        """ Función para abortar la venta y actualizar estado a 'Cancelada'. """
        @requiere_admin
        def accion(parent):
            manejadorVentas = ManejadorVentas(self.conn)
            
            if manejadorVentas.actualizarEstadoVenta(self.idVentas, 'Cancelada',
                                                     commit=True):
                self.goHome()
        
        qm = QtWidgets.QMessageBox
        
        ret = qm.question(self, 'Atención', 
                          '¿Desea cancelar la venta? Esta acción no puede deshacerse.',
                          qm.Yes | qm.No)
        if ret == qm.Yes:
            accion(self)
    
    def goHome(self):
        """ Cierra la ventana y crea otra venta. """
        from Home import App_Home
        
        parent = self.parentWidget().parentWidget() # QMainWindow, ventana principal
        new = App_Home(parent)
        parent.setCentralWidget(new)
        
        self.close()


###########################################
# WIDGETS PERSONALIZADOS PARA ESTE MÓDULO #
###########################################
from PySide6.QtWidgets import QVBoxLayout, QTextBrowser, QWidget
from PySide6.QtGui import (QPainter, QColor, QPolygon, 
                         QFont, QPainterPath)
from PySide6.QtCore import Qt, QRectF, QPoint

class SpeechBubble(QWidget):
    def __init__(self, parent, text = ''):
        super().__init__(parent)

        # Create the layout and QTextBrowser
        layout = QVBoxLayout(self)
        layout.setContentsMargins(17, 17, 17, 17)

        self.text_browser = QTextBrowser()
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
        self.text_browser.setFont(QFont("MS Shell Dlg 2", 11))
        self.text_browser.setLineWrapMode(QTextBrowser.LineWrapMode.FixedPixelWidth)
        self.text_browser.setLineWrapColumnOrWidth(295)
        self.text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
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


"""
function agregarProducto(nuevo: Item){
    prods = Obtener productos no duplex y duplex existentes con el código nuevo

    Si prods no es vacío:
        prods += nuevo

        Calcular número total de unidades entre existentes y nuevo (prods)
        Verificar si alguno de lo anterior es duplex

        Para cada producto en prods:
            Establecer nuevo precio(codigo, cantidad total, duplex)
    
    ventaDatos.productos.append(prod)
    tabla()
    cerrar()
}

function eliminarProducto(idx: int){
    codigo = ventaDatos.productos[idx].codigo

    ventaDatos.productos.pop(idx)
    prods = Obtener productos no duplex y duplex existentes con el código dado

    Si prods no es vacío:
        Calcular número total de unidades entre existentes y nuevo (prods)
        Verificar si alguno de lo anterior es duplex

        Para cada producto en prods:
            Establecer nuevo precio(codigo, cantidad total, duplex)

    tabla()
    cerrar()
}
"""