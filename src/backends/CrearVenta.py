from PySide6 import QtWidgets
from PySide6.QtWidgets import QMessageBox as qm
from PySide6.QtCore import QDate, QDateTime, Signal, Qt

from .AdministrarClientes import App_RegistrarCliente, App_EditarCliente
from .AdministrarVentas import Base_PagarVenta
from .AdministrarProductos import Base_VisualizarProductos
from pdf import ImpresoraOrdenes, ImpresoraTickets
from protocols import ModuloPrincipal
from sql import ManejadorClientes, ManejadorProductos, ManejadorVentas
from utils import Moneda
from utils.mydataclasses import Venta
from utils.mydecorators import fondo_oscuro, requiere_admin
from utils.myutils import *
from utils.mywidgets import DimBackground, LabelAdvertencia, SpeechBubble


#####################
# VENTANA PRINCIPAL #
#####################
ventaDatos: Venta = ...


class App_CrearVenta(ModuloPrincipal):
    """ Backend para la función de crear ventas.
        TODO:
            - mandar ticket por whatsapp o imprimir, sí o sí """

    def __init__(self, conn, user):
        from ui.Ui_CrearVenta import Ui_CrearVenta

        super().__init__()
        self.ui = Ui_CrearVenta()
        self.ui.setupUi(self)

        LabelAdvertencia(self.ui.tabla_productos, '¡Aún no hay productos!')

        # VARIABLE DE LA VENTA ACTIVA ACTUAL
        global ventaDatos
        ventaDatos = Venta()

        # guardar conexión y usuarios como atributos
        self.conn = conn
        self.user = user

        # cuadro de texto para los descuentos del cliente
        self.dialogoDescuentos = SpeechBubble(self)
        self.dialogoDescuentos.setVisible(False)

        # datos por defecto
        self.ui.txtVendedor.setText(self.user.nombre)
        self.ui.lbFecha.setText(formatDate(ventaDatos.fechaEntrega))
        self.ui.btDeshacer.setVisible(False)
        self.ui.btDescuentosCliente.hide()

        # crear eventos para los botones
        self.ui.btCalendario.clicked.connect(self.cambiarFechaEntrega)
        self.ui.btAgregar.clicked.connect(self.agregarProducto)
        self.ui.btEliminar.clicked.connect(self.quitarProducto)
        self.ui.btRegresar.clicked.connect(self._salir)

        ocultar_boton = lambda: (self.ui.btDescuentosCliente.setVisible(False),
                                 self.dialogoDescuentos.setVisible(False))

        self.ui.txtCliente.textChanged.connect(ocultar_boton)
        self.ui.txtCorreo.textChanged.connect(ocultar_boton)
        self.ui.txtTelefono.textChanged.connect(ocultar_boton)

        self.ui.tabla_productos.itemChanged.connect(self.item_changed)
        self.ui.btRegistrar.clicked.connect(self.insertarCliente)
        self.ui.btSeleccionar.clicked.connect(
            lambda: App_SeleccionarCliente(self, conn)
                    .success.connect(self.seleccionarCliente))
        self.ui.btDescuento.clicked.connect(self.agregarDescuento)
        self.ui.btDescuentosCliente.clicked.connect(self.dialogoDescuentos.alternarDescuentos)
        self.ui.btDeshacer.clicked.connect(self.deshacerFechaEntrega)
        self.ui.btCotizacion.clicked.connect(self.enviarCotizacion)
        self.ui.btListo.clicked.connect(self.confirmarVenta)

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
        self.ui.lbTotal.setText(str(total := ventaDatos.total))
        self.ui.lbSubtotal.setText(str(subtotal := total / 1.16))
        self.ui.lbImpuestos.setText(str(total - subtotal))
        self.ui.lbDescuento.setText(str(ventaDatos.total_descuentos))
        # </calcular precios y mostrar>

        self.ui.txtNumProds.setText(f'{(l := len(ventaDatos))} producto'
                                    + ('s' if l != 1 else ''))

    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def insertarCliente(self):
        """ Abre ventana para registrar un cliente. """
        modulo = App_RegistrarCliente(self, self.conn, self.user)
        modulo.agregarDatosPorDefecto(
            nombre=self.ui.txtCliente.text(),
            celular=self.ui.txtTelefono.text(),
            correo=self.ui.txtCorreo.text()
        )
        modulo.success.connect(self.establecerCliente)
    
    def seleccionarCliente(self, selected: list[QtWidgets.QTableWidgetItem]):
        # recuérdese que Clientes(Nombre, Teléfono, Correo, Dirección, RFC)
        self.establecerCliente(
            nombre := selected[0].text(),
            telefono := selected[1].text(),
            selected[2].text())

        # checar si el cliente es especial
        manejador = ManejadorClientes(self.conn)
        especial, descuentos = manejador.obtenerDescuentosCliente(nombre, telefono)
        self.ui.btDescuentosCliente.setVisible(especial)

        if descuentos is None or not (txt := descuentos.strip()):
            txt = 'El cliente aún no tiene descuentos.'
        self.dialogoDescuentos.setText(txt)

    def cambiarFechaEntrega(self):
        modulo = App_FechaEntrega(self)
        modulo.success.connect(self.actualizarLabelFecha)

    def agregarProducto(self):
        modulo = App_AgregarProducto(self, self.conn)
        modulo.success.connect(self.colorearActualizar)

    def quitarProducto(self):
        """ Pide confirmación para eliminar un producto de la tabla. """
        if not (selected := {i.row() for i in self.ui.tabla_productos.selectedIndexes()}):
            return

        ret = qm.question(self, 'Atención',
                          '¿Desea descartar de la venta los productos seleccionados?')
        if ret == qm.Yes:
            self._quitarProducto(selected)

    @requiere_admin
    def _quitarProducto(self, selected, conn):
        """ En método separado para solicitar contraseña. """
        for row in sorted(selected, reverse=True):
            ventaDatos.quitarProducto(row)

        man = ManejadorProductos(self.conn)
        ventaDatos.reajustarPrecios(man)
        self.colorearActualizar()

    def agregarDescuento(self):
        """ Abre ventana para agregar un descuento a la orden si el cliente es especial. """
        if not ventaDatos.ventaVacia:
            modulo = App_AgregarDescuento(self, self.conn, self.user)
            modulo.success.connect(
                lambda: (self.ui.btSeleccionar.setEnabled(False),
                         self.ui.txtCliente.setReadOnly(True),
                         self.ui.txtCorreo.setReadOnly(True),
                         self.ui.txtTelefono.setReadOnly(True),
                         self.colorearActualizar())
            )
    
    def enviarCotizacion(self):
        if not ventaDatos.ventaVacia:
            cliente = self.ui.txtCliente.text()
            telefono = self.ui.txtTelefono.text()
            vendedor = self.ui.txtVendedor.text()
            wdg = App_EnviarCotizacion(self, cliente, telefono, vendedor)

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
        id_, nombre, telefono, correo, direccion, rfc = range(6)

        if not ventaDatos.esVentaDirecta and cliente[id_] == 1:
            warning('No se puede generar un pedido a nombre de "Público general".\n'
                    'Por favor, seleccione un cliente y/o regístrelo.')
            return

        if self.ui.tickFacturaSi.isChecked():
            if cliente[id_] == 1:
                warning('No se puede generar una factura a nombre de "Público general".\n'
                        'Por favor, verifique que los datos del cliente sean correctos.')
                return

            if not all((cliente[correo], cliente[direccion], cliente[rfc])):
                modulo = App_EditarCliente(self, self.conn, self.user, cliente[id_])
                modulo.success.connect(self.establecerCliente)

                warning('El cliente no tiene completos sus datos para la factura.\n'
                        'Por favor, llene los datos como corresponde.')
                return
        return cliente[id_]

    def confirmarVenta(self):
        """ Abre ventana para confirmar y terminar la venta. """
        if ventaDatos.ventaVacia or (id_cliente := self.verificarCliente()) is None:
            return

        ret = qm.question(self, 'Concluir venta',
                          'Verifique todos los datos ingresados.\n'
                          '¿Desea concluir la venta?')
        if ret != qm.Yes:
            return

        ventaDatos.id_cliente = id_cliente
        ventaDatos.requiere_factura = self.ui.tickFacturaSi.isChecked()
        ventaDatos.comentarios = self.ui.txtComentarios.toPlainText()

        modulo = App_ConfirmarVenta(
            self.ui.btMetodoGrupo.checkedButton().text(), self.conn, self.user, self)
        modulo.success.connect(self.go_back.emit)

        # brincar el proceso si el pago es de cero
        if not ventaDatos.total:
            modulo.listo()
        else:
            modulo.show()

    @requiere_admin
    def _salir(self, conn):
        """ Cierra la ventana y regresa al inicio. """
        self.go_back.emit()


#################################
# VENTANAS PARA EDITAR LA VENTA #
#################################
@fondo_oscuro
class App_AgregarProducto(Base_VisualizarProductos):
    """ Backend para la función de agregar un producto a la venta. """
    success = Signal()

    def __init__(self, parent, conn):
        super().__init__(parent, conn)

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
        elif event.key() == Qt.Key_Escape:
            self.close()

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
            man = ManejadorProductos(self.conn)
            ventaDatos.agregarProducto(item)
            ventaDatos.reajustarPrecios(man)
            
            self.success.emit()
            self.close()


@fondo_oscuro
class App_SeleccionarCliente(QtWidgets.QWidget):
    """ Backend para la función de seleccionar un cliente de la base de datos. """
    success = Signal(list)

    def __init__(self, parent, conn):
        from ui.Ui_SeleccionarCliente import Ui_SeleccionarCliente

        super().__init__(parent)

        self.ui = Ui_SeleccionarCliente()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)

        LabelAdvertencia(self.ui.tabla_seleccionar, '¡No se encontró ningún cliente!')

        # llena la tabla con todos los clientes existentes
        manejador = ManejadorClientes(conn)
        self.all = [datos[1:] for datos in manejador.obtenerVista('view_all_clientes')]

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
        elif event.key() == Qt.Key_Escape:
            self.close()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def update_display(self, txt_busqueda: str = ''):
        """ Actualiza la tabla y el contador de clientes.
            Acepta una cadena de texto para la búsqueda de clientes.
            También lee de nuevo la tabla de clientes, si se desea. """
        if txt_busqueda:
            found = [cliente for cliente in self.all
                     if son_similar(txt_busqueda, cliente[0])]
        else:
            found = self.all

        tabla = self.ui.tabla_seleccionar
        tabla.llenar(found)
        tabla.resizeRowsToContents()

    def done(self):
        """ Modifica datos de cliente en la ventana principal (CrearVenta). """
        if selected := self.ui.tabla_seleccionar.selectedItems():
            self.success.emit(selected)
            self.close()


@fondo_oscuro
class App_FechaEntrega(QtWidgets.QWidget):
    """ Backend para la función de cambiar fecha de entrega. """
    success = Signal()

    def __init__(self, parent):
        from ui.Ui_FechaEntrega import Ui_FechaEntrega

        super().__init__(parent)

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
        elif event.key() == Qt.Key_Escape:
            self.close()

    def done(self):
        """ Acepta los cambios y modifica la fecha seleccionada 
            en la ventana principal (CrearVenta). """
        dateTime = QDateTime(
            self.ui.calendario.selectedDate(),
            self.ui.horaEdit.time())

        ventaDatos.fechaEntrega = dateTime
        self.success.emit()
        self.close()


@fondo_oscuro
class App_AgregarDescuento(QtWidgets.QWidget):
    """ Backend para agregar descuento a la orden. """
    success = Signal()

    def __init__(self, parent, conn, user):
        from ui.Ui_AgregarDescuento import Ui_AgregarDescuento

        super().__init__(parent)

        self.conn = conn
        self.user = user

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
        elif event.key() == Qt.Key_Escape:
            self.close()

    # ================ #
    # FUNCIONES ÚTILES #
    # ================ #
    @requiere_admin
    def done(self, conn):
        """ Acepta los cambios e inserta descuento en la lista de productos. """
        try:
            row = self.ui.tabla_productos.selectedItems()[0].row()
            nuevo_precio = float(self.ui.txtPrecio.text())
        except (IndexError, ValueError):
            return

        prod = ventaDatos[row]
        prod.descuento_unit = clamp(prod.precio_unit - nuevo_precio, 0., prod.precio_unit)

        self.success.emit()
        self.close()


@fondo_oscuro
class App_EnviarCotizacion(QtWidgets.QWidget):
    """ Backend para agregar descuento a la orden. """

    def __init__(self, parent, txtCliente: str, txtTelefono: str, txtVendedor: str):
        from ui.Ui_Cotizacion import Ui_EnviarCotizacion

        super().__init__(parent)

        self.ui = Ui_EnviarCotizacion()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)

        self.txtCliente = txtCliente
        self.txtTelefono = txtTelefono
        self.txtVendedor = txtVendedor

        # añade eventos para los botones
        self.ui.btRegresar.clicked.connect(self.close)
        self.ui.btTicket.clicked.connect(self.imprimirTicket)
        self.ui.btWhatsapp.clicked.connect(self.enviarWhatsApp)

        # deshabilita eventos del mouse para los textos en los botones
        for name, item in vars(self.ui).items():
            if 'label_' in name:
                item.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    # ================ #
    # FUNCIONES ÚTILES #
    # ================ #
    def enviarWhatsApp(self):
        mensaje = [
            '*COTIZACIÓN DE VENTA*',
            f'Cliente: *{self.txtCliente}*',
            '-------------------------------------------',
            f'Fecha: *{formatDate()}*',
            '-------------------------------------------'
        ]

        for prod in ventaDatos:
            mensaje.extend([
                f'{prod.nombre_ticket} || {prod.cantidad} unidades',
                f'Importe: ${prod.importe:,.2f}',
                ''
            ])

        mensaje.append(f'*Total a pagar: ${ventaDatos.total}*')
        mensaje = '\n'.join(mensaje)

        if enviarWhatsApp(self.txtTelefono, mensaje):
            self.close()

    def imprimirTicket(self):
        impresora = ImpresoraTickets()
        impresora.imprimirTicketPresupuesto(ventaDatos, self.txtVendedor)
        self.close()


class App_ConfirmarVenta(Base_PagarVenta):
    """ Backend para la ventana de finalización de venta. """
    success = Signal()

    def __init__(self, metodo_pago: str, conn, user, parent=None) -> None:
        super().__init__(parent, conn, user)
        
        self.ui.stackPagos.permitir_nulo = True

        # seleccionar método para WidgetPago
        wdg = self.stackPagos[0]
        wdg.metodoSeleccionado = metodo_pago

        if metodo_pago != 'Efectivo':
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

    def showEvent(self, event) -> None:
        if parent := self.parentWidget():
            bg = DimBackground(parent)     # parent = módulo CrearVenta

        tabla = self.ui.tabla_productos
        tabla.modelo = tabla.Modelos.CREAR_VENTA
        tabla.llenar(ventaDatos)

    def closeEvent(self, event) -> None:
        if event.spontaneous():
            event.ignore()
        else:
            super().closeEvent(event)

    # ================
    # FUNCIONES ÚTILES
    # ================
    def calcularTotal(self) -> Moneda:
        return ventaDatos.total

    def obtenerDatosGenerales(self) -> tuple:
        manejadorClientes = ManejadorClientes(self.conn)
        _, nombreCliente, telefono, correo, *_ = manejadorClientes.obtenerCliente(ventaDatos.id_cliente)
        return (nombreCliente, correo, telefono, ventaDatos.fechaCreacion, ventaDatos.fechaEntrega)

    def pagoPredeterminado(self) -> Moneda:
        return ventaDatos.total if ventaDatos.esVentaDirecta else ventaDatos.total / 2

    def obtenerIdVenta(self) -> int:
        """ Registra datos principales de venta en DB
            y regresa folio de venta insertada. """
        manejadorVentas = ManejadorVentas(self.conn)
        ventas_db_parametros = self.obtenerParametrosVentas()
        ventas_detallado_db_parametros = self.obtenerParametrosVentasDetallado()

        if (
            (id_ventas := manejadorVentas.insertarVenta(ventas_db_parametros))
            and manejadorVentas.insertarDetallesVenta(id_ventas,
                                                      ventas_detallado_db_parametros)
        ):
            return id_ventas
        return None

    def obtenerParametrosVentas(self) -> tuple:
        """ Parámetros para tabla ventas (datos generales). """
        return (ventaDatos.id_cliente,
                self.user.id,
                ventaDatos.fechaCreacion.toPython(),
                ventaDatos.fechaEntrega.toPython(),
                ventaDatos.comentarios.strip(),
                ventaDatos.requiere_factura,
                'No terminada')

    def obtenerParametrosVentasDetallado(self) -> list[tuple]:
        """ Parámetros para tabla ventas_detallado (datos de productos). """
        return [(prod.id,
                 prod.cantidad,
                 prod.precio_unit,
                 prod.descuento_unit,
                 prod.notas,
                 prod.duplex,
                 prod.importe)
                for prod in ventaDatos]

    def listo(self) -> None:
        """ Intenta finalizar la compra o pedido, actualizando el estado
            e insertando los correspondientes movimientos en la tabla Caja. """
        if not ventaDatos.total / 2 <= self.para_pagar:
            ret = qm.question(self, 'Atención',
                              'El anticipo está por debajo del 50% del total de compra.\n'
                              '¿Desea continuar?')
            if ret == qm.Yes:
                self.listoAdmin()
        else:
            super().listo()

    @requiere_admin
    def listoAdmin(self, conn) -> None:
        """ Saltar verificación con cuenta de administrador. """
        super().listo()

    def actualizarEstadoVenta(self) -> bool:
        """ Tras verificar todas las condiciones, finalizar venta y
            registrarla en la base de datos. """
        manejadorVentas = ManejadorVentas(self.conn)
        estado = 'Terminada' if ventaDatos.esVentaDirecta else f'Recibido ${self.para_pagar}'
        return manejadorVentas.actualizarEstadoVenta(self.id_ventas, estado, commit=True)

    def dialogoExito(self) -> None:
        if not ventaDatos.esVentaDirecta:
            qm.information(self, 'Éxito', 'Venta terminada. Se imprimirá ahora la orden de compra.')

            impresora = ImpresoraOrdenes(self.conn, self)
            impresora.imprimirOrdenCompra(self.id_ventas)
        else:
            ret = qm.question(self, 'Éxito',
                              'Venta terminada. ¡Recuerde ofrecer el ticket de compra! '
                              '¿Desea imprimirlo?')
            if ret == qm.Yes:
                impresora = ImpresoraTickets(self.conn)
                impresora.imprimirTicketCompra(self.id_ventas)
        self.success.emit()
        self.close()

    def abortar(self) -> None:
        """ Función para abortar la venta y actualizar estado a 'Cancelada'. """
        ret = qm.question(self, 'Atención',
                          '¿Desea cancelar la venta? Esta acción no puede deshacerse.')
        if ret == qm.Yes:
            self._abortar()

    @requiere_admin
    def _abortar(self, conn) -> None:
        manejadorAdmin = ManejadorVentas(conn)

        estado = 'Cancelada por ' + manejadorAdmin.nombreUsuarioActivo
        if manejadorAdmin.actualizarEstadoVenta(self.id_ventas, estado, commit=True):
            self.success.emit()
            self.close()
