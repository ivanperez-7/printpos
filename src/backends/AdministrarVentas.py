from datetime import datetime
from math import ceil

from PySide6 import QtWidgets
from PySide6.QtGui import QFont, QColor, QIcon
from PySide6.QtCore import QDateTime, QModelIndex, Qt, Signal

from utils.mydecorators import con_fondo, requiere_admin
from utils.myinterfaces import InterfazFechas, InterfazFiltro, InterfazPaginas
from utils.myutils import *
from utils.mywidgets import LabelAdvertencia, VentanaPrincipal
from utils.pdf import ImpresoraOrdenes, ImpresoraTickets
from utils.sql import ManejadorVentas


#####################
# VENTANA PRINCIPAL #
#####################
class App_AdministrarVentas(QtWidgets.QWidget):
    """ Backend para la ventana de administración de ventas.
        TODO:
        -   ocultamiento de folios """
    
    def __init__(self, parent: VentanaPrincipal):
        from ui.Ui_AdministrarVentas import Ui_AdministrarVentas
        
        super().__init__()
        
        self.ui = Ui_AdministrarVentas()
        self.ui.setupUi(self)
        
        LabelAdvertencia(self.ui.tabla_ventasDirectas, '¡No se encontró ninguna venta!')
        LabelAdvertencia(self.ui.tabla_pedidos, '¡No se encontró ningún pedido!')
        
        # otras variables importantes
        self.chunk_size = 50
        
        # guardar conexión y usuario como atributos
        self.conn = parent.conn
        self.user = parent.user
        
        # fechas por defecto
        manejador = ManejadorVentas(self.conn)
        fechaMin = manejador.obtenerFechaPrimeraVenta(None)
        
        InterfazFechas(self.ui.btHoy, self.ui.btEstaSemana, self.ui.btEsteMes,
                       self.ui.dateDesde, self.ui.dateHasta, fechaMin)
        
        # añadir menú de opciones al botón para filtrar
        self.filtro = InterfazFiltro(self.ui.btFiltrar, [
            ('Folio', 'folio', 0),
            ('Vendedor', 'vendedor', 1),
            ('Cliente', 'cliente', 2)
        ])
        self.filtro.filtroCambiado.connect(
            lambda txt: (self.ui.searchBar.setPlaceholderText(f'Busque venta por {txt}...'),
                         self.update_display()))
        
        # crear eventos para los botones
        self.ui.btRegresar.clicked.connect(self.goHome)
        self.ui.btTerminar.clicked.connect(self.terminarVenta)
        self.ui.btCancelar.clicked.connect(self.cancelarVenta)
        self.ui.btOrden.clicked.connect(self.imprimirOrden)
        self.ui.btRecibo.clicked.connect(self.imprimirTicket)
        self.ui.searchBar.textChanged.connect(self.update_display)
        
        self.ui.dateDesde.dateChanged.connect(self.rescan_update)
        self.ui.dateHasta.dateChanged.connect(self.rescan_update)
        
        self.ui.tabla_ventasDirectas.doubleClicked.connect(self.detallesVenta)
        self.ui.tabla_pedidos.doubleClicked.connect(self.detallesVenta)
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
        self.ui.tabla_ventasDirectas.configurarCabecera(lambda col: col in {0, 3, 4, 5, 6, 7})
        self.ui.tabla_pedidos.configurarCabecera(lambda col: col in {0, 3, 4, 5, 7, 8})
    
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
    
    def cambiar_pestana(self, nuevo):
        """ Cambia el label con el contador de ventas, según la pestaña,
            y reajusta la tabla correspondiente a ella. También modifica
            los valores del navegador de páginas de la tabla. """
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
    
    def rescan_update(self):
        """ Actualiza la tabla y el contador de clientes.
            Lee de nuevo la tabla de clientes, si se desea. """
        self.rescan_db()
        self.update_display()
    
    def rescan_db(self):
        """ Releer base de datos y almacenar en atributos.
            TODO: en hilo separado. """
        fechaDesde = self.ui.dateDesde.date()
        fechaHasta = self.ui.dateHasta.date()
        restrict = self.user.id if not self.user.administrador else None
        
        manejador = ManejadorVentas(self.conn)
        self.all_directas = manejador.tablaVentas(fechaDesde, fechaHasta, restrict)
        self.all_pedidos = manejador.tablaPedidos(fechaDesde, fechaHasta, None)
    
    def update_display(self):
        self.llenar_tabla_ventas()
        self.llenar_tabla_pedidos()
        self.cambiar_pestana(self.ui.tabWidget.currentIndex())
    
    def llenar_tabla_ventas(self):
        """ Actualizar tabla de ventas directas. """
        bold = QFont()
        bold.setBold(True)
        
        tabla = self.ui.tabla_ventasDirectas
        tabla.setRowCount(0)
        
        compras = self.all_directas
        
        if txt_busqueda := self.ui.searchBar.text().strip():
            compras = [c for c in compras
                       if c[self.filtro.filtro]
                       if son_similar(txt_busqueda, c[self.filtro.filtro])]
        
        chunks = chunkify(compras, self.chunk_size) or [[]]
        
        currentPage = clamp(tabla.property('paginaActual'), 0, ceil(len(compras) / self.chunk_size) - 1)
        tabla.setProperty('paginaActual', currentPage) # truncar valor de la página si se sale del rango
        
        data = chunks[currentPage]
        tabla.setRowCount(len(data))
        
        for row, compra in enumerate(data):
            for col, dato in enumerate(compra):
                if isinstance(dato, datetime):
                    cell = formatDate(dato)
                elif isinstance(dato, float):
                    cell = f'${dato:,.2f}'
                else:
                    cell = str(dato or '')
                tabla.setItem(row, col, QtWidgets.QTableWidgetItem(cell))
            
            tabla.item(row, 4).setFont(bold)
            
            estado = tabla.item(row, 5).text()
            
            if estado.startswith('Cancelada'):
                tabla.item(row, 5).setBackground(QColor(ColorsEnum.ROJO))
            elif estado.startswith('Terminada'):
                tabla.item(row, 5).setBackground(QColor(ColorsEnum.VERDE))
    
    def llenar_tabla_pedidos(self):
        """ Actualizar tabla de ventas sobre pedido. """
        bold = QFont()
        bold.setBold(True)
        icon = QIcon(":/img/resources/images/whatsapp.png")
        
        tabla = self.ui.tabla_pedidos
        tabla.setRowCount(0)
        
        compras = self.all_pedidos
        
        if txt_busqueda := self.ui.searchBar.text().strip():
            compras = [c for c in compras
                       if c[self.filtro.filtro]
                       if son_similar(txt_busqueda, c[self.filtro.filtro])]
        
        chunks = chunkify(compras, self.chunk_size) or [[]]
        
        currentPage = clamp(tabla.property('paginaActual'), 0, ceil(len(compras) / self.chunk_size) - 1)
        tabla.setProperty('paginaActual', currentPage) # truncar valor de la página si se sale del rango
        
        data = chunks[currentPage]
        tabla.setRowCount(len(data))
        
        for row, compra in enumerate(data):            
            for col, dato in enumerate(compra):
                if isinstance(dato, datetime):
                    cell = formatDate(dato)
                elif isinstance(dato, float):
                    cell = f'${dato:,.2f}'
                else:
                    cell = str(dato or '')
                tabla.setItem(row, col, QtWidgets.QTableWidgetItem(cell))
            
            tabla.item(row, 5).setFont(bold)
            
            estado_cell = tabla.item(row, 6)
            estado = estado_cell.text()
            
            if estado.startswith('Cancelada'):
                estado_cell.setBackground(QColor(ColorsEnum.ROJO))
            elif estado.startswith('Entregado') or estado.startswith('Terminada'):
                estado_cell.setBackground(QColor(ColorsEnum.VERDE))
            elif estado.startswith('Recibido'):
                estado_cell.setBackground(QColor(ColorsEnum.AMARILLO))
                
                button_cell = QtWidgets.QPushButton(' Enviar recordatorio')
                button_cell.setIcon(icon)
                button_cell.setFlat(True)
                button_cell.clicked.connect(self.enviarRecordatorio)
                
                tabla.setCellWidget(row, 10, button_cell)
                
                # resaltar pedidos con fechas de entrega ya pasadas
                if QDateTime.currentDateTime() > compra[4]:
                    tabla.item(row, 4).setBackground(QColor(ColorsEnum.ROJO))
    
    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def enviarRecordatorio(self):
        qm = QtWidgets.QMessageBox
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
            widget = App_TerminarVenta(self, idVenta)
            widget.success.connect(self.rescan_update)
            return
        
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Atención',
                          'Este pedido no tiene saldo restante. '
                          '¿Desea marcar la venta como terminada?')
        if ret != qm.Yes:
            return
        
        # terminar venta directamente, al no tener saldo restante
        man = ManejadorVentas(self.conn)
        if not manejador.actualizarEstadoVenta(idVenta, 'Entregado por ' + man.usuarioActivo,
                                               commit=True):
            return
        
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
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Atención',
                          'La venta seleccionada se marcará como cancelada.\n'
                          'Esta operación no se puede deshacer. ¿Desea continuar?')
        if ret == qm.Yes:
            self._cancelarVenta(selected[0].text())
    
    @requiere_admin
    def _cancelarVenta(self, idVenta, conn):
        # preguntar por devolución y manejar tabla ventas_pagos como corresponde
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Devolución de dinero',
                          '¿Desea registrar la devolución de los pagos realizados en esta venta?')
        
        manejador = ManejadorVentas(conn)
        estado = 'Cancelada por ' + manejador.usuarioActivo
        
        if ret == qm.Yes:
            if not manejador.anularPagos(idVenta):
                return
        if not manejador.actualizarEstadoVenta(idVenta, estado, commit=True):
            return
        
        qm.information(self, 'Éxito', 'Se marcó como cancelada la venta seleccionada.')
        self.rescan_update()
    
    def detallesVenta(self, idxs: QModelIndex):
        """ Abre ventana que muestra los detalles de una venta seleccionada. """
        widget = App_DetallesVenta(self, idxs.siblingAtColumn(0).data())
    
    def imprimirTicket(self):
        """ Imprime ticket de una venta dado el folio de esta. """
        if not (selected := self.tabla_actual.selectedItems()):
            return
        
        checar_estado = lambda i: selected[i].text().startswith('Cancelada')
        if checar_estado(5) or checar_estado(6):
            return
        
        idVenta = selected[0].text()
        man = ManejadorVentas(self.conn)
        
        pagos = man.obtenerPagosVenta(idVenta)
        if len(pagos) > 1:
            wdg = App_ImprimirTickets(self, pagos, idVenta)
            return
        
        # abrir pregunta
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Atención',
                          'Se imprimirá el ticket de compra de la venta '
                          f'con folio {idVenta}. ¿Desea continuar?')
        
        if ret == qm.Yes:
            impresora = ImpresoraTickets(self)
            impresora.imprimirTicketCompra(idVenta)
    
    def imprimirOrden(self):
        """ Imprime orden de compra de un pedido dado el folio de esta. """
        selected = self.tabla_actual.selectedItems()
        
        if not selected or not selected[6].text().startswith('Recibido'):
            return
        
        idVenta = selected[0].text()
        
        # abrir pregunta
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Atención',
                          'Se imprimirá la orden de compra de la venta '
                          f'con folio {idVenta}. ¿Desea continuar?')
        
        if ret == qm.Yes:
            impresora = ImpresoraOrdenes(self)
            impresora.imprimirOrdenCompra(idVenta)
    
    def goHome(self):
        """ Cierra la ventana y regresa al inicio. """
        parent: VentanaPrincipal = self.parentWidget()
        parent.goHome()


#################################
# VENTANAS USADAS POR EL MÓDULO #
#################################
@con_fondo
class App_DetallesVenta(QtWidgets.QWidget):
    """ Backend para la ventana que muestra los detalles de una venta. """
    
    def __init__(self, first: App_AdministrarVentas, idx):
        from ui.Ui_DetallesVenta import Ui_DetallesVenta
        
        super().__init__(first)
        
        self.ui = Ui_DetallesVenta()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window) 
        
        # total de la venta, anticipo y saldo
        conn = first.conn
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
        self.ui.txtCreacion.setText(formatDate(fechaCreacion))
        self.ui.txtEntrega.setText(formatDate(fechaEntrega))
        self.ui.txtComentarios.setPlainText(comentarios)
        self.ui.txtVendedor.setText(nombreUsuario)
        self.ui.lbFolio.setText(idx)
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


@con_fondo
class App_TerminarVenta(QtWidgets.QWidget):
    """ Backend para la ventana para terminar una venta sobre pedido. """
    success = Signal()
    
    def __init__(self, first: App_AdministrarVentas, idx):
        from ui.Ui_TerminarVenta import Ui_TerminarVenta
        
        super().__init__(first)
        
        self.ui = Ui_TerminarVenta()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)
        self.setFixedSize(833, 759)
        
        self.id_ventas = idx
        
        # guardar conexión y usuario como atributos
        self.conn = first.conn
        
        manejador = ManejadorVentas(first.conn)
        saldo = manejador.obtenerSaldoRestante(idx)
        self.saldo = saldo
        
        self.ui.stackPagos.total = self.ui.txtAbono.cantidad = saldo
        self.ui.stackPagos.agregarPago()
        
        nombreCliente, correo, telefono, fechaCreacion, fechaEntrega, *_ \
            = manejador.obtenerDatosGeneralesVenta(idx)
        
        self.ui.txtCliente.setText(nombreCliente)
        self.ui.txtCorreo.setText(correo)
        self.ui.txtTelefono.setText(telefono)
        self.ui.txtCreacion.setText(formatDate(fechaCreacion))
        self.ui.txtEntrega.setText(formatDate(fechaEntrega))
        self.ui.lbFolio.setText(idx)
        self.ui.lbSaldo.setText(str(saldo))
        
        # eventos para widgets
        self.ui.btListo.clicked.connect(self.done)
        self.ui.btCancelar.clicked.connect(self.close)
        self.ui.txtAbono.textChanged.connect(self.cambiarAnticipo)
        
        self.ui.btAgregar.clicked.connect(self.ui.stackPagos.agregarPago)
        self.ui.btAgregar.clicked.connect(self.modificar_contador)
        self.ui.btQuitar.clicked.connect(self.ui.stackPagos.quitarPago)
        self.ui.btQuitar.clicked.connect(self.modificar_contador)
        self.ui.btAnterior.clicked.connect(self.ui.stackPagos.retroceder)
        self.ui.btAnterior.clicked.connect(self.modificar_contador)
        self.ui.btSiguiente.clicked.connect(self.ui.stackPagos.avanzar)
        self.ui.btSiguiente.clicked.connect(self.modificar_contador)
        
        # configurar tabla de productos
        self.ui.tabla_productos.quitarBordeCabecera()
        self.ui.tabla_productos.configurarCabecera(
            lambda col: col != 2,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self.show()
    
    def showEvent(self, event):
        manejador = ManejadorVentas(self.conn)
        productos = manejador.obtenerTablaProductosVenta(self.id_ventas)
        
        tabla = self.ui.tabla_productos
        tabla.modelo = tabla.Modelos.CREAR_VENTA
        tabla.llenar(productos)
    
    ####################
    # FUNCIONES ÚTILES #
    ####################
    @property
    def para_pagar(self):
        return self.ui.txtAbono.cantidad
    
    def cambiarAnticipo(self):
        """ Cambiar el anticipo pagado por el cliente. """
        self.ui.stackPagos.total = self.ui.txtAbono.cantidad
        
    def modificar_contador(self):
        self.ui.lbContador.setText('Pago {}/{}'.format(self.ui.stackPagos.currentIndex()+1,
                                                       self.ui.stackPagos.count()))
    
    def done(self):
        """ Verifica restricciones y abona pagos a pedido.
             1. Checar que la suma de abonos no sobrepase saldo restante
             2. Insertar pagos en tabla VENTAS_PAGOS
             3. Actualizar estado (Recibido xx.xx o Entregado)"""
        if not (0. < self.para_pagar <= self.saldo 
                and self.ui.stackPagos.pagosValidos):
            return
        
        # registrar pagos en tabla ventas_pagos
        manejadorVentas = ManejadorVentas(self.conn)
        
        for wdg in self.ui.stackPagos.widgetsPago:
            montoAPagar = (wdg.montoPagado if wdg.metodoSeleccionado != 'Efectivo'
                else self.ui.stackPagos.restanteEnEfectivo)
            
            if not manejadorVentas.insertarPago(self.id_ventas, wdg.metodoSeleccionado,
                                                montoAPagar, wdg.montoPagado):
                return
        
        # actualizar estado de venta
        if self.para_pagar == self.saldo:
            estado = 'Entregado por ' + manejadorVentas.usuarioActivo
            prompt = 'La venta ha sido marcada como terminada.'
        else:
            anticipo = manejadorVentas.obtenerAnticipo(self.id_ventas)
            estado = f'Recibido ${anticipo + self.para_pagar}'
            prompt = 'Pago(s) abonado(s) al pedido.'
        
        if not manejadorVentas.actualizarEstadoVenta(self.id_ventas, estado, commit=True):
            return
        
        QtWidgets.QMessageBox.information(self, 'Éxito', prompt)
        
        self.success.emit()
        self.close()


@con_fondo
class App_ImprimirTickets(QtWidgets.QWidget):
    """ Backend para seleccionar tickets a imprimir de una venta/pedido. """
    
    def __init__(self, first: App_AdministrarVentas, pagos, idVenta):
        from ui.Ui_ImprimirTickets import Ui_ImprimirTickets
        
        super().__init__(first)
        
        self.conn = first.conn
        self.idVenta = idVenta
        
        self.ui = Ui_ImprimirTickets()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)
        self.setFixedSize(self.size())
        
        self.ui.btRegresar.clicked.connect(self.close)
        self.ui.btMarcar.clicked.connect(self.marcarTodo)
        self.ui.btDesmarcar.clicked.connect(self.desmarcarTodo)
        self.ui.btListo.clicked.connect(self.done)
        
        font = QFont()
        font.setPointSize(12)
        
        for i, (fecha, metodo, monto, _) in enumerate(pagos):
            txt = f'  Pago {i+1}: ${monto:.2f}, {metodo.lower()} ({formatDate(fecha)})'
            checkbox = QtWidgets.QCheckBox(txt)
            checkbox.setFont(font)
            checkbox.setChecked(True)
            checkbox.setProperty('pago_idx', i)
            self.ui.layoutScroll.addWidget(checkbox, 0, Qt.AlignTop)
        
        self.show()
    
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
