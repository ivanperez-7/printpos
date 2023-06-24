from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QDate, QDateTime, QModelIndex, QRegExp, Qt

from math import ceil
from myutils import (chunkify, clamp, formatDate, generarOrdenCompra, 
                     generarTicketCompra, lbAdvertencia, ColorsEnum, son_similar)
from mydecorators import con_fondo, run_in_thread
from mywidgets import WarningDialog

import fdb


#####################
# VENTANA PRINCIPAL #
#####################

class App_AdministrarVentas(QtWidgets.QMainWindow):
    """
    Backend para la ventana de administración de ventas.
    TODO:
    -   ocultamiento de folios
    """
    def __init__(self, parent=None):
        from AdministrarVentas.Ui_AdministrarVentas import Ui_AdministrarVentas
        
        super().__init__()

        self.ui = Ui_AdministrarVentas()
        self.ui.setupUi(self)
        
        self.session = parent.session  # conexión a la base de datos y usuario actual
        self.filtro = 0
        
        lbAdvertencia(self.ui.tabla_ventasDirectas, '¡No se encontró ninguna venta!')
        lbAdvertencia(self.ui.tabla_pedidos, '¡No se encontró ningún pedido!')
        
        # fechas por defecto
        hoy = QDate.currentDate()
        fechaMin, = self.session['conn'] \
                    .cursor() \
                    .execute('SELECT MIN(fechaHoraCreacion) FROM Ventas;') \
                    .fetchone()
        fechaMin = QDateTime.fromSecsSinceEpoch(fechaMin).date() if fechaMin else hoy
        
        self.ui.dateDesde.setDate(hoy)
        self.ui.dateDesde.setMaximumDate(hoy)
        self.ui.dateDesde.setMinimumDate(fechaMin)
        
        self.ui.dateHasta.setDate(hoy)
        self.ui.dateHasta.setMaximumDate(hoy)
        self.ui.dateHasta.setMinimumDate(fechaMin)
        
        # deshabilitar botones (¿cuáles?) es caso de no ser administrador
        if not self.session['user'].administrador:
            self.ui.lbCancelar.hide()

        # añadir menú de opciones al botón para filtrar
        popup = QtWidgets.QMenu()

        default = popup.addAction(
            'Folio', lambda: self.cambiar_filtro('folio', 0))
        popup.addAction(
            'Vendedor', lambda: self.cambiar_filtro('vendedor', 1))
        popup.addAction(
            'Cliente', lambda: self.cambiar_filtro('cliente', 2))
        
        popup.setDefaultAction(default)

        self.ui.btFiltrar.setMenu(popup)
        self.ui.btFiltrar.clicked.connect(lambda: self.cambiar_filtro('folio', 0))

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
        
        # tamaño de elementos para cada página de la tabla
        self.chunk_size = 50
                
        # crear eventos para los botones
        self.ui.lbRegresar.mousePressEvent = self.goHome
        self.ui.lbTerminar.mousePressEvent = self.terminarVenta
        self.ui.lbCancelar.mousePressEvent = self.cancelarVenta
        self.ui.btOrden.clicked.connect(self.imprimirOrden)
        self.ui.btRecibo.clicked.connect(self.imprimirTicket)
        self.ui.searchBar.textChanged.connect(lambda: self.update_display())
        
        self.ui.dateDesde.dateChanged.connect(lambda: self.update_display())
        self.ui.dateHasta.dateChanged.connect(lambda: self.update_display())
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
    
    def showEvent(self, event):
        self.update_display(rescan=True)        
        
        self.ui.lbContador.setText(
            f'{len(self.all_directas)} ventas directas en la base de datos.')
        self.ui.lbPagina.setText(
            f'1 de {ceil(len(self.all_directas) / self.chunk_size) or 1}')
    
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
        """
        Cambia el label con el contador de ventas, según la pestaña,
        y reajusta la tabla correspondiente a ella. También modifica
        los valores del navegador de páginas de la tabla
        """
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
        """
        Modifica el filtro de búsqueda.
        """
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
        """
        Actualiza la tabla y el contador de clientes.
        Lee de nuevo la tabla de clientes, si se desea.
        """
        if rescan:
            user = self.session['user']
            crsr = self.session['conn'].cursor()
            
            restrict = f'AND Usuarios.idUsuarios = {user.id}' \
                       if not user.administrador else ''

            crsr.execute(f'''
            SELECT  Ventas.idVentas,
                    Usuarios.nombre,
                    Clientes.nombre,
                    fechaHoraCreacion,
                    SUM(importe) AS total,
                    estado,
                    metodoPago,
                    comentarios
            FROM    Ventas
                    LEFT JOIN Usuarios
                           ON Ventas.idUsuarios = Usuarios.idUsuarios
                    LEFT JOIN Clientes
                           ON Ventas.idClientes = Clientes.idClientes
                    LEFT JOIN VentasDetallado
                           ON Ventas.idVentas = VentasDetallado.idVentas
			WHERE   fechaHoraCreacion = fechaHoraEntrega
                    {restrict}
            GROUP   BY 1, 2, 3, 4, 6, 7, 8
            ORDER	BY Ventas.idVentas DESC;
            ''')

            self.all_directas = crsr.fetchall()

            crsr.execute(f'''
            SELECT  Ventas.idVentas,
                    Usuarios.nombre,
                    Clientes.nombre,
                    fechaHoraCreacion,
                    fechaHoraEntrega,
                    SUM(importe) AS total,
                    estado,
                    metodoPago,
                    comentarios
            FROM    Ventas
                    LEFT JOIN Usuarios
                           ON Ventas.idUsuarios = Usuarios.idUsuarios
                    LEFT JOIN Clientes
                           ON Ventas.idClientes = Clientes.idClientes
                    LEFT JOIN VentasDetallado
                           ON Ventas.idVentas = VentasDetallado.idVentas
			WHERE   fechaHoraCreacion != fechaHoraEntrega
                    {restrict}
            GROUP   BY 1, 2, 3, 4, 5, 7, 8, 9
            ORDER	BY Ventas.idVentas DESC;
            ''')
            
            self.all_pedidos = crsr.fetchall()

        bold = QtGui.QFont()
        bold.setBold(True)
        
        fechaDesde = self.ui.dateDesde.date()
        fechaHasta = self.ui.dateHasta.date()
        
        dateFromSecs = lambda s: QDateTime.fromSecsSinceEpoch(s).date()
        
        # texto introducido por el usuario
        txt_busqueda = self.ui.searchBar.text().strip()

        # <llenar primera tabla>
        tabla = self.ui.tabla_ventasDirectas
        tabla.setRowCount(0)
        
        compras = filter(
                      lambda c: fechaDesde <= dateFromSecs(c[3]) <= fechaHasta, 
                      self.all_directas)
                
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
                if isinstance(dato, int) and col > 0:
                    cell = formatDate(dato)
                elif isinstance(dato, float):
                    cell = f'{dato:,.2f}'
                else:
                    cell = str(dato or '')
                tabla.setItem(row, col, QtWidgets.QTableWidgetItem(cell))
            
            tabla.item(row, 4).setFont(bold)
            
            estado = tabla.item(row, 5).text()
            
            if estado.startswith('Cancelada'):
                tabla.item(row, 5).setBackground(QtGui.QColor(ColorsEnum.ROJO))
            elif estado.startswith('Terminada'):
                tabla.item(row, 5).setBackground(QtGui.QColor(ColorsEnum.VERDE))
        # </llenar primera tabla>

        # <llenar segunda tabla>
        tabla = self.ui.tabla_pedidos
        tabla.setRowCount(0)

        compras = filter(
                      lambda c: fechaDesde <= dateFromSecs(c[3]) <= fechaHasta
                                or c[6].startswith('Recibido'), 
                      self.all_pedidos)
                
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
                if isinstance(dato, int) and col > 0:
                    cell = formatDate(dato)
                elif isinstance(dato, float):
                    cell = f'{dato:,.2f}'
                else:
                    cell = str(dato or '')
                tabla.setItem(row, col, QtWidgets.QTableWidgetItem(cell))
            
            tabla.item(row, 5).setFont(bold)
            
            estado = tabla.item(row, 6).text()
            
            if estado.startswith('Cancelada'):
                tabla.item(row, 6).setBackground(QtGui.QColor(ColorsEnum.ROJO))
            elif estado.startswith('Terminada'):
                tabla.item(row, 6).setBackground(QtGui.QColor(ColorsEnum.VERDE))
            elif estado.startswith('Recibido'):
                tabla.item(row, 6).setBackground(QtGui.QColor(ColorsEnum.AMARILLO))
            
                button_cell = QtWidgets.QPushButton(' Enviar recordatorio')
                button_cell.setIcon(QtGui.QIcon(":/img/resources/images/whatsapp.png"))
                button_cell.clicked.connect(self.enviarRecordatorio)
                
                tabla.setCellWidget(row, col+1, button_cell)
            
                # resaltar pedidos con fechas de entrega ya pasadas
                entrega = compra[4]
                
                if QDateTime.currentDateTime().toSecsSinceEpoch() > entrega:
                    tabla.item(row, 4).setBackground(QtGui.QColor(ColorsEnum.ROJO))
        # </llenar segunda tabla>
        
        self.tabla_actual.resizeRowsToContents() 

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
        idVenta = self.tabla_actual.selectedItems()[0].text()
        
        conn = self.session['conn']
        crsr = conn.cursor()
        
        crsr.execute('''
        SELECT  C.nombre,
                C.telefono
        FROM    Ventas AS V
                LEFT JOIN Clientes AS C
                       ON V.idClientes = C.idClientes
        WHERE   idVentas = ?;
        ''', (idVenta,))
        
        nombre, celular = crsr.fetchone()
        
        # mensaje a enviar
        mensaje = ' '.join([
            f'*Apreciable {nombre}*:\nLe recordamos que ya puede pasar a Printcopy',
            f'a recoger su pedido con folio {idVenta}. ¡Recuerde traer su orden de compra',
            f'para concretar el pedido!\n\n¡Esperamos verle pronto! 😊'
        ])
        
        self.abrir_whatsapp(celular, mensaje)
    
    @run_in_thread
    def abrir_whatsapp(self, celular, mensaje):
        """
        En función separada para ejecutar en hilo separado.
        """
        import pywhatkit
        
        try:
            pywhatkit.sendwhatmsg_instantly(celular, mensaje, 
                                        close_time=300, wait_time=300)
        except Exception as err:
            print(err)
        
    def terminarVenta(self, _):
        """
        Pide confirmación para marcar como cancelada una venta.
        """
        selected = self.tabla_actual.selectedItems()
        
        try:
            idVenta = selected[0].text()
            importe = selected[5].text().replace(',','')
            estado = selected[6].text()
            
            saldo = float(importe) - float(estado.split()[1])
        except (IndexError, ValueError):
            return
        
        qm = QtWidgets.QMessageBox
        
        if saldo > 0.:
            self.new = App_TerminarVenta(self, idVenta)
            return
        
        ret = qm.question(self, 'Atención', 
                            'Este pedido no tiene saldo restante. '
                            '¿Desea marcar la venta como terminada?', qm.Yes | qm.No)
        
        if ret != qm.Yes:
            return
        
        conn = self.session['conn']
        crsr = conn.cursor()

        # crea un cuadro que notifica el resultado de la operación
        try:
            crsr.execute('''
            UPDATE  Ventas
            SET     estado = 'Terminada'
            WHERE   idVentas = ?;
            ''', (idVenta,))

            conn.commit()
        except fdb.Error as err:
            conn.rollback()

            WarningDialog(self, '¡Hubo un error!', str(err))
            return
        
        qm.information(self, 'Éxito', 'Se marcó como terminada la venta seleccionada.', qm.Ok)
        self.update_display(rescan=True)
            
    def cancelarVenta(self, _):
        """
        Pide confirmación para marcar como cancelada una venta.
        """
        selected = self.tabla_actual.selectedItems()
        
        try:
            idVenta = selected[0].text()
            estado = selected[6].text()
        except IndexError:
            return
        
        if estado == 'Cancelada':
            return

        # abrir pregunta
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Atención', 
                          'La venta seleccionada se marcará como cancelada.\n'
                          'Esta operación no se puede deshacer. ¿Desea continuar?', qm.Yes | qm.No)

        if ret != qm.Yes:
            return
        
        conn = self.session['conn']
        crsr = conn.cursor()

        # crea un cuadro que notifica el resultado de la operación
        try:
            crsr.execute('''
            UPDATE  Ventas
            SET     estado = 'Cancelada'
            WHERE   idVentas = ?;
            ''', (idVenta,))

            conn.commit()
        except fdb.Error as err:
            conn.rollback()

            WarningDialog(self, '¡Hubo un error!', str(err))
            return
        
        qm.information(self, 'Éxito', 'Se marcó como cancelada la venta seleccionada.', qm.Ok)
        self.update_display(rescan=True)

    def detallesVenta(self, idxs: QModelIndex):
        """
        Abre ventana que muestra los detalles de una venta seleccionada.
        """
        self.new = App_DetallesVenta(self, idxs.siblingAtColumn(0).data(0))

    def imprimirTicket(self):
        """
        Imprime ticket de una venta dado el folio de esta.
        """
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
            generarTicketCompra(self.session['conn'].cursor(), idVenta)

    def imprimirOrden(self):
        """
        Imprime orden de compra de un pedido dado el folio de esta.
        """
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
            generarOrdenCompra(self.session['conn'].cursor(), idVenta)

    def goHome(self, _):
        """
        Cierra la ventana y regresa al inicio.
        """
        from Home import App_Home

        parent = self.parentWidget()       # QMainWindow
        new = App_Home(parent)
        parent.setCentralWidget(new)


#################################
# VENTANAS USADAS POR EL MÓDULO #
#################################
@con_fondo
class App_DetallesVenta(QtWidgets.QMainWindow):
    """
    Backend para la ventana que muestra los detalles de una venta.
    """
    def __init__(self, first, idx):
        from AdministrarVentas.Ui_DetallesVenta import Ui_DetallesVenta
        
        super().__init__(first)

        self.ui = Ui_DetallesVenta()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)
        
        session = first.session # conexión a base de datos, y usuario
        
        self.first = first  # ventana de administrar ventas

        # dar formato a la tabla principal
        header = self.ui.tabla_productos.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        for col in range(self.ui.tabla_productos.columnCount()):
            if col == 2:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
        
        # llenar de productos la tabla
        crsr = session['conn'].cursor()
        
        crsr.execute('''
        SELECT  cantidad,
                codigo,
                especificaciones,
                precio,
                descuentoPrecio,
                importe
        FROM    VentasDetallado
                LEFT JOIN Productos
                       ON VentasDetallado.idProductos = Productos.idProductos
        WHERE   idVentas = ?;
        ''', (idx,))

        tabla = self.ui.tabla_productos
        tabla.setRowCount(0)

        for row, prod in enumerate(crsr):
            tabla.insertRow(row)

            for col, dato in enumerate(prod):
                if isinstance(dato, float):
                    if col == 4 and not dato: cell = ''
                    else: cell = f'{dato:,.2f}'
                else:
                    cell = str(dato or '')
                    
                cell = QtWidgets.QTableWidgetItem(cell)
                tabla.setItem(row, col, cell)

        # total de la venta, anticipo y saldo
        crsr.execute('''
        SELECT	SUM(importe) AS total,
                estado
        FROM	Ventas AS V
                LEFT JOIN VentasDetallado AS VD
                       ON V.idVentas = VD.idVentas
        WHERE	V.idVentas = ?
        GROUP   BY 2;
        ''', (idx,))

        total, estado = crsr.fetchone()
        
        # intenta calcular el saldo restante, asumiendo
        # que el estado comienza con 'Recibido'
        try:
            anticipo = float(estado.split()[1])
            
            self.ui.lbAnticipo.setText(f'{anticipo:,.2f}')
            self.ui.lbSaldo.setText(f'{total-anticipo + 0.:,.2f}')
        except (IndexError, ValueError):
            # el estado no comienza con 'Recibido'
            for w in [self.ui.lbAnticipo,
                      self.ui.lbSaldo,
                      self.ui.temp1,
                      self.ui.temp2,
                      self.ui.temp3,
                      self.ui.temp4]:
                w.hide()

        crsr.execute('''
        SELECT  Clientes.nombre,
                correo,
                telefono,
                fechaHoraCreacion,
                fechaHoraEntrega,
                comentarios,
                Usuarios.nombre
        FROM    Ventas
                LEFT JOIN Clientes
                       ON Ventas.idClientes = Clientes.idClientes
                LEFT JOIN Usuarios
                       ON Ventas.idUsuarios = Usuarios.idUsuarios
        WHERE   idVentas = ?;
        ''', (idx,))

        nombreCliente, correo, telefono, fechaCreacion, \
        fechaEntrega, comentarios, nombreUsuario = crsr.fetchone()
        
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
        self.ui.lbRegresar.mousePressEvent = self.closeEvent

        self.show()
    
    def showEvent(self, event):
        self.ui.tabla_productos.resizeRowsToContents()


@con_fondo
class App_TerminarVenta(QtWidgets.QMainWindow):
    """
    Backend para la ventana para terminar una venta sobre pedido.
    """
    def __init__(self, first, idx):        
        from AdministrarVentas.Ui_TerminarVenta import Ui_TerminarVenta
        
        super().__init__(first)

        self.ui = Ui_TerminarVenta()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)
        
        session = first.session # conexión a base de datos, y usuario
        
        self.first = first  # ventana de administrar ventas
        self.idVentas = idx

        # dar formato a la tabla principal
        header = self.ui.tabla_productos.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        for col in range(self.ui.tabla_productos.columnCount()):
            if col == 2:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
        
        # llenar de productos la tabla
        crsr = session['conn'].cursor()
        
        crsr.execute('''
        SELECT  cantidad,
                codigo,
                especificaciones,
                precio,
                descuentoPrecio,
                importe
        FROM    VentasDetallado
                LEFT JOIN Productos
                       ON VentasDetallado.idProductos = Productos.idProductos
        WHERE   idVentas = ?;
        ''', (idx,))

        tabla = self.ui.tabla_productos
        tabla.setRowCount(0)

        for row, prod in enumerate(crsr):
            tabla.insertRow(row)

            for col, dato in enumerate(prod):
                if isinstance(dato, float):
                    if col == 4 and not dato: cell = ''
                    else: cell = f'{dato:,.2f}'
                else:
                    cell = str(dato or '')
                    
                cell = QtWidgets.QTableWidgetItem(cell)
                tabla.setItem(row, col, cell)

        crsr.execute('''
        SELECT	SUM(importe) AS total,
                estado
        FROM	Ventas AS V
                LEFT JOIN VentasDetallado AS VD
                       ON V.idVentas = VD.idVentas
        WHERE	V.idVentas = ?
        GROUP   BY 2;
        ''', (idx,))

        total, estado = crsr.fetchone()
        
        # calcular el saldo restante
        anticipo = float(estado.split()[1])
        self.paraPagar = total-anticipo

        crsr.execute('''
        SELECT  Clientes.nombre,
                correo,
                telefono,
                fechaHoraCreacion,
                fechaHoraEntrega
        FROM    Ventas
                LEFT JOIN Clientes
                       ON Ventas.idClientes = Clientes.idClientes
        WHERE   idVentas = ?;
        ''', (idx,))

        nombreCliente, correo, telefono, \
        fechaCreacion, fechaEntrega = crsr.fetchone()

        self.ui.txtCliente.setText(nombreCliente)
        self.ui.txtCorreo.setText(correo)
        self.ui.txtTelefono.setText(telefono)
        self.ui.txtCreacion.setText(formatDate(fechaCreacion))
        self.ui.txtEntrega.setText(formatDate(fechaEntrega))
        self.ui.lbFolio.setText(f'{idx}')
        self.ui.lbSaldo.setText(f'{self.paraPagar:,.2f}')
        
        # validadores para datos numéricos
        regexp_numero = QRegExp(r'\d*\.?\d*')
        validador = QtGui.QRegExpValidator(regexp_numero)
        self.ui.txtPago.setValidator(validador)

        # eventos para widgets
        self.ui.btListo.clicked.connect(self.done)
        self.ui.btCancelar.clicked.connect(self.closeEvent)
        self.ui.txtPago.textChanged.connect(self.calcularCambio)

        self.show()
    
    def showEvent(self, event):
        self.ui.tabla_productos.resizeRowsToContents()

    ####################
    # FUNCIONES ÚTILES #
    ####################
    def calcularCambio(self, txt):
        """
        Recalcular cambio a entregar.
        """
        try:
            pago = float(txt)
        except ValueError:
            pago = 0.
        
        cambio = max(0., pago - self.paraPagar)
        self.ui.lbCambio.setText(f'{cambio:,.2f}')
    
    def done(self):
        """
        Acepta los cambios y modifica la fecha seleccionada en la ventana principal (CrearVenta).
        """
        try:
            pago = float(self.ui.txtPago.text())
        except:
            pago = 0.
        
        metodoPago = self.ui.groupMetodo.checkedButton().text()
        pagoAceptado = pago >= self.paraPagar if metodoPago == 'Efectivo' \
                       else pago == self.paraPagar
                       
        if not pagoAceptado:
            return
        
        session = self.first.session
        conn = session['conn']
        crsr = conn.cursor()
        
        try:
            crsr.execute('''
            UPDATE  Ventas
            SET     estado = 'Terminada'
            WHERE   idVentas = ?;
            ''', (self.idVentas,))
            
            # registrar ingreso (sin cambio) en caja
            hoy = QDateTime.currentDateTime().toSecsSinceEpoch()
            
            caja_db_parametros = [(
                hoy,
                pago,
                f'Pago de venta con folio {self.idVentas}',
                metodoPago,
                session['user'].id
            )]
            
            # registrar egreso (cambio) en caja
            if (cambio := pago - self.paraPagar):
                caja_db_parametros.append((
                    hoy,
                    -cambio,
                    f'Cambio de venta con folio {self.idVentas}',
                    metodoPago,
                    session['user'].id
                ))
            
            crsr.executemany('''
            INSERT INTO Caja (
                fechaHora, monto,
                descripcion, metodo, idUsuarios
            )
            VALUES
                (?,?,?,?,?);
            ''', caja_db_parametros)

            conn.commit()
        except fdb.Error as err:
            conn.rollback()

            WarningDialog(self, '¡Hubo un error!', str(err))
            return

        qm = QtWidgets.QMessageBox
        
        qm.information(self, 'Éxito', 'La venta ha sido marcada como terminada.', qm.Ok)
        self.first.update_display(rescan=True)
        self.close()
