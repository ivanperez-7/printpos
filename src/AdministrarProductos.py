import fdb

from PySide6 import QtWidgets
from PySide6.QtGui import QFont, QColor, QPixmap, QIcon, QRegularExpressionValidator
from PySide6.QtCore import Qt, QRegularExpression, Signal

from utils.databasemanagers import ManejadorInventario, ManejadorProductos
from utils.mydecorators import con_fondo
from utils.myinterfaces import InterfazFiltro
from utils.myutils import ColorsEnum, son_similar
from utils.mywidgets import LabelAdvertencia, VentanaPrincipal


#####################
# VENTANA PRINCIPAL #
#####################
class App_AdministrarProductos(QtWidgets.QMainWindow):
    """ Backend para la ventana de administración de productos. """
    
    def __init__(self, parent: VentanaPrincipal):
        from ui.Ui_AdministrarProductos import Ui_AdministrarProductos
        
        super().__init__()
        
        self.ui = Ui_AdministrarProductos()
        self.ui.setupUi(self)
        
        LabelAdvertencia(self.ui.tabla_productos, '¡No se encontró ningún producto!')
        
        # guardar conexión y usuario como atributos
        self.conn = parent.conn
        self.user = parent.user
        
        # añadir menú de opciones al botón para filtrar
        self.filtro = InterfazFiltro(self.ui.btFiltrar, [
            ('Código', 'código', 1),
            ('Descripción', 'descripción', 2)
        ])
        self.filtro.filtroCambiado.connect(
            lambda txt: self.ui.searchBar.setPlaceholderText(f'Busque producto por {txt}...')
                        or self.update_display())
        
        # eventos para los botones
        self.ui.btAgregar.clicked.connect(self.agregarProducto)
        self.ui.btEditar.clicked.connect(self.editarProducto)
        self.ui.btEliminar.clicked.connect(self.quitarProducto)
        self.ui.btRegresar.clicked.connect(self.goHome)
        
        self.ui.searchBar.textChanged.connect(lambda: self.update_display())
        
        self.ui.tabla_productos.configurarCabecera(lambda col: col not in [1, 2, 3])
    
    def showEvent(self, event):
        self.update_display(rescan=True)
    
    def resizeEvent(self, event):
        if self.isVisible():
            self.ui.tabla_productos.resizeRowsToContents()
    
    # ==================
    #  FUNCIONES ÚTILES
    # ==================    
    def update_display(self, rescan: bool = False):
        """ Actualiza la tabla y el contador de productos.
            Acepta una cadena de texto para la búsqueda de productos.
            También lee de nuevo la tabla de productos, si se desea. """
        if rescan:
            manejador = ManejadorProductos(self.conn)
            self.all = manejador.obtenerTablaPrincipal() or []
            self.ui.lbContador.setText(f'{len(self.all)} productos en la base de datos.')
        
        tabla = self.ui.tabla_productos
        tabla.setRowCount(0)
        
        bold = QFont()
        bold.setBold(True)
        
        # texto introducido por el usuario
        txt_busqueda = self.ui.searchBar.text().strip()
        
        found = self.all if not txt_busqueda else \
            filter(
                lambda c: c[self.filtro.filtro]
                          and son_similar(txt_busqueda, c[self.filtro.filtro]),
                self.all)
        
        for row, item in enumerate(found):
            tabla.insertRow(row)
            
            for col, dato in enumerate(item):
                if isinstance(dato, float):
                    cell = f'{dato:,.2f}'
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
    
    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def agregarProducto(self):
        self.new = App_RegistrarProducto(self)
        self.new.success.connect(
            lambda: self.update_display(rescan=True))
    
    def editarProducto(self):
        selected = self.ui.tabla_productos.selectedItems()
        
        if selected:
            self.new = App_EditarProducto(self, selected[0].text())
            self.new.success.connect(
                lambda: self.update_display(rescan=True))
    
    def quitarProducto(self):
        """ Elimina un producto de la base de datos.
            Primero se verifica si hay elementos que este utilizan. """
        try:
            id_productos = self.ui.tabla_productos.selectedItems()[0].text()
        except IndexError:
            return
        
        qm = QtWidgets.QMessageBox
        
        manejador = ManejadorProductos(self.conn, '¡No se pudo eliminar el producto!')
        result = manejador.obtenerRelacionVentas(id_productos)
        
        if result:
            qm.warning(self, 'Atención',
                       'No se puede eliminar este producto debido '
                       'a que hay ventas que lo incluyen.')
            return
        
        # abrir pregunta
        ret = qm.question(self, 'Atención',
                          'El producto seleccionado se eliminará de la base de datos. '
                          '¿Desea continuar?')
        
        if ret != qm.Yes:
            return
        
        if not manejador.eliminarProducto(id_productos):
            return
        
        qm.information(self, 'Éxito', 'Se eliminó el producto seleccionado.')
        self.update_display(rescan=True)
    
    def goHome(self):
        """ Cierra la ventana y regresa al inicio. """
        from Home import App_Home
        
        parent = self.parentWidget()  # QMainWindow
        new = App_Home(parent)
        parent.setCentralWidget(new)


#################################
# VENTANAS USADAS POR EL MÓDULO #
#################################
@con_fondo
class Base_EditarProducto(QtWidgets.QMainWindow):
    """ Backend para la ventana para editar un producto de la base de datos. """
    MENSAJE_EXITO: str
    MENSAJE_ERROR: str
    
    success = Signal()
    
    def __init__(self, first: App_AdministrarProductos):
        from ui.Ui_EditarProducto import Ui_EditarProducto
        
        super().__init__(first)
        
        self.ui = Ui_EditarProducto()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)
        
        # guardar conexión y usuario como atributos
        self.conn = first.conn
        self.user = first.user
        
        # formato tabla de precios
        header = self.ui.tabla_precios.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        
        # eventos para botones
        self.ui.btAceptar.clicked.connect(self.done)
        self.ui.btAgregar.clicked.connect(lambda: self.agregarProductoALista())
        
        self.ui.btAgregarIntervalo.clicked.connect(
            lambda: self.agregarIntervalo(row=self.ui.tabla_precios.rowCount()))
        self.ui.btEliminarIntervalo.clicked.connect(self.quitarIntervalo)
        
        self.ui.btRegresar.clicked.connect(self.close)
        
        self.show()
    
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
        
        if (idx := tabla.selectedIndexes()):
            row = idx[0].row()
        else:
            row = tabla.rowCount() - 1
        tabla.removeRow(row)
    
    def agregarProductoALista(self, nombre: str = '', cantidad: int = 1):
        # crear widget y agregar a la lista
        nuevo = WidgetElemento()
        
        # evento para eliminar la entrada
        nuevo.btEliminar.clicked.connect(
            lambda: self.ui.layoutScroll.removeWidget(nuevo)
                    or nuevo.setParent(None))
        
        # validador para datos numéricos
        regexp_numero = QRegularExpression(r'\d*\.?\d*')
        validador = QRegularExpressionValidator(regexp_numero)
        nuevo.txtProductoUtiliza.setValidator(validador)
        
        # llenar caja de opciones con elementos del inventario
        manejador = ManejadorInventario(self.conn)
        elementos = manejador.obtenerListaNombres()
        nuevo.boxElemento.addItems([nombre for nombre, in elementos])
        
        # modificar valores a los de la base de datos
        nuevo.boxElemento.setCurrentText(nombre)
        nuevo.txtProductoUtiliza.setText(f'{cantidad}')
        
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
        elementos: list[WidgetElemento] = self.ui.scrollAreaLista.children()[1:]
        
        try:
            elementos = [(e.elementoSeleccionado, float(e.cantidadElemento))
                         for e in elementos]
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self, 'Atención',
                '¡Verifique que los datos numéricos sean correctos!')
            return None
        
        PUI_db_parametros = []
        manejador = ManejadorInventario(self.conn)
        
        for nombre, cantidad in elementos:
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
        qm = QtWidgets.QMessageBox
        
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
        result = self.ejecutarOperacion(self.conn, productos_db_parametros)
        if not result:
            return
        
        idx, = result
        manejador = ManejadorProductos(self.conn, self.MENSAJE_ERROR)
        
        # transacción principal, se checa si cada operación fue exitosa
        if not manejador.eliminarProdUtilizaInv(idx):
            return
        if not manejador.insertarProdUtilizaInv(idx, PUI_db_parametros):
            return
        if not manejador.eliminarPrecios(idx):
            return
        
        if self.categoriaActual == 'S':
            result = manejador.insertarProductosIntervalos(idx, precios_db_parametros)
        else:
            result = manejador.insertarProductoGranFormato(idx, precios_db_parametros)
        
        if not result:
            return
        
        qm.information(self, 'Éxito', self.MENSAJE_EXITO)
        self.success.emit()
        self.close()
    
    def ejecutarOperacion(self, conn: fdb.Connection, params: tuple) -> tuple:
        """ Devuelve tupla con índice del producto registrado o editado. """
        pass


class App_RegistrarProducto(Base_EditarProducto):
    """ Backend para la ventana para insertar un producto a la base de datos. """
    MENSAJE_EXITO = '¡Se registró el producto!'
    MENSAJE_ERROR = '¡No se pudo registrar el producto!'
    
    def __init__(self, first: App_AdministrarProductos):
        super().__init__(first)
        
        self.ui.lbTitulo.setText('Registrar producto')
        self.ui.btAceptar.setText(' Registrar producto')
        self.ui.btAceptar.setIcon(QIcon(QPixmap(':/img/resources/images/plus.png')))
    
    def ejecutarOperacion(self, conn, params):
        manejador = ManejadorProductos(conn, self.MENSAJE_ERROR)
        return manejador.insertarProducto(params)


class App_EditarProducto(Base_EditarProducto):
    """ Backend para la ventana para editar un producto de la base de datos. """
    MENSAJE_EXITO = '¡Se editó el producto!'
    MENSAJE_ERROR = '¡No se pudo editar el producto!'
    
    def __init__(self, first: App_AdministrarProductos, idx: int):
        super().__init__(first)
        
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
        utiliza_inventario = manejador.obtenerUtilizaInventario(idx)
        
        for nombre, cantidad in utiliza_inventario:
            self.agregarProductoALista(nombre, cantidad)
        
        self.idx = idx  # id del elemento a editar
    
    def ejecutarOperacion(self, conn, params):
        manejador = ManejadorProductos(conn, self.MENSAJE_ERROR)
        return manejador.editarProducto(self.idx, params)


#########################################
# WIDGETS PERSONALIZADOS PARA EL MÓDULO #
#########################################
class WidgetElemento(QtWidgets.QWidget):
    def __init__(self):
        from PySide6 import QtCore, QtWidgets, QtGui
        
        super().__init__()
        
        self.resize(390, 70)
        self.setMinimumSize(390, 70)
        boxElemento = QtWidgets.QComboBox(self)
        boxElemento.setGeometry(QtCore.QRect(35, 10, 271, 22))
        boxElemento.setMinimumSize(QtCore.QSize(271, 22))
        font = QFont()
        font.setPointSize(11)
        boxElemento.setFont(font)
        lbContador = QtWidgets.QLabel(self)
        lbContador.setGeometry(QtCore.QRect(5, 10, 21, 21))
        lbContador.setMinimumSize(QtCore.QSize(21, 21))
        lbContador.setPixmap(QtGui.QPixmap(":/img/resources/images/inventory.png"))
        lbContador.setScaledContents(True)
        
        btEliminar = QtWidgets.QPushButton(self)
        btEliminar.setGeometry(QtCore.QRect(343, 12, 35, 35))
        btEliminar.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btEliminar.setStyleSheet("QPushButton {\n"
                                 "        background-color: transparent;\n"
                                 "        border: none;\n"
                                 "        padding: 0px;\n"
                                 "    }\n"
                                 "    QPushButton:hover {\n"
                                 "        background-color: rgba(255, 255, 255, 0);\n"
                                 "    }\n"
                                 "    QPushButton:pressed {\n"
                                 "        background-color: rgba(255, 255, 255, 0);\n"
                                 "    }")
        icon = QIcon()
        icon.addFile(":/img/resources/images/cancel.png", QtCore.QSize(), QIcon.Normal, QIcon.Off)
        btEliminar.setIcon(icon)
        btEliminar.setIconSize(QtCore.QSize(35, 35))
        btEliminar.setFlat(True)
        
        label = QtWidgets.QLabel(self)
        label.setGeometry(QtCore.QRect(35, 40, 273, 21))
        label.setMinimumSize(QtCore.QSize(273, 21))
        label.setFont(font)
        label.setText("se usa          unidades de este elemento.")
        txtProductoUtiliza = QtWidgets.QLineEdit(self)
        txtProductoUtiliza.setGeometry(QtCore.QRect(84, 40, 39, 20))
        txtProductoUtiliza.setMinimumSize(QtCore.QSize(39, 20))
        txtProductoUtiliza.setFont(font)
        QtCore.QMetaObject.connectSlotsByName(self)
        
        # guardar widgets importantes como atributos
        self.boxElemento = boxElemento
        self.btEliminar = btEliminar
        self.txtProductoUtiliza = txtProductoUtiliza
    
    @property
    def elementoSeleccionado(self):
        return self.boxElemento.currentText()
    
    @property
    def cantidadElemento(self):
        return self.txtProductoUtiliza.text()


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
