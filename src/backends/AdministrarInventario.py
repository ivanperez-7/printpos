from PySide6 import QtWidgets
from PySide6.QtGui import QFont, QColor, QPixmap, QIcon
from PySide6.QtCore import Qt, Signal, QMutex

from context import user_context
from core import ROJO, NumeroDecimal
from interfaces import IModuloPrincipal
from sql import ManejadorInventario, ManejadorProductos
from utils.mydecorators import fondo_oscuro, run_in_thread
from utils.myutils import son_similar
from utils.mywidgets import LabelAdvertencia


#####################
# VENTANA PRINCIPAL #
#####################
class App_AdministrarInventario(QtWidgets.QWidget, IModuloPrincipal):
    """Backend para la ventana de administración de inventario."""

    rescanned = Signal()

    def crear(self):
        from ui.Ui_AdministrarInventario import Ui_AdministrarInventario

        self.ui = Ui_AdministrarInventario()
        self.ui.setupUi(self)

        self.mutex = QMutex()

        LabelAdvertencia(self.ui.tabla_inventario, '¡No se encontró ningún elemento!')

        # guardar conexión y usuarios como atributos
        self.conn = user_context.conn
        self.user = user_context.user

        self.all = []

        # añade eventos para los botones
        self.ui.btAgregar.clicked.connect(self.agregarInventario)
        self.ui.btEditar.clicked.connect(self.editarInventario)
        self.ui.btEliminar.clicked.connect(self.quitarInventario)
        self.ui.btRegresar.clicked.connect(self.go_back.emit)
        self.ui.searchBar.textChanged.connect(self.update_display)
        self.rescanned.connect(self.update_display)

        self.ui.tabla_inventario.configurarCabecera(lambda col: col == 0)

    def showEvent(self, event):
        self.rescan_update()

    def resizeEvent(self, event):
        if self.isVisible():
            self.ui.tabla_inventario.resizeRowsToContents()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @run_in_thread
    def rescan_update(self, *args):
        if not self.mutex.try_lock():
            return

        self.ui.lbContador.setText(f'Recuperando información...')

        manejador = ManejadorInventario(self.conn)
        self.all = manejador.obtenerTablaPrincipal() or []
        self.ui.lbContador.setText(f'{len(self.all)} elementos en la base de datos.')

        self.rescanned.emit()

    def update_display(self):
        """Actualiza la tabla y el contador de elementos.
        Acepta una cadena de texto para la búsqueda de elementos.
        También lee de nuevo la tabla de elementos, si se desea."""
        tabla = self.ui.tabla_inventario
        tabla.setRowCount(0)

        bold = QFont()
        bold.setBold(True)

        if txt_busqueda := self.ui.searchBar.text().strip():
            found = [c for c in self.all if c[1] if son_similar(txt_busqueda, c[1])]
        else:
            found = self.all

        tabla.setRowCount(len(found))

        for row, item in enumerate(found):
            for col, dato in enumerate(item):
                if isinstance(dato, int):
                    cell = f'{dato:,d}'
                elif isinstance(dato, float):
                    cell = f'{dato:,.2f}'
                else:
                    cell = str(dato or '')

                if col in {2, 5}:
                    cell += ' unidades'
                if col in {4, 6}:
                    cell += ' lotes'
                tabla.setItem(row, col, QtWidgets.QTableWidgetItem(cell))

            tabla.item(row, 1).setFont(bold)

            btSurtir = QtWidgets.QPushButton('Surtir existencias')
            btSurtir.clicked.connect(self.surtirExistencias)
            tabla.setCellWidget(row, col + 1, btSurtir)

            # resaltar si hay menos cantidad que el mínimo
            if item[6] < item[4]:
                color = QColor(ROJO)
                tabla.item(row, 6).setBackground(color)

        tabla.resizeRowsToContents()
        self.mutex.unlock()

    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def surtirExistencias(self):
        idx = self.ui.tabla_inventario.selectedItems()[0].text()

        self.Dialog = ExistenciasWidget(idx, self)
        self.Dialog.success.connect(self.rescan_update)

    def agregarInventario(self):
        widget = App_RegistrarInventario(self)
        widget.success.connect(self.rescan_update)

    def editarInventario(self):
        if selected := self.ui.tabla_inventario.selectedItems():
            widget = App_EditarInventario(selected[0].text(), self)
            widget.success.connect(self.rescan_update)

    def quitarInventario(self):
        """Elimina un material de la base de datos.
        Primero se verifica si hay productos que lo utilizan."""
        try:
            id_inventario = self.ui.tabla_inventario.selectedItems()[0].text()
        except IndexError:
            return

        qm = QtWidgets.QMessageBox

        manejador = ManejadorInventario(self.conn, '¡No se pudo eliminar el elemento!')
        result = manejador.obtenerProdUtilizaInv(id_inventario)

        if result:
            qm.warning(
                self,
                'Atención',
                'No se puede eliminar este elemento debido '
                'a que hay productos que lo utilizan. Haga doble '
                'click en algún elemento para ver estos productos.',
            )
            return

        # abrir pregunta
        ret = qm.question(
            self, 'Atención', 'El elemento seleccionado se eliminará de la base de datos. ¿Desea continuar?',
        )
        if ret != qm.Yes:
            return

        if manejador.eliminarElemento(id_inventario):
            qm.information(self, 'Éxito', 'Se eliminó el elemento seleccionado.')
            self.rescan_update()


#################################
# VENTANAS USADAS POR EL MÓDULO #
#################################
@fondo_oscuro
class Base_EditarInventario(QtWidgets.QWidget):
    """Clase base para módulo de registrar o modificar elemento."""

    MENSAJE_EXITO: str
    MENSAJE_ERROR: str

    success = Signal()

    def __init__(self, parent=None):
        from ui.Ui_EditarInventario import Ui_EditarInventario

        super().__init__(parent)

        self.ui = Ui_EditarInventario()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)

        # guardar conexión como atributo
        self.conn = user_context.conn

        # validadores para datos numéricos
        validador = NumeroDecimal

        self.ui.txtPrecioCompra.setValidator(validador)
        self.ui.txtExistencia.setValidator(validador)
        self.ui.txtMinimo.setValidator(validador)
        self.ui.txtTamano.setValidator(validador)

        # evento para botón de regresar
        self.ui.btAceptar.clicked.connect(self.done)
        self.ui.btAgregar.clicked.connect(lambda: self.agregarProductoALista())
        self.ui.btRegresar.clicked.connect(self.close)

        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    ####################
    # FUNCIONES ÚTILES #
    ####################
    def agregarProductoALista(self, codigo: str = '', cantidad: int = 1):
        # crear widget y agregar a la lista
        nuevo = WidgetProducto()

        # llenar caja de opciones con productos
        manejador = ManejadorProductos(self.conn)
        codigos = manejador.obtenerListaCodigos()

        nuevo.boxProducto.addItems([codigo for codigo, in codigos])
        nuevo.productoSeleccionado = codigo
        nuevo.cantidadProducto = cantidad

        self.ui.layoutScroll.addWidget(nuevo)

    def obtenerParametrosInventario(self):
        """Parámetros para la tabla inventario."""
        try:
            if not (tamanoLote := float(self.ui.txtTamano.text())):
                return None

            return (
                self.ui.txtNombre.text().strip() or None,
                tamanoLote,
                float(self.ui.txtPrecioCompra.text()),
                float(self.ui.txtMinimo.text()),
                float(self.ui.txtExistencia.text()),
            )
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self, 'Atención', '¡Verifique que los datos numéricos sean correctos!'
            )
            return None

    def obtenerParametrosProdUtilizaInv(self):
        """Parámetros para la tabla productos_utiliza_inventario."""
        productos: list[WidgetProducto] = self.ui.scrollAreaLista.children()[1:]

        PUI_db_parametros = []
        manejador = ManejadorProductos(self.conn)

        for wdg in productos:
            codigo, cantidad = wdg.productoSeleccionado, wdg.cantidadProducto
            if not codigo or cantidad < 1:
                return None

            idProducto = manejador.obtenerIdProducto(codigo)
            PUI_db_parametros.append((idProducto, cantidad))

        return PUI_db_parametros

    def done(self):
        """Función donde se registrará o actualizará elemento del inventario."""
        #### obtención de parámetros ####
        inventario_db_parametros = self.obtenerParametrosInventario()
        PUI_db_parametros = self.obtenerParametrosProdUtilizaInv()

        if inventario_db_parametros is None or PUI_db_parametros is None:
            return

        # ejecuta internamente un fetchone, por lo que se desempaca luego
        if not (result := self.insertar_o_modificar(inventario_db_parametros)):
            return
        (idx,) = result
        manejador = ManejadorInventario(self.conn, self.MENSAJE_ERROR)

        # transacción principal, se checa si cada operación fue exitosa
        if manejador.eliminarProdUtilizaInv(idx) and manejador.insertarProdUtilizaInv(idx, PUI_db_parametros):
            QtWidgets.QMessageBox.information(self, 'Éxito', self.MENSAJE_EXITO)
            self.success.emit()
            self.close()

    def insertar_o_modificar(self, inventario_db_parametros: tuple) -> tuple:
        """Devuelve tupla con índice del elemento registrado o editado."""
        raise NotImplementedError('BEIS CLASSSSSSS')


class App_RegistrarInventario(Base_EditarInventario):
    """Backend para la ventana para registrar un material del inventario."""

    MENSAJE_EXITO = '¡Se registró el elemento!'
    MENSAJE_ERROR = '¡No se pudo registrar el elemento!'

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui.lbTitulo.setText('Registrar elemento')
        self.ui.btAceptar.setText(' Registrar elemento')
        self.ui.btAceptar.setIcon(QIcon(':/img/resources/images/plus.png'))

    ####################
    # FUNCIONES ÚTILES #
    ####################
    def insertar_o_modificar(self, inventario_db_parametros):
        manejador = ManejadorInventario(self.conn, self.MENSAJE_ERROR)
        return manejador.insertarElemento(inventario_db_parametros)


class App_EditarInventario(Base_EditarInventario):
    """Backend para la ventana para editar un material del inventario."""

    MENSAJE_EXITO = '¡Se editó el elemento!'
    MENSAJE_ERROR = '¡No se pudo editar el elemento!'

    def __init__(self, idx: int, parent=None):
        super().__init__(parent)

        self.idx = idx  # id del elemento a editar

        manejador = ManejadorInventario(self.conn)

        # datos de la primera página
        (nombre, tamano, precio, minimo, existencia,) = manejador.obtenerInformacionPrincipal(idx)

        self.ui.txtNombre.setText(nombre)
        self.ui.txtTamano.setText(f'{tamano:.2f}')
        self.ui.txtPrecioCompra.setText(f'{precio:.2f}')
        self.ui.txtExistencia.setText(f'{existencia:.2f}')
        self.ui.txtMinimo.setText(f'{minimo:.2f}')

        # agregar productos de la segunda página
        productos = manejador.obtenerProdUtilizaInv(idx)

        for codigo, cantidad in productos:
            self.agregarProductoALista(codigo, cantidad)

    ####################
    # FUNCIONES ÚTILES #
    ####################
    def insertar_o_modificar(self, inventario_db_parametros):
        manejador = ManejadorInventario(self.conn, self.MENSAJE_ERROR)
        return manejador.editarElemento(self.idx, inventario_db_parametros)


#########################################
# WIDGETS PERSONALIZADOS PARA EL MÓDULO #
#########################################
class WidgetProducto(QtWidgets.QWidget):
    def __init__(self):
        from ui.Ui_WidgetElemento import Ui_WidgetElemento

        super().__init__()
        self.ui = Ui_WidgetElemento()
        self.ui.setupUi(self)
        self.setMinimumSize(self.size())

        self.ui.label.setPixmap(QPixmap(':/img/resources/images/package_2.png'))

        self.ui.btEliminar.clicked.connect(lambda: self.setParent(None))

        # guardar widgets importantes como atributos
        self.boxProducto = self.ui.boxElemento

    @property
    def productoSeleccionado(self):
        return self.ui.boxElemento.currentText()

    @productoSeleccionado.setter
    def productoSeleccionado(self, val: str):
        self.ui.boxElemento.setCurrentText(val)

    @property
    def cantidadProducto(self):
        return self.ui.boxProductoUtiliza.value()

    @cantidadProducto.setter
    def cantidadProducto(self, val: int):
        self.ui.boxProductoUtiliza.setValue(val)


class ExistenciasWidget(QtWidgets.QDialog):
    success = Signal()

    def __init__(self, idx: int, parent=None):
        from PySide6 import QtCore

        super().__init__(parent)
        self.conn = user_context.conn
        self.idx = idx

        self.resize(340, 80)
        self.setWindowTitle('Surtir existencias')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setModal(True)
        self.setWindowModality(Qt.ApplicationModal)
        gridLayout = QtWidgets.QGridLayout(self)
        gridLayout.setContentsMargins(-1, -1, -1, 9)
        label = QtWidgets.QLabel(self)
        font = QFont()
        font.setPointSize(9)
        label.setFont(font)
        label.setText('Suministrar ')
        gridLayout.addWidget(label, 0, 0, 1, 1)
        txtCantidad = QtWidgets.QLineEdit(self)
        txtCantidad.setFont(font)
        txtCantidad.setValidator(NumeroDecimal)
        gridLayout.addWidget(txtCantidad, 0, 1, 1, 1)
        label_2 = QtWidgets.QLabel(self)
        label_2.setFont(font)
        label_2.setText(' lotes para este elemento.')
        gridLayout.addWidget(label_2, 0, 2, 1, 1)
        buttonBox = QtWidgets.QDialogButtonBox(self)
        buttonBox.setFont(font)
        buttonBox.setOrientation(Qt.Horizontal)
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        buttonBox.setCenterButtons(True)
        gridLayout.addWidget(buttonBox, 1, 0, 1, 3, Qt.AlignBottom)

        buttonBox.accepted.connect(self.accept)  # type: ignore
        buttonBox.rejected.connect(self.reject)  # type: ignore
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

        # guardar widgets importantes como atributos
        self.txtCantidad = txtCantidad

    @property
    def cantidadLotes(self):
        try:
            return float(self.txtCantidad.text())
        except ValueError:
            return 0.0

    def accept(self):
        if not self.cantidadLotes:
            return
        if ManejadorInventario(self.conn).agregarLotes(self.idx, self.cantidadLotes):
            self.success.emit()
            self.close()
