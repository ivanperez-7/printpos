import copy
from dataclasses import dataclass, field

from PySide6 import QtWidgets
from PySide6.QtCore import QDate, QDateTime, Qt

from utils.dinero import Dinero
from utils.mydecorators import con_fondo, requiere_admin
from utils.myutils import clamp, enviarWhatsApp, FabricaValidadores, formatDate, son_similar
from utils.mywidgets import DimBackground, LabelAdvertencia, SpeechBubble, VentanaPrincipal
from utils.pdf import ImpresoraOrdenes, ImpresoraTickets
from utils import sql

##################
# CLASE AUXILIAR #
##################
@dataclass
class ItemVenta:
    """ Clase para mantener registro de un producto simple de la venta. """
    id: int  # identificador interno en la base de datos
    codigo: str  # nombre del producto
    precio_unit: float  # precio por unidad
    descuento_unit: float  # cantidad a descontar por unidad
    cantidad: int  # cantidad solicitada por el cliente
    notas: str  # especificaciones del producto
    duplex: bool  # dicta si el producto es duplex
    
    @property
    def importe(self) -> float:
        """ Costo total del producto. """
        return (self.precio_unit - self.descuento_unit) * self.cantidad
    
    @property
    def total_descuentos(self) -> float:
        """ Regresa el total de descuentos (descuento * cantidad). """
        return self.descuento_unit * self.cantidad
    
    @classmethod
    def generarItemComision(cls, importe: Dinero, porcentaje: float):
        """ Generar item de comisión por pago con tarjeta """
        return cls(0, 'COMISION', 1., 0.,
                   importe * porcentaje / 100,
                   'COMISIÓN POR PAGO CON TARJETA', False)
    
    def __iter__(self):
        """ Regresa iterable para alimentar las tablas de productos.
            Cantidad | Código | Especificaciones | Precio | Descuento | Importe """
        return iter((self.cantidad,
                     self.codigo + (' (a doble cara)' if self.duplex else ''),
                     self.notas,
                     self.precio_unit,
                     self.descuento_unit,
                     self.importe))


@dataclass
class ItemGranFormato(ItemVenta):
    """ Clase para un producto de tipo gran formato.
        Reimplementa métodos `importe` y `total_descuentos`. """
    _min_m2: float
    
    @property
    def importe(self) -> float:
        cantidad = max(self._min_m2, self.cantidad)
        return (self.precio_unit - self.descuento_unit) * cantidad
    
    @property
    def total_descuentos(self) -> float:
        cantidad = max(self._min_m2, self.cantidad)
        return self.descuento_unit * cantidad


@dataclass
class Venta:
    """ Clase para mantener registro de una venta. """
    productos: list[ItemVenta] = field(default_factory=list)
    fechaCreacion: QDateTime = QDateTime.currentDateTime()
    fechaEntrega: QDateTime = QDateTime(fechaCreacion)
    requiereFactura: bool = False
    comentarios: str = ''
    id_cliente: int = 1
    
    @property
    def total(self) -> Dinero:
        return Dinero(sum(prod.importe for prod in self.productos))
    
    @property
    def total_descuentos(self) -> Dinero:
        return Dinero(sum(prod.total_descuentos for prod in self.productos))
    
    @property
    def esVentaDirecta(self) -> bool:
        """ Compara fechas de creación y entrega para determinar si la venta será un pedido. """
        return self.fechaCreacion == self.fechaEntrega
    
    def agregarProducto(self, item: ItemVenta):
        self.productos.append(item)
    
    def quitarProducto(self, row: int):
        self.productos.pop(row)
    
    def reajustarPrecios(self, conn: sql.Connection):
        ids = {p.id for p in self.productos}
        manejador = sql.ManejadorProductos(conn)
        
        for id in ids:
            productos = self.obtenerProductosExistentes(id)
            productosNormal = sum(p.cantidad for p in productos if not p.duplex)
            productosDuplex = sum(p.cantidad for p in productos if p.duplex)
            
            precioNormal = manejador.obtenerPrecioSimple(
                id,
                productosNormal + productosDuplex,
                False)
            
            if not precioNormal: continue
            
            precioDuplex = manejador.obtenerPrecioSimple(
                id,
                productosDuplex,
                True)
            nuevoPrecio = min(precioNormal, precioDuplex or precioNormal)
            
            for p in productos: p.precio_unit = nuevoPrecio
    
    def obtenerProductosExistentes(self, id: int):
        """ Obtiene todos los productos que tienen el identificador dado. """
        return [p for p in self.productos if p.id == id]
    
    def __iter__(self):
        return iter(self.productos)


#####################
# VENTANA PRINCIPAL #
#####################
class App_CrearVenta(QtWidgets.QMainWindow):
    """ Backend para la función de crear ventas.
        TODO:
            - mandar ticket por whatsapp o imprimir, sí o sí """
    
    def __init__(self, parent: VentanaPrincipal):
        from ui.Ui_CrearVenta import Ui_CrearVenta
        
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
        self.dialogoDescuentos.setVisible(False)
        
        # datos por defecto
        self.ui.txtVendedor.setText(self.user.nombre)
        self.ui.lbFecha.setText(formatDate(self.ventaDatos.fechaEntrega))
        self.ui.btDeshacer.setVisible(False)
        
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
        
        self.ui.tabla_productos.itemChanged.connect(self.item_changed)
        self.ui.btRegistrar.clicked.connect(self.insertarCliente)
        self.ui.btSeleccionar.clicked.connect(self.seleccionarCliente)
        self.ui.btDescuento.clicked.connect(
            lambda: self.agregarDescuento() if self.ui.tabla_productos.rowCount() else None)
        self.ui.btDescuentosCliente.clicked.connect(self.dialogoDescuentos.alternarDescuentos)
        self.ui.btDeshacer.clicked.connect(self.deshacerFechaEntrega)
        self.ui.btCotizacion.clicked.connect(self.generarCotizacion)
        self.ui.btListo.clicked.connect(self.confirmarVenta)
        
        self.ui.btDescuentosCliente.hide()
        
        self.ui.tabla_productos.quitarBordeCabecera()
        self.ui.tabla_productos.cambiarColorCabecera('#000')
        self.ui.tabla_productos.configurarCabecera(
            lambda col: col != 2,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    
    def showEvent(self, event):
        parent: VentanaPrincipal = self.parentWidget()
        parent.en_venta = True
    
    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def item_changed(self, item: QtWidgets.QTableWidgetItem):
        if item.column() == 2:
            self.ventaDatos.productos[item.row()].notas = item.text()
    
    def establecerCliente(self, nombre: str, telefono: str, correo: str):
        """ Atajo para modificar datos del cliente seleccionado. """
        self.ui.txtCliente.setText(nombre)
        self.ui.txtTelefono.setText(telefono)
        self.ui.txtCorreo.setText(correo)
    
    def actualizarLabelFecha(self):
        """ Actualizar widget de fecha de entrega:
            label y botón de deshacer. """
        self.ui.lbFecha.setText(formatDate(self.ventaDatos.fechaEntrega))
        self.ui.btDeshacer.setVisible(not self.ventaDatos.esVentaDirecta)
    
    def deshacerFechaEntrega(self):
        """ Deshacer cambio de fecha de entrega. """
        self.ventaDatos.fechaEntrega = QDateTime(self.ventaDatos.fechaCreacion)
        self.actualizarLabelFecha()
    
    def colorearActualizar(self):
        """ Llenar tabla con los productos seleccionados,
            luego calcular precios y actualizar los QLabel. """
        # <llenar tabla>
        tabla = self.ui.tabla_productos
        tabla.setRowCount(0)
        
        for row, prod in enumerate(self.ventaDatos):
            tabla.insertRow(row)
            
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
        
        self.ui.lbTotal.setText(f'{preciosConIVA}')
        self.ui.lbSubtotal.setText(f'{preciosSinIVA}')
        self.ui.lbImpuestos.setText(f'{impuestos}')
        self.ui.lbDescuento.setText(f'{self.ventaDatos.total_descuentos}')
        # </calcular precios y mostrar>
        
        tabla.resizeRowsToContents()
    
    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def cambiarFecha(self):
        """ Abre ventana para cambiar la fecha de entrega. """
        modulo = App_FechaEntrega(self)
    
    def seleccionarCliente(self):
        """ Abre ventana para seleccionar un cliente de la base de datos. """
        modulo = App_SeleccionarCliente(self)
    
    def insertarCliente(self):
        """ Abre ventana para registrar un cliente. """
        from AdministrarClientes import App_RegistrarCliente
        
        modulo = App_RegistrarCliente(
            self,
            nombre=self.ui.txtCliente.text(),
            celular=self.ui.txtTelefono.text(),
            correo=self.ui.txtCorreo.text()
        )
        modulo.success.connect(self.establecerCliente)
    
    def agregarProducto(self):
        """ Abre ventana para agregar un producto a la orden. """
        modulo = App_AgregarProducto(self)
    
    def quitarProducto(self):
        """ Pide confirmación para eliminar un producto de la tabla. """
        selected = {i.row() for i in self.ui.tabla_productos.selectedIndexes()}
        
        if not selected:
            return
        
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Atención',
                          '¿Desea descartar de la venta los productos seleccionados?')
        if ret == qm.Yes:
            self._quitarProducto(selected)
    
    @requiere_admin
    def _quitarProducto(self, selected: set[int], conn):
        """ En método separado para solicitar contraseña. """
        for row in sorted(selected, reverse=True):
            self.ventaDatos.quitarProducto(row)
        
        self.ventaDatos.reajustarPrecios(self.conn)
        self.colorearActualizar()
    
    @requiere_admin
    def agregarDescuento(self, conn):
        """ Abre ventana para agregar un descuento a la orden si el cliente es especial. """
        modulo = App_AgregarDescuento(self)
    
    def generarCotizacion(self):
        """ Genera PDF con cotización de la orden actual. """
        if self.ui.tabla_productos.rowCount():
            modulo = App_EnviarCotizacion(self)
    
    def confirmarVenta(self):
        """ Abre ventana para confirmar y terminar la venta. """
        if not self.ui.tabla_productos.rowCount():
            return
        
        qm = QtWidgets.QMessageBox
        
        # se confirma si existe el cliente en la base de datos
        manejador = sql.ManejadorClientes(self.conn)
        
        nombre = self.ui.txtCliente.text().strip()
        telefono = self.ui.txtTelefono.text().strip()
        
        cliente = manejador.obtenerCliente(nombre, telefono)
        
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
                
                modulo = App_EditarCliente(self, cliente[id])
                modulo.success.connect(self.establecerCliente)
                
                qm.warning(self, '¡Atención!',
                           'El cliente no tiene completos sus datos para la factura.\n'
                           'Por favor, llene los datos como corresponde.')
                return
        
        # todos los datos del cliente y fecha de entrega son correctos,
        # ahora se checa el monto total de la venta
        ret = qm.question(self, 'Concluir venta',
                          'Verifique todos los datos ingresados.\n'
                          '¿Desea concluir la venta?')
        
        if ret == qm.Yes:
            self.ventaDatos.id_cliente = cliente[id]
            self.ventaDatos.requiereFactura = self.ui.tickFacturaSi.isChecked()
            self.ventaDatos.comentarios = self.ui.txtComentarios.toPlainText()
            
            bg = DimBackground(self)
            modulo = App_ConfirmarVenta(self, self.ventaDatos)
    
    @requiere_admin
    def goHome(self, conn):
        """ Cierra la ventana y regresa al inicio. """
        parent: VentanaPrincipal = self.parentWidget()
        parent.goHome()


#################################
# VENTANAS PARA EDITAR LA VENTA #
#################################
@con_fondo
class App_AgregarProducto(QtWidgets.QMainWindow):
    """ Backend para la función de agregar un producto a la venta. """
    
    def __init__(self, first: App_CrearVenta):
        from ui.Ui_AgregarProducto import Ui_AgregarProducto
        
        super().__init__(first)
        
        self.ui = Ui_AgregarProducto()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)
        
        LabelAdvertencia(self.ui.tabla_seleccionar, '¡No se encontró ningún producto!')
        LabelAdvertencia(self.ui.tabla_granformato, '¡No se encontró ningún producto!')
        
        # referencia a widget padre
        self.first = first
        
        # guardar conexión y usuarios como atributos
        self.conn = first.conn
        self.user = first.user
        
        manejador = sql.ManejadorProductos(self.conn)
        
        # llena la tabla de productos no gran formato        
        self.all_prod = manejador.obtenerVista('View_Productos_Simples')
        # llena la tabla de productos gran formato
        self.all_gran = manejador.obtenerVista('View_Gran_Formato')
        
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
        self.ui.txtCantidad.setValidator(
            FabricaValidadores.NumeroDecimal)
        
        self.ui.tabla_seleccionar.configurarCabecera(lambda col: col != 1)
        self.ui.tabla_granformato.configurarCabecera(lambda col: col != 1)
        
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
        
        if not item:
            return
        
        self.first.ventaDatos.agregarProducto(item)
        self.first.ventaDatos.reajustarPrecios(self.conn)
        
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
        manejador = sql.ManejadorProductos(self.conn)
        
        idProducto = manejador.obtenerIdProducto(codigo)
        
        # obtener precio basado en cantidad
        duplex = self.ui.checkDuplex.isChecked()
        precio = manejador.obtenerPrecioSimple(idProducto, cantidad, duplex)
        
        if not precio:
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
        manejador = sql.ManejadorProductos(self.conn)
        idProducto = manejador.obtenerIdProducto(codigo)
        
        min_m2, precio = manejador.obtenerGranFormato(idProducto)
        
        # insertar información del producto con cantidad y especificaciones
        return ItemGranFormato(
            idProducto, codigo, precio, 0.0, cantidad,
            self.ui.txtNotas_2.text().strip(), False, min_m2)


@con_fondo
class App_SeleccionarCliente(QtWidgets.QMainWindow):
    """ Backend para la función de seleccionar un cliente de la base de datos. """
    
    def __init__(self, first: App_CrearVenta):
        from ui.Ui_SeleccionarCliente import Ui_SeleccionarCliente
        
        super().__init__(first)
        
        self.ui = Ui_SeleccionarCliente()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)
        
        LabelAdvertencia(self.ui.tabla_seleccionar, '¡No se encontró ningún cliente!')
        
        # otras variables importantes
        self.first = first
        
        # guardar conexión y usuarios como atributos
        self.conn = first.conn
        self.user = first.user
        
        # llena la tabla con todos los clientes existentes
        manejador = sql.ManejadorClientes(self.conn)
        
        self.all = [datos for (id, *datos) in manejador.obtenerTablaPrincipal()]
        
        # añade eventos para los botones
        self.ui.btRegresar.clicked.connect(self.close)
        self.ui.btAgregar.clicked.connect(self.done)
        self.ui.searchBar.textChanged.connect(self.update_display)
        self.ui.tabla_seleccionar.itemDoubleClicked.connect(self.done)
        
        self.ui.tabla_seleccionar.configurarCabecera(lambda col: col in [1, 4])
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
        
        self.first.establecerCliente(nombre, telefono, correo)
        
        # checar si el cliente es especial
        manejador = sql.ManejadorClientes(self.conn)
        
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
        from ui.Ui_FechaEntrega import Ui_FechaEntrega
        
        super().__init__(first)
        
        self.ui = Ui_FechaEntrega()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)
        
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
        self.first.actualizarLabelFecha()
        
        self.close()


@con_fondo
class App_AgregarDescuento(QtWidgets.QMainWindow):
    """ Backend para agregar descuento a la orden. """
    
    def __init__(self, first: App_CrearVenta):
        from ui.Ui_AgregarDescuento import Ui_AgregarDescuento
        
        super().__init__(first)
        
        self.ui = Ui_AgregarDescuento()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)
        
        self.first = first
        
        # añade eventos para los botones
        self.ui.btRegresar.clicked.connect(self.close)
        self.ui.btListo.clicked.connect(self.done)
        
        # validadores numéricos
        self.ui.txtPrecio.setValidator(
            FabricaValidadores.NumeroDecimal)
        
        self.ui.tabla_productos.quitarBordeCabecera()
        self.ui.tabla_productos.cambiarColorCabecera('#000')
        self.ui.tabla_productos.configurarCabecera(
            lambda col: col != 2,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self.show()
    
    def showEvent(self, event):
        self.update_display()
    
    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() in {Qt.Key_Return, Qt.Key_Enter}:
            self.done()
    
    # ================ #
    # FUNCIONES ÚTILES #
    # ================ #
    def update_display(self):
        """ Insertar productos a la tabla. """
        tabla = self.ui.tabla_productos
        tabla.setRowCount(0)
        
        self.productosVenta = self.first.ventaDatos.productos
        
        for row, prod in enumerate(self.productosVenta):
            tabla.insertRow(row)
            
            for col, dato in enumerate(prod):
                if isinstance(dato, float):
                    cell = f'{dato:,.2f}'
                else:
                    cell = str(dato or '')
                
                cell = QtWidgets.QTableWidgetItem(cell)
                tabla.setItem(row, col, cell)
    
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
        from ui.Ui_Cotizacion import Ui_EnviarCotizacion
        
        super().__init__(first)
        
        self.ui = Ui_EnviarCotizacion()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)
        
        self.first = first
        self.conn = first.conn
        
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
        
        impresora = ImpresoraTickets(self)
        impresora.imprimirTicketPresupuesto(productos, vendedor)
        
        self.close()


class App_ConfirmarVenta(QtWidgets.QMainWindow):
    """ Backend para la ventana de finalización de venta. """
    COMISION_DEBITO = 1.98
    COMISION_CREDITO = 3.16
    
    def __init__(self, first: App_CrearVenta, ventaDatos: Venta):
        from ui.Ui_ConfirmarVenta import Ui_ConfirmarVenta
        
        super().__init__(first)
        
        self.ui = Ui_ConfirmarVenta()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)
        self.setFixedWidth(833)
        
        # guardar conexión y usuarios como atributos
        self.conn = first.conn
        self.user = first.user
        
        # venta inicial, SIN NIGUNA COMISIÓN POR TARJETA
        self.ventaDatos = ventaDatos
        
        # si la venta es directa, ocultar los widgets para apartados
        if ventaDatos.esVentaDirecta:
            ventaDatos.fechaCreacion = QDateTime.currentDateTime()
            ventaDatos.fechaEntrega = QDateTime(ventaDatos.fechaCreacion)
            
            for w in [self.ui.boxFechaEntrega,
                      self.ui.lbAnticipo1,
                      self.ui.lbAnticipo2,
                      self.ui.txtAnticipo,
                      self.ui.lbCincuenta]:
                w.hide()
            
            self.setFixedHeight(759)
        else:
            ventaDatos.fechaCreacion = QDateTime.currentDateTime()
            self.setFixedHeight(795)
        
        # agregar pago y seleccionar botón de método
        wdg = self.ui.stackedWidget.agregarPago()
        
        for bt in wdg.grupoBotones.buttons():
            bt.setChecked(
                first.ui.btMetodoGrupo.checkedButton().text() == bt.text())
        
        # mostrar datos del cliente, fechas, etc.
        self.id_ventas = self.registrarVenta()
        
        manejadorClientes = sql.ManejadorClientes(self.conn)
        _, nombre, telefono, correo, *_ = manejadorClientes.obtenerCliente(ventaDatos.id_cliente)
        
        self.ui.txtCliente.setText(nombre)
        self.ui.txtCorreo.setText(correo)
        self.ui.txtTelefono.setText(telefono)
        self.ui.txtCreacion.setText(formatDate(ventaDatos.fechaCreacion))
        self.ui.txtEntrega.setText(formatDate(ventaDatos.fechaEntrega))
        self.ui.lbFolio.setText(f'{self.id_ventas}')
        
        self.ui.lbCincuenta.setText(f'(${ventaDatos.total / 2})')
        
        # añade eventos para los botones
        self.ui.btListo.clicked.connect(self.verificar)
        self.ui.btCancelar.clicked.connect(self.abortar)
        self.ui.txtAnticipo.textChanged.connect(self.cambiarAnticipo)
        
        self.ui.btAgregar.clicked.connect(self.ui.stackedWidget.agregarPago)
        self.ui.btAgregar.clicked.connect(self.modificar_contador)
        self.ui.btQuitar.clicked.connect(self.ui.stackedWidget.quitarPago)
        self.ui.btQuitar.clicked.connect(self.modificar_contador)
        self.ui.btAnterior.clicked.connect(self.ui.stackedWidget.retroceder)
        self.ui.btAnterior.clicked.connect(self.modificar_contador)
        self.ui.btSiguiente.clicked.connect(self.ui.stackedWidget.avanzar)
        self.ui.btSiguiente.clicked.connect(self.modificar_contador)
        
        # configurar tabla de productos
        self.ui.tabla_productos.quitarBordeCabecera()
        self.ui.tabla_productos.configurarCabecera(
            lambda col: col != 2,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self.recalcularImportes(self.ventaDatos)
        self.update_display(self.ventaDatos)
        
        self.show()
        
        # brincar el proceso si el pago es de cero
        if self.para_pagar <= 0:
            self.terminarVenta()
    
    def closeEvent(self, event):
        event.ignore()
    
    # ================
    # FUNCIONES ÚTILES
    # ================
    def modificar_contador(self):
        self.ui.lbContador.setText('Pago {}/{}'.format(self.ui.stackedWidget.currentIndex()+1,
                                                       self.ui.stackedWidget.count()))
        
    def registrarVenta(self) -> int:
        """ Registra datos principales de venta en DB
            y regresa folio de venta insertada. """
        manejadorVentas = sql.ManejadorVentas(self.conn)
        ventas_db_parametros = self.obtenerParametrosVentas()
        ventas_detallado_db_parametros = self.obtenerParametrosVentasDetallado()
        
        # ejecuta internamente un fetchone, por lo que se desempaca luego
        result = manejadorVentas.insertarVenta(ventas_db_parametros)
        if not result:
            return
        
        id_ventas, = result
        manejadorVentas.insertarDetallesVenta(id_ventas,
                                              ventas_detallado_db_parametros)
        return id_ventas
    
    def handleComision(self, bt: QtWidgets.QRadioButton):
        """ Mostrar u ocultar comisión según método de pago. """
        venta = copy.deepcopy(self.ventaDatos)
        metodo = bt.text()
        
        if metodo.endswith('crédito'):
            item = ItemVenta.generarItemComision(venta.total, self.COMISION_CREDITO)
            venta.agregarProducto(item)
        elif metodo.endswith('débito'):
            item = ItemVenta.generarItemComision(venta.total, self.COMISION_DEBITO)
            venta.agregarProducto(item)
        else:
            venta = self.ventaDatos
        
        self.recalcularImportes(venta)
        self.update_display(venta)
    
    def update_display(self, venta: Venta):
        """ Llenar tabla de productos. """
        tabla = self.ui.tabla_productos
        tabla.setRowCount(0)
        
        for row, prod in enumerate(venta):
            tabla.insertRow(row)
            
            for col, dato in enumerate(prod):
                if isinstance(dato, float):
                    if col == 4 and not dato:
                        cell = ''
                    else:
                        cell = f'{dato:,.2f}'
                else:
                    cell = str(dato or '')
                
                cell = QtWidgets.QTableWidgetItem(cell)
                tabla.setItem(row, col, cell)
        
        tabla.resizeRowsToContents()
    
    def recalcularImportes(self, venta: Venta):
        """ Calcular total de la compra y precio a pagarse ahora mismo. """
        self.total = venta.total
        self.para_pagar = venta.total if venta.esVentaDirecta \
            else venta.total / 2
        
        self.ui.lbTotal.setText(f'{self.total}')
        self.ui.txtAnticipo.cantidad = self.para_pagar
        self.ui.stackedWidget.total = self.para_pagar
    
    def obtenerParametrosVentas(self):
        """ Parámetros para tabla ventas (datos generales). """
        return (self.ventaDatos.id_cliente,
                self.user.id,
                self.ventaDatos.fechaCreacion.toPython(),
                self.ventaDatos.fechaEntrega.toPython(),
                self.ventaDatos.comentarios.strip(),
                self.ventaDatos.requiereFactura,
                'No terminada')
    
    def obtenerParametrosVentasDetallado(self):
        """ Parámetros para tabla ventas_detallado (datos de productos). """
        return [(prod.id,
                 prod.cantidad,
                 prod.precio_unit,
                 prod.descuento_unit,
                 prod.notas,
                 prod.duplex,
                 prod.importe)
                for prod in self.ventaDatos.productos]
    
    def cambiarAnticipo(self):
        """ Cambiar el anticipo pagado por el cliente. """
        self.para_pagar = self.ui.txtAnticipo.cantidad
        self.ui.stackedWidget.total = self.para_pagar
    
    def verificar(self):
        """ Intenta finalizar la compra o pedido, actualizando el estado
            e insertando los correspondientes movimientos en la tabla Caja. """
        if not 0. <= self.para_pagar <= self.total:
            return
        
        if not self.ui.stackedWidget.pagosValidos:
            return
        if not self.total / 2 <= self.para_pagar:
            qm = QtWidgets.QMessageBox
            ret = qm.question(self, 'Atención',
                              'El anticipo está por debajo del 50% del total de compra.\n'
                              '¿Desea continuar?')
            if ret == qm.Yes:
                self.terminarVentaAdmin()
        else:
            self.terminarVenta()
    
    @requiere_admin
    def terminarVentaAdmin(self, conn):
        """ Saltar ciertas verificaciones, pero con cuenta de administrador. """
        self.terminarVenta()
    
    def terminarVenta(self):
        """ Tras verificar todas las condiciones, finalizar venta y
            registrarla en la base de datos. """
        manejadorVentas = sql.ManejadorVentas(self.conn)
        
        # registrar pagos en tabla ventas_pagos
        for wdg in self.ui.stackedWidget.widgetsPago:
            montoAPagar = wdg.montoPagado if wdg.metodoSeleccionado != 'Efectivo' \
                else self.ui.stackedWidget.totalEnEfectivo
                
            if not manejadorVentas.insertarPago(self.id_ventas, wdg.metodoSeleccionado,
                                                montoAPagar, wdg.montoPagado):
                return
        
        # cambiar el estado de la venta a 'Terminada' o 'Recibido xx.xx'
        # y también cambiar método de pago
        esDirecta = not self.ui.boxFechaEntrega.isVisible()
        estado = 'Terminada' if esDirecta else f'Recibido ${self.para_pagar}'
        
        if manejadorVentas.actualizarEstadoVenta(self.id_ventas, estado, commit=True):
            self.dialogoExito()
    
    def dialogoExito(self):
        esDirecta = not self.ui.boxFechaEntrega.isVisible()
        qm = QtWidgets.QMessageBox
        
        if not esDirecta:
            qm.information(self, 'Éxito', 'Venta terminada. Se imprimirá ahora la orden de compra.')
            
            impresora = ImpresoraOrdenes(self)
            impresora.imprimirOrdenCompra(self.id_ventas)
        else:
            ret = qm.question(self, 'Éxito',
                              'Venta terminada. ¡Recuerde ofrecer el ticket de compra! '
                              '¿Desea imprimirlo?')
            if ret == qm.Yes:
                impresora = ImpresoraTickets(self)
                impresora.imprimirTicketCompra(self.id_ventas)
        self.goHome()
    
    def abortar(self):
        """ Función para abortar la venta y actualizar estado a 'Cancelada'. """
        qm = QtWidgets.QMessageBox
        
        ret = qm.question(self, 'Atención',
                          '¿Desea cancelar la venta? Esta acción no puede deshacerse.')
        if ret == qm.Yes:
            self._abortar()
    
    @requiere_admin
    def _abortar(self, conn):
        manejadorAdmin = sql.ManejadorVentas(conn)
        
        estado = 'Cancelada por ' + manejadorAdmin.usuarioActivo
        if manejadorAdmin.actualizarEstadoVenta(self.id_ventas, estado,
                                                commit=True):
            self.goHome()
    
    def goHome(self):
        """ Cierra la ventana y crea otra venta. """
        parent: VentanaPrincipal = self.parentWidget().parentWidget()
        parent.goHome()
        self.close()
