from dataclasses import dataclass

import fdb

from PyQt5 import QtWidgets
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import (QDate, QDateTime, QRegExp, Qt,
                          QPropertyAnimation, QRect, QEasingCurve)

from mydecorators import con_fondo, requiere_admin
from myutils import (clamp, enviarWhatsApp, formatDate,
                     generarOrdenCompra, generarTicketCompra,
                     generarTicketPresupuesto, son_similar)
from mywidgets import DimBackground, LabelAdvertencia, SpeechBubble, WarningDialog


##################
# CLASE AUXILIAR #
##################
@dataclass
class ItemVenta:
    """
    Clase para mantener registro de un producto de la venta.
    """
    id: int               # identificador interno en la base de datos
    codigo: str           # nombre del producto
    precio_unit: float    # precio por unidad
    descuento_unit: float # cantidad a descontar por unidad
    cantidad: int         # cantidad solicitada por el cliente
    notas: str            # especificaciones del producto
    duplex: bool          # dicta si el producto es a doble cara

    @property
    def importe(self) -> float:
        """
        Costo total del producto.
        """
        return (self.precio_unit - self.descuento_unit) * self.cantidad
    
    def __iter__(self) -> tuple:
        """
        Regresa iterable para alimentar las tablas de productos.
        Cantidad | Código | Especificaciones | Precio | Descuento | Importe
        """
        return iter((self.cantidad, self.codigo, self.notas, 
                     self.precio_unit, self.descuento_unit, self.importe))

#####################
# VENTANA PRINCIPAL #
#####################
class App_CrearVenta(QtWidgets.QMainWindow):
    """
    Backend para la función de crear ventas.
    TODO:
    -   mandar ticket por whatsapp o imprimir, sí o sí
    """
    def __init__(self, parent=None):
        from CrearVenta.Ui_CrearVenta import Ui_CrearVenta
        
        super().__init__()

        self.ui = Ui_CrearVenta()
        self.ui.setupUi(self)

        self.session = parent.session # conexión y usuario actual
        self.fechaHoraActual = QDateTime.currentDateTime() # fecha y hora en que se abre esta ventana
        
        LabelAdvertencia(self.ui.tabla_productos, '¡Aún no hay productos!')
        
        # cuadro de texto para los descuentos del cliente
        self.dialogoDescuentos = SpeechBubble(self)
        self.dialogoDescuentos.setGeometry(610, 28, 0, 165)
        self.dialogoDescuentos.setVisible(False)

        #### otras variables IMPORTANTES para la venta ####
        self.fechaEntrega = QDateTime.currentDateTime()
        self.productosVenta: list[ItemVenta] = []

        # datos por defecto
        self.ui.txtVendedor.setText(self.session['user'].nombre)
        self.ui.lbFecha.setText(formatDate(self.fechaEntrega))

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
        self.ui.lbCalendario.mousePressEvent = self.cambiarFecha
        self.ui.lbAgregar.mousePressEvent = self.agregarProducto
        self.ui.lbQuitar.mousePressEvent = self.quitarProducto
        
        ocultar_boton = lambda: self.ui.btDescuentosCliente.setVisible(False) \
                                or self.dialogoDescuentos.setVisible(False)
        
        self.ui.txtCliente.textChanged.connect(ocultar_boton)
        self.ui.txtCorreo.textChanged.connect(ocultar_boton)
        self.ui.txtTelefono.textChanged.connect(ocultar_boton)
        
        self.ui.tabla_productos.itemChanged.connect(self.itemChanged_handle)
        self.ui.lbRegresar.mousePressEvent = self.goHome
        self.ui.btRegistrar.clicked.connect(self.registrarCliente)
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
    def itemChanged_handle(self, item):
        if item.column() == 2:
            self.productosVenta[item.row()].notas = item.text()
    
    @requiere_admin
    def goHome(self, _):
        from Home import App_Home
        
        parent = self.parentWidget()    # QMainWindow
        new = App_Home(parent)
        parent.setCentralWidget(new)
        
    def colorearActualizar(self):
        """
        Llenar tabla con los productos seleccionados,
        luego calcular precios y actualizar los QLabel.
        """       
        # <llenar tabla>
        tabla = self.ui.tabla_productos
        tabla.setRowCount(0)

        for row, prod in enumerate(self.productosVenta):
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
        preciosConIVA = [p.importe for p in self.productosVenta]
        preciosSinIVA = [p/1.16 for p in preciosConIVA]
        impuestos = [con-sin for con, sin in zip(preciosConIVA, preciosSinIVA)]
        
        descuentos = [p.descuento_unit * p.cantidad for p in self.productosVenta]

        self.ui.lbTotal.setText(f'{sum(preciosConIVA):,.2f}')
        self.ui.lbSubtotal.setText(f'{sum(preciosSinIVA):,.2f}')
        self.ui.lbImpuestos.setText(f'{sum(impuestos):,.2f}')
        self.ui.lbDescuento.setText(f'{sum(descuentos):,.2f}')
        # </calcular precios y mostrar>
        
        tabla.resizeRowsToContents()
    
    def alternarDescuentos(self, _):
        """
        Se llama a esta función al hacer click en la foto de perfil
        del usuario. Anima el tamaño de la caja de notificaciones.
        """
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
    def cambiarFecha(self, _):
        """
        Abre ventana para cambiar la fecha de entrega.
        """
        self.new = App_FechaEntrega(self)

    def seleccionarCliente(self):
        """
        Abre ventana para seleccionar un cliente de la base de datos.
        """
        self.new = App_SeleccionarCliente(self)

    def registrarCliente(self):
        """
        Abre ventana para registrar un cliente.
        """
        from AdministrarClientes import App_EditarCliente

        self.new = App_EditarCliente(
            self,
            nombre = self.ui.txtCliente.text(),
            celular = self.ui.txtTelefono.text(),
            correo = self.ui.txtCorreo.text()
        )
        self.new.success.connect(
            lambda:    self.ui.txtCliente.setText(self.new.ui.txtNombre.text())
                    or self.ui.txtTelefono.setText(self.new.numeroTelefono)
                    or self.ui.txtCorreo.setText(self.new.ui.txtCorreo.text()))

    def agregarProducto(self, _):
        """
        Abre ventana para agregar un producto a la orden.
        """
        self.new = App_AgregarProducto(self)
        
    def quitarProducto(self, _):
        """
        Pide confirmación para eliminar un producto de la tabla.
        """
        @requiere_admin
        def accion(parent, selected):
            for row in sorted(selected, reverse=True):
                self.productosVenta.pop(row)
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
    
    def agregarDescuento(self, _):
        """
        Abre ventana para agregar un descuento a la orden si el cliente es especial.
        """
        @requiere_admin
        def accion(parent):
            self.new = App_AgregarDescuento(self)
        
        if self.ui.tabla_productos.rowCount():
            accion(self)
    
    def generarCotizacion(self):
        """
        Genera PDF con cotización de la orden actual.
        """
        if not self.ui.tabla_productos.rowCount():
            return
        
        self.new = App_EnviarCotizacion(self)

    def confirmarVenta(self):
        """
        Abre ventana para confirmar y terminar la venta.
        """
        if not self.ui.tabla_productos.rowCount():
            return
        
        qm = QtWidgets.QMessageBox

        # se confirma si existe el cliente en la base de datos
        crsr = self.session['conn'].cursor()
        nombre = self.ui.txtCliente.text().strip()
        telefono = self.ui.txtTelefono.text().strip()

        crsr.execute('''
        SELECT  *
        FROM    Clientes
        WHERE   nombre = ?
                AND telefono = ?;
        ''', (nombre, telefono))

        cliente = crsr.fetchone()

        if not cliente:
            qm.warning(self, '¡Atención!', 
                       'No se encontró el cliente en la base de datos.\n'
                       'Por favor, regístrelo como un nuevo cliente o seleccione "Público general".')
            return

        # indices para acceder a la tupla `cliente`
        id, nombre, telefono, correo, direccion, rfc, _, _ = range(8)
        
        if self.ui.tickDirectaNo.isChecked():
            if cliente[nombre] == 'Público general':
                qm.warning(self, '¡Atención!', 
                           'No se puede generar un pedido a nombre de "Público general".\n'
                           'Por favor, seleccione un cliente y/o regístrelo.')
                return

            if self.fechaHoraActual == self.fechaEntrega:
                qm.warning(self, '¡Atención!', 
                           '¡La fecha de entrega del pedido no ha sido cambiada!\n'
                           'Verifique que esta sea correcta.')
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
                    lambda:    self.ui.txtCliente.setText(self.new.ui.txtNombre.text())
                            or self.ui.txtTelefono.setText(self.new.numeroTelefono)
                            or self.ui.txtCorreo.setText(self.new.ui.txtCorreo.text()))
                
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
            ventaDatos = {
                'productos': self.productosVenta,
                'total': float(self.ui.lbTotal.text().replace(',','')),
                'fechaEntrega': self.fechaEntrega,
                'fechaCreacion': QDateTime.currentDateTime(),
                'idCliente': cliente[id],
                'metodo_pago': self.ui.btMetodoGrupo.checkedButton().text(),
                'comentarios': self.ui.txtComentarios.toPlainText().strip(),
                'requiere_factura': self.ui.tickFacturaSi.isChecked()
            }
            
            bg = DimBackground(self)
            self.new = App_ConfirmarVenta(self, ventaDatos)


#################################
# VENTANAS PARA EDITAR LA VENTA #
#################################
@con_fondo
class App_AgregarProducto(QtWidgets.QMainWindow):
    """
    Backend para la función de agregar un producto a la venta.
    """
    def __init__(self, first):
        from CrearVenta.Ui_AgregarProducto import Ui_AgregarProducto
        
        super().__init__(first)

        self.ui = Ui_AgregarProducto()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)

        self.first = first # referencia a la ventana de crear venta
        LabelAdvertencia(self.ui.tabla_seleccionar, '¡No se encontró ningún producto!')
        LabelAdvertencia(self.ui.tabla_granformato, '¡No se encontró ningún producto!')

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

        # llena la tabla de productos no gran formato
        crsr = first.session['conn'].cursor()
        
        crsr.execute('SELECT * FROM View_Productos_Simples;')
        self.all_prod = crsr.fetchall()
        
        # llena la tabla de productos gran formato
        crsr.execute('SELECT * FROM View_Gran_Formato;')
        self.all_gran = crsr.fetchall()

        # añade eventos para los botones
        self.ui.lbRegresar.mousePressEvent = self.closeEvent
        self.ui.btAgregar.clicked.connect(self.done)
        self.ui.searchBar.textChanged.connect(self.update_display)
        self.ui.tabla_seleccionar.itemDoubleClicked.connect(self.done)
        self.ui.tabWidget.currentChanged.connect(lambda: self.tabla_actual.resizeRowsToContents())
        
        self.ui.groupFiltro.buttonClicked.connect(
            lambda: self.update_display(self.ui.searchBar.text()))
        
        # validadores para datos numéricos
        regexp_numero = QRegExp(r'\d*\.?\d*')
        validador = QRegExpValidator(regexp_numero)
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
        """
        Actualiza la tabla y el contador de clientes.
        Acepta una cadena de texto para la búsqueda de clientes.
        También lee de nuevo la tabla de clientes, si se desea.
        """
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
        """
        Determina la rutina a ejecutar basándose en la pestaña actual.
        """
        current = self.ui.tabWidget.currentIndex()
        
        if current == 0:
            self.agregarSimple()
        elif current == 1:
            self.agregarGranFormato()
    
    def agregarSimple(self):
        selected = self.ui.tabla_seleccionar.selectedItems()
        
        if not selected:
            return
        
        try:
            cantidad = (float(self.ui.txtCantidad.text() or 1))
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self, 'Atención',
                '¡Algo anda mal! La cantidad debe ser un número.')
            return
        
        if cantidad <= 0:
            return
        
        # obtener información del producto
        codigo = selected[0].text()
        
        crsr = self.first.session['conn'].cursor()
        crsr.execute('SELECT id_productos FROM Productos WHERE codigo = ?;', (codigo,))
        
        idProducto, = crsr.fetchone()
        
        # obtener precio basado en cantidad
        restrict = 'AND duplex' if self.ui.checkDuplex.isChecked() else ''

        query = f'''
        SELECT * FROM (
            SELECT  FIRST 1 precio_con_iva
            FROM    Productos_Intervalos
            WHERE   id_productos = ?
                    AND desde <= ?
                    {restrict}
            ORDER   BY desde DESC)
        UNION ALL
        SELECT * FROM (
            SELECT  FIRST 1 precio_con_iva
            FROM    Productos_Intervalos
            WHERE   id_productos = ?
                    AND desde <= ?
            ORDER   BY desde DESC)
        '''
        
        try:
            crsr.execute(query, (idProducto, cantidad)*2)
            precio, = crsr.fetchone()
        except TypeError:
            QtWidgets.QMessageBox.warning(
                self, 'Atención',
                'No existe ningún precio de este producto '
                'asociado a la cantidad proporcionada.')
            return

        # insertar información del producto con cantidad y especificaciones
        codigo += ' (a doble cara)' if self.ui.checkDuplex.isChecked() else ''
        
        self.first.productosVenta.append(
            ItemVenta(
                idProducto, codigo, precio, 0.0, cantidad, 
                self.ui.txtNotas.text().strip(), self.ui.checkDuplex.isChecked()))
        
        self.first.colorearActualizar()
        self.close()
        
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
        crsr = self.first.session['conn'].cursor()
        crsr.execute('SELECT id_productos FROM Productos WHERE codigo = ?;', (codigo,))
        
        idProducto, = crsr.fetchone()
        
        # obtener precio basado en cantidad
        crsr.execute('''
        SELECT  min_ancho,
                min_alto,
                precio_m2
        FROM    Productos_Gran_Formato
        WHERE   id_productos = ?;
        ''', (idProducto,))
        
        try:
            min_ancho, min_alto, precio = crsr.fetchone()
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
        self.first.productosVenta.append(
            ItemVenta(
                idProducto, codigo, precio, 0.0, cantidad, 
                self.ui.txtNotas_2.text().strip(), False))
        
        self.first.colorearActualizar()
        self.close()


@con_fondo
class App_SeleccionarCliente(QtWidgets.QMainWindow):
    """
    Backend para la función de seleccionar un cliente de la base de datos.
    """
    def __init__(self, first):
        from CrearVenta.Ui_SeleccionarCliente import Ui_SeleccionarCliente
        
        super().__init__(first)

        self.ui = Ui_SeleccionarCliente()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)

        self.first = first # referencia a la ventana de crear venta
        
        LabelAdvertencia(self.ui.tabla_seleccionar, '¡No se encontró ningún cliente!')

        # dar formato a la tabla principal
        header = self.ui.tabla_seleccionar.horizontalHeader()

        for col in range(self.ui.tabla_seleccionar.columnCount()):
            if col == 3:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)

        # llena la tabla con todos los clientes existentes
        crsr = self.first.session['conn'].cursor()
        crsr.execute('SELECT nombre, telefono, correo, direccion, RFC FROM Clientes;')
        self.all = crsr.fetchall()

        # añade eventos para los botones
        self.ui.lbRegresar.mousePressEvent = self.closeEvent
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
        """
        Actualiza la tabla y el contador de clientes.
        Acepta una cadena de texto para la búsqueda de clientes.
        También lee de nuevo la tabla de clientes, si se desea.
        """
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
        """
        Acepta los cambios y modifica la fecha seleccionada en la ventana principal (CrearVenta).
        """
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
        crsr = self.first.session['conn'].cursor()
        crsr.execute('''
        SELECT  cliente_especial,
                descuentos
        FROM    Clientes
        WHERE   nombre = ?
                AND telefono = ?;
        ''', (nombre, telefono))
        
        especial, descuentos = crsr.fetchone()
        self.first.ui.btDescuentosCliente.setVisible(especial)
        
        if descuentos:
            txt = descuentos.strip() or 'El cliente aún no tiene descuentos.'
        else:
            txt = 'El cliente aún no tiene descuentos.'
        self.first.dialogoDescuentos.setText(txt)

        self.close()


@con_fondo
class App_FechaEntrega(QtWidgets.QMainWindow):
    """
    Backend para la función de cambiar fecha de entrega.
    """
    def __init__(self, first):
        from CrearVenta.Ui_FechaEntrega import Ui_FechaEntrega
        
        super().__init__(first)

        self.ui = Ui_FechaEntrega()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)

        self.first = first # referencia a la ventana de crear venta
        
        # datos por defecto        
        self.ui.calendario.setSelectedDate(first.fechaEntrega.date())
        self.ui.horaEdit.setTime(first.fechaEntrega.time())
        
        hoy = QDate.currentDate()
        self.ui.calendario.setMinimumDate(hoy)
        self.ui.calendario.setMaximumDate(hoy.addYears(1))

        # añade eventos para los botones
        self.ui.lbRegresar.mousePressEvent = self.closeEvent
        self.ui.btListo.clicked.connect(self.done)

        self.show()
    
    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() in {Qt.Key_Return, Qt.Key_Enter}:
            self.done()

    def done(self):
        """
        Acepta los cambios y modifica la fecha seleccionada en la ventana principal (CrearVenta).
        """
        dateTime = QDateTime(
            self.ui.calendario.selectedDate(), 
            self.ui.horaEdit.time())

        self.first.fechaEntrega = dateTime
        self.first.ui.lbFecha.setText(formatDate(dateTime))

        self.close()


@con_fondo
class App_AgregarDescuento(QtWidgets.QMainWindow):
    """
    Backend para agregar descuento a la orden.
    """
    def __init__(self, first):
        from CrearVenta.Ui_AgregarDescuento import Ui_AgregarDescuento
        
        super().__init__(first)

        self.ui = Ui_AgregarDescuento()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)

        self.first = first # referencia a la ventana de crear venta
        
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
        
        self.productosVenta = first.productosVenta

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
        self.ui.lbRegresar.mousePressEvent = self.closeEvent
        self.ui.btListo.clicked.connect(self.done)
        
        # validadores numéricos
        regexp_numero = QRegExp(r'\d*\.?\d*')
        validador = QRegExpValidator(regexp_numero)
        self.ui.txtPrecio.setValidator(validador)
        
        self.show()
    
    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() in {Qt.Key_Return, Qt.Key_Enter}:
            self.done()
        
    # ================ #
    # FUNCIONES ÚTILES #
    # ================ #
    def done(self):
        """
        Acepta los cambios e inserta descuento en la lista de productos.
        """
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
    """
    Backend para agregar descuento a la orden.
    """
    def __init__(self, first):
        from CrearVenta.Ui_Cotizacion import Ui_EnviarCotizacion
        
        super().__init__(first)

        self.ui = Ui_EnviarCotizacion()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)

        self.first = first # referencia a la ventana de crear venta

        # añade eventos para los botones
        self.ui.lbRegresar.mousePressEvent = self.closeEvent
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
        
        for prod in self.first.productosVenta:
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
                     for prod in self.first.productosVenta]
        
        vendedor = self.first.ui.txtVendedor.text()
        
        generarTicketPresupuesto(productos, vendedor)
        self.close()


class App_ConfirmarVenta(QtWidgets.QMainWindow):
    """
    Backend para la ventana de finalización de venta.
    """
    def __init__(self, first, ventaDatos):
        from CrearVenta.Ui_ConfirmarVenta import Ui_ConfirmarVenta
        
        super().__init__(first)

        self.ui = Ui_ConfirmarVenta()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)
        
        # datos de la ventana padre
        session = first.session
        esDirecta = first.ui.tickDirectaSi.isChecked()
        
        self.session = session
        self.ventaDatos = ventaDatos

        # total de la compra y precio a pagarse ahora mismo
        self.total = ventaDatos['total']
        self.paraPagar = self.total if esDirecta else self.total/2

        # dar formato a la tabla principal
        header = self.ui.tabla_productos.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        for col in range(self.ui.tabla_productos.columnCount()):
            if col == 2:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)

        # llenar de productos la tabla
        tabla = self.ui.tabla_productos
        tabla.setRowCount(0)

        for row, prod in enumerate(ventaDatos['productos']):
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

        # si la venta es directa, ocultar los widgets para apartados
        if esDirecta:
            for w in [self.ui.boxFechaEntrega,
                      self.ui.lbAnticipo1,
                      self.ui.lbAnticipo2,
                      self.ui.txtAnticipo]:
                w.hide()
            
            fechaEntrega = ventaDatos['fechaCreacion']
        else:
            fechaEntrega = ventaDatos['fechaEntrega']

        # crear nuevas entradas en la base de datos
        conn = session['conn']
        crsr = conn.cursor()

        try:
            ventas_db_parametros = (
                ventaDatos['idCliente'],
                session['user'].id,
                ventaDatos['fechaCreacion'].toSecsSinceEpoch(),
                fechaEntrega.toSecsSinceEpoch(),
                ventaDatos['comentarios'].strip(),
                ventaDatos['metodo_pago'],
                int(ventaDatos['requiere_factura']),
                'No terminada'
            )
        
            crsr.execute('''
            INSERT INTO Ventas (
                id_clientes, id_usuarios, fecha_hora_creacion, 
                fecha_hora_entrega, comentarios, metodo_pago, 
                requiere_factura, estado
            ) 
            VALUES 
                (?,?,?,?,?,?,?,?)
            RETURNING
                id_ventas;
            ''', ventas_db_parametros)

            self.id_ventas, = crsr.fetchone() # ID de la venta que se acaba de insertar
            productos = ventaDatos['productos']

            Ventas_Detallado_db_parametros = [(
                self.id_ventas,
                int(prod.id),
                float(prod.cantidad),
                float(prod.precio_unit),
                float(prod.descuento_unit),
                prod.notas,
                prod.duplex
            ) for prod in productos]

            crsr.executemany('''
            INSERT INTO Ventas_Detallado (
                id_ventas, id_productos, cantidad, precio, 
                descuento, especificaciones, duplex
            ) 
            VALUES 
                (?,?,?,?,?,?,?);
            ''', Ventas_Detallado_db_parametros)

            conn.commit()
        except fdb.Error as err:
            conn.rollback()

            WarningDialog(self, '¡Hubo un error!', str(err))
            return

        # modifica datos de venta
        crsr.execute('''
        SELECT  nombre,
                telefono,
                correo
        FROM    Clientes
        WHERE   id_clientes = ?;
        ''', (ventaDatos['idCliente'],))

        nombre, correo, telefono = crsr.fetchone()

        self.ui.lbFolio.setText(f'{self.id_ventas}')
        self.ui.txtCliente.setText(nombre)
        self.ui.txtCorreo.setText(correo)
        self.ui.txtTelefono.setText(telefono)
        self.ui.txtCreacion.setText(formatDate(ventaDatos['fechaCreacion']))
        self.ui.txtEntrega.setText(formatDate(ventaDatos['fechaEntrega']))
        self.ui.lbTotal.setText(f'{ventaDatos["total"]:,.2f}')
        self.ui.txtAnticipo.setText(f'{self.paraPagar:.2f}')
        
        # validadores para datos numéricos
        regexp_numero = QRegExp(r'\d*\.?\d*')
        validador = QRegExpValidator(regexp_numero)
        
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
    
    def closeEvent(self, event):
        event.ignore()
    
    # ================
    # FUNCIONES ÚTILES
    # ================
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
    
    def cambiarAnticipo(self, txt):
        """
        Cambiar el anticipo pagado por el cliente.
        """
        try:
            self.paraPagar = float(txt)
        except ValueError:
            self.paraPagar = self.total/2  # regresar al 50%
            self.ui.txtAnticipo.setText(f'{self.paraPagar:.2f}')
        
        self.calcularCambio(self.ui.txtPago.text())
    
    def done(self):
        """
        Acepta los cambios y modifica la fecha seleccionada en la ventana principal (CrearVenta).
        """
        esDirecta = not self.ui.boxFechaEntrega.isVisible()
        
        try:
            pago = float(self.ui.txtPago.text())
        except ValueError:
            pago = 0.
        
        pagoAceptado = pago >= self.paraPagar if self.ventaDatos['metodo_pago'] == 'Efectivo' \
                       else pago == self.paraPagar
        
        if not pagoAceptado or not (self.total/2 <= self.paraPagar <= self.total):
            return
        
        conn = self.session['conn']
        crsr = conn.cursor()

        try:
            # cambiar el estado de la venta a 'Terminada' o 'Recibido xx.xx'
            estado = 'Terminada' if esDirecta else f'Recibido {self.paraPagar:.2f}'
            
            crsr.execute('''
            UPDATE  Ventas
            SET     estado = ?,
                    recibido = ?
            WHERE   id_ventas = ?;
            ''', (estado, pago, self.id_ventas))
            
            # registrar ingreso (sin cambio) en caja
            hoy = QDateTime.currentDateTime().toSecsSinceEpoch()
            metodo = self.ventaDatos['metodo_pago']
            
            caja_db_parametros = [(
                hoy,
                pago,
                f'Pago de venta con folio {self.id_ventas}',
                metodo,
                self.session['user'].id
            )]
            
            # registrar egreso (cambio) en caja
            if (cambio := pago - self.paraPagar):
                caja_db_parametros.append((
                    hoy,
                    -cambio,
                    f'Cambio de venta con folio {self.id_ventas}',
                    metodo,
                    self.session['user'].id
                ))
            
            if pago > 0.:
                crsr.executemany('''
                INSERT INTO Caja (
                    fecha_hora, monto,
                    descripcion, metodo, id_usuarios
                )
                VALUES
                    (?,?,?,?,?);
                ''', caja_db_parametros)

            conn.commit()
        except fdb.Error as err:
            conn.rollback()

            WarningDialog(self, '¡Hubo un error!', str(err))
            return

        # abrir pregunta
        qm = QtWidgets.QMessageBox

        if not esDirecta:
            qm.information(self, 'Éxito', 'Venta terminada. Se imprimirá ahora la orden de compra.')
            generarOrdenCompra(conn.cursor(), self.id_ventas)
        else:
            box = qm(qm.Icon.Question, 'Éxito',
                     'Venta terminada. ¡Recuerde ofrecer el ticket de compra! ¿Desea imprimirlo?',
                     qm.Yes | qm.No, self)
            
            #box.button(qm.Yes).setText('Imprimir ticket')
            #box.button(qm.No).setText('Enviar por WhatsApp')
            ret = box.exec()
            
            if ret == qm.Yes:
                generarTicketCompra(conn.cursor(), self.id_ventas)
            else:
                print("enviar PDF por wa")
        
        self.goHome()
    
    def abortar(self, _):
        @requiere_admin
        def accion(parent):
            try:
                conn = self.session['conn']
                crsr = conn.cursor()
                
                crsr.execute('''
                UPDATE  Ventas
                SET     estado = 'Cancelada'
                WHERE   id_ventas = ?;
                ''', (self.id_ventas,))

                conn.commit()
                
                self.goHome()
            except fdb.Error as err:
                conn.rollback()
                WarningDialog(self, '¡Hubo un error!', str(err))
        
        qm = QtWidgets.QMessageBox
        
        ret = qm.question(self, 'Atención', 
                          '¿Desea cancelar la venta? Esta acción no puede deshacerse.',
                          qm.Yes | qm.No)
        if ret == qm.Yes:
            accion(self)
    
    def goHome(self):
        """
        Cierra la ventana y crea otra venta.
        """
        from Home import App_Home
        
        parent = self.parentWidget().parentWidget() # QMainWindow, ventana principal
        new = App_Home(parent)
        parent.setCentralWidget(new)
        
        self.close()
