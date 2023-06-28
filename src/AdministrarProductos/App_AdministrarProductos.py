from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QRegExp

from myutils import ColorsEnum, son_similar
from mydecorators import con_fondo
from mywidgets import LabelAdvertencia, WarningDialog

import fdb

class App_AdministrarProductos(QtWidgets.QMainWindow):
    """
    Backend para la ventana de administración de productos.
    """
    def __init__(self, parent=None):
        from AdministrarProductos.Ui_AdministrarProductos import Ui_AdministrarProductos
        
        super().__init__()

        self.ui = Ui_AdministrarProductos()
        self.ui.setupUi(self)
        
        session = parent.session

        self.session = session  # conexión y usuario actual
        self.filtro = 1
        
        LabelAdvertencia(self.ui.tabla_productos, '¡No se encontró ningún producto!')
        
        # dar formato a la tabla principal
        header = self.ui.tabla_productos.horizontalHeader()
        
        for col in range(self.ui.tabla_productos.columnCount()):
            if col not in {1, 2, 3}:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
        
        # eventos para los botones
        self.ui.lbAgregar.mousePressEvent = self.agregarProducto
        self.ui.lbEditar.mousePressEvent = self.editarProducto
        self.ui.lbQuitar.mousePressEvent = self.quitarProducto
        self.ui.lbRegresar.mousePressEvent = self.goHome
        self.ui.searchBar.textChanged.connect(lambda: self.update_display())
    
    def showEvent(self, event):
        self.update_display(rescan=True)
    
    def resizeEvent(self, event):
        if self.isVisible():
            self.ui.tabla_productos.resizeRowsToContents()
    
    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def update_display(self, rescan: bool = False):
        """
        Actualiza la tabla y el contador de productos.
        Acepta una cadena de texto para la búsqueda de productos.
        También lee de nuevo la tabla de productos, si se desea.
        """
        if rescan:
            crsr = self.session['conn'].cursor()
            
            crsr.execute('''
            WITH CostoProduccion (idProductos, costo) AS (
            SELECT	P.idProductos,
                    SUM(
                        COALESCE(PUI.utilizaInventario * I.precioCompra, 
                        0.0)
                    ) AS costo
            FROM  	Productos AS P
                    LEFT JOIN ProductosUtilizaInventario AS PUI
                           ON P.idProductos = PUI.idProductos
                    LEFT JOIN Inventario AS I
                           ON PUI.idInventario = I.idInventario
            GROUP	BY P.idProductos
            ORDER	BY P.idProductos ASC
            )

            SELECT  P.idProductos,
                    P.codigo,
                    P.descripcion 
                        || COALESCE(', desde ' || ROUND(PInv.desde, 1) || ' unidades', '')
                        || IIF(PInv.duplex, ' [PRECIO DUPLEX]', ''),
                    P.abreviado,
                    COALESCE(P_gran.precio_m2, PInv.precioConIVA) AS precio_con_iva, 
                    COALESCE(P_gran.precio_m2, PInv.precioConIVA) / 1.16 AS precio_sin_iva,
                    CProd.costo,
                    COALESCE(
                        COALESCE(P_gran.precio_m2, PInv.precioConIVA) - CProd.costo, 
                        0) AS utilidad
            FROM    Productos AS P
                    LEFT JOIN ProductosIntervalos AS PInv
                           ON PInv.idProductos = P.idProductos
                    LEFT JOIN Productos_Granformato AS P_gran
                           ON P.idProductos = P_gran.idProductos
                    LEFT JOIN CostoProduccion AS CProd
                           ON P.idProductos = CProd.idProductos
            ORDER   BY P.idProductos, desde ASC;
            ''')

            self.all = crsr.fetchall()
            self.ui.lbContador.setText(f'{len(self.all)} productos en la base de datos.')
        
        tabla = self.ui.tabla_productos
        tabla.setRowCount(0)
        
        bold = QtGui.QFont()
        bold.setBold(True)
        
        # texto introducido por el usuario
        txt_busqueda = self.ui.searchBar.text().strip()
        
        found = self.all if not txt_busqueda else \
                filter(
                    lambda c: c[self.filtro] 
                              and son_similar(txt_busqueda, c[self.filtro]), 
                    self.all)
        
        for row, item in enumerate(found):
            tabla.insertRow(row)

            for col, dato in enumerate(item):
                if isinstance(dato, float):
                    cell = f'{dato:,.2f}'
                else:
                    cell = str(dato or '')
                
                # item a insertar en la tabla
                widget = QtWidgets.QTableWidgetItem(cell)
                # reemplazar el método < para usar nuestro propio ordenamiento
                widget.__lt__ = lambda _: False
                # insertar item en la tabla
                tabla.setItem(row, col, widget)
            
            tabla.item(row, 1).setFont(bold)
            
            # resaltar si la utilidad es nula o negativa
            if item[-1] <= 0:
                color = QtGui.QColor(ColorsEnum.ROJO)
                tabla.item(row, 7).setBackground(color)

        tabla.resizeRowsToContents()
    
    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def agregarProducto(self, _):
        self.new = App_EditarProducto(self)
    
    def editarProducto(self, _):
        selected = self.ui.tabla_productos.selectedItems()
        
        if selected:
            self.new = App_EditarProducto(self, selected[0].text())
    
    def quitarProducto(self, _):
        """
        Elimina un producto de la base de datos.
        Primero se verifica si hay elementos que este utilizan.
        """
        try:
            idProducto = self.ui.tabla_productos.selectedItems()[0].text()
        except IndexError:
            return
        
        qm = QtWidgets.QMessageBox
        
        conn = self.session['conn']
        crsr = conn.cursor()
        
        crsr.execute('''
        SELECT	COUNT(idProductos)
        FROM	VentasDetallado
        WHERE	idProductos = ?;
        ''', (idProducto,))
        
        # numero de ventas que contienen este producto
        count, = crsr.fetchone()
        
        if count > 0:
            qm.warning(self, 'Atención', 
                       'No se puede eliminar este producto debido '
                       'a que hay ventas que lo incluyen.', qm.Ok)
            return
        
        # abrir pregunta
        ret = qm.question(self, 'Atención',
                          'El producto seleccionado se eliminará de la base de datos. '
                          '¿Desea continuar?',
                          qm.Yes | qm.No)
        
        if ret != qm.Yes:
            return
        
        try:
            crsr.execute('DELETE FROM ProductosUtilizaInventario WHERE idProductos = ?;', (idProducto,))
            crsr.execute('DELETE FROM ProductosIntervalos WHERE idProductos = ?;', (idProducto,))
            crsr.execute('DELETE FROM Productos WHERE idProductos = ?;', (idProducto,))
            
            conn.commit()
        except fdb.Error as err:
            conn.rollback()

            WarningDialog(self, '¡No se pudo eliminar el producto!', str(err))
            return
        
        qm.information(self, 'Éxito', 'Se eliminó el producto seleccionado.', qm.Ok)
        self.update_display(rescan=True)        
    
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
class App_EditarProducto(QtWidgets.QMainWindow):
    """
    Backend para la ventana para editar un producto de la base de datos.
    """
    def __init__(self, first, idx: int = None):
        from AdministrarProductos.Ui_EditarProducto import Ui_EditarProducto
        
        super().__init__(first)

        self.ui = Ui_EditarProducto()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)
        
        self.first = first # ventana de administrar productos
        self.session = first.session # conexión a la base de datos y usuario actual
        self.idx = idx  # id del elemento a editar
        
        # eventos para botones
        self.ui.btAceptar.clicked.connect(self.done)
        self.ui.btAgregar.clicked.connect(lambda _: self.agregarProductoALista())
        self.ui.lbAgregar.mousePressEvent = self.agregarIntervalo
        self.ui.lbQuitar.mousePressEvent = self.quitarIntervalo
        self.ui.lbRegresar.mousePressEvent = self.closeEvent
        
        if not idx:  # elemento no existente
            self.show()
            return
        
        crsr = first.session['conn'].cursor()
        
        # datos de la primera página
        crsr.execute('SELECT * FROM Productos WHERE idProductos = ?;', (idx,))
        
        _, codigo, descripcion, abreviado, categoria = crsr.fetchone()
        
        self.ui.txtCodigo.setText(codigo)
        self.ui.txtDescripcion.setPlainText(descripcion)
        self.ui.txtNombre.setText(abreviado)
        
        if categoria == 'S':
            self.ui.tabWidget.setCurrentIndex(0)
            
            # agregar intervalos de precios a la tabla
            crsr.execute('''
            SELECT	desde,
                    precioConIVA,
                    duplex
            FROM	ProductosIntervalos AS PInv
            WHERE 	idProductos = ?
            ORDER   BY desde ASC, duplex ASC;
            ''', (idx,))
            
            for row, (intervalo, precio, duplex) in enumerate(crsr):
                self.ui.tabla_precios.insertRow(row)
                
                item = QtWidgets.QTableWidgetItem(f'{intervalo:,.2f}')
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.ui.tabla_precios.setItem(row, 0, item)
                
                item = QtWidgets.QTableWidgetItem(f'{precio:,.2f}')
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.ui.tabla_precios.setItem(row, 1, item)

                widget = QtWidgets.QWidget()
                widget.setMinimumHeight(32)
                layout = QtWidgets.QHBoxLayout(widget)
                layout.setAlignment(Qt.AlignCenter)
                checkbox = QtWidgets.QCheckBox(widget)
                checkbox.setChecked(duplex)
                layout.addWidget(checkbox)
                self.ui.tabla_precios.setCellWidget(row, 2, widget)
        elif categoria == 'G':
            self.ui.tabWidget.setCurrentIndex(1)
            
            crsr.execute('''
            SELECT  min_ancho,
                    min_alto,
                    precio_m2
            FROM    Productos_granformato
            WHERE 	idProductos = ?;
            ''', (idx,))
            
            try:
                min_ancho, min_alto, precio = crsr.fetchone()
                
                self.ui.txtAnchoMin.setText(f'{min_ancho:,.2f}')
                self.ui.txtAltoMin.setText(f'{min_alto:,.2f}')
                self.ui.txtPrecio.setText(f'{precio:,.2f}')
            except:
                pass
        
        # agregar elementos de la segunda página
        crsr.execute('''
        SELECT	nombre,
                utilizaInventario
        FROM	ProductosUtilizaInventario AS PUI
                LEFT JOIN Inventario AS I
                        ON PUI.idInventario = I.idInventario
        WHERE 	idProductos = ?;
        ''', (idx,))
                
        for nombre, cantidad in crsr:
            self.agregarProductoALista(nombre, cantidad)

        self.show()
    
    ##################################
    # WIDGET PARA LISTA DE PRODUCTOS #
    ##################################
    def widgetElemento(self):
        from PyQt5 import QtCore
        
        frameProducto = QtWidgets.QFrame()
        frameProducto.resize(390, 70)
        frameProducto.setMinimumSize(390, 70)
        boxProducto = QtWidgets.QComboBox(frameProducto)
        boxProducto.setGeometry(QtCore.QRect(35, 10, 271, 22))
        boxProducto.setMinimumSize(QtCore.QSize(271, 22))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        boxProducto.setFont(font)
        lbContador = QtWidgets.QLabel(frameProducto)
        lbContador.setGeometry(QtCore.QRect(5, 10, 21, 21))
        lbContador.setMinimumSize(QtCore.QSize(21, 21))
        lbContador.setPixmap(QtGui.QPixmap(":/img/resources/images/inventory.png"))
        lbContador.setScaledContents(True)
        lbEliminar = QtWidgets.QLabel(frameProducto)
        lbEliminar.setGeometry(QtCore.QRect(343, 12, 35, 35))
        lbEliminar.setMinimumSize(QtCore.QSize(35, 35))
        lbEliminar.setPixmap(QtGui.QPixmap(":/img/resources/images/cancel.png"))
        lbEliminar.setScaledContents(True)
        lbEliminar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        label = QtWidgets.QLabel(frameProducto)
        label.setGeometry(QtCore.QRect(35, 40, 271, 21))
        label.setMinimumSize(QtCore.QSize(271, 21))
        label.setFont(font)
        label.setText("se usa            unidades de este elemento.")
        txtProductoUtiliza = QtWidgets.QLineEdit(frameProducto)
        txtProductoUtiliza.setGeometry(QtCore.QRect(84, 40, 39, 20))
        txtProductoUtiliza.setMinimumSize(QtCore.QSize(39, 20))
        txtProductoUtiliza.setFont(font)
        QtCore.QMetaObject.connectSlotsByName(frameProducto)
        
        return frameProducto
    
    ####################
    # FUNCIONES ÚTILES #
    ####################
    def agregarIntervalo(self, _):
        tabla = self.ui.tabla_precios
        
        if (idx := tabla.selectedIndexes()):
            row = idx[0].row() + 1
        else:
            row = tabla.rowCount()    
        tabla.insertRow(row)
        
        tabla.setItem(row, 0, QtWidgets.QTableWidgetItem(''))
        tabla.setItem(row, 1, QtWidgets.QTableWidgetItem(''))
        
        widget = QtWidgets.QWidget()
        widget.setMinimumHeight(32)
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        checkbox = QtWidgets.QCheckBox(widget)
        layout.addWidget(checkbox)
        self.ui.tabla_precios.setCellWidget(row, 2, widget)
    
    def quitarIntervalo(self, _):
        tabla = self.ui.tabla_precios
        
        if (idx := tabla.selectedIndexes()):
            row = idx[0].row()
        else:
            row = tabla.rowCount() - 1
        tabla.removeRow(row)
    
    def agregarProductoALista(self, nombre: str = '', cantidad: int = 1):
        # crear widget y agregar a la lista
        nuevo = self.widgetElemento()
        box, _, lbCancelar, _, line = nuevo.children()
        
        # evento para eliminar la entrada
        lbCancelar.mousePressEvent = lambda _: self.ui.layoutScroll.removeWidget(nuevo) \
                                               or nuevo.setParent(None)
        
        # validador para datos numéricos
        regexp_numero = QRegExp(r'\d*\.?\d*')
        validador = QtGui.QRegExpValidator(regexp_numero)
        line.setValidator(validador)
        
        # llenar caja de opciones con productos
        crsr = self.session['conn'].cursor()
        
        crsr.execute('SELECT nombre FROM Inventario;')
        box.addItems([nombre for nombre, in crsr])
        
        # modificar valores a los de la base de datos
        box.setCurrentText(nombre)
        line.setText(f'{cantidad}')
        
        self.ui.layoutScroll.addWidget(nuevo)
    
    def done(self):
        """
        Actualiza la base de datos y sale de la ventana.
        """
        qm = QtWidgets.QMessageBox
        categoria = ['S', 'G'][self.ui.tabWidget.currentIndex()]
        
        # <tabla Productos>
        productos_db_parametros = (
            self.ui.txtCodigo.text().strip() or None,
            self.ui.txtDescripcion.toPlainText().strip() or None,
            self.ui.txtNombre.text() or None,
            categoria
        )

        conn = self.session['conn']
        crsr = conn.cursor()

        try:
            if self.idx:        # el producto no existe
                crsr.execute('''
                UPDATE  Productos
                SET     codigo = ?,
                        descripcion = ?,
                        abreviado = ?,
                        categoria = ?
                WHERE   idProductos = ?;
                ''', (*productos_db_parametros, self.idx))
            else:                   # actualizar producto
                crsr.execute('''
                INSERT INTO Productos (
                    codigo, descripcion, abreviado, categoria
                )
                VALUES
                    (?,?,?,?)
                RETURNING
                    idProductos;
                ''', productos_db_parametros)
                
                self.idx, = crsr.fetchone()
        except fdb.Error as err:
            WarningDialog(self, '¡No se pudo editar el producto!', str(err))
            return
        # </tabla Productos>
        
        # <tabla ProductosUtilizaInventario>
        elementos = self.ui.scrollAreaLista.children()[1:]  # QFrames
        elementos = [elem.children() for elem in elementos] # hijos de cada QFrame
        
        try:
            elementos = [(box.currentText(), float(line.text()))    # codigo y cantidad
                         for (box, _, _, _, line) in elementos]
        except ValueError:
            qm.warning(self, 'Atención', '¡Verifique que los datos en la lista de materia prima sean correctos!', qm.Ok)
            return
        
        PUI_db_parametros = []
            
        for nombre, cantidad in elementos:
            if not nombre or cantidad < 1:
                return 
            
            crsr.execute('SELECT idInventario FROM Inventario WHERE nombre = ?;', (nombre,))
            idInventario, = crsr.fetchone()
            
            PUI_db_parametros.append((self.idx, idInventario, cantidad))

        # primero borrar las entradas existentes
        crsr.execute('''
        DELETE  FROM ProductosUtilizaInventario
        WHERE   idProductos = ?;
        ''', (self.idx,))
        
        try:    
            # nuevas entradas, introducidas por el usuario
            crsr.executemany('''
            INSERT INTO ProductosUtilizaInventario (
                idProductos, idInventario, utilizaInventario
            )
            VALUES
                (?,?,?);
            ''', PUI_db_parametros)
        except fdb.Error as err:            
            WarningDialog(self, '¡No se pudo editar el producto!', str(err))
            return
        # </tabla ProductosUtilizaInventario>
        
        # <tabla ProductosIntervalos>
        crsr.execute('DELETE FROM ProductosIntervalos WHERE idProductos = ?;', (self.idx,))
        crsr.execute('DELETE FROM Productos_Granformato WHERE idProductos = ?;', (self.idx,))
        
        if categoria == 'S':
            tabla = self.ui.tabla_precios
            Prod_db_parametros = []
            
            for row in range(tabla.rowCount()):
                desde = tabla.item(row, 0).text().replace(',', '')
                precio = tabla.item(row, 1).text().replace(',', '')
                duplex = tabla.cellWidget(row, 2).children()[1].isChecked()
                
                try:
                    Prod_db_parametros.append((self.idx, float(desde), float(precio), duplex))
                except ValueError:
                    qm.warning(self, 'Atención', '¡Verifique que los datos en la tabla de precio sean correctos!', qm.Ok)
                    return
            
            query = '''
            INSERT INTO ProductosIntervalos (
                idProductos, desde, precioConIVA, duplex
            )
            VALUES
                (?,?,?,?);
            '''
        elif categoria == 'G':
            Prod_db_parametros = [(
                self.idx,
                self.ui.txtAnchoMin.text(),
                self.ui.txtAltoMin.text(),
                self.ui.txtPrecio.text())]
            
            query = '''
            INSERT INTO Productos_Granformato (
                idProductos, min_ancho, min_alto, precio_m2
            )
            VALUES
                (?,?,?,?);
            '''
        
        try:
            # nuevas entradas, introducidas por el usuario
            crsr.executemany(query, Prod_db_parametros)
            conn.commit()
        except fdb.Error as err:
            conn.rollback()
            
            WarningDialog(self, '¡No se pudo editar el producto!', str(err))
            return
        # </tabla ProductosIntervalos>
        
        qm.information(self, 'Éxito', '¡Se editó el producto!', qm.Ok)
        
        self.first.update_display(rescan=True)
        self.close()
