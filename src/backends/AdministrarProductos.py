from PySide6 import QtWidgets
from PySide6.QtGui import QFont, QColor, QIcon
from PySide6.QtCore import Qt, Signal, QMutex
from sqlalchemy import String
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func, case

from context import user_context
from core import ROJO
from interfaces import IModuloPrincipal
from sql.models import Producto, ProductoGranFormato, ProductoIntervalo, ProductoUtilizaInventario, Inventario
from utils.mydecorators import fondo_oscuro, run_in_thread
from utils.myinterfaces import InterfazFiltro
from utils.myutils import son_similar
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

        # guardar conexión y usuario como atributos
        self.conn = user_context.conn
        self.user = user_context.user
        self.session = user_context.session

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
    #@run_in_thread
    def rescan_update(self):
        """ Actualiza la lista de productos desde la base de datos usando SQLAlchemy. """
        if not self.mutex.try_lock():
            return

        self.ui.lbContador.setText('Recuperando información...')

        try:
            P_Inv = aliased(ProductoIntervalo)
            P_Gran = aliased(ProductoGranFormato)

            # Subquery for production cost
            costo_produccion = (
                self.session.query(
                    Producto.id_productos,
                    func.coalesce(func.sum(ProductoUtilizaInventario.utiliza_inventario * Inventario.precio_unidad), 0.0).label('costo')
                )
                .outerjoin(ProductoUtilizaInventario, Producto.id_productos == ProductoUtilizaInventario.id_productos)
                .outerjoin(Inventario, ProductoUtilizaInventario.id_inventario == Inventario.id_inventario)
                .group_by(Producto.id_productos)
                .subquery()
            )

            # Main query
            query = (
                self.session.query(
                    Producto.id_productos,
                    Producto.codigo,
                    case(
                        (
                            P_Inv.id_productos.isnot(None),
                            Producto.descripcion
                            + func.coalesce(
                                ', desde ' + func.cast(func.round(P_Inv.desde, 0), String) + ' unidades ',
                                ''
                            )
                            + func.coalesce(
                                '[PRECIO DUPLEX]' if P_Inv.duplex else '',
                                ''
                            ),
                        ),
                        else_=Producto.descripcion
                    ).label('descripcion'),
                    Producto.abreviado,
                    func.coalesce(P_Inv.precio_con_iva, P_Gran.precio_m2).label('precio_con_iva'),
                    (func.coalesce(P_Inv.precio_con_iva, P_Gran.precio_m2) / 1.16).label('precio_sin_iva'),
                    costo_produccion.c.costo.label('costo_prod'),
                    (func.coalesce(P_Inv.precio_con_iva, P_Gran.precio_m2) - costo_produccion.c.costo).label('utilidad')
                )
                .outerjoin(P_Inv, Producto.id_productos == P_Inv.id_productos)
                .outerjoin(P_Gran, Producto.id_productos == P_Gran.id_productos)
                .join(costo_produccion, Producto.id_productos == costo_produccion.c.id_productos)
                .filter(Producto.is_active.is_(True))
                .order_by(Producto.id_productos.asc())
            )

            self.all = query.all()
            self.ui.lbContador.setText(f'{len(self.all)} productos en la base de datos.')
        except Exception as e:
            self.ui.lbContador.setText('Error al recuperar información.')
            QtWidgets.QMessageBox.critical(self, 'Error', f'Error al recuperar productos: {e}')
        finally:
            self.rescanned.emit()
            self.mutex.unlock()

    def update_display(self):
        """ Actualiza la tabla y el contador de productos. """
        tabla = self.ui.tabla_productos
        tabla.setRowCount(0)

        bold = QFont()
        bold.setBold(True)

        if txt_busqueda := self.ui.searchBar.text().strip():
            found = [c for c in self.all if son_similar(txt_busqueda, c.codigo) or son_similar(txt_busqueda, c.descripcion)]
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

            # Resaltar si la utilidad es nula o negativa
            if item.utilidad <= 0:
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
        
        # Confirmar eliminación
        ret = qm.question(self, 'Atención', '¿Desea descontinuar este producto?')
        if ret != qm.Yes:
            return

        try:
            producto = self.session.query(Producto).filter_by(id_productos=id_productos).one_or_none()
            producto.is_active = False
            
            self.session.commit()
            qm.information(self, 'Éxito', 'Se descontinuó el producto seleccionado.')
            self.rescan_update()
        except Exception as e:
            self.session.rollback()
            qm.critical(self, 'Error', f'¡No se pudo descontinuar el producto!\n{e}')


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

        # obtener sesión de base de datos desde user_context
        self.session = user_context.session

        # formato tabla de precios
        header = self.ui.tabla_precios.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)

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

    def agregarProductoALista(self, nombre: str = '', cantidad: int = 1):
        """ Agrega un producto a la lista usando datos del inventario. """
        # Crear widget y agregar a la lista
        nuevo = WidgetElemento()

        try:
            elementos = self.session.query(Inventario.nombre).all()
            nuevo.boxElemento.addItems([nombre for nombre, in elementos])
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Error', f'Error al cargar inventario: {e}')
            return

        nuevo.elementoSeleccionado = nombre
        nuevo.cantidadElemento = cantidad

        self.ui.layoutScroll.addWidget(nuevo)

    def obtenerParametrosProductos(self):
        """ Parámetros para la tabla productos. """
        return {
            'codigo': self.ui.txtCodigo.text().strip(),
            'descripcion': self.ui.txtDescripcion.toPlainText().strip(),
            'abreviado': self.ui.txtNombre.text(),
            'categoria': self.categoriaActual,
        }

    def obtenerParametrosProdUtilizaInv(self):
        """ Parámetros para la tabla productos_utiliza_inventario. """
        wdg: list[WidgetElemento] = self.ui.scrollAreaLista.children()[1:]

        PUI_db_parametros = []

        for elemento in wdg:
            nombre, cantidad = elemento.elementoSeleccionado, elemento.cantidadElemento
            if not nombre or cantidad < 1:
                return None

            # Buscar el inventario por nombre usando SQLAlchemy
            inventario = self.session.query(Inventario).filter_by(nombre=nombre).one_or_none()
            if not inventario:
                QtWidgets.QMessageBox.warning(self, 'Atención', f'¡El inventario "{nombre}" no existe!')
                return None

            PUI_db_parametros.append((inventario.id_inventario, cantidad))

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
                Prod_db_parametros.append((float(desde), float(precio), duplex.isChecked))
            except ValueError:
                QtWidgets.QMessageBox.warning(
                    self, 'Atención', '¡Verifique que los datos numéricos sean correctos!',
                )
                return None

        return Prod_db_parametros

    def obtenerParametrosProdGranFormato(self):
        """ Parámetros para la tabla productos_gran_formato. """
        try:
            return (float(self.ui.txtMinM2.text()), float(self.ui.txtPrecio.text()))
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self, 'Atención', '¡Verifique que los datos numéricos sean correctos!'
            )
            return None

    def done(self):
        """ Función donde se registrará o actualizará producto. """
        try:
            # obtención de parámetros
            producto_params = self.obtenerParametrosProductos()
            inventario_params = self.obtenerParametrosProdUtilizaInv()

            if self.categoriaActual == 'S':
                precios_params = self.obtenerParametrosProdIntervalos()
            else:
                precios_params = self.obtenerParametrosProdGranFormato()

            if any(params is None for params in (producto_params, inventario_params, precios_params)):
                return

            producto = self.insertar_o_modificar(producto_params)

            # actualizar relaciones
            self.session.query(ProductoUtilizaInventario).filter_by(id_productos=producto.id_productos).delete()
            for inv_id, cantidad in inventario_params:
                self.session.add(ProductoUtilizaInventario(
                    id_productos=producto.id_productos,
                    id_inventario=inv_id,
                    utiliza_inventario=cantidad
                ))

            if self.categoriaActual == 'S':
                self.session.query(ProductoIntervalo).filter_by(id_productos=producto.id_productos).delete()
                for desde, precio, duplex in precios_params:
                    self.session.add(ProductoIntervalo(
                        id_productos=producto.id_productos,
                        desde=desde,
                        precio_con_iva=precio,
                        duplex=duplex
                    ))
            else:
                self.session.query(ProductoGranFormato).filter_by(id_productos=producto.id_productos).delete()
                min_m2, precio = precios_params
                self.session.add(ProductoGranFormato(
                    id_productos=producto.id_productos,
                    min_m2=min_m2,
                    precio_m2=precio
                ))

            self.session.commit()
            QtWidgets.QMessageBox.information(self, 'Éxito', self.MENSAJE_EXITO)
            self.success.emit()
            self.close()
        except Exception as e:
            self.session.rollback()
            QtWidgets.QMessageBox.critical(self, 'Error', f'{self.MENSAJE_ERROR}\n{e}')

    def insertar_o_modificar(self, producto_params):
        """ Inserta o actualiza un producto en la base de datos. """
        raise NotImplementedError('Debe ser implementado por las subclases.')


class App_RegistrarProducto(Base_EditarProducto):
    """ Backend para la ventana para insertar un producto a la base de datos. """

    MENSAJE_EXITO = '¡Se registró el producto!'
    MENSAJE_ERROR = '¡No se pudo registrar el producto!'

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui.lbTitulo.setText('Registrar producto')
        self.ui.btAceptar.setText(' Registrar producto')
        self.ui.btAceptar.setIcon(QIcon(':/img/resources/images/plus.png'))

    def insertar_o_modificar(self, producto_params):
        producto = Producto(**producto_params)
        self.session.add(producto)
        self.session.flush()  # Obtener el ID del producto recién insertado
        return producto


class App_EditarProducto(Base_EditarProducto):
    """ Backend para la ventana para editar un producto de la base de datos. """

    MENSAJE_EXITO = '¡Se editó el producto!'
    MENSAJE_ERROR = '¡No se pudo editar el producto!'

    def __init__(self, idx: int, parent=None):
        super().__init__(parent)

        self.idx = idx  # id del elemento a editar

        producto = self.session.query(Producto).filter_by(id_productos=idx).one()
        self.ui.txtCodigo.setText(producto.codigo)
        self.ui.txtDescripcion.setPlainText(producto.descripcion)
        self.ui.txtNombre.setText(producto.abreviado)

        if producto.categoria == 'S':
            self.ui.tabWidget.setCurrentIndex(0)
            for intervalo in producto.intervalos:
                self.agregarIntervalo(
                    row=self.ui.tabla_precios.rowCount(),
                    desde=intervalo.desde,
                    precio=intervalo.precio_con_iva,
                    duplex=intervalo.duplex
                )
        elif producto.categoria == 'G':
            self.ui.tabWidget.setCurrentIndex(1)
            gran_formato = producto.gran_formato[0]
            self.ui.txtMinM2.setText(f'{gran_formato.min_m2:,.2f}')
            self.ui.txtPrecio.setText(f'{gran_formato.precio_m2:,.2f}')

        for utiliza in producto.utiliza_inventario:
            self.agregarProductoALista(
                nombre=utiliza.inventario.nombre,
                cantidad=utiliza.utiliza_inventario
            )

    def insertar_o_modificar(self, producto_params):
        producto = self.session.query(Producto).filter_by(id_productos=self.idx).one()
        for key, value in producto_params.items():
            setattr(producto, key, value)
        return producto


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
