from PySide6 import QtWidgets
from PySide6.QtGui import QFont, QColor, QIcon
from PySide6.QtCore import Qt, Signal, QMutex

from sql import ManejadorInventario, ManejadorProductos
from utils import Moneda
from utils.mydataclasses import ItemVenta, ItemGranFormato
from utils.mydecorators import fondo_oscuro, run_in_thread
from utils.myinterfaces import InterfazFiltro
from utils.myutils import *
from utils.mywidgets import LabelAdvertencia


#####################
# VENTANA PRINCIPAL #
#####################
class App_AdministrarProductos(QtWidgets.QWidget):
    """ Backend para la ventana de administración de productos. """
    rescanned = Signal()

    def __init__(self, conn, user):
        from ui.Ui_AdministrarProductos import Ui_AdministrarProductos

        super().__init__()
        self.ui = Ui_AdministrarProductos()
        self.ui.setupUi(self)

        self.mutex = QMutex()

        LabelAdvertencia(self.ui.tabla_productos, '¡No se encontró ningún producto!')

        # guardar conexión y usuario como atributos
        self.conn = conn
        self.user = user

        self.all = []

        # añadir menú de opciones al botón para filtrar
        self.filtro = InterfazFiltro(self.ui.btFiltrar, self.ui.searchBar,
            [('Código', 1),
             ('Descripción', 2)])
        self.filtro.cambiado.connect(self.update_display)

        # eventos para los botones
        self.ui.btAgregar.clicked.connect(self.agregarProducto)
        self.ui.btEditar.clicked.connect(self.editarProducto)
        self.ui.btEliminar.clicked.connect(self.quitarProducto)
        self.ui.btRegresar.clicked.connect(self.goHome)
        self.rescanned.connect(self.update_display)

        self.ui.searchBar.textChanged.connect(self.update_display)

        self.ui.tabla_productos.configurarCabecera(lambda col: col not in {1, 2, 3})

    def showEvent(self, event):
        self.rescan_update()

    def resizeEvent(self, event):
        if self.isVisible():
            self.ui.tabla_productos.resizeRowsToContents()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @run_in_thread
    def rescan_update(self):
        if not self.mutex.try_lock():
            return

        self.ui.lbContador.setText('Recuperando información...')

        manejador = ManejadorProductos(self.conn)
        self.all = manejador.obtenerVista('view_all_productos') or []
        self.ui.lbContador.setText(f'{len(self.all)} productos en la base de datos.')

        self.rescanned.emit()

    def update_display(self):
        """ Actualiza la tabla y el contador de productos.
            Acepta una cadena de texto para la búsqueda de productos.
            También lee de nuevo la tabla de productos, si se desea. """
        tabla = self.ui.tabla_productos
        tabla.setRowCount(0)

        bold = QFont()
        bold.setBold(True)

        if txt_busqueda := self.ui.searchBar.text().strip():
            found = [c for c in self.all
                     if son_similar(txt_busqueda, c[self.filtro.idx])]
        else:
            found = self.all

        tabla.setRowCount(len(found))

        for row, item in enumerate(found):
            for col, dato in enumerate(item):
                if isinstance(dato, float):
                    cell = f'${dato:,.2f}'
                else:
                    cell = str(dato or '')

                widget = QtWidgets.QTableWidgetItem(cell)
                tabla.setItem(row, col, widget)

            tabla.item(row, 1).setFont(bold)

            # resaltar si la utilidad es nula o negativa
            if item[-1] <= 0:
                color = QColor(ColorsEnum.ROJO)
                tabla.item(row, 7).setBackground(color)

        tabla.resizeRowsToContents()
        self.mutex.unlock()

    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def agregarProducto(self):
        widget = App_RegistrarProducto(self, self.conn, self.user)
        widget.success.connect(self.rescan_update)

    def editarProducto(self):
        if selected := self.ui.tabla_productos.selectedItems():
            widget = App_EditarProducto(self, self.conn, self.user, selected[0].text())
            widget.success.connect(self.rescan_update)

    def quitarProducto(self):
        """ Elimina un producto de la base de datos.
            Primero se verifica si hay elementos que este utilizan. """
        try:
            id_productos = self.ui.tabla_productos.selectedItems()[0].text()
        except IndexError:
            return

        qm = QtWidgets.QMessageBox
        manejador = ManejadorProductos(self.conn, '¡No se pudo eliminar el producto!')

        if manejador.obtenerRelacionVentas(id_productos):
            qm.warning(self, 'Atención',
                       'No se puede eliminar este producto debido '
                       'a que hay ventas que lo incluyen.')
            return

        # abrir pregunta
        ret = qm.question(self, 'Atención',
                          'El producto seleccionado se eliminará de la base de datos. '
                          '¿Desea continuar?')

        if ret == qm.Yes and manejador.eliminarProducto(id_productos):
            qm.information(self, 'Éxito', 'Se eliminó el producto seleccionado.')
            self.rescan_update()

    def goHome(self):
        """ Cierra la ventana y regresa al inicio. """
        self.parentWidget().goHome()


#################################
# VENTANAS USADAS POR EL MÓDULO #
#################################
class Base_VisualizarProductos(QtWidgets.QWidget):
    dataChanged = Signal()  # señal para actualizar tabla en hilo principal

    def __init__(self, parent, conn, *, extern: bool = False):
        from ui.Ui_VisualizadorProductos import Ui_VisualizadorProductos

        super().__init__(None if extern else parent)

        self.ui = Ui_VisualizadorProductos()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())

        self.warnings = True

        LabelAdvertencia(self.ui.tabla_seleccionar, '¡No se encontró ningún producto!')
        LabelAdvertencia(self.ui.tabla_granformato, '¡No se encontró ningún producto!')

        # guardar conexión, usuario y un manejador de DB como atributos
        self.conn = conn
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
        self.event_reader = Runner(self.startEvents)
        self.event_reader.start()
        self.dataChanged.connect(self.rescan_display)

    def showEvent(self, event):
        self.rescan_display()

    def closeEvent(self, event):
        # no recomendado generalmente para terminar hilos, sin embargo,
        # esta vez se puede hacer así al no ser una función crítica.
        self.event_reader.stop()
        event.accept()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @property
    def tabla_actual(self):
        return [self.ui.tabla_seleccionar, self.ui.tabla_granformato][self.ui.tabWidget.currentIndex()]

    def startEvents(self):
        # eventos de Firebird para escuchar cambios en tabla productos
        self.event_conduit = self.conn.event_conduit(['cambio_productos'])
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

        # obtener información del producto
        codigo = selected[0].text()
        manejador = ManejadorProductos(self.conn)

        idProducto = manejador.obtenerIdProducto(codigo)
        nombre_ticket = manejador.obtenerNombreParaTicket(codigo)
        min_m2, precio_m2 = manejador.obtenerGranFormato(idProducto)

        # si el alto del producto sobrepasa el ancho del material, quiere decir
        # que no se pudo imprimir de forma normal; por lo tanto, cobrar sobrante.
        desc_unit = 0.

        if alto_producto > ancho_material:
            # sobrante_ancho = ancho_material - ancho_producto
            # descuento_sobre_total = manejador.obtenerDescuentoSobrante(idProducto, sobrante_ancho)
            # desc_unit = precio_m2 * descuento_sobre_total
            ancho_producto = ancho_material

        # insertar información del producto con cantidad y especificaciones
        return ItemGranFormato(
            idProducto, codigo, nombre_ticket, precio_m2, desc_unit, ancho_producto * alto_producto,
            self.ui.txtNotas_2.text().strip(), min_m2)

    def rescan_display(self):
        """ Lee de nuevo las tablas de productos y actualiza tablas. """
        self.all_prod = self.manejador.obtenerVista('view_productos_simples')
        self.all_gran = self.manejador.obtenerVista('view_gran_formato')
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


class App_ConsultarPrecios(Base_VisualizarProductos):
    """ Backend para el módulo de consultar precios.
        No se puede cerrar hasta cerrar por completo el sistema. """

    def __init__(self, parent, conn):
        super().__init__(parent, conn, extern=True)

        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint)
        self.setWindowTitle('Consultar precios')
        self.setWindowIcon(QIcon(':img/icon.ico'))

        self.warnings = False

        self.ui.label.setText('Consultar precios')
        self.ui.btRegresar.setCursor(Qt.CursorShape.ArrowCursor)
        self.ui.btRegresar.setIcon(QIcon(':/img/resources/images/package.png'))

        self.ui.btAgregar.hide()
        self.ui.groupBoxEspecGran.hide()
        self.ui.groupBoxEspecSimple.hide()

        # eventos para tabla de productos simples
        self.ui.tabla_seleccionar.itemClicked.connect(self.mostrarSimple)
        self.ui.txtCantidad.textChanged.connect(self.mostrarSimple)
        self.ui.checkDuplex.toggled.connect(self.mostrarSimple)

        # eventos para tabla de gran formato
        self.ui.tabla_granformato.itemClicked.connect(self.medidasHandle)
        self.ui.txtAnchoMaterial.textChanged.connect(self.medidasHandle)
        self.ui.txtAltoMaterial.textChanged.connect(self.medidasHandle)
        # lo demás está en la superclase :p

        self.showMinimized()

    def closeEvent(self, event):
        if event.spontaneous():
            event.ignore()
        else:
            super().closeEvent(event)

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def mostrarSimple(self):
        if item := self.generarSimple():
            self.ui.lbTotalSimple.setText(f'Total: ${Moneda(item.importe)}')
        else:
            self.ui.lbTotalSimple.setText('Total: ...')

    def medidasHandle(self):
        if item := self.generarGranFormato():
            self.ui.lbTotalGran.setText(f'Total: ${Moneda(item.importe)}')
        else:
            self.ui.lbTotalGran.setText('Total: ...')


@fondo_oscuro
class Base_EditarProducto(QtWidgets.QWidget):
    """ Backend para la ventana para editar un producto de la base de datos. """
    MENSAJE_EXITO: str
    MENSAJE_ERROR: str

    success = Signal()

    def __init__(self, parent, conn, user):
        from ui.Ui_EditarProducto import Ui_EditarProducto

        super().__init__(parent)

        self.ui = Ui_EditarProducto()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)

        # guardar conexión y usuario como atributos
        self.conn = conn
        self.user = user

        # formato tabla de precios
        header = self.ui.tabla_precios.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)

        # eventos para botones
        self.ui.btAceptar.clicked.connect(self.done)
        self.ui.btAgregar.clicked.connect(self.agregarProductoALista)

        self.ui.btAgregarIntervalo.clicked.connect(
            lambda: self.agregarIntervalo(row=self.ui.tabla_precios.rowCount()))
        self.ui.btEliminarIntervalo.clicked.connect(self.quitarIntervalo)

        self.ui.btRegresar.clicked.connect(self.close)

        self.show()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    ####################
    # FUNCIONES ÚTILES #
    ####################
    @property
    def categoriaActual(self):
        return ['S', 'G'][self.ui.tabWidget.currentIndex()]

    def agregarIntervalo(self, row: int, desde: float = 0.,
                         precio: float = 0., duplex: bool = False):
        """ Agrega entrada a la tabla de precios. """
        self.ui.tabla_precios.insertRow(row)

        cell = QtWidgets.QTableWidgetItem(f'{desde:,.2f}' if desde else '')
        cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ui.tabla_precios.setItem(row, 0, cell)

        cell = QtWidgets.QTableWidgetItem(f'{precio:,.2f}' if precio else '')
        cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ui.tabla_precios.setItem(row, 1, cell)

        self.ui.tabla_precios.setCellWidget(row, 2, ItemAuxiliar(duplex))

    def quitarIntervalo(self):
        tabla = self.ui.tabla_precios

        if idx := tabla.selectedIndexes():
            row = idx[0].row()
        else:
            row = tabla.rowCount() - 1
        tabla.removeRow(row)

    def agregarProductoALista(self, nombre: str = '', cantidad: int = 1):
        # crear widget y agregar a la lista
        nuevo = WidgetElemento()

        # llenar caja de opciones con elementos del inventario
        manejador = ManejadorInventario(self.conn)
        elementos = manejador.obtenerListaNombres()
        nuevo.boxElemento.addItems([nombre for nombre, in elementos])

        # modificar valores a los de la base de datos
        nuevo.elementoSeleccionado = nombre
        nuevo.cantidadElemento = cantidad

        self.ui.layoutScroll.addWidget(nuevo)

    def obtenerParametrosProductos(self):
        """ Parámetros para la tabla productos. """
        return tuple(v or None for v in (
            self.ui.txtCodigo.text().strip(),
            self.ui.txtDescripcion.toPlainText().strip(),
            self.ui.txtNombre.text(),
            self.categoriaActual))

    def obtenerParametrosProdUtilizaInv(self):
        """ Parámetros para la tabla productos_utiliza_inventario. """
        wdg: list[WidgetElemento] = self.ui.scrollAreaLista.children()[1:]

        PUI_db_parametros = []
        manejador = ManejadorInventario(self.conn)

        for elemento in wdg:
            nombre, cantidad = elemento.elementoSeleccionado, elemento.cantidadElemento
            if not nombre or cantidad < 1:
                return None

            id_inventario, = manejador.obtenerIdInventario(nombre)
            PUI_db_parametros.append((id_inventario, cantidad))

        return PUI_db_parametros

    def obtenerParametrosProdIntervalos(self):
        """ Parámetros para la tabla productos_intervalos. """
        tabla = self.ui.tabla_precios
        Prod_db_parametros = []

        if not self.ui.tabla_precios.rowCount():
            QtWidgets.QMessageBox.warning(
                self, 'Atención',
                '¡La tabla de precios se encuentra vacía!')
            return None

        for row in range(tabla.rowCount()):
            desde = tabla.item(row, 0).text().replace(',', '')
            precio = tabla.item(row, 1).text().replace(',', '')
            duplex: ItemAuxiliar = tabla.cellWidget(row, 2)

            try:
                Prod_db_parametros.append((float(desde), float(precio), duplex.isChecked))
            except ValueError:
                QtWidgets.QMessageBox.warning(
                    self, 'Atención',
                    '¡Verifique que los datos numéricos sean correctos!')
                return None

        return Prod_db_parametros

    def obtenerParametrosProdGranFormato(self):
        """ Parámetros para la tabla productos_gran_formato. """
        try:
            return (float(self.ui.txtMinM2.text()),
                    float(self.ui.txtPrecio.text()))
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self, 'Atención',
                '¡Verifique que los datos numéricos sean correctos!')
            return None

    def done(self):
        """ Función donde se registrará o actualizará producto. """
        #### obtención de parámetros ####
        productos_db_parametros = self.obtenerParametrosProductos()
        PUI_db_parametros = self.obtenerParametrosProdUtilizaInv()

        if self.categoriaActual == 'S':
            precios_db_parametros = self.obtenerParametrosProdIntervalos()
        else:
            precios_db_parametros = self.obtenerParametrosProdGranFormato()

        if any(params is None for params in (productos_db_parametros,
                                             PUI_db_parametros,
                                             precios_db_parametros)):
            return

        # ejecuta internamente un fetchone, por lo que se desempaca luego
        result = self.insertar_o_modificar(productos_db_parametros)
        if not result:
            return

        idx, = result
        manejador = ManejadorProductos(self.conn, self.MENSAJE_ERROR)

        # transacción principal, se checa si cada operación fue exitosa
        if not (
                manejador.eliminarProdUtilizaInv(idx)
                and manejador.insertarProdUtilizaInv(idx, PUI_db_parametros)
                and manejador.eliminarPrecios(idx)
        ):
            return

        if self.categoriaActual == 'S':
            result = manejador.insertarProductosIntervalos(idx, precios_db_parametros)
        else:
            result = manejador.insertarProductoGranFormato(idx, precios_db_parametros)

        if result:
            QtWidgets.QMessageBox.information(self, 'Éxito', self.MENSAJE_EXITO)
            self.success.emit()
            self.close()

    def insertar_o_modificar(self, productos_db_parametros: tuple) -> tuple:
        """ Devuelve tupla con índice del producto registrado o editado. """
        raise NotImplementedError('BEIS CLASSSSSSS')


class App_RegistrarProducto(Base_EditarProducto):
    """ Backend para la ventana para insertar un producto a la base de datos. """
    MENSAJE_EXITO = '¡Se registró el producto!'
    MENSAJE_ERROR = '¡No se pudo registrar el producto!'

    def __init__(self, parent, conn, user):
        super().__init__(parent, conn, user)

        self.ui.lbTitulo.setText('Registrar producto')
        self.ui.btAceptar.setText(' Registrar producto')
        self.ui.btAceptar.setIcon(QIcon(':/img/resources/images/plus.png'))

    def insertar_o_modificar(self, productos_db_parametros):
        manejador = ManejadorProductos(self.conn, self.MENSAJE_ERROR)
        return manejador.insertarProducto(productos_db_parametros)


class App_EditarProducto(Base_EditarProducto):
    """ Backend para la ventana para editar un producto de la base de datos. """
    MENSAJE_EXITO = '¡Se editó el producto!'
    MENSAJE_ERROR = '¡No se pudo editar el producto!'

    def __init__(self, parent, conn, user, idx: int):
        super().__init__(parent, conn, user)

        self.idx = idx  # id del elemento a editar

        manejador = ManejadorProductos(self.conn)

        _, codigo, descripcion, abreviado, categoria \
            = manejador.obtenerProducto(idx)

        self.ui.txtCodigo.setText(codigo)
        self.ui.txtDescripcion.setPlainText(descripcion)
        self.ui.txtNombre.setText(abreviado)

        if categoria == 'S':
            self.ui.tabWidget.setCurrentIndex(0)

            # agregar intervalos de precios a la tabla
            precios = manejador.obtenerTablaPrecios(idx)

            for row, (desde, precio, duplex) in enumerate(precios):
                self.agregarIntervalo(row, desde, precio, duplex)
        elif categoria == 'G':
            self.ui.tabWidget.setCurrentIndex(1)

            min_m2, precio = manejador.obtenerGranFormato(idx)

            self.ui.txtMinM2.setText(f'{min_m2:,.2f}')
            self.ui.txtPrecio.setText(f'{precio:,.2f}')

        # agregar elementos de la segunda página
        for nombre, cantidad in manejador.obtenerUtilizaInventario(idx):
            self.agregarProductoALista(nombre, cantidad)

    def insertar_o_modificar(self, productos_db_parametros):
        manejador = ManejadorProductos(self.conn, self.MENSAJE_ERROR)
        return manejador.editarProducto(self.idx, productos_db_parametros)


#########################################
# WIDGETS PERSONALIZADOS PARA EL MÓDULO #
#########################################
class WidgetElemento(QtWidgets.QWidget):
    def __init__(self):
        from ui.Ui_WidgetElemento import Ui_WidgetElemento
        
        super().__init__()
        self.ui = Ui_WidgetElemento()
        self.ui.setupUi(self)
        self.setMinimumSize(self.size())
        
        self.ui.btEliminar.clicked.connect(lambda: self.setParent(None))

        # guardar widgets importantes como atributos
        self.boxElemento = self.ui.boxElemento

    @property
    def elementoSeleccionado(self):
        return self.ui.boxElemento.currentText()
    
    @elementoSeleccionado.setter
    def elementoSeleccionado(self, val: str):
        self.ui.boxElemento.setCurrentText(val)
        
    @property
    def cantidadElemento(self):
        return self.ui.boxProductoUtiliza.value()
    
    @cantidadElemento.setter
    def cantidadElemento(self, val: int):
        self.ui.boxProductoUtiliza.setValue(val)


class ItemAuxiliar(QtWidgets.QWidget):
    def __init__(self, duplex: bool = False):
        super().__init__()

        self.setMinimumHeight(32)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        checkbox = QtWidgets.QCheckBox(self)
        checkbox.setChecked(duplex)
        layout.addWidget(checkbox)

        # guardar widgets importantes como atributos
        self.checkBox = checkbox

    @property
    def isChecked(self):
        return self.checkBox.isChecked()
