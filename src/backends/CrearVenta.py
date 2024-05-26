from dataclasses import dataclass, field
from typing import Iterator

from PySide6 import QtWidgets
from PySide6.QtCore import QDate, QDateTime, Signal, Qt

from .AdministrarVentas import Base_PagarVenta
from utils import Moneda
from utils.mydecorators import con_fondo, requiere_admin
from utils.myutils import *
from utils.mywidgets import DimBackground, LabelAdvertencia, SpeechBubble, VentanaPrincipal
from utils.pdf import ImpresoraOrdenes, ImpresoraTickets
from utils.sql import ManejadorClientes, ManejadorProductos, ManejadorVentas

##################
# CLASE AUXILIAR #
##################
@dataclass
class BaseItem:
    """ Clase para mantener registro de un producto simple de la venta. """
    id: int  # identificador interno en la base de datos
    codigo: str  # nombre del producto
    nombre_ticket: str # nombre para mostrar en tickets y órdenes
    precio_unit: float  # precio por unidad
    descuento_unit: float  # cantidad a descontar por unidad
    cantidad: int  # cantidad solicitada por el cliente
    notas: str  # especificaciones del producto
    
    @property
    def importe(self):
        """ Costo total del producto. """
        raise NotImplementedError('BEIS CLASSSS')
    
    @property
    def total_descuentos(self):
        """ Regresa el total de descuentos (descuento * cantidad). """
        raise NotImplementedError('BEIS CLASSSS')


@dataclass
class ItemVenta(BaseItem):
    """ Clase para mantener registro de un producto simple de la venta. """
    duplex: bool  # dicta si el producto es duplex
    
    def __post_init__(self):
        if self.duplex:
            self.nombre_ticket += ' (a doble cara)'
    
    @property
    def importe(self):
        """ Costo total del producto. """
        return (self.precio_unit - self.descuento_unit) * self.cantidad
    
    @property
    def total_descuentos(self):
        """ Regresa el total de descuentos (descuento * cantidad). """
        return self.descuento_unit * self.cantidad
    
    def __iter__(self):
        """ Regresa iterable para alimentar las tablas de productos.
            Cantidad | Código | Especificaciones | Precio | Descuento | Importe """
        yield from (self.cantidad,
                    self.codigo + (' (a doble cara)' if self.duplex else ''),
                    self.notas,
                    self.precio_unit,
                    self.descuento_unit,
                    self.importe)


@dataclass
class ItemGranFormato(BaseItem):
    """ Clase para un producto de tipo gran formato.
        Reimplementa métodos `importe` y `total_descuentos`. """
    min_m2: float

    @property
    def importe(self):
        cantidad = max(self.min_m2, self.cantidad)
        return (self.precio_unit - self.descuento_unit) * cantidad
    
    @property
    def total_descuentos(self):
        cantidad = max(self.min_m2, self.cantidad)
        return self.descuento_unit * cantidad

    def __iter__(self):
        """ Regresa iterable para alimentar las tablas de productos.
            Cantidad | Código | Especificaciones | Precio | Descuento | Importe """
        yield from (self.cantidad,
                    self.codigo,
                    self.notas,
                    self.precio_unit,
                    self.descuento_unit,
                    self.importe)


@dataclass
class Venta:
    """ Clase para mantener registro de una venta. """
    productos: list[BaseItem] = field(default_factory=list)
    fechaCreacion: QDateTime = QDateTime.currentDateTime()
    fechaEntrega: QDateTime = QDateTime(fechaCreacion)
    requiere_factura: bool = False
    comentarios: str = ''
    id_cliente: int = 1
    
    @property
    def total(self):
        return Moneda.sum(prod.importe for prod in self.productos)
    
    @property
    def total_descuentos(self):
        return Moneda.sum(prod.total_descuentos for prod in self.productos)
    
    @property
    def esVentaDirecta(self):
        """ Compara fechas de creación y entrega para determinar si la venta será un pedido. """
        return self.fechaCreacion == self.fechaEntrega
    
    @property
    def ventaVacia(self):
        return len(self.productos) == 0
    
    def agregarProducto(self, item: ItemVenta):
        self.productos.append(item)
    
    def quitarProducto(self, idx: int):
        self.productos.pop(idx)
    
    def reajustarPrecios(self, conn):
        """ Algoritmo para reajustar precios de productos simples al haber cambios de cantidad.
            Por cada grupo de productos idénticos:
                1. Calcular cantidad de productos duplex y cantidad de no duplex.
                2. Obtener precio NO DUPLEX con el total de ambas cantidades.
                3. Obtener precio DUPLEX con la cantidad duplex correspondiente.
                4. A todos los productos del grupo, asignar el mínimo de los dos precios obtenidos. """
        manejador = ManejadorProductos(conn)
        
        for productos in self._obtenerGruposProductos():
            productosNormal = sum(p.cantidad for p in productos if not p.duplex)
            productosDuplex = sum(p.cantidad for p in productos if p.duplex)
            
            precioNormal = manejador.obtenerPrecioSimple(
                productos[0].id, productosNormal + productosDuplex, False)
            
            if precioNormal is None:
                continue
            
            precioDuplex = manejador.obtenerPrecioSimple(
                productos[0].id, productosDuplex, True)
            nuevoPrecio = min(precioNormal, precioDuplex or precioNormal)
            
            for p in productos:
                p.precio_unit = nuevoPrecio
    
    def _obtenerGruposProductos(self) -> Iterator[list[ItemVenta]]:
        """ Obtiene un generador con listas de productos, separadas por identificador. """
        out = dict()
        for prod in self.productos:
            if not isinstance(prod, ItemVenta):
                continue
            try:
                out[prod.id].append(prod)
            except KeyError:
                out[prod.id] = [prod]
        yield from out.values()
    
    def __len__(self):
        return len(self.productos)
    
    def __iter__(self):
        yield from self.productos
    
    def __getitem__(self, i: int):
        return self.productos[i]


#####################
# VENTANA PRINCIPAL #
#####################
ventaDatos: Venta = ...

class App_CrearVenta(QtWidgets.QWidget):
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
        global ventaDatos
        ventaDatos = Venta()
        
        # guardar conexión y usuarios como atributos
        self.conn = parent.conn
        self.user = parent.user
        
        # cuadro de texto para los descuentos del cliente
        self.dialogoDescuentos = SpeechBubble(self)
        self.dialogoDescuentos.setVisible(False)
        
        # datos por defecto
        self.ui.txtVendedor.setText(self.user.nombre)
        self.ui.lbFecha.setText(formatDate(ventaDatos.fechaEntrega))
        self.ui.btDeshacer.setVisible(False)
        
        # crear eventos para los botones
        self.ui.btCalendario.clicked.connect(self.cambiarFechaEntrega)
        self.ui.btAgregar.clicked.connect(self.agregarProducto)
        self.ui.btEliminar.clicked.connect(self.quitarProducto)
        self.ui.btRegresar.clicked.connect(self.goHome)
        
        ocultar_boton = lambda: (self.ui.btDescuentosCliente.setVisible(False),
                                 self.dialogoDescuentos.setVisible(False))
        
        self.ui.txtCliente.textChanged.connect(ocultar_boton)
        self.ui.txtCorreo.textChanged.connect(ocultar_boton)
        self.ui.txtTelefono.textChanged.connect(ocultar_boton)
        
        self.ui.tabla_productos.itemChanged.connect(self.item_changed)
        self.ui.btRegistrar.clicked.connect(self.insertarCliente)
        self.ui.btSeleccionar.clicked.connect(lambda: App_SeleccionarCliente(self))
        self.ui.btDescuento.clicked.connect(
            lambda: self.agregarDescuento() if not ventaDatos.ventaVacia else None)
        self.ui.btDescuentosCliente.clicked.connect(self.dialogoDescuentos.alternarDescuentos)
        self.ui.btDeshacer.clicked.connect(self.deshacerFechaEntrega)
        self.ui.btCotizacion.clicked.connect(
            lambda: App_EnviarCotizacion(self) if not ventaDatos.ventaVacia else None)
        self.ui.btListo.clicked.connect(self.confirmarVenta)
        
        self.ui.btDescuentosCliente.hide()
        
        self.ui.tabla_productos.quitarBordeCabecera()
        self.ui.tabla_productos.cambiarColorCabecera(Qt.black)
        self.ui.tabla_productos.configurarCabecera(
            lambda col: col != 2,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    
    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def item_changed(self, item: QtWidgets.QTableWidgetItem):
        if item.column() == 2:
            ventaDatos[item.row()].notas = item.text()
    
    def establecerCliente(self, nombre: str, telefono: str, correo: str):
        """ Atajo para modificar datos del cliente seleccionado. """
        self.ui.txtCliente.setText(nombre)
        self.ui.txtTelefono.setText(telefono)
        self.ui.txtCorreo.setText(correo)
    
    def actualizarLabelFecha(self):
        """ Actualizar widget de fecha de entrega:
            label y botón de deshacer. """
        self.ui.lbFecha.setText(formatDate(ventaDatos.fechaEntrega))
        self.ui.btDeshacer.setVisible(not ventaDatos.esVentaDirecta)
    
    def deshacerFechaEntrega(self):
        """ Deshacer cambio de fecha de entrega. """
        ventaDatos.fechaEntrega = QDateTime(ventaDatos.fechaCreacion)
        self.actualizarLabelFecha()
    
    def colorearActualizar(self):
        """ Llenar tabla con los productos seleccionados,
            luego calcular precios y actualizar los QLabel. """
        tabla = self.ui.tabla_productos
        tabla.modelo = tabla.Modelos.CREAR_VENTA
        tabla.llenar(ventaDatos)
        
        # <calcular precios y mostrar>
        preciosConIVA = ventaDatos.total
        preciosSinIVA = preciosConIVA / 1.16
        
        self.ui.lbTotal.setText(str(preciosConIVA))
        self.ui.lbSubtotal.setText(str(preciosSinIVA))
        self.ui.lbImpuestos.setText(str(preciosConIVA - preciosSinIVA))
        self.ui.lbDescuento.setText(str(ventaDatos.total_descuentos))
        # </calcular precios y mostrar>
        
        self.ui.txtNumProds.setText(f'{len(ventaDatos)} producto'
                                     + ('s' if len(ventaDatos) != 1 else ''))
    
    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def insertarCliente(self):
        """ Abre ventana para registrar un cliente. """
        from .AdministrarClientes import App_RegistrarCliente
        
        modulo = App_RegistrarCliente(
            self,
            nombre=self.ui.txtCliente.text(),
            celular=self.ui.txtTelefono.text(),
            correo=self.ui.txtCorreo.text()
        )
        modulo.success.connect(self.establecerCliente)
    
    def cambiarFechaEntrega(self):
        modulo = App_FechaEntrega(self)
        modulo.success.connect(self.actualizarLabelFecha)
    
    def agregarProducto(self):
        modulo = App_AgregarProducto(self)
        modulo.success.connect(self.colorearActualizar)
    
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
    def _quitarProducto(self, selected, conn):
        """ En método separado para solicitar contraseña. """
        for row in sorted(selected, reverse=True):
            ventaDatos.quitarProducto(row)
        
        ventaDatos.reajustarPrecios(self.conn)
        self.colorearActualizar()
    
    @requiere_admin
    def agregarDescuento(self, conn):
        """ Abre ventana para agregar un descuento a la orden si el cliente es especial. """
        modulo = App_AgregarDescuento(self)
        modulo.success.connect(
            lambda: (self.ui.btSeleccionar.setEnabled(False),
                     self.ui.txtCliente.setReadOnly(True),
                     self.ui.txtCorreo.setReadOnly(True),
                     self.ui.txtTelefono.setReadOnly(True),
                     self.colorearActualizar())
        )
    
    def verificarCliente(self):
        # se confirma si existe el cliente en la base de datos
        manejador = ManejadorClientes(self.conn)
        
        nombre = self.ui.txtCliente.text().strip()
        telefono = self.ui.txtTelefono.text().strip()
        cliente = manejador.obtenerCliente(nombre, telefono)
        
        warning = lambda txt: QtWidgets.QMessageBox.warning(self, '¡Atención!', txt)
        
        if not cliente:
            warning('No se encontró el cliente en la base de datos.\n'
                    'Por favor, regístrelo como un nuevo cliente o seleccione "Público general".')
            return
        
        # indices para acceder a la tupla `cliente`
        id, nombre, telefono, correo, direccion, rfc = range(6)
        
        if not ventaDatos.esVentaDirecta and cliente[id] == 1:
            warning('No se puede generar un pedido a nombre de "Público general".\n'
                    'Por favor, seleccione un cliente y/o regístrelo.')
            return
        
        if self.ui.tickFacturaSi.isChecked():
            if cliente[id] == 1:
                warning('No se puede generar una factura a nombre de "Público general".\n'
                        'Por favor, verifique que los datos del cliente sean correctos.')
                return
            
            if not all((cliente[correo], cliente[direccion], cliente[rfc])):
                from .AdministrarClientes import App_EditarCliente
                
                modulo = App_EditarCliente(self, cliente[id])
                modulo.success.connect(self.establecerCliente)
                
                warning('El cliente no tiene completos sus datos para la factura.\n'
                        'Por favor, llene los datos como corresponde.')
                return
        return cliente[id]
    
    def confirmarVenta(self):
        """ Abre ventana para confirmar y terminar la venta. """
        if ventaDatos.ventaVacia or (id_cliente := self.verificarCliente()) is None:
            return
        
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Concluir venta',
                          'Verifique todos los datos ingresados.\n'
                          '¿Desea concluir la venta?')
        if ret != qm.Yes:
            return
        
        ventaDatos.id_cliente = id_cliente
        ventaDatos.requiere_factura = self.ui.tickFacturaSi.isChecked()
        ventaDatos.comentarios = self.ui.txtComentarios.toPlainText()
        
        if ventaDatos.total > 0.:
            bg = DimBackground(self)
        modulo = App_ConfirmarVenta(self)
    
    @requiere_admin
    def goHome(self, conn):
        """ Cierra la ventana y regresa al inicio. """
        parent: VentanaPrincipal = self.parentWidget()
        parent.goHome()


#################################
# VENTANAS PARA EDITAR LA VENTA #
#################################
class Base_VisualizarProductos(QtWidgets.QWidget):
    dataChanged = Signal()  # señal para actualizar tabla en hilo principal
    
    def __init__(self, first: VentanaPrincipal, *, extern: bool = False):
        from ui.Ui_VisualizadorProductos import Ui_VisualizadorProductos
        
        super().__init__(None if extern else first)
        
        self.ui = Ui_VisualizadorProductos()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        
        self.warnings = True
        
        LabelAdvertencia(self.ui.tabla_seleccionar, '¡No se encontró ningún producto!')
        LabelAdvertencia(self.ui.tabla_granformato, '¡No se encontró ningún producto!')
        
        # guardar conexión, usuario y un manejador de DB como atributos
        self.conn = first.conn
        self.manejador = ManejadorProductos(self.conn)
        
        # eventos para widgets
        self.ui.searchBar.textChanged.connect(self.update_display)
        self.ui.groupFiltro.buttonClicked.connect(self.update_display)
        self.ui.tabWidget.currentChanged.connect(
            lambda: self.tabla_actual.resizeRowsToContents())
        
        self.ui.btIntercambiarProducto.clicked.connect(self.intercambiarProducto)
        self.ui.btIntercambiarMaterial.clicked.connect(self.intercambiarMaterial)
        
        self.ui.txtAncho.textChanged.connect(self.medidasHandle)
        self.ui.txtAlto.textChanged.connect(self.medidasHandle)
        self.ui.grupoBotonesAlto.buttonClicked.connect(self.medidasHandle)
        self.ui.grupoBotonesAncho.buttonClicked.connect(self.medidasHandle)
        
        # validadores para datos numéricos
        self.ui.txtCantidad.setValidator(FabricaValidadores.NumeroDecimal)
        self.ui.txtAlto.setValidator(FabricaValidadores.NumeroDecimal)
        self.ui.txtAncho.setValidator(FabricaValidadores.NumeroDecimal)
        self.ui.txtAltoMaterial.setValidator(FabricaValidadores.NumeroDecimal)
        self.ui.txtAnchoMaterial.setValidator(FabricaValidadores.NumeroDecimal)
        
        self.ui.tabla_seleccionar.configurarCabecera(lambda col: col != 1)
        self.ui.tabla_granformato.configurarCabecera(lambda col: col != 1)
        self.ui.tabla_seleccionar.setSortingEnabled(True)
        self.ui.tabla_granformato.setSortingEnabled(True)
        
        # evento para leer cambios en tabla PRODUCTOS
        self.event_conduit = self.conn.event_conduit(['cambio_productos'])
        self.event_reader = Runner(self.startEvents)
        self.event_reader.start()
        self.dataChanged.connect(self.rescan_display)
    
    def showEvent(self, event):
        self.rescan_display()
    
    def closeEvent(self, event):
        if event.spontaneous():
            event.ignore()
        else:
            # no recomendado generalmente para terminar hilos, sin embargo,
            # esta vez se puede hacer así al no ser una función crítica.
            self.event_reader.stop()
            self.event_conduit.close()
            event.accept()
    
    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @property
    def tabla_actual(self):
        return [self.ui.tabla_seleccionar, self.ui.tabla_granformato][self.ui.tabWidget.currentIndex()]
    
    def startEvents(self):
        # eventos de Firebird para escuchar cambios en tabla productos
        self.event_conduit.begin()
        
        while True:
            self.event_conduit.wait()
            self.dataChanged.emit()
            self.event_conduit.flush()
    
    def medidasHandle(self):
        raise NotImplementedError('BEIS CLASSSSSSS')
    
    def _intercambiarDimensiones(self, alto_textbox, ancho_textbox,
                                       bt_alto_cm, bt_ancho_cm,
                                       bt_alto_m, bt_ancho_m):
        alto = alto_textbox.text()
        ancho = ancho_textbox.text()
        bt_alto = bt_alto_cm if bt_ancho_cm.isChecked() else bt_alto_m
        bt_ancho = bt_ancho_cm if bt_alto_cm.isChecked() else bt_ancho_m
        
        if alto and ancho:
            alto_textbox.setText(ancho)
            ancho_textbox.setText(alto)
            bt_alto.setChecked(True)
            bt_ancho.setChecked(True)
            self.medidasHandle()

    def intercambiarProducto(self):
        self._intercambiarDimensiones(self.ui.txtAlto, self.ui.txtAncho,
                                      self.ui.btAltoCm, self.ui.btAnchoCm,
                                      self.ui.btAltoM, self.ui.btAnchoM)
            
    def intercambiarMaterial(self):
        self._intercambiarDimensiones(self.ui.txtAltoMaterial, self.ui.txtAnchoMaterial,
                                      self.ui.btAltoCm_2, self.ui.btAnchoCm_2,
                                      self.ui.btAltoM_2, self.ui.btAnchoM_2)
    
    def obtenerMedidasProducto(self):
        """ Calcular medidas del producto, regresa tupla (ancho, alto). """
        ancho_producto = self.ui.txtAncho.text()
        div_ancho = 100 if self.ui.btAnchoCm.isChecked() else 1
        
        alto_producto = self.ui.txtAlto.text()
        div_alto = 100 if self.ui.btAltoCm.isChecked() else 1
        
        try:
            ancho_producto = float(ancho_producto) / div_ancho
            alto_producto = float(alto_producto) / div_alto
            return (ancho_producto, alto_producto)
        except ValueError:
            return (0., 0.)
    
    def obtenerMedidasMaterial(self):
        """ Calcular medidas del material, regresa tupla (ancho, alto). """
        ancho_material = self.ui.txtAnchoMaterial.text()
        div_ancho_material = 100 if self.ui.btAnchoCm_2.isChecked() else 1
        
        alto_material = self.ui.txtAltoMaterial.text()
        div_alto_material = 100 if self.ui.btAltoCm_2.isChecked() else 1
        
        try:
            ancho_material = float(ancho_material) / div_ancho_material
            alto_material = float(alto_material) / div_alto_material
            return (ancho_material, alto_material)
        except ValueError:
            return (0., 0.)
    
    def generarSimple(self):
        if not (selected := self.ui.tabla_seleccionar.selectedItems()):
            return
        
        try:
            cantidad = int(float(self.ui.txtCantidad.text() or 1))
        except ValueError:
            return
        
        if cantidad <= 0:
            return
        
        # obtener información del producto
        codigo = selected[0].text()
        manejador = ManejadorProductos(self.conn)
        
        idProducto = manejador.obtenerIdProducto(codigo)
        nombre_ticket = manejador.obtenerNombreParaTicket(codigo)
        
        # obtener precio basado en cantidad
        duplex = self.ui.checkDuplex.isChecked()
        precio = manejador.obtenerPrecioSimple(idProducto, cantidad, duplex)
        
        if not precio and self.warnings:
            QtWidgets.QMessageBox.warning(
                self, 'Atención',
                'No existe ningún precio de este producto '
                'asociado a la cantidad proporcionada.')
            return
        
        # insertar información del producto con cantidad y especificaciones
        return ItemVenta(
            idProducto, codigo, nombre_ticket, precio, 0.0, cantidad,
            self.ui.txtNotas.text().strip(), duplex)
    
    def generarGranFormato(self):
        if not (selected := self.ui.tabla_granformato.selectedItems()):
            return
        
        ancho_producto, alto_producto = self.obtenerMedidasProducto()
        ancho_material, alto_material = self.obtenerMedidasMaterial()
        
        if not all([ancho_producto, alto_producto, ancho_material, alto_material]):
            return
        if (ancho_producto > ancho_material or alto_producto > alto_material) and self.warnings:
            QtWidgets.QMessageBox.warning(
                self, 'Atención',
                'Las medidas del producto sobrepasan las medidas del material.')
            return
        
        # si el alto del producto sobrepasa el ancho del material, quiere decir
        # que no se pudo imprimir de forma normal; por lo tanto, cobrar sobrante.
        if alto_producto > ancho_material:
            ancho_producto = ancho_material
        
        # obtener información del producto
        codigo = selected[0].text()
        manejador = ManejadorProductos(self.conn)
        
        idProducto = manejador.obtenerIdProducto(codigo)
        nombre_ticket = manejador.obtenerNombreParaTicket(codigo)
        min_m2, precio_m2 = manejador.obtenerGranFormato(idProducto)
        
        # insertar información del producto con cantidad y especificaciones
        return ItemGranFormato(
            idProducto, codigo, nombre_ticket, precio_m2, 0.0, ancho_producto * alto_producto,
            self.ui.txtNotas_2.text().strip(), min_m2)
    
    def rescan_display(self):
        """ Lee de nuevo las tablas de productos y actualiza tablas. """
        self.all_prod = self.manejador.obtenerVista('View_Productos_Simples')
        self.all_gran = self.manejador.obtenerVista('View_Gran_Formato')
        self.update_display()
    
    def update_display(self):
        """ Actualiza la tabla y el contador de clientes.
            Acepta una cadena de texto para la búsqueda de clientes. """
        filtro = self.ui.btDescripcion.isChecked()
        txt_busqueda = self.ui.searchBar.text()
        
        # <tabla de productos normales>
        if txt_busqueda:
            found = [prod for prod in self.all_prod
                     if prod[filtro]
                     if son_similar(txt_busqueda, prod[filtro])]
        else:
            found = self.all_prod
        
        tabla = self.ui.tabla_seleccionar
        tabla.llenar(found)
        # </tabla de productos normales>
        
        # <tabla de gran formato>
        if txt_busqueda:
            found = [prod for prod in self.all_gran
                     if prod[filtro]
                     if son_similar(txt_busqueda, prod[filtro])]
        else:
            found = self.all_gran
        
        tabla = self.ui.tabla_granformato
        tabla.llenar(found)
        # </tabla de gran formato>
        
        self.tabla_actual.resizeRowsToContents()


@con_fondo
class App_AgregarProducto(Base_VisualizarProductos):
    """ Backend para la función de agregar un producto a la venta. """
    success = Signal()
    
    def __init__(self, first: App_CrearVenta):
        super().__init__(first)
        
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        self.ui.lbTotalGran.hide()
        self.ui.lbTotalSimple.hide()
        
        # añade eventos para los botones
        self.ui.btRegresar.clicked.connect(self.close)
        self.ui.btAgregar.clicked.connect(self.done)
        self.ui.tabla_seleccionar.itemDoubleClicked.connect(self.done)
        self.ui.tabla_granformato.itemDoubleClicked.connect(self.done)
        
        self.show()
        
    def keyPressEvent(self, event):
        if event.key() in {Qt.Key_Return, Qt.Key_Enter}:
            self.done()
    
    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def medidasHandle(self):
        """ Especificar medidas en producto. """
        ancho = self.ui.txtAncho.text()
        anchoMedida = 'cm' if self.ui.btAnchoCm.isChecked() else 'm'
        
        alto = self.ui.txtAlto.text()
        altoMedida = 'cm' if self.ui.btAltoCm.isChecked() else 'm'
        
        if all([ancho, anchoMedida, alto, altoMedida]):
            spec = f'Medidas: {ancho} {anchoMedida} por {alto} {altoMedida}. '
            self.ui.txtNotas_2.setText(spec)
    
    def done(self):
        """ Determina la rutina a ejecutar basándose en la pestaña actual. """
        current = self.ui.tabWidget.currentIndex()
        
        if current == 0:
            item = self.generarSimple()
        elif current == 1:
            item = self.generarGranFormato()
        
        if item:
            ventaDatos.agregarProducto(item)
            ventaDatos.reajustarPrecios(self.conn)
            self.success.emit()
            self.close()


@con_fondo
class App_SeleccionarCliente(QtWidgets.QWidget):
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
        manejador = ManejadorClientes(self.conn)
        self.all = [datos for (_, *datos) in manejador.obtenerTablaPrincipal()]
        
        # añade eventos para los botones
        self.ui.btRegresar.clicked.connect(self.close)
        self.ui.btAgregar.clicked.connect(self.done)
        self.ui.searchBar.textChanged.connect(self.update_display)
        self.ui.tabla_seleccionar.itemDoubleClicked.connect(self.done)
        
        self.ui.tabla_seleccionar.configurarCabecera(lambda col: col in {1, 4})
        self.ui.tabla_seleccionar.setSortingEnabled(True)
        self.show()
    
    def showEvent(self, event):
        self.update_display()
    
    def keyPressEvent(self, event):
        if event.key() in {Qt.Key_Return, Qt.Key_Enter}:
            self.done()
    
    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def update_display(self, txt_busqueda: str = ''):
        """ Actualiza la tabla y el contador de clientes.
            Acepta una cadena de texto para la búsqueda de clientes.
            También lee de nuevo la tabla de clientes, si se desea. """
        if txt_busqueda:
            found = [cliente for cliente in self.all
                     if cliente[0]
                     if son_similar(txt_busqueda, cliente[0])]
        else:
            found = self.all
        
        tabla = self.ui.tabla_seleccionar
        tabla.llenar(found)
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
class App_FechaEntrega(QtWidgets.QWidget):
    """ Backend para la función de cambiar fecha de entrega. """
    success = Signal()
    
    def __init__(self, first: App_CrearVenta):
        from ui.Ui_FechaEntrega import Ui_FechaEntrega
        
        super().__init__(first)
        
        self.ui = Ui_FechaEntrega()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)
        
        # datos por defecto
        fechaEntrega = ventaDatos.fechaEntrega
        self.ui.calendario.setSelectedDate(fechaEntrega.date())
        self.ui.horaEdit.setTime(fechaEntrega.time())
        
        hoy = QDate.currentDate()
        self.ui.calendario.setMinimumDate(hoy)
        self.ui.calendario.setMaximumDate(hoy.addYears(1))
        
        # añade eventos para los botones
        self.ui.btRegresar.clicked.connect(self.close)
        self.ui.btListo.clicked.connect(self.done)
        
        self.show()
    
    def keyPressEvent(self, event):
        if event.key() in {Qt.Key_Return, Qt.Key_Enter}:
            self.done()
    
    def done(self):
        """ Acepta los cambios y modifica la fecha seleccionada 
            en la ventana principal (CrearVenta). """
        dateTime = QDateTime(
            self.ui.calendario.selectedDate(),
            self.ui.horaEdit.time())
        
        ventaDatos.fechaEntrega = dateTime
        self.success.emit()
        self.close()


@con_fondo
class App_AgregarDescuento(QtWidgets.QWidget):
    """ Backend para agregar descuento a la orden. """
    success = Signal()
    
    def __init__(self, first: App_CrearVenta):
        from ui.Ui_AgregarDescuento import Ui_AgregarDescuento
        
        super().__init__(first)
        
        self.ui = Ui_AgregarDescuento()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)
        
        # añade eventos para los botones
        self.ui.btRegresar.clicked.connect(self.close)
        self.ui.btListo.clicked.connect(self.done)
        
        # validadores numéricos
        self.ui.txtPrecio.setValidator(
            FabricaValidadores.NumeroDecimal)
        
        self.ui.tabla_productos.quitarBordeCabecera()
        self.ui.tabla_productos.cambiarColorCabecera(Qt.black)
        self.ui.tabla_productos.configurarCabecera(
            lambda col: col != 2,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self.show()
    
    def showEvent(self, event):
        tabla = self.ui.tabla_productos
        tabla.modelo = tabla.Modelos.CREAR_VENTA
        tabla.llenar(ventaDatos)
    
    def keyPressEvent(self, event):
        if event.key() in {Qt.Key_Return, Qt.Key_Enter}:
            self.done()
    
    # ================ #
    # FUNCIONES ÚTILES #
    # ================ #
    def done(self):
        """ Acepta los cambios e inserta descuento en la lista de productos. """
        selected = self.ui.tabla_productos.selectedItems()
        
        if not selected:
            return
        
        prod = ventaDatos[selected[0].row()]
        
        try:
            nuevo_precio = float(self.ui.txtPrecio.text())
        except ValueError:
            return
        
        prod.descuento_unit = clamp(prod.precio_unit - nuevo_precio, 0., prod.precio_unit)
        
        self.success.emit()
        self.close()


@con_fondo
class App_EnviarCotizacion(QtWidgets.QWidget):
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
        for name, item in vars(self.ui).items():
            if 'label_' in name:
                item.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        self.show()
    
    # ================ #
    # FUNCIONES ÚTILES #
    # ================ #
    def enviarWhatsApp(self):
        mensaje = [
            '*COTIZACIÓN DE VENTA*',
            'Cliente: *' + self.first.ui.txtCliente.text() + '*',
            '-------------------------------------------',
            'Fecha: *' + formatDate() + '*',
            '-------------------------------------------'
        ]
        
        for prod in ventaDatos:
            mensaje.extend([
                f'{prod.nombre_ticket} || {prod.cantidad} unidades',
                f'Importe: ${prod.importe:,.2f}',
                ''
            ])
        
        mensaje.append('*Total a pagar: $' + self.first.ui.lbTotal.text() + '*')
        mensaje = '\n'.join(mensaje)
        celular = self.first.ui.txtTelefono.text()
        
        if enviarWhatsApp(celular, mensaje):
            self.close()
    
    def imprimirTicket(self):
        vendedor = self.first.ui.txtVendedor.text()
        
        impresora = ImpresoraTickets(self)
        impresora.imprimirTicketPresupuesto(ventaDatos.productos, vendedor)
        
        self.close()


class App_ConfirmarVenta(Base_PagarVenta):
    """ Backend para la ventana de finalización de venta. """
    def __init__(self, first: App_CrearVenta):
        super().__init__(first)
        
        # seleccionar método para WidgetPago
        wdg = list(self.ui.stackPagos)[0]
        wdg.metodoSeleccionado = first.ui.btMetodoGrupo.checkedButton().text()
        
        if wdg.metodoSeleccionado != 'Efectivo':
            self._handleCounters()
        
        # si la venta es directa, ocultar los widgets para apartados
        now = QDateTime.currentDateTime()
        
        if ventaDatos.esVentaDirecta:
            ventaDatos.fechaEntrega = now
            self.setFixedHeight(759)
            
            for w in [self.ui.boxFechaEntrega,
                      self.ui.lbAnticipo1,
                      self.ui.lbAnticipo2,
                      self.ui.txtAnticipo,
                      self.ui.lbCincuenta]:
                w.hide()
                
        ventaDatos.fechaCreacion = now  # tiene que ser después del if
        
        # llenar total y monto a pagar
        self.ui.lbCincuenta.setText(f'(${ventaDatos.total / 2})')
        
        # brincar el proceso si el pago es de cero
        if not ventaDatos.total:
            self.terminarVenta()
        else:
            self.show()
    
    def showEvent(self, event):
        tabla = self.ui.tabla_productos
        tabla.modelo = tabla.Modelos.CREAR_VENTA
        tabla.llenar(ventaDatos)
    
    def closeEvent(self, event):
        event.ignore()
    
    # ================
    # FUNCIONES ÚTILES
    # ================
    def calcularTotal(self) -> Moneda:
        return ventaDatos.total
    
    def obtenerDatosGenerales(self):
        manejadorClientes = ManejadorClientes(self.conn)
        _, nombreCliente, telefono, correo, *_ = manejadorClientes.obtenerCliente(ventaDatos.id_cliente)  
        return (nombreCliente, correo, telefono, ventaDatos.fechaCreacion, ventaDatos.fechaEntrega)
    
    def pagoPredeterminado(self):
        return ventaDatos.total if ventaDatos.esVentaDirecta else ventaDatos.total / 2
    
    def obtenerIdVenta(self) -> int:
        """ Registra datos principales de venta en DB
            y regresa folio de venta insertada. """
        manejadorVentas = ManejadorVentas(self.conn)
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

    def obtenerParametrosVentas(self):
        """ Parámetros para tabla ventas (datos generales). """
        return (ventaDatos.id_cliente,
                self.user.id,
                ventaDatos.fechaCreacion.toPython(),
                ventaDatos.fechaEntrega.toPython(),
                ventaDatos.comentarios.strip(),
                ventaDatos.requiere_factura,
                'No terminada')
    
    def obtenerParametrosVentasDetallado(self):
        """ Parámetros para tabla ventas_detallado (datos de productos). """
        return [(prod.id,
                 prod.cantidad,
                 prod.precio_unit,
                 prod.descuento_unit,
                 prod.notas,
                 prod.duplex if isinstance(prod, ItemVenta) else False,
                 prod.importe)
                for prod in ventaDatos]
    
    def listo(self):
        """ Intenta finalizar la compra o pedido, actualizando el estado
            e insertando los correspondientes movimientos en la tabla Caja. """
        if not ventaDatos.total / 2 <= self.para_pagar:
            qm = QtWidgets.QMessageBox
            ret = qm.question(self, 'Atención',
                              'El anticipo está por debajo del 50% del total de compra.\n'
                              '¿Desea continuar?')
            if ret == qm.Yes:
                self.listoAdmin()
        else:
            super().listo()
    
    @requiere_admin
    def listoAdmin(self, conn):
        """ Saltar ciertas verificaciones con cuenta de administrador. """
        super().listo()
    
    def actualizarEstadoVenta(self) -> bool:
        """ Tras verificar todas las condiciones, finalizar venta y
            registrarla en la base de datos. """
        manejadorVentas = ManejadorVentas(self.conn)
        estado = 'Terminada' if ventaDatos.esVentaDirecta else f'Recibido ${self.para_pagar}'
        return manejadorVentas.actualizarEstadoVenta(self.id_ventas, estado, commit=True)
    
    def dialogoExito(self):
        qm = QtWidgets.QMessageBox
        
        if not ventaDatos.esVentaDirecta:
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
        manejadorAdmin = ManejadorVentas(conn)
        
        estado = 'Cancelada por ' + manejadorAdmin.usuarioActivo
        if manejadorAdmin.actualizarEstadoVenta(self.id_ventas, estado, commit=True):
            self.goHome()
    
    def goHome(self):
        """ Cierra la ventana y crea otra venta. """
        parent: VentanaPrincipal = self.parentWidget().parentWidget()
        parent.goHome()
        self.close()
