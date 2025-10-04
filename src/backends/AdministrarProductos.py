from PySide6 import QtWidgets
from PySide6.QtGui import QFont, QColor, QIcon
from PySide6.QtCore import Qt, Signal, QMutex

from context import user_context
from core import ROJO
from interfaces import IModuloPrincipal
from sql import ManejadorInventario, ManejadorProductos
from urls import urls
from utils.mydecorators import fondo_oscuro, run_in_thread
from utils.myinterfaces import InterfazFiltro
from utils.myutils import request_handler, son_similar
from utils.mywidgets import LabelAdvertencia


#####################
# VENTANA PRINCIPAL #
#####################
class App_AdministrarProductos(QtWidgets.QWidget, IModuloPrincipal):
    """ Backend para la ventana de administración de productos. """

    rescanned = Signal()

    def crear(self):
        from ui.Ui_AdministrarProductos import Ui_AdministrarProductos

        self.ui = Ui_AdministrarProductos()
        self.ui.setupUi(self)

        self.mutex = QMutex()

        LabelAdvertencia(self.ui.tabla_productos, '¡No se encontró ningún producto!')

        self.token = user_context.token
        self.all = []

        # añadir menú de opciones al botón para filtrar
        self.filtro = InterfazFiltro(
            self.ui.btFiltrar, self.ui.searchBar, [('Código', 1), ('Descripción', 2)]
        )
        self.filtro.cambiado.connect(self.update_display)

        # eventos para los botones
        self.ui.btAgregar.clicked.connect(self.agregarProducto)
        self.ui.btEditar.clicked.connect(self.editarProducto)
        self.ui.btEliminar.clicked.connect(self.quitarProducto)
        self.ui.btRegresar.clicked.connect(self.go_back.emit)
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

        req = request_handler(urls['productos'], token=self.token)
        self.all = req.json()
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
            found = [c for c in self.all if son_similar(txt_busqueda, c[self.filtro.idx])]
        else:
            found = self.all

        tabla.setRowCount(len(found))

        for row, item in enumerate(found):
            for col, dato in enumerate(item.values()):
                if isinstance(dato, float):
                    cell = f'${dato:,.2f}'
                else:
                    cell = str(dato or '')

                widget = QtWidgets.QTableWidgetItem(cell)
                tabla.setItem(row, col, widget)

            tabla.item(row, 1).setFont(bold)

            # resaltar si la utilidad es nula o negativa
            if item['utilidad'] is not None and item['utilidad'] <= 0:
                color = QColor(ROJO)
                tabla.item(row, 7).setBackground(color)

        tabla.resizeRowsToContents()
        self.mutex.unlock()

    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def agregarProducto(self):
        widget = App_RegistrarProducto(self)
        widget.success.connect(self.rescan_update)

    def editarProducto(self):
        if selected := self.ui.tabla_productos.selectedItems():
            widget = App_EditarProducto(selected[0].text(), self)
            widget.success.connect(self.rescan_update)

    def quitarProducto(self):
        """ Elimina un producto de la base de datos.
        Primero se verifica si hay elementos que este utilizan. """
        try:
            id_productos = self.ui.tabla_productos.selectedItems()[0].text()
        except IndexError:
            return

        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Atención', '¿Desea descontinuar este producto?',)

        if ret != qm.Yes:
            return
        
        res = request_handler(urls['productos'] + id_productos + '/', 'PATCH', {'is_active': False})
        if res.status_code == 200:
            qm.information(self, 'Éxito', 'Se descontinuó el producto seleccionado.')
            self.rescan_update()
        else:
            mssg = res.json()['error']
            qm.warning(self, 'Error', f'Error al descontinuar producto: {mssg}')


#################################
# VENTANAS USADAS POR EL MÓDULO #
#################################
@fondo_oscuro
class Base_EditarProducto(QtWidgets.QWidget):
    """ Backend para la ventana para editar un producto de la base de datos. """

    MENSAJE_EXITO: str
    MENSAJE_ERROR: str

    success = Signal()

    def __init__(self, parent=None):
        from ui.Ui_EditarProducto import Ui_EditarProducto

        super().__init__(parent)

        self.ui = Ui_EditarProducto()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)

        self.idx = None

        # formato tabla de precios
        header = self.ui.tabla_precios.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)

        # obtener objetos de la tabla Inventario
        req = request_handler(urls['inventario'])
        self.elementos_inventario = req.json()

        # eventos para botones
        self.ui.btAceptar.clicked.connect(self.done)
        self.ui.btAgregar.clicked.connect(lambda: self.agregarProductoALista())

        self.ui.btAgregarIntervalo.clicked.connect(
            lambda: self.agregarIntervalo(row=self.ui.tabla_precios.rowCount())
        )
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

    def agregarIntervalo(self, row: int, desde: float = 0.0, precio: float = 0.0, duplex: bool = False):
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

    def agregarProductoALista(self, inventario_id: int = '', cantidad: int = 1):
        # crear widget y agregar a la lista
        nuevo = WidgetElemento()

        # llenar caja de opciones con elementos del inventario
        nuevo.boxElemento.addItems([elem['nombre'] for elem in self.elementos_inventario])
        nuevo.elementoSeleccionado = next((elem['nombre'] for elem in self.elementos_inventario if elem['id'] == inventario_id), None)
        nuevo.cantidadElemento = cantidad

        self.ui.layoutScroll.addWidget(nuevo)

    def obtenerParametrosProductos(self):
        """ Parámetros para la tabla productos. """
        return {
            'codigo': self.ui.txtCodigo.text().strip() or None,
            'descripcion': self.ui.txtDescripcion.toPlainText().strip() or None,
            'abreviado': self.ui.txtNombre.text() or None,
            'categoria': self.categoriaActual or None,
            'is_active': True
        }

    def obtenerParametrosProdUtilizaInv(self):
        """ Parámetros para la tabla productos_utiliza_inventario. """
        wdg: list[WidgetElemento] = self.ui.scrollAreaLista.children()[1:]
        PUI_db_parametros = []

        for elemento in wdg:
            nombre, cantidad = elemento.elementoSeleccionado, elemento.cantidadElemento
            if not nombre or cantidad < 1:
                return None

            id_inventario = next((elem['id'] for elem in self.elementos_inventario if elem['nombre'] == nombre), None)
            PUI_db_parametros.append({"inventario": id_inventario, "utiliza_inventario": cantidad})

        return PUI_db_parametros

    def obtenerParametrosProdIntervalos(self):
        """ Parámetros para la tabla productos_intervalos. """
        tabla = self.ui.tabla_precios
        Prod_db_parametros = []

        if not self.ui.tabla_precios.rowCount():
            QtWidgets.QMessageBox.warning(self, 'Atención', '¡La tabla de precios se encuentra vacía!')
            return None

        for row in range(tabla.rowCount()):
            desde = tabla.item(row, 0).text().replace(',', '')
            precio = tabla.item(row, 1).text().replace(',', '')
            duplex: ItemAuxiliar = tabla.cellWidget(row, 2)

            try:
                Prod_db_parametros.append({'desde': float(desde), 'precio_con_iva': float(precio), 'duplex': duplex.isChecked})
            except ValueError:
                QtWidgets.QMessageBox.warning(
                    self, 'Atención', '¡Verifique que los datos numéricos sean correctos!',
                )
                return None

        return Prod_db_parametros

    def obtenerParametrosProdGranFormato(self):
        """ Parámetros para la tabla productos_gran_formato. """
        try:
            return {'min_m2': float(self.ui.txtMinM2.text()), 'precio_m2': float(self.ui.txtPrecio.text())}
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self, 'Atención', '¡Verifique que los datos numéricos sean correctos!'
            )
            return None

    def done(self):
        """ Función donde se registrará o actualizará producto. """
        #### obtención de parámetros ####
        productos_db_parametros = self.obtenerParametrosProductos()
        PUI_db_parametros = self.obtenerParametrosProdUtilizaInv()

        if self.categoriaActual == 'S':
            intervalos = self.obtenerParametrosProdIntervalos()
            gran_formato = None
        else:
            intervalos = []
            gran_formato = self.obtenerParametrosProdGranFormato()

        # llamar a API
        payload = productos_db_parametros | {
            'inventarios': PUI_db_parametros,
            'intervalos': intervalos,
            'gran_formato': gran_formato
        }
        if self.idx:
            res = request_handler(urls['productos']+str(self.idx)+'/', 'PATCH', payload)
        else:
            res = request_handler(urls['productos'], 'POST', payload)

        if res.status_code in [200, 201]:
            QtWidgets.QMessageBox.information(self, 'Éxito', self.MENSAJE_EXITO)
            self.success.emit()
            self.close()
        else:
            mssg = res.json()['error']
            QtWidgets.QMessageBox.warning(self, 'Error', f'Error al registrar producto: {mssg}')

    def insertar_o_modificar(self, productos_db_parametros: tuple) -> tuple:
        """ Devuelve tupla con índice del producto registrado o editado. """
        raise NotImplementedError('BEIS CLASSSSSSS')


class App_RegistrarProducto(Base_EditarProducto):
    """ Backend para la ventana para insertar un producto a la base de datos. """

    MENSAJE_EXITO = '¡Se registró el producto!'
    MENSAJE_ERROR = '¡No se pudo registrar el producto!'

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui.lbTitulo.setText('Registrar producto')
        self.ui.btAceptar.setText(' Registrar producto')
        self.ui.btAceptar.setIcon(QIcon(':/img/resources/images/plus.png'))


class App_EditarProducto(Base_EditarProducto):
    """ Backend para la ventana para editar un producto de la base de datos. """

    MENSAJE_EXITO = '¡Se editó el producto!'
    MENSAJE_ERROR = '¡No se pudo editar el producto!'

    def __init__(self, idx: int, parent=None):
        super().__init__(parent)

        self.idx = idx  # id del elemento a editar

        req = request_handler(urls['productos'] + str(idx))
        producto = req.json()

        self.ui.txtCodigo.setText(producto['codigo'])
        self.ui.txtDescripcion.setPlainText(producto['descripcion'])
        self.ui.txtNombre.setText(producto['abreviado'])

        if producto['categoria'] == 'S':
            self.ui.tabWidget.setCurrentIndex(0)

            for row, obj in enumerate(producto['intervalos']):
                self.agregarIntervalo(row, obj['desde'], obj['precio_con_iva'], obj['duplex'])
        elif producto['categoria'] == 'G':
            self.ui.tabWidget.setCurrentIndex(1)

            self.ui.txtMinM2.setText(f'{producto["gran_formato"]["min_m2"]:,.2f}')
            self.ui.txtPrecio.setText(f'{producto["gran_formato"]["precio_m2"]:,.2f}')

        # agregar elementos de la segunda página
        for obj in producto['inventarios']:
            self.agregarProductoALista(obj['inventario'], obj['utiliza_inventario'])


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
