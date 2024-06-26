from math import ceil

from PySide6 import QtWidgets
from PySide6.QtWidgets import QMessageBox as qm
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, Signal, QMutex

from core import Moneda
from mixins import ModuloPrincipal, HasConnUser
from pdf import ImpresoraOrdenes, ImpresoraTickets
from sql import ManejadorVentas
from utils.mydecorators import fondo_oscuro, requiere_admin, run_in_thread
from utils.myinterfaces import InterfazFechas, InterfazFiltro, InterfazPaginas
from utils.myutils import *
from utils.mywidgets import LabelAdvertencia


#####################
# VENTANA PRINCIPAL #
#####################
class App_AdministrarVentas(ModuloPrincipal):
    """ Backend para la ventana de administración de ventas.
        TODO:
        -   ocultamiento de folios """
    rescanned = Signal()

    def __init__(self, conn, user):
        from ui.Ui_AdministrarVentas import Ui_AdministrarVentas

        super().__init__()
        self.ui = Ui_AdministrarVentas()
        self.ui.setupUi(self)

        self.mutex = QMutex()

        LabelAdvertencia(self.ui.tabla_ventasDirectas, '¡No se encontró ninguna venta!')
        LabelAdvertencia(self.ui.tabla_pedidos, '¡No se encontró ningún pedido!')

        # otras variables importantes
        self.chunk_size = 50
        self.all_directas = []
        self.all_pedidos = []

        # guardar conexión y usuario como atributos
        self.conn = conn
        self.user = user

        # fechas por defecto
        manejador = ManejadorVentas(conn)
        fechaMin = manejador.obtenerFechaPrimeraVenta()

        InterfazFechas(
            self.ui.btHoy, self.ui.btEstaSemana, self.ui.btEsteMes,
            self.ui.dateDesde, self.ui.dateHasta, fechaMin).dateChanged.connect(self.rescan_update)

        # añadir menú de opciones al botón para filtrar
        self.filtro = InterfazFiltro(self.ui.btFiltrar, self.ui.searchBar, 
            [('Folio', 0),
             ('Vendedor', 1),
             ('Cliente', 2)])
        self.filtro.cambiado.connect(self.update_display)

        # crear eventos para los botones
        self.ui.btRegresar.clicked.connect(self.go_back.emit)
        self.ui.btTerminar.clicked.connect(self.terminarVenta)
        self.ui.btCancelar.clicked.connect(self.cancelarVenta)
        self.ui.btOrden.clicked.connect(self.imprimirOrden)
        self.ui.btRecibo.clicked.connect(self.imprimirTicket)
        self.ui.searchBar.textChanged.connect(self.update_display)
        
        self.rescanned.connect(self.update_display)

        detallesVenta = lambda idxs: App_DetallesVenta(idxs.siblingAtColumn(0).data(), conn, self)
        self.ui.tabla_ventasDirectas.doubleClicked.connect(detallesVenta)
        self.ui.tabla_pedidos.doubleClicked.connect(detallesVenta)
        self.ui.tabWidget.currentChanged.connect(self.cambiar_pestana)

        (InterfazPaginas(
            self.ui.btAdelante, self.ui.btUltimo,
            self.ui.btAtras, self.ui.btPrimero, self.ui.tabla_ventasDirectas)
         .paginaCambiada.connect(self.update_display))

        (InterfazPaginas(
            self.ui.btAdelante, self.ui.btUltimo,
            self.ui.btAtras, self.ui.btPrimero, self.ui.tabla_pedidos)
         .paginaCambiada.connect(self.update_display))

        # configurar y llenar tablas
        self.ui.tabla_ventasDirectas.configurarCabecera(lambda col: col in {0, 3, 4, 5})
        self.ui.tabla_pedidos.configurarCabecera(lambda col: col in {0, 3, 4, 5, 6})

    def showEvent(self, event):
        self.rescan_update()

    def resizeEvent(self, event):
        if self.isVisible():
            self.tabla_actual.resizeRowsToContents()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @property
    def tabla_actual(self):
        return [self.ui.tabla_ventasDirectas, self.ui.tabla_pedidos][self.ui.tabWidget.currentIndex()]

    def cambiar_pestana(self, nuevo=None):
        """ Cambia el label con el contador de ventas, según la pestaña,
            y reajusta la tabla correspondiente a ella. También modifica
            los valores del navegador de páginas de la tabla. """
        nuevo = nuevo or self.ui.tabWidget.currentIndex()

        if nuevo == 0:
            label = 'ventas directas'
            num_compras = len(self.all_directas)
        else:
            label = 'pedidos'
            num_compras = len(self.all_pedidos)

        num_pagina = self.tabla_actual.property('paginaActual')

        self.ui.lbContador.setText(
            '{} {} en la base de datos.'.format(num_compras, label))
        self.ui.lbPagina.setText(
            '{} de {}'.format(num_pagina + 1, ceil(num_compras / self.chunk_size) or 1))

        self.tabla_actual.resizeRowsToContents()

    @run_in_thread
    def rescan_update(self, *args):  # ??? TODO: ignorar parámetros
        """ Actualiza la tabla y el contador de clientes.
            Lee de nuevo la tabla de clientes, si se desea. """
        if not self.mutex.try_lock():
            return

        self.ui.lbContador.setText('Recuperando información...')

        fechaDesde = self.ui.dateDesde.date()
        fechaHasta = self.ui.dateHasta.date()
        restrict = self.user.id if self.user.rol != 'ADMINISTRADOR' else None

        manejador = ManejadorVentas(self.conn)
        self.all_directas = manejador.tablaVentas(fechaDesde, fechaHasta, restrict)
        self.all_pedidos = manejador.tablaPedidos(fechaDesde, fechaHasta)

        self.rescanned.emit()

    def update_display(self):
        self.llenar_tabla_ventas()
        self.llenar_tabla_pedidos()
        self.cambiar_pestana()
        self.mutex.unlock()

    def llenar_tabla_ventas(self):
        """ Actualizar tabla de ventas directas. """
        compras = self.all_directas

        if txt_busqueda := self.ui.searchBar.text().strip():
            compras = [c for c in compras
                       if son_similar(txt_busqueda, c[self.filtro.idx])]

        chunks = chunkify(compras, self.chunk_size) or [[]]

        tabla = self.ui.tabla_ventasDirectas
        currentPage = clamp(tabla.property('paginaActual'), 0, ceil(len(compras) / self.chunk_size) - 1)
        tabla.setProperty('paginaActual', currentPage)  # truncar valor de la página si se sale del rango

        data = chunks[currentPage]

        tabla.modelo = tabla.Modelos.TABLA_VENTAS_DIRECTAS
        tabla.llenar(data)

    def llenar_tabla_pedidos(self):
        """ Actualizar tabla de ventas sobre pedido. """
        compras = self.all_pedidos

        if txt_busqueda := self.ui.searchBar.text().strip():
            compras = [c for c in compras
                       if son_similar(txt_busqueda, c[self.filtro.idx])]

        chunks = chunkify(compras, self.chunk_size) or [[]]

        tabla = self.ui.tabla_pedidos
        currentPage = clamp(tabla.property('paginaActual'), 0, ceil(len(compras) / self.chunk_size) - 1)
        tabla.setProperty('paginaActual', currentPage)  # truncar valor de la página si se sale del rango

        data = chunks[currentPage]

        tabla.modelo = tabla.Modelos.TABLA_PEDIDOS
        tabla.llenar(data)

        for r in range(tabla.rowCount()):
            if bt := tabla.cellWidget(r, 8):
                bt.clicked.connect(self.enviarRecordatorio)

    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def enviarRecordatorio(self):
        ret = qm.question(self, 'Atención',
                          '¿Desea enviarle un recordatorio al cliente sobre '
                          'este pedido?')
        if ret != qm.Yes:
            return

        # obtener número y nombre del cliente
        manejador = ManejadorVentas(self.conn)
        id_venta = self.tabla_actual.selectedItems()[0].text()

        saldo = manejador.obtenerSaldoRestante(id_venta)
        nombre, celular = manejador.obtenerClienteAsociado(id_venta)

        # mensaje a enviar
        mensaje = (
            '*Apreciable {}*:\n'
            'Le informamos que ya puede pasar a Printcopy a recoger su pedido '
            'con folio {}, que presenta un saldo de {} pesos. ¡Recuerde traer su '
            'orden de compra para concretar el pedido!\n\n'
            '¡Esperamos verle pronto! 😊'
        ).format(nombre, id_venta, saldo)

        enviarWhatsApp(celular, mensaje)

    def terminarVenta(self):
        """ Pide confirmación para marcar como cancelada una venta. """
        if not (selected := self.tabla_actual.selectedItems()):
            return

        idVenta = selected[0].text()
        manejador = ManejadorVentas(self.conn)

        if manejador.obtenerAnticipo(idVenta) is None:
            return

        if manejador.obtenerSaldoRestante(idVenta):
            widget = App_TerminarVenta(idVenta, self.conn, self.user, self)
            widget.success.connect(self.rescan_update)
            return

        ret = qm.question(self, 'Atención',
                          'Este pedido no tiene saldo restante. '
                          '¿Desea marcar la venta como terminada?')
        if ret != qm.Yes:
            return

        # terminar venta directamente, al no tener saldo restante
        if manejador.actualizarEstadoVenta(idVenta, 'Entregado por ' + self.user.nombre,
                                           commit=True):
            qm.information(self, 'Éxito', 'Se marcó como terminada la venta seleccionada.')
            self.rescan_update()

    def cancelarVenta(self):
        """ Pide confirmación para marcar como cancelada una venta. """
        if not (selected := self.tabla_actual.selectedItems()):
            return

        checar_estado = lambda i: selected[i].text().startswith('Cancelada')
        if checar_estado(5) or checar_estado(6):
            return

        # abrir pregunta
        ret = qm.question(self, 'Atención',
                          'La venta seleccionada se marcará como cancelada.\n'
                          'Esta operación no se puede deshacer. ¿Desea continuar?')
        if ret == qm.Yes:
            self._cancelarVenta(selected[0].text())

    @requiere_admin
    def _cancelarVenta(self, idVenta, conn):
        # preguntar por devolución y manejar tabla ventas_pagos como corresponde
        ret = qm.question(self, 'Devolución de dinero',
                          '¿Desea registrar la devolución de los pagos realizados en esta venta?')

        manejador = ManejadorVentas(conn)
        estado = 'Cancelada por ' + manejador.nombreUsuarioActivo

        if ret == qm.Yes and not manejador.anularPagos(idVenta, manejador.idUsuarioActivo):
            return
        if manejador.actualizarEstadoVenta(idVenta, estado, commit=True):
            qm.information(self, 'Éxito', 'Se marcó como cancelada la venta seleccionada.')
            self.rescan_update()

    def imprimirTicket(self):
        """ Imprime ticket de una venta dado el folio de esta. """
        if not (selected := self.tabla_actual.selectedItems()):
            return

        checar_estado = lambda i: selected[i].text().startswith('Cancelada')
        if checar_estado(5) or checar_estado(6):
            return

        idVenta = selected[0].text()
        man = ManejadorVentas(self.conn)

        if man.verificarPagos(idVenta) > 1:
            wdg = App_ImprimirTickets(idVenta, self.conn, self)
            return

        # abrir pregunta
        ret = qm.question(self, 'Atención',
                          'Se imprimirá el ticket de compra de la venta '
                          f'con folio {idVenta}. ¿Desea continuar?')
        if ret == qm.Yes:
            impresora = ImpresoraTickets(self.conn)
            impresora.imprimirTicketCompra(idVenta)

    def imprimirOrden(self):
        """ Imprime orden de compra de un pedido dado el folio de esta. """
        if (selected := self.tabla_actual.selectedItems()) \
                and selected[6].text().startswith('Recibido'):
            impresora = ImpresoraOrdenes(self.conn, self)
            impresora.imprimirOrdenCompra(selected[0].text())


#################################
# VENTANAS USADAS POR EL MÓDULO #
#################################
@fondo_oscuro
class App_DetallesVenta(QtWidgets.QWidget):
    """ Backend para la ventana que muestra los detalles de una venta. """

    def __init__(self, idx: int, conn, parent=None):
        from ui.Ui_DetallesVenta import Ui_DetallesVenta

        super().__init__(parent)

        self.ui = Ui_DetallesVenta()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)

        # total de la venta, anticipo y saldo
        manejador = ManejadorVentas(conn)

        total = manejador.obtenerImporteTotal(idx)
        anticipo = manejador.obtenerAnticipo(idx)

        # intenta calcular el saldo restante
        if anticipo:
            self.ui.lbAnticipo.setText(str(anticipo))
            self.ui.lbSaldo.setText(str(total - anticipo))
        else:
            for w in [self.ui.lbAnticipo,
                      self.ui.lbSaldo,
                      self.ui.temp1,
                      self.ui.temp2,
                      self.ui.temp3,
                      self.ui.temp4]:
                w.hide()

        nombreCliente, correo, telefono, fechaCreacion, \
            fechaEntrega, comentarios, nombreUsuario = \
            manejador.obtenerDatosGeneralesVenta(idx)

        # ocultar widgets que no sean necesarios
        if fechaCreacion == fechaEntrega:
            self.ui.boxEntrega.hide()

        self.ui.txtCliente.setText(nombreCliente)
        self.ui.txtCorreo.setText(correo)
        self.ui.txtTelefono.setText(telefono)
        self.ui.txtCreacion.setText(formatdate(fechaCreacion))
        self.ui.txtEntrega.setText(formatdate(fechaEntrega))
        self.ui.txtComentarios.setPlainText(comentarios)
        self.ui.txtVendedor.setText(nombreUsuario)
        self.ui.lbFolio.setText(str(idx))
        self.ui.lbTotal.setText(str(total))

        # evento para botón de regresar
        self.ui.btRegresar.clicked.connect(self.close)

        tabla = self.ui.tabla_productos
        tabla.quitarBordeCabecera()
        tabla.configurarCabecera(
            lambda col: col != 2,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        productos = manejador.obtenerTablaProductosVenta(idx)

        tabla.modelo = tabla.Modelos.CREAR_VENTA
        tabla.llenar(productos)

        self.show()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


class Base_PagarVenta(QtWidgets.QWidget, HasConnUser):
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

        nombreCliente, correo, telefono, fechaCreacion, fechaEntrega = self.obtenerDatosGenerales()

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
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

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
        """ Cambiar el anticipo pagado por el cliente. """
        self.stackPagos.total = self.ui.txtAnticipo.cantidad
        self._handleCounters()

    def modificar_contador(self) -> None:
        self.ui.lbContador.setText('Pago {}/{}'.format(self.stackPagos.currentIndex() + 1,
                                                       self.stackPagos.count()))

    def _handleCounters(self) -> None:
        """ Seguir las mismas reglas de `StackPagos.pagosValidos`
            para actualizar y colorear contadores. """
        stack = self.stackPagos
        n_efec = [wdg.metodoSeleccionado for wdg in stack].count('Efectivo')

        if n_efec:  # hay pagos en efectivo
            m = sum(wdg.montoPagado for wdg in stack  # pagado en efectivo
                    if wdg.metodoSeleccionado == 'Efectivo')
            m = max(Moneda.cero, m - stack.restanteEnEfectivo)  # pagado - restante (en efectivo)
            self.ui.lbCambio.setText(f'Cambio: ${m}')
        else:
            self.ui.lbCambio.clear()  # ignorar cambio

        res = stack.total - sum(wdg.montoPagado for wdg in stack)  # total - pagado (cualquiera)

        if res < 0.0 and (not n_efec or stack.restanteEnEfectivo <= 0.):
            # sobra dinero y sin efectivo, o efectivo no necesario
            style = 'color: red;'
        else:  # recalcular restante, considerando que hay efectivo y necesario
            res = max(Moneda.cero, res)  # por el cambio a entregar
            style = ''
        if stack.pagosValidos:  # todo bien
            style = 'color: green;'

        self.ui.lbRestante.setStyleSheet(style)
        self.ui.lbRestante.setText(f'Restante: ${res}')

        self.ui.btListo.setEnabled(stack.pagosValidos
                                   and 0. <= stack.total <= self.total)

    def actualizarEstadoVenta(self) -> bool:
        raise NotImplementedError('CLASE BASE BROU')

    def dialogoExito(self) -> None:
        raise NotImplementedError('CLASE BASE BROU')

    def listo(self) -> None:
        """ Concluye la venta de la siguiente forma:
            1. Inserta pagos en tabla ventas_pagos.
            2. Si actualizarEstadoVenta, entonces dialogoExito. """
        manejadorVentas = ManejadorVentas(self.conn)

        # registrar pagos en tabla ventas_pagos
        for wdg in self.stackPagos:
            if wdg.metodoSeleccionado == 'Efectivo':
                monto = self.stackPagos.restanteEnEfectivo
                recibido = wdg.montoPagado if monto else None
            else:
                monto = wdg.montoPagado
                recibido = None

            if not manejadorVentas.insertarPago(self.id_ventas, wdg.metodoSeleccionado,
                                                monto, recibido, self.user.id):
                return

        if self.actualizarEstadoVenta():
            self.dialogoExito()

    def abortar(self) -> None:
        raise NotImplementedError('CLASE BASE BROU')


@fondo_oscuro
class App_TerminarVenta(Base_PagarVenta):
    """ Backend para la ventana para terminar una venta sobre pedido. """
    success = Signal()

    def __init__(self, idx: int, conn, user, parent=None):
        super().__init__(idx, conn, user, parent)

        self.ui.lbCincuenta.hide()
        self.ui.label_17.setText('Abonar pago(s) a pedido')
        self.ui.lbAnticipo1.setText('Abono')
        self.ui.label_20.setText('Saldo restante')
        self.ui.btCancelar.setText(' Regresar')
        self.ui.btCancelar.setIcon(QIcon(':/img/resources/images/cancel.png'))

        self.show()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def showEvent(self, event):
        manejador = ManejadorVentas(self.conn)
        productos = manejador.obtenerTablaProductosVenta(self.id_ventas)

        tabla = self.ui.tabla_productos
        tabla.modelo = tabla.Modelos.CREAR_VENTA
        tabla.llenar(productos)

    ####################
    # FUNCIONES ÚTILES #
    ####################
    def calcularTotal(self) -> Moneda:
        manejador = ManejadorVentas(self.conn)
        saldo = manejador.obtenerSaldoRestante(self.id_ventas)
        return saldo

    def obtenerDatosGenerales(self):
        manejador = ManejadorVentas(self.conn)
        nombreCliente, correo, telefono, fechaCreacion, fechaEntrega, *_ = \
            manejador.obtenerDatosGeneralesVenta(self.id_ventas)
        return (nombreCliente, correo, telefono, fechaCreacion, fechaEntrega)

    def pagoPredeterminado(self):
        return self.total

    def actualizarEstadoVenta(self) -> bool:
        manejador = ManejadorVentas(self.conn)

        if self.para_pagar == self.total:
            estado = 'Entregado por ' + self.user.nombre
        else:
            anticipo = manejador.obtenerAnticipo(self.id_ventas)
            estado = f'Recibido ${anticipo + self.para_pagar}'

        return manejador.actualizarEstadoVenta(self.id_ventas, estado, commit=True)

    def dialogoExito(self):
        if self.para_pagar == self.total:
            prompt = 'La venta ha sido marcada como terminada.'
        else:
            prompt = 'Pago(s) abonado(s) al pedido.'

        ret = qm.question(self, 'Éxito', prompt + '\n¿Desea imprimir los tickets de los pagos?')

        if ret == qm.Yes:
            slais = slice(-self.ui.stackPagos.count(), None)
            impresora = ImpresoraTickets(self.conn)
            impresora.imprimirTicketCompra(self.id_ventas, slais)

        self.success.emit()
        self.close()

    def abortar(self):
        self.close()


@fondo_oscuro
class App_ImprimirTickets(QtWidgets.QWidget):
    """ Backend para seleccionar tickets a imprimir de una venta/pedido. """

    def __init__(self, idVenta: int, conn, parent=None):
        from ui.Ui_ImprimirTickets import Ui_ImprimirTickets

        super().__init__(parent)

        self.ui = Ui_ImprimirTickets()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)
        self.setFixedSize(self.size())

        self.conn = conn
        self.idVenta = idVenta

        self.ui.btRegresar.clicked.connect(self.close)
        self.ui.btMarcar.clicked.connect(self.marcarTodo)
        self.ui.btDesmarcar.clicked.connect(self.desmarcarTodo)
        self.ui.btListo.clicked.connect(self.done)

        font = QFont()
        font.setPointSize(12)

        pagos = ManejadorVentas(conn).obtenerPagosVenta(idVenta)

        for i, (fecha, metodo, monto, r, v) in enumerate(pagos):
            txt = f'  Pago {i + 1}: ${monto:.2f}, {metodo.lower()} ({formatdate(fecha)})'
            checkbox = QtWidgets.QCheckBox(txt)
            checkbox.setFont(font)
            checkbox.setChecked(True)
            checkbox.setProperty('pago_idx', i)
            self.ui.layoutScroll.addWidget(checkbox, 0, Qt.AlignTop)

        self.show()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def checkboxes(self) -> list[QtWidgets.QCheckBox]:
        return self.ui.scrollAreaWidgetContents.children()[1:]

    def desmarcarTodo(self):
        for wdg in self.checkboxes():
            wdg.setChecked(False)

    def marcarTodo(self):
        for wdg in self.checkboxes():
            wdg.setChecked(True)

    def done(self):
        idxs = [wdg.property('pago_idx')
                for wdg in self.checkboxes()
                if wdg.isChecked()]

        if idxs:
            impresora = ImpresoraTickets(self.conn)
            impresora.imprimirTicketCompra(self.idVenta, idxs)
            self.close()
