from PySide6 import QtWidgets
from PySide6.QtCore import Signal, Qt

from core import Moneda, NumeroDecimal, Runner
from sql import ManejadorProductos, ManejadorVentas
from utils.mydataclasses import ItemVenta, ItemGranFormato
from utils.mywidgets import LabelAdvertencia
from utils.myutils import son_similar, formatdate


class Base_PagarVenta(QtWidgets.QWidget):
    def __init__(self, idx: int, conn, user, parent=None) -> None:
        from ui.Ui_ConfirmarVenta import Ui_ConfirmarVenta

        super().__init__(parent)

        self.ui = Ui_ConfirmarVenta()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)
        self.setFixedSize(833, 795)

        self.stackPagos = self.ui.stackPagos

        # guardar conexión y usuario como atributos
        self.conn = conn
        self.user = user

        if idx is None:
            self.id_ventas = self.obtenerIdVenta()
        else:
            self.id_ventas = idx

        assert self.id_ventas is not None

        # llenar labels y campos de texto
        self.total = self.calcularTotal()
        self.ui.lbTotal.setText(f'{self.total}')

        (
            nombreCliente,
            correo,
            telefono,
            fechaCreacion,
            fechaEntrega,
        ) = self.obtenerDatosGenerales()

        self.ui.txtCliente.setText(nombreCliente)
        self.ui.txtCorreo.setText(correo)
        self.ui.txtTelefono.setText(telefono)
        self.ui.txtCreacion.setText(formatdate(fechaCreacion))
        self.ui.txtEntrega.setText(formatdate(fechaEntrega))
        self.ui.lbFolio.setText(str(self.id_ventas))

        # configurar tabla de productos
        self.ui.tabla_productos.quitarBordeCabecera()
        self.ui.tabla_productos.configurarCabecera(
            lambda col: col != 2,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )

        # eventos para widgets
        self.ui.btListo.clicked.connect(self.listo)
        self.ui.btCancelar.clicked.connect(self.abortar)
        self.ui.txtAnticipo.textChanged.connect(self.cambiarAnticipo)
        self.stackPagos.cambio_pagos.connect(self._handleCounters)

        # interfaz de botones para stackPagos
        self.ui.btAgregar.clicked.connect(self.stackPagos.agregarPago)
        self.ui.btAgregar.clicked.connect(self.modificar_contador)
        self.ui.btQuitar.clicked.connect(self.stackPagos.quitarPago)
        self.ui.btQuitar.clicked.connect(self.modificar_contador)
        self.ui.btAnterior.clicked.connect(self.stackPagos.retroceder)
        self.ui.btAnterior.clicked.connect(self.modificar_contador)
        self.ui.btSiguiente.clicked.connect(self.stackPagos.avanzar)
        self.ui.btSiguiente.clicked.connect(self.modificar_contador)

        self.stackPagos.total = self.ui.txtAnticipo.cantidad = self.pagoPredeterminado()
        self.stackPagos.agregarPago()

    ####################
    # FUNCIONES ÚTILES #
    ####################
    def calcularTotal(self) -> Moneda:
        raise NotImplementedError('CLASE BASE BROU')

    def obtenerDatosGenerales(self) -> tuple:
        raise NotImplementedError('CLASE BASE BROU')

    def pagoPredeterminado(self) -> Moneda:
        raise NotImplementedError('CLASE BASE BROU')

    def obtenerIdVenta(self) -> int:
        raise NotImplementedError('CLASE BASE BROU')

    @property
    def para_pagar(self) -> Moneda:
        return self.ui.txtAnticipo.cantidad

    def cambiarAnticipo(self) -> None:
        """Cambiar el anticipo pagado por el cliente."""
        self.stackPagos.total = self.ui.txtAnticipo.cantidad
        self._handleCounters()

    def modificar_contador(self) -> None:
        self.ui.lbContador.setText(
            'Pago {}/{}'.format(
                self.stackPagos.currentIndex() + 1, self.stackPagos.count()
            )
        )

    def _handleCounters(self) -> None:
        """Seguir las mismas reglas de `StackPagos.pagosValidos`
        para actualizar y colorear contadores."""
        stack = self.stackPagos
        n_efec = [wdg.metodoSeleccionado for wdg in stack].count('Efectivo')

        if n_efec:  # hay pagos en efectivo
            m = sum(
                wdg.montoPagado
                for wdg in stack  # pagado en efectivo
                if wdg.metodoSeleccionado == 'Efectivo'
            )
            m = max(
                Moneda.cero, m - stack.restanteEnEfectivo
            )  # pagado - restante (en efectivo)
            self.ui.lbCambio.setText(f'Cambio: ${m}')
        else:
            self.ui.lbCambio.clear()  # ignorar cambio

        res = stack.total - sum(
            wdg.montoPagado for wdg in stack
        )  # total - pagado (cualquiera)

        if res < 0.0 and (not n_efec or stack.restanteEnEfectivo <= 0.0):
            # sobra dinero y sin efectivo, o efectivo no necesario
            style = 'color: red;'
        else:  # recalcular restante, considerando que hay efectivo y necesario
            res = max(Moneda.cero, res)  # por el cambio a entregar
            style = ''
        if stack.pagosValidos:  # todo bien
            style = 'color: green;'

        self.ui.lbRestante.setStyleSheet(style)
        self.ui.lbRestante.setText(f'Restante: ${res}')

        self.ui.btListo.setEnabled(
            stack.pagosValidos and 0.0 <= stack.total <= self.total
        )

    def actualizarEstadoVenta(self) -> bool:
        raise NotImplementedError('CLASE BASE BROU')

    def dialogoExito(self) -> None:
        raise NotImplementedError('CLASE BASE BROU')

    def listo(self) -> None:
        """Concluye la venta de la siguiente forma:
        1. Inserta pagos en tabla ventas_pagos.
        2. Si actualizarEstadoVenta, entonces dialogoExito."""
        manejadorVentas = ManejadorVentas(self.conn)

        # registrar pagos en tabla ventas_pagos
        for wdg in self.stackPagos:
            if wdg.metodoSeleccionado == 'Efectivo':
                monto = self.stackPagos.restanteEnEfectivo
                recibido = wdg.montoPagado if monto else None
            else:
                monto = wdg.montoPagado
                recibido = None

            if not manejadorVentas.insertarPago(
                self.id_ventas, wdg.metodoSeleccionado, monto, recibido, self.user.id
            ):
                return

        if self.actualizarEstadoVenta():
            self.dialogoExito()

    def abortar(self) -> None:
        raise NotImplementedError('CLASE BASE BROU')


class Base_VisualizarProductos(QtWidgets.QWidget):
    dataChanged = Signal()  # señal para actualizar tabla en hilo principal

    def __init__(self, conn, parent=None):
        from ui.Ui_VisualizadorProductos import Ui_VisualizadorProductos

        super().__init__(parent)

        self.ui = Ui_VisualizadorProductos()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())

        self.warnings = True

        LabelAdvertencia(self.ui.tabla_seleccionar, '¡No se encontró ningún producto!')
        LabelAdvertencia(self.ui.tabla_granformato, '¡No se encontró ningún producto!')

        # guardar conexión, usuario y un manejador de DB como atributos
        self.conn = conn
        self.manejador = ManejadorProductos(conn)

        # eventos para widgets
        self.ui.searchBar.textChanged.connect(self.update_display)
        self.ui.groupFiltro.buttonClicked.connect(self.update_display)
        self.ui.tabWidget.currentChanged.connect(
            lambda: self.tabla_actual.resizeRowsToContents()
        )
        self.dataChanged.connect(self.rescan_display)

        self.ui.btIntercambiarProducto.clicked.connect(self.intercambiarProducto)
        self.ui.btIntercambiarMaterial.clicked.connect(self.intercambiarMaterial)

        self.ui.txtAncho.textChanged.connect(self.medidasHandle)
        self.ui.txtAlto.textChanged.connect(self.medidasHandle)
        self.ui.grupoBotonesAlto.buttonClicked.connect(self.medidasHandle)
        self.ui.grupoBotonesAncho.buttonClicked.connect(self.medidasHandle)

        # validadores para datos numéricos
        self.ui.txtCantidad.setValidator(NumeroDecimal)
        self.ui.txtAlto.setValidator(NumeroDecimal)
        self.ui.txtAncho.setValidator(NumeroDecimal)
        self.ui.txtAltoMaterial.setValidator(NumeroDecimal)
        self.ui.txtAnchoMaterial.setValidator(NumeroDecimal)

        self.ui.tabla_seleccionar.configurarCabecera(lambda col: col != 1)
        self.ui.tabla_granformato.configurarCabecera(lambda col: col != 1)
        self.ui.tabla_seleccionar.setSortingEnabled(True)
        self.ui.tabla_granformato.setSortingEnabled(True)

        # evento para leer cambios en tabla PRODUCTOS
        self.event_conduit = self.conn.event_conduit(['cambio_productos'])
        self.event_reader = Runner(self.startEvents)
        self.event_reader.start()

    def showEvent(self, event):
        self.rescan_display()

    def closeEvent(self, event):
        # no recomendado generalmente para terminar hilos, sin embargo,
        # esta vez se puede hacer así al no ser una función crítica.
        self.event_reader.terminate()
        self.event_reader.wait(0)
        self.event_reader.moveToThread(None)
        self.event_conduit.close()
        event.accept()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @property
    def tabla_actual(self):
        return [self.ui.tabla_seleccionar, self.ui.tabla_granformato][
            self.ui.tabWidget.currentIndex()
        ]

    def startEvents(self):  # async
        # eventos de Firebird para escuchar cambios en tabla productos
        self.event_conduit.begin()
        while True:
            self.event_conduit.wait()
            self.dataChanged.emit()
            self.event_conduit.flush()

    def medidasHandle(self):
        raise NotImplementedError('BEIS CLASSSSSSS')

    def _intercambiarDimensiones(
        self,
        alto_textbox,
        ancho_textbox,
        bt_alto_cm,
        bt_ancho_cm,
        bt_alto_m,
        bt_ancho_m,
    ):
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
        self._intercambiarDimensiones(
            self.ui.txtAlto,
            self.ui.txtAncho,
            self.ui.btAltoCm,
            self.ui.btAnchoCm,
            self.ui.btAltoM,
            self.ui.btAnchoM,
        )

    def intercambiarMaterial(self):
        self._intercambiarDimensiones(
            self.ui.txtAltoMaterial,
            self.ui.txtAnchoMaterial,
            self.ui.btAltoCm_2,
            self.ui.btAnchoCm_2,
            self.ui.btAltoM_2,
            self.ui.btAnchoM_2,
        )

    def obtenerMedidasProducto(self):
        """Calcular medidas del producto, regresa tupla (ancho, alto)."""
        ancho_producto = self.ui.txtAncho.text()
        div_ancho = 100 if self.ui.btAnchoCm.isChecked() else 1

        alto_producto = self.ui.txtAlto.text()
        div_alto = 100 if self.ui.btAltoCm.isChecked() else 1

        try:
            ancho_producto = float(ancho_producto) / div_ancho
            alto_producto = float(alto_producto) / div_alto
            return (ancho_producto, alto_producto)
        except ValueError:
            return (0.0, 0.0)

    def obtenerMedidasMaterial(self):
        """Calcular medidas del material, regresa tupla (ancho, alto)."""
        ancho_material = self.ui.txtAnchoMaterial.text()
        div_ancho_material = 100 if self.ui.btAnchoCm_2.isChecked() else 1

        alto_material = self.ui.txtAltoMaterial.text()
        div_alto_material = 100 if self.ui.btAltoCm_2.isChecked() else 1

        try:
            ancho_material = float(ancho_material) / div_ancho_material
            alto_material = float(alto_material) / div_alto_material
            return (ancho_material, alto_material)
        except ValueError:
            return (0.0, 0.0)

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
                self,
                'Atención',
                'No existe ningún precio de este producto '
                'asociado a la cantidad proporcionada.',
            )
            return

        # insertar información del producto con cantidad y especificaciones
        return ItemVenta(
            idProducto,
            codigo,
            nombre_ticket,
            precio,
            0.0,
            cantidad,
            self.ui.txtNotas.text().strip(),
            duplex,
        )

    def generarGranFormato(self):
        if not (selected := self.ui.tabla_granformato.selectedItems()):
            return

        ancho_producto, alto_producto = self.obtenerMedidasProducto()
        ancho_material, alto_material = self.obtenerMedidasMaterial()

        if not all([ancho_producto, alto_producto, ancho_material, alto_material]):
            return
        if (
            ancho_producto > ancho_material or alto_producto > alto_material
        ) and self.warnings:
            QtWidgets.QMessageBox.warning(
                self,
                'Atención',
                'Las medidas del producto sobrepasan las medidas del material.',
            )
            return

        # obtener información del producto
        codigo = selected[0].text()
        manejador = ManejadorProductos(self.conn)

        idProducto = manejador.obtenerIdProducto(codigo)
        nombre_ticket = manejador.obtenerNombreParaTicket(codigo)
        min_m2, precio_m2 = manejador.obtenerGranFormato(idProducto)

        # si el alto del producto sobrepasa el ancho del material, quiere decir
        # que no se pudo imprimir de forma normal; por lo tanto, cobrar sobrante.
        desc_unit = 0.0

        if alto_producto > ancho_material:
            # sobrante_ancho = ancho_material - ancho_producto
            # descuento_sobre_total = manejador.obtenerDescuentoSobrante(idProducto, sobrante_ancho)
            # desc_unit = precio_m2 * descuento_sobre_total
            ancho_producto = ancho_material

        # insertar información del producto con cantidad y especificaciones
        return ItemGranFormato(
            idProducto,
            codigo,
            nombre_ticket,
            precio_m2,
            desc_unit,
            ancho_producto * alto_producto,
            self.ui.txtNotas_2.text().strip(),
            min_m2,
        )

    def rescan_display(self):
        """Lee de nuevo las tablas de productos y actualiza tablas."""
        self.all_prod = self.manejador.obtener_vista('view_productos_simples')
        self.all_gran = self.manejador.obtener_vista('view_gran_formato')
        self.update_display()

    def update_display(self):
        """Actualiza la tabla y el contador de clientes.
        Acepta una cadena de texto para la búsqueda de clientes."""
        filtro = self.ui.btDescripcion.isChecked()
        txt_busqueda = self.ui.searchBar.text()

        # <tabla de productos normales>
        if txt_busqueda:
            found = [
                prod
                for prod in self.all_prod
                if prod[filtro]
                if son_similar(txt_busqueda, prod[filtro])
            ]
        else:
            found = self.all_prod

        tabla = self.ui.tabla_seleccionar
        tabla.llenar(found)
        # </tabla de productos normales>

        # <tabla de gran formato>
        if txt_busqueda:
            found = [
                prod
                for prod in self.all_gran
                if prod[filtro]
                if son_similar(txt_busqueda, prod[filtro])
            ]
        else:
            found = self.all_gran

        tabla = self.ui.tabla_granformato
        tabla.llenar(found)
        # </tabla de gran formato>

        self.tabla_actual.resizeRowsToContents()
