from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QColor, QPixmap, QCursor, QRegExpValidator
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
        
        # añadir menú de opciones al botón para filtrar
        popup = QtWidgets.QMenu()

        default = popup.addAction(
            'Código', lambda: self.cambiar_filtro('código', 1))
        popup.addAction(
            'Descripción', lambda: self.cambiar_filtro('descripción', 2))
        popup.setDefaultAction(default)

        self.ui.btFiltrar.setMenu(popup)
        self.ui.btFiltrar.clicked.connect(lambda: self.cambiar_filtro('código', 1))
        
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
    def cambiar_filtro(self, filtro, idx):
        """
        Modifica el filtro de búsqueda.
        """
        self.filtro = idx
        self.ui.searchBar.setPlaceholderText(f'Busque producto por {filtro}...')
        
        if self.ui.searchBar.text():
            self.update_display()
            
    def update_display(self, rescan: bool = False):
        """
        Actualiza la tabla y el contador de productos.
        Acepta una cadena de texto para la búsqueda de productos.
        También lee de nuevo la tabla de productos, si se desea.
        """
        if rescan:
            crsr = self.session['conn'].cursor()
            
            crsr.execute('''
            WITH Costo_Produccion (id_productos, costo) AS (
            SELECT	P.id_productos,
                    SUM(
                        COALESCE(PUI.utiliza_inventario * I.precio_unidad, 
                                0.0)
                    ) AS costo
            FROM  	Productos AS P
                    LEFT JOIN Productos_Utiliza_Inventario AS PUI
                           ON P.id_productos = PUI.id_productos
                    LEFT JOIN Inventario AS I
                           ON PUI.id_inventario = I.id_inventario
            GROUP	BY P.id_productos
            ORDER	BY P.id_productos ASC
            )

            SELECT  P.id_productos,
                    P.codigo,
                    P.descripcion 
                        || IIF(desde > 1, ', desde ' || ROUND(desde, 1) || ' unidades ', '')
                        || IIF(P_Inv.duplex, ' [PRECIO DUPLEX]', ''),
                    P.abreviado,
                    COALESCE(P_gran.precio_m2, P_Inv.precio_con_iva) AS precio_con_iva, 
                    COALESCE(P_gran.precio_m2, P_Inv.precio_con_iva) / 1.16 AS precio_sin_iva,
                    C_Prod.costo,
                    COALESCE(P_gran.precio_m2, P_Inv.precio_con_iva) - C_Prod.costo AS utilidad
            FROM    Productos AS P
                    LEFT JOIN Productos_Intervalos AS P_Inv
                           ON P_Inv.id_productos = P.id_productos
                    LEFT JOIN Productos_Gran_Formato AS P_gran
                           ON P.id_productos = P_gran.id_productos
                    LEFT JOIN Costo_Produccion AS C_Prod
                           ON P.id_productos = C_Prod.id_productos
            ORDER   BY P.id_productos, desde ASC;
            ''')

            self.all = crsr.fetchall()
            self.ui.lbContador.setText(f'{len(self.all)} productos en la base de datos.')
        
        tabla = self.ui.tabla_productos
        tabla.setRowCount(0)
        
        bold = QFont()
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
                color = QColor(ColorsEnum.ROJO)
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
        SELECT	COUNT(id_productos)
        FROM	Ventas_Detallado
        WHERE	id_productos = ?;
        ''', (idProducto,))
        
        # numero de ventas que contienen este producto
        count, = crsr.fetchone()
        
        if count > 0:
            qm.warning(self, 'Atención', 
                       'No se puede eliminar este producto debido '
                       'a que hay ventas que lo incluyen.')
            return
        
        # abrir pregunta
        ret = qm.question(self, 'Atención',
                          'El producto seleccionado se eliminará de la base de datos. '
                          '¿Desea continuar?',
                          qm.Yes | qm.No)
        
        if ret != qm.Yes:
            return
        
        try:
            crsr.execute('DELETE FROM Productos_Utiliza_Inventario WHERE id_productos = ?;', (idProducto,))
            crsr.execute('DELETE FROM Productos_Gran_Formato WHERE id_productos = ?;', (idProducto,))
            crsr.execute('DELETE FROM Productos_Intervalos WHERE id_productos = ?;', (idProducto,))
            crsr.execute('DELETE FROM Productos WHERE id_productos = ?;', (idProducto,))
            
            conn.commit()
        except fdb.Error as err:
            conn.rollback()

            WarningDialog(self, '¡No se pudo eliminar el producto!', str(err))
            return
        
        qm.information(self, 'Éxito', 'Se eliminó el producto seleccionado.')
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
        
        # formato tabla de precios
        header = self.ui.tabla_precios.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        
        # eventos para botones
        self.ui.btAceptar.clicked.connect(self.done)
        self.ui.btAgregar.clicked.connect(lambda: self.agregarProductoALista())
        self.ui.lbAgregar.mousePressEvent = lambda _: self.agregarIntervalo(row=self.ui.tabla_precios.rowCount())
        self.ui.lbQuitar.mousePressEvent = self.quitarIntervalo
        self.ui.lbRegresar.mousePressEvent = self.closeEvent
        
        if not idx:  # elemento no existente
            self.show()
            return
        
        crsr = first.session['conn'].cursor()
        
        # datos de la primera página
        crsr.execute('SELECT * FROM Productos WHERE id_productos = ?;', (idx,))
        
        _, codigo, descripcion, abreviado, categoria = crsr.fetchone()
        
        self.ui.txtCodigo.setText(codigo)
        self.ui.txtDescripcion.setPlainText(descripcion)
        self.ui.txtNombre.setText(abreviado)
        
        if categoria == 'S':
            self.ui.tabWidget.setCurrentIndex(0)
            
            # agregar intervalos de precios a la tabla
            crsr.execute('''
            SELECT	desde,
                    precio_con_iva,
                    duplex
            FROM	Productos_Intervalos AS P_Inv
            WHERE 	id_productos = ?
            ORDER   BY desde ASC, duplex ASC;
            ''', (idx,))
            
            for row, (desde, precio, duplex) in enumerate(crsr):
                self.agregarIntervalo(row, desde, precio, duplex)
        elif categoria == 'G':
            self.ui.tabWidget.setCurrentIndex(1)
            
            crsr.execute('''
            SELECT  min_ancho,
                    min_alto,
                    precio_m2
            FROM    Productos_Gran_Formato
            WHERE 	id_productos = ?;
            ''', (idx,))
        
            min_ancho, min_alto, precio = crsr.fetchone()
            
            self.ui.txtAnchoMin.setText(f'{min_ancho:,.2f}')
            self.ui.txtAltoMin.setText(f'{min_alto:,.2f}')
            self.ui.txtPrecio.setText(f'{precio:,.2f}')
        
        # agregar elementos de la segunda página
        crsr.execute('''
        SELECT	nombre,
                utiliza_inventario
        FROM	Productos_Utiliza_Inventario AS PUI
                LEFT JOIN Inventario AS I
                        ON PUI.id_inventario = I.id_inventario
        WHERE 	id_productos = ?;
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
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        boxProducto.setFont(font)
        lbContador = QtWidgets.QLabel(frameProducto)
        lbContador.setGeometry(QtCore.QRect(5, 10, 21, 21))
        lbContador.setMinimumSize(QtCore.QSize(21, 21))
        lbContador.setPixmap(QPixmap(":/img/resources/images/inventory.png"))
        lbContador.setScaledContents(True)
        lbEliminar = QtWidgets.QLabel(frameProducto)
        lbEliminar.setGeometry(QtCore.QRect(343, 12, 35, 35))
        lbEliminar.setMinimumSize(QtCore.QSize(35, 35))
        lbEliminar.setPixmap(QPixmap(":/img/resources/images/cancel.png"))
        lbEliminar.setScaledContents(True)
        lbEliminar.setCursor(QCursor(Qt.PointingHandCursor))
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
    def agregarIntervalo(self, row: int, desde: float = 0., 
                         precio: float = 0., duplex: bool = False):
        """
        Agrega entrada a la tabla de precios.
        """ 
        self.ui.tabla_precios.insertRow(row)
        
        cell = QtWidgets.QTableWidgetItem(f'{desde:,.2f}' if desde else '')
        cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ui.tabla_precios.setItem(row, 0, cell)
        
        cell = QtWidgets.QTableWidgetItem(f'{precio:,.2f}' if precio else '')
        cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ui.tabla_precios.setItem(row, 1, cell)
        
        widget = QtWidgets.QWidget()
        widget.setMinimumHeight(32)
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        checkbox = QtWidgets.QCheckBox(widget)
        checkbox.setChecked(duplex)
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
        validador = QRegExpValidator(regexp_numero)
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
        categoria = ['S','G'][self.ui.tabWidget.currentIndex()]
        
        #### <tabla Productos> ####
        productos_db_parametros = (
            self.ui.txtCodigo.text().strip() or None,
            self.ui.txtDescripcion.toPlainText().strip() or None,
            self.ui.txtNombre.text() or None,
            categoria
        )

        conn = self.session['conn']
        crsr = conn.cursor()

        try:
            if self.idx:        # actualizar producto
                idx = self.idx
                
                crsr.execute('''
                UPDATE  Productos
                SET     codigo = ?,
                        descripcion = ?,
                        abreviado = ?,
                        categoria = ?
                WHERE   id_productos = ?;
                ''', (*productos_db_parametros, idx))
            else:                # el producto no existe
                crsr.execute('''
                INSERT INTO Productos (
                    codigo, descripcion, abreviado, categoria
                )
                VALUES
                    (?,?,?,?)
                RETURNING
                    id_productos;
                ''', productos_db_parametros)
                
                idx, = crsr.fetchone()
        except fdb.Error as err:
            conn.rollback()
            WarningDialog(self, '¡No se pudo editar el producto!', str(err))
            return
        #### </tabla Productos> ####
        
        #### <tabla Productos_Utiliza_Inventario> ####
        elementos = self.ui.scrollAreaLista.children()[1:]  # QFrames
        elementos = [elem.children() for elem in elementos] # hijos de cada QFrame
        
        try:
            elementos = [(box.currentText(), float(line.text()))    # codigo y cantidad
                         for (box, _, _, _, line) in elementos]
        except ValueError:
            conn.rollback()
            qm.warning(self, 'Atención', '¡Verifique que los datos en la lista de materia prima sean correctos!')
            return
        
        PUI_db_parametros = []
            
        for nombre, cantidad in elementos:
            if not nombre or cantidad < 1:
                conn.rollback()
                return 
            
            crsr.execute('SELECT id_inventario FROM Inventario WHERE nombre = ?;', (nombre,))
            id_inventario, = crsr.fetchone()
            
            PUI_db_parametros.append((idx, id_inventario, cantidad))

        # primero borrar las entradas existentes
        crsr.execute('''
        DELETE  FROM Productos_Utiliza_Inventario
        WHERE   id_productos = ?;
        ''', (idx,))
        
        try:    
            # nuevas entradas, introducidas por el usuario
            crsr.executemany('''
            INSERT INTO Productos_Utiliza_Inventario (
                id_productos, id_inventario, utiliza_inventario
            )
            VALUES
                (?,?,?);
            ''', PUI_db_parametros)
        except fdb.Error as err:
            conn.rollback()
            WarningDialog(self, '¡No se pudo editar el producto!', str(err))
            return
        #### </tabla Productos_Utiliza_Inventario> ####
        
        #### <tabla Productos_Intervalos> ####
        crsr.execute('DELETE FROM Productos_Intervalos WHERE id_productos = ?;', (idx,))
        crsr.execute('DELETE FROM Productos_Gran_Formato WHERE id_productos = ?;', (idx,))
        
        if categoria == 'S':
            tabla = self.ui.tabla_precios
            Prod_db_parametros = []
            
            if self.ui.tabla_precios.rowCount() == 0:
                conn.rollback()
                qm.warning(self, 'Atención', '¡Tabla de precios vacía!')
                return
            
            for row in range(tabla.rowCount()):
                desde = tabla.item(row, 0).text().replace(',', '')
                precio = tabla.item(row, 1).text().replace(',', '')
                duplex = tabla.cellWidget(row, 2).children()[1].isChecked()
                
                try:
                    Prod_db_parametros.append((idx, float(desde), float(precio), duplex))
                except ValueError:
                    conn.rollback()
                    qm.warning(self, 'Atención', '¡Verifique que los datos en la tabla de precio sean correctos!')
                    return
            
            query = '''
            INSERT INTO Productos_Intervalos (
                id_productos, desde, precio_con_iva, duplex
            )
            VALUES
                (?,?,?,?);
            '''
        elif categoria == 'G':
            try:
                Prod_db_parametros = [(
                    idx,
                    float(self.ui.txtAnchoMin.text()),
                    float(self.ui.txtAltoMin.text()),
                    float(self.ui.txtPrecio.text()))]
            except ValueError:
                conn.rollback()
                qm.warning(self, 'Atención', '¡Datos incorrectos!')
                return
            
            query = '''
            INSERT INTO Productos_Gran_Formato (
                id_productos, min_ancho, min_alto, precio_m2
            )
            VALUES
                (?,?,?,?);
            '''
        
        try:
            crsr.executemany(query, Prod_db_parametros)
            conn.commit()
        except fdb.Error as err:
            conn.rollback()
            WarningDialog(self, '¡No se pudo editar el producto!', str(err))
            return
        #### </tabla Productos_Intervalos> ####
        
        qm.information(self, 'Éxito', '¡Se editó el producto!')
        
        self.first.update_display(rescan=True)
        self.close()
