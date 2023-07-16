from datetime import datetime
from math import ceil

from PySide6 import QtWidgets
from PySide6.QtGui import QFont, QColor, QIcon, QRegularExpressionValidator
from PySide6.QtCore import (QDate, QDateTime, QModelIndex,
                          QRegularExpression, Qt, Signal)

from utils.databasemanagers import ManejadorCaja, ManejadorVentas
from utils.mydecorators import con_fondo, run_in_thread
from utils.myutils import (chunkify, clamp, enviarWhatsApp, formatDate, generarOrdenCompra, 
                     generarTicketCompra, ColorsEnum, son_similar)
from utils.mywidgets import LabelAdvertencia, VentanaPrincipal


#####################
# VENTANA PRINCIPAL #
#####################
class App_AdministrarVentas(QtWidgets.QMainWindow):
    """ Backend para la ventana de administración de ventas.
        TODO:
        -   ocultamiento de folios """
    rescaned = Signal()
    
    def __init__(self, parent: VentanaPrincipal):
        from ui.Ui_AdministrarVentas import Ui_AdministrarVentas
        
        super().__init__()

        self.ui = Ui_AdministrarVentas()
        self.ui.setupUi(self)
        
        LabelAdvertencia(self.ui.tabla_ventasDirectas, '¡No se encontró ninguna venta!')
        LabelAdvertencia(self.ui.tabla_pedidos, '¡No se encontró ningún pedido!')
        
        # otras variables importantes
        self.filtro = 0
        self.chunk_size = 50
        
        # guardar conexión y usuario como atributos
        self.conn = parent.conn
        self.user = parent.user
        
        # fechas por defecto
        manejador = ManejadorVentas(self.conn)
        hoy = QDate.currentDate()
        
        restrict = self.user.id if not self.user.administrador else None
        fechaMin, = manejador.obtenerFechaPrimeraVenta(restrict)
        
        fechaMin = QDateTime(fechaMin).date() if fechaMin else hoy
        
        self.ui.dateDesde.setDate(hoy)
        self.ui.dateDesde.setMaximumDate(hoy)
        self.ui.dateDesde.setMinimumDate(fechaMin)
        
        self.ui.dateHasta.setDate(hoy)
        self.ui.dateHasta.setMaximumDate(hoy)
        self.ui.dateHasta.setMinimumDate(fechaMin)
        
        # deshabilitar botones es caso de no ser administrador
        if not self.user.administrador:
            self.ui.btCancelar.hide()

        # añadir menú de opciones al botón para filtrar
        popup = QtWidgets.QMenu(self.ui.btFiltrar)

        default = popup.addAction(
            'Folio', lambda: self.cambiar_filtro('folio', 0))
        popup.addAction(
            'Vendedor', lambda: self.cambiar_filtro('vendedor', 1))
        popup.addAction(
            'Cliente', lambda: self.cambiar_filtro('cliente', 2))
        
        popup.setDefaultAction(default)

        self.ui.btFiltrar.setMenu(popup)
        self.ui.btFiltrar.clicked.connect(lambda: self.cambiar_filtro('folio', 0))
        
        # crear eventos para los botones
        self.ui.btRegresar.clicked.connect(self.goHome)
        self.ui.btTerminar.clicked.connect(self.terminarVenta)
        self.ui.btCancelar.clicked.connect(self.cancelarVenta)
        self.ui.btOrden.clicked.connect(self.imprimirOrden)
        self.ui.btRecibo.clicked.connect(self.imprimirTicket)
        self.ui.searchBar.textChanged.connect(lambda: self.update_display())
        
        self.ui.dateDesde.dateChanged.connect(lambda: self.update_display(rescan=True))
        self.ui.dateHasta.dateChanged.connect(lambda: self.update_display(rescan=True))
        self.ui.btHoy.clicked.connect(self.hoy_handle)
        self.ui.btEstaSemana.clicked.connect(self.semana_handle)
        self.ui.btEsteMes.clicked.connect(self.mes_handle)
        
        self.ui.tabla_ventasDirectas.doubleClicked.connect(self.detallesVenta)
        self.ui.tabla_pedidos.doubleClicked.connect(self.detallesVenta)
        self.ui.tabWidget.currentChanged.connect(self.cambiar_pestana)
        self.ui.btAdelante.clicked.connect(self.ir_adelante)
        self.ui.btUltimo.clicked.connect(self.ir_ultimo)
        self.ui.btAtras.clicked.connect(self.ir_atras)
        self.ui.btPrimero.clicked.connect(self.ir_primero)
        
        self.rescaned.connect(self.update_display)
    
    def showEvent(self, event):
        # dar formato a las tabla principales
        # TABLA DE VENTAS DIRECTAS
        header = self.ui.tabla_ventasDirectas.horizontalHeader()

        for col in range(self.ui.tabla_ventasDirectas.columnCount()):
            if col not in {0, 3, 4, 5, 6}:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)

        # TABLA DE VENTAS SOBRE PEDIDO
        header = self.ui.tabla_pedidos.horizontalHeader()

        for col in range(self.ui.tabla_pedidos.columnCount()):
            if col not in {0, 5, 6, 7}:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
        
        self.update_display(rescan=True)
    
    def resizeEvent(self, event):
        if self.isVisible():
            self.tabla_actual.resizeRowsToContents()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @property
    def tabla_actual(self):
        return [self.ui.tabla_ventasDirectas, self.ui.tabla_pedidos][self.ui.tabWidget.currentIndex()]
    
    def ir_adelante(self):
        tabla = self.tabla_actual
        
        currentPage = tabla.property('paginaActual')
        tabla.setProperty('paginaActual', currentPage + 1)
        
        self.update_display()
    
    def ir_ultimo(self):
        self.tabla_actual.setProperty(
            'paginaActual',
            len(self.all_directas) + len(self.all_pedidos))
            
        self.update_display()
    
    def ir_atras(self):
        tabla = self.tabla_actual
        
        currentPage = tabla.property('paginaActual')
        tabla.setProperty('paginaActual', currentPage - 1)
        
        self.update_display()
    
    def ir_primero(self):
        self.tabla_actual.setProperty('paginaActual', 0)
        self.update_display()
        
    def cambiar_pestana(self, nuevo):
        """ Cambia el label con el contador de ventas, según la pestaña,
            y reajusta la tabla correspondiente a ella. También modifica
            los valores del navegador de páginas de la tabla. """
        if nuevo == 0:
            label = 'ventas directas'
            compras = self.all_directas
        else:
            label = 'pedidos'
            compras = self.all_pedidos
        
        num_pagina = self.tabla_actual.property('paginaActual')
        
        self.ui.lbContador.setText(
            f'{len(compras)} {label} en la base de datos.')
        self.ui.lbPagina.setText(
            f'{num_pagina + 1} de {ceil(len(compras) / self.chunk_size) or 1}')
        
        self.tabla_actual.resizeRowsToContents()
        
    def cambiar_filtro(self, filtro, idx):
        """ Modifica el filtro de búsqueda. """
        self.filtro = idx
        self.ui.searchBar.setPlaceholderText(f'Busque venta por {filtro}...')
        self.update_display()
    
    def hoy_handle(self):
        hoy = QDate.currentDate()
        self.ui.dateDesde.setDate(hoy)
        self.ui.dateHasta.setDate(hoy)
        
    def semana_handle(self):
        hoy = QDate.currentDate()
        
        start = hoy.addDays(-hoy.dayOfWeek())
        end = hoy.addDays(6 - hoy.dayOfWeek())
        
        self.ui.dateDesde.setDate(start)
        self.ui.dateHasta.setDate(end)
    
    def mes_handle(self):
        hoy = QDate.currentDate()
        
        start = QDate(hoy.year(), hoy.month(), 1)
        end = QDate(hoy.year(), hoy.month(), hoy.daysInMonth())
        
        self.ui.dateDesde.setDate(start)
        self.ui.dateHasta.setDate(end)

    def update_display(self, rescan: bool = False):
        """ Actualiza la tabla y el contador de clientes.
            Lee de nuevo la tabla de clientes, si se desea. """
        if rescan:
            self.rescan_db()
            return
        
        self.llenar_tabla_ventas()
        self.llenar_tabla_pedidos()
        
        self.cambiar_pestana(self.ui.tabWidget.currentIndex())

    def rescan_db(self):
        """ Releer base de datos y almacenar en atributos.
            TODO: en hilo separado. """
        fechaDesde = self.ui.dateDesde.date()
        fechaHasta = self.ui.dateHasta.date()
        restrict = self.user.id if not self.user.administrador else None
            
        manejador = ManejadorVentas(self.conn)

        self.all_directas = manejador.tablaVentas(fechaDesde, fechaHasta, restrict)
        self.all_pedidos = manejador.tablaPedidos(fechaDesde, fechaHasta, restrict)
        
        self.rescaned.emit()
    
    def llenar_tabla_ventas(self):
        """ Actualizar tabla de ventas directas. """
        bold = QFont()
        bold.setBold(True)
        
        # texto introducido por el usuario
        txt_busqueda = self.ui.searchBar.text().strip()

        tabla = self.ui.tabla_ventasDirectas
        tabla.setRowCount(0)
        
        compras = self.all_directas

        if txt_busqueda:
            compras = filter(
                          lambda c: c[self.filtro] 
                                    and son_similar(txt_busqueda, c[self.filtro]),
                          compras)
        
        compras = list(compras)
        chunks = chunkify(compras, self.chunk_size) or [[]]
        
        tabla.setProperty(      # truncar valor de la página si se sale del rango
            'paginaActual',
            clamp(tabla.property('paginaActual'),
                  0, ceil(len(compras) / self.chunk_size)-1))
        
        currentPage = tabla.property('paginaActual')
        
        for row, compra in enumerate(chunks[currentPage]):
            tabla.insertRow(row)

            for col, dato in enumerate(compra):
                if isinstance(dato, datetime):
                    cell = formatDate(dato)
                elif isinstance(dato, float):
                    cell = f'{dato:,.2f}'
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
        
        # texto introducido por el usuario
        txt_busqueda = self.ui.searchBar.text().strip()
        
        tabla = self.ui.tabla_pedidos
        tabla.setRowCount(0)
        
        compras = self.all_pedidos
                
        if txt_busqueda:
            compras = filter(
                          lambda c: c[self.filtro] 
                                    and son_similar(txt_busqueda, c[self.filtro]),
                          compras)
        
        compras = list(compras)
        chunks = chunkify(compras, self.chunk_size) or [[]]
        
        tabla.setProperty(      # truncar valor de la página si se sale del rango
            'paginaActual',
            clamp(tabla.property('paginaActual'),
                  0, ceil(len(compras) / self.chunk_size)-1))
        
        currentPage = tabla.property('paginaActual')

        for row, compra in enumerate(chunks[currentPage]):
            tabla.insertRow(row)

            for col, dato in enumerate(compra):
                if isinstance(dato, datetime):
                    cell = formatDate(dato)
                elif isinstance(dato, float):
                    cell = f'{dato:,.2f}'
                else:
                    cell = str(dato or '')
                tabla.setItem(row, col, QtWidgets.QTableWidgetItem(cell))
            
            tabla.item(row, 5).setFont(bold)
            
            estado = tabla.item(row, 6).text()
            
            if estado.startswith('Cancelada'):
                tabla.item(row, 6).setBackground(QColor(ColorsEnum.ROJO))
            elif estado.startswith('Terminada'):
                tabla.item(row, 6).setBackground(QColor(ColorsEnum.VERDE))
            elif estado.startswith('Recibido'):
                tabla.item(row, 6).setBackground(QColor(ColorsEnum.AMARILLO))
            
                button_cell = QtWidgets.QPushButton(' Enviar recordatorio')
                button_cell.setIcon(QIcon(":/img/resources/images/whatsapp.png"))
                button_cell.clicked.connect(self.enviarRecordatorio)
                
                tabla.setCellWidget(row, col+1, button_cell)
            
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
                          'este pedido?', qm.Yes | qm.No)
        
        if ret != qm.Yes:
            return
        
        # obtener número y nombre del cliente
        manejador = ManejadorVentas(self.conn)
        idVenta = self.tabla_actual.selectedItems()[0].text()
        
        nombre, celular = manejador.obtenerClienteAsociado(idVenta)
        
        # mensaje a enviar
        mensaje = ' '.join([
            f'*Apreciable {nombre}*:\nLe informamos que ya puede pasar a Printcopy',
            f'a recoger su pedido con folio {idVenta}. ¡Recuerde traer su orden de compra',
            f'para concretar el pedido!\n\n¡Esperamos verle pronto! 😊'
        ])
        
        enviarWhatsApp(celular, mensaje)
        
    def terminarVenta(self):
        """ Pide confirmación para marcar como cancelada una venta. """
        if not (selected := self.tabla_actual.selectedItems()):
            return
        
        idVenta = selected[0].text()
        manejador = ManejadorVentas(self.conn)
        
        if not (anticipo := manejador.obtenerAnticipo(idVenta)):
            return
        
        saldo = manejador.obtenerImporteTotal(idVenta) - anticipo
        
        if saldo > 0.:
            self.new = App_TerminarVenta(self, idVenta)
            self.new.success.connect(
                lambda: self.update_display(rescan=True))
            return
        
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Atención', 
                            'Este pedido no tiene saldo restante. '
                            '¿Desea marcar la venta como terminada?', qm.Yes | qm.No)
        
        if ret != qm.Yes:
            return

        # terminar venta directamente, al no tener saldo restante
        if not manejador.actualizarEstadoVenta(idVenta, 'Terminada', commit=True):
            return
        
        qm.information(self, 'Éxito', 'Se marcó como terminada la venta seleccionada.')
        self.update_display(rescan=True)
            
    def cancelarVenta(self):
        """ Pide confirmación para marcar como cancelada una venta. """
        if not (selected := self.tabla_actual.selectedItems()):
            return
        
        idVenta = selected[0].text()
        estado = selected[6].text()
        
        if estado == 'Cancelada':
            return

        # abrir pregunta
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Atención', 
                          'La venta seleccionada se marcará como cancelada.\n'
                          'Esta operación no se puede deshacer. ¿Desea continuar?', qm.Yes | qm.No)

        if ret != qm.Yes:
            return
        
        manejador = ManejadorVentas(self.conn)
        if not manejador.actualizarEstadoVenta(idVenta, 'Cancelada', commit=True):
            return
        
        qm.information(self, 'Éxito', 'Se marcó como cancelada la venta seleccionada.')
        self.update_display(rescan=True)

    def detallesVenta(self, idxs: QModelIndex):
        """ Abre ventana que muestra los detalles de una venta seleccionada. """
        self.new = App_DetallesVenta(self, idxs.siblingAtColumn(0).data())

    def imprimirTicket(self):
        """ Imprime ticket de una venta dado el folio de esta. """
        try:
            idVenta = self.tabla_actual.selectedItems()[0].text()
        except IndexError:
            return

        # abrir pregunta
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Atención',
                          'Se imprimirá el ticket de compra de la venta '
                          f'con folio {idVenta}. ¿Desea continuar?', qm.Yes | qm.No)

        if ret == qm.Yes:
            generarTicketCompra(self.conn, idVenta)

    def imprimirOrden(self):
        """ Imprime orden de compra de un pedido dado el folio de esta. """
        selected = self.tabla_actual.selectedItems()

        if not len(selected) or not selected[6].text().startswith('Recibido'):
            return

        idVenta = selected[0].text()

        # abrir pregunta
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Atención', 
                          'Se imprimirá la orden de compra de la venta '
                          f'con folio {idVenta}. ¿Desea continuar?', qm.Yes | qm.No)

        if ret == qm.Yes:
            generarOrdenCompra(self.conn, idVenta)

    def goHome(self):
        """ Cierra la ventana y regresa al inicio. """
        from Home import App_Home

        parent = self.parentWidget()       # QMainWindow
        new = App_Home(parent)
        parent.setCentralWidget(new)


#################################
# VENTANAS USADAS POR EL MÓDULO #
#################################
@con_fondo
class App_DetallesVenta(QtWidgets.QMainWindow):
    """ Backend para la ventana que muestra los detalles de una venta. """
    def __init__(self, first: App_AdministrarVentas, idx):
        from ui.Ui_DetallesVenta import Ui_DetallesVenta
        
        super().__init__(first)

        self.ui = Ui_DetallesVenta()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)
        
        self.conn = first.conn
        self.id_ventas = idx

        # total de la venta, anticipo y saldo
        manejador = ManejadorVentas(self.conn)
        
        total = manejador.obtenerImporteTotal(idx)
        anticipo = manejador.obtenerAnticipo(idx)
        
        # intenta calcular el saldo restante
        if anticipo:
            self.ui.lbAnticipo.setText(f'{anticipo:,.2f}')
            self.ui.lbSaldo.setText(f'{total-anticipo:,.2f}')
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
        self.ui.lbFolio.setText(f'{idx}')
        self.ui.lbTotal.setText(f'{total:,.2f}')

        # evento para botón de regresar
        self.ui.btRegresar.clicked.connect(self.close)

        self.show()
    
    def showEvent(self, event):
        # dar formato a la tabla principal
        header = self.ui.tabla_productos.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        for col in range(self.ui.tabla_productos.columnCount()):
            if col == 2:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
        
        self.update_display()
        event.accept()
    
    def update_display(self):
        # llenar de productos la tabla
        manejador = ManejadorVentas(self.conn)
        productos = manejador.obtenerTablaProductosVenta(self.id_ventas)

        tabla = self.ui.tabla_productos
        tabla.setRowCount(0)

        for row, prod in enumerate(productos):
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


@con_fondo
class App_TerminarVenta(QtWidgets.QMainWindow):
    """ Backend para la ventana para terminar una venta sobre pedido. """
    success = Signal()
    
    def __init__(self, first: App_AdministrarVentas, idx):        
        from ui.Ui_TerminarVenta import Ui_TerminarVenta
        
        super().__init__(first)

        self.ui = Ui_TerminarVenta()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)
        
        self.id_ventas = idx
        
        # guardar conexión y usuario como atributos
        self.conn = first.conn
        self.user = first.user
        
        manejador = ManejadorVentas(first.conn)
        
        # calcular el saldo restante
        total = manejador.obtenerImporteTotal(idx)
        anticipo = manejador.obtenerAnticipo(idx)
        
        self.paraPagar = round(total-anticipo, 2)

        nombreCliente, correo, telefono, fechaCreacion, fechaEntrega, *_ \
            = manejador.obtenerDatosGeneralesVenta(idx)

        self.ui.txtCliente.setText(nombreCliente)
        self.ui.txtCorreo.setText(correo)
        self.ui.txtTelefono.setText(telefono)
        self.ui.txtCreacion.setText(formatDate(fechaCreacion))
        self.ui.txtEntrega.setText(formatDate(fechaEntrega))
        self.ui.lbFolio.setText(f'{idx}')
        self.ui.lbSaldo.setText(f'{self.paraPagar:,.2f}')
        
        # validadores para datos numéricos
        regexp_numero = QRegularExpression(r'\d*\.?\d*')
        validador = QRegularExpressionValidator(regexp_numero)
        self.ui.txtPago.setValidator(validador)

        # eventos para widgets
        self.ui.btListo.clicked.connect(self.done)
        self.ui.btCancelar.clicked.connect(self.close)
        self.ui.txtPago.textChanged.connect(self.calcularCambio)

        self.show()
    
    def showEvent(self, event):
        # dar formato a la tabla principal
        header = self.ui.tabla_productos.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        for col in range(self.ui.tabla_productos.columnCount()):
            if col == 2:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
        
        self.update_display()
        event.accept()

    ####################
    # FUNCIONES ÚTILES #
    ####################
    def update_display(self):
        """ Llenar de productos la tabla. """
        manejador = ManejadorVentas(self.conn)
        productos = manejador.obtenerTablaProductosVenta(self.id_ventas)

        tabla = self.ui.tabla_productos
        tabla.setRowCount(0)

        for row, prod in enumerate(productos):
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
    
    def calcularCambio(self, txt):
        """ Recalcular cambio a entregar. """
        try:
            pago = float(txt)
        except ValueError:
            pago = 0.
        
        cambio = max(0., pago - self.paraPagar)
        self.ui.lbCambio.setText(f'{cambio:,.2f}')
    
    def done(self):
        """ Verifica restricciones y termina venta. """
        try:
            pago = float(self.ui.txtPago.text())
        except ValueError:
            pago = 0.
        
        metodo_pago = self.ui.groupMetodo.checkedButton().text()
        pagoAceptado = pago >= self.paraPagar if metodo_pago == 'Efectivo' \
                       else pago == self.paraPagar
                       
        if not pagoAceptado:
            return
        
        manejadorCaja = ManejadorCaja(self.conn)
        hoy = QDateTime.currentDateTime().toPython()
        
        # registrar ingreso (sin cambio) en caja
        ingreso_db_parametros = (
            hoy,
            self.paraPagar,
            f'Pago de venta con folio {self.id_ventas}',
            metodo_pago,
            self.user.id
        )
        
        if not manejadorCaja.insertarMovimiento(ingreso_db_parametros,
                                                commit=False):
            return
        
        # marcar venta como terminada
        manejadorVentas = ManejadorVentas(self.conn)
        
        if not manejadorVentas.actualizarEstadoVenta(self.id_ventas, 'Terminada',
                                                     commit=True):
            return
        
        QtWidgets.QMessageBox.information(
            self, 'Éxito', 'La venta ha sido marcada como terminada.')
        
        self.success.emit()
        self.close()