from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QRegExp

from myutils import lbAdvertencia, ColorsEnum, son_similar
from mydecorators import con_fondo
from mywidgets import WarningDialog

import fdb

class App_AdministrarInventario(QtWidgets.QMainWindow):
    """
    Backend para la ventana de administración de inventario.
    TODO:
    -   alimentar inventario por mayoreo pero monitorear por unidades
    """
    def __init__(self, parent=None):
        from AdministrarInventario.Ui_AdministrarInventario import Ui_AdministrarInventario
        
        super().__init__()

        self.ui = Ui_AdministrarInventario()
        self.ui.setupUi(self)

        self.session = parent.session  # conexión y usuario actual
        self.filtro = 1
        
        lbAdvertencia(self.ui.tabla_inventario, '¡No se encontró ningún elemento!')

        # añadir menú de opciones al botón para filtrar
        popup = QtWidgets.QMenu()

        default = popup.addAction('Nombre', lambda: self.cambiar_filtro('nombre'))
        popup.addAction('Teléfono', lambda: self.cambiar_filtro('teléfono'))
        popup.setDefaultAction(default)

        self.ui.btFiltrar.setMenu(popup)
        self.ui.btFiltrar.clicked.connect(lambda: self.cambiar_filtro('nombre'))

        # dar formato a la tabla principal
        header = self.ui.tabla_inventario.horizontalHeader()
        
        for col in range(self.ui.tabla_inventario.columnCount()):
            if col == 0:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)

        # añade eventos para los botones
        self.ui.lbAgregar.mousePressEvent = self.agregarInventario
        self.ui.lbEditar.mousePressEvent = self.editarInventario
        self.ui.lbQuitar.mousePressEvent = self.quitarInventario
        self.ui.lbRegresar.mousePressEvent = self.goHome
        self.ui.searchBar.textChanged.connect(lambda : self.update_display())
    
    def showEvent(self, event):
        self.update_display(rescan=True)
    
    def resizeEvent(self, event):
        if self.isVisible():
            self.ui.tabla_inventario.resizeRowsToContents()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def generarCodigoQR(self, lista: list[tuple]):
        """
        Genera un código QR que codifica una lista de tuplas.
        Las tuplas contienen dos números: (idInventario, cantidad).
        """
        """import qrcode
        
        data = f't = {str(lista)}'
        
        img = qrcode.make(data)
        img.save('MyQRCode1.png')"""
    
    def cambiar_filtro(self, *args):
        ...
        self.update_display()
    
    def update_display(self, rescan: bool = False):
        """
        Actualiza la tabla y el contador de elementos.
        Acepta una cadena de texto para la búsqueda de elementos.
        También lee de nuevo la tabla de elementos, si se desea.
        """
        if rescan:
            crsr = self.session['conn'].cursor()
            crsr.execute('SELECT * FROM Inventario;')

            self.all = crsr.fetchall()
            self.ui.lbContador.setText(f'{len(self.all)} elementos en la base de datos.')
        
        tabla = self.ui.tabla_inventario
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
                if isinstance(dato, int):
                    cell = f'{dato:,d}'
                elif isinstance(dato, float):
                    cell = f'{dato:,.2f}'
                else:
                    cell = str(dato or '')
                tabla.setItem(row, col, QtWidgets.QTableWidgetItem(cell))
            
            tabla.item(row, 1).setFont(bold)
            
            # resaltar si hay menos cantidad que el mínimo
            if item[3] < item[4]:
                color = QtGui.QColor(ColorsEnum.ROJO)
                tabla.item(row, 3).setBackground(color)

        tabla.resizeRowsToContents()
    
    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def agregarInventario(self, _):
        self.new = App_EditarInventario(self)
    
    def editarInventario(self, _):
        selected = self.ui.tabla_inventario.selectedItems()
        
        if selected:        
            self.new = App_EditarInventario(self, selected[0].text())
    
    def quitarInventario(self, _):
        """
        Elimina un material de la base de datos.
        Primero se verifica si hay productos que lo utilizan.
        """
        try:
            idInventario = self.ui.tabla_inventario.selectedItems()[0].text()
        except IndexError:
            return
        
        qm = QtWidgets.QMessageBox
        
        conn = self.session['conn']
        crsr = conn.cursor()
        
        crsr.execute('''
        SELECT	idProductos
        FROM	ProductosUtilizaInventario
        WHERE	idInventario = ?;
        ''', (idInventario,))
        
        if crsr.fetchall():
            qm.warning(self, 'Atención', 
                       'No se puede eliminar este elemento debido '
                       'a que hay productos que lo utilizan. Haga doble '
                       'click en algún elemento para ver estos productos.',
                       qm.Ok)
            return
        
        # abrir pregunta
        ret = qm.question(self, 'Atención',
                          'El elemento seleccionado se eliminará de la base de datos. '
                          '¿Desea continuar?',
                          qm.Yes | qm.No)
        
        if ret != qm.Yes:
            return
        
        # crea un cuadro que notifica el resultado de la operación
        try:
            crsr.execute('DELETE FROM Inventario WHERE idInventario = ?;', (idInventario,))
            conn.commit()
        except fdb.Error as err:
            conn.rollback()

            WarningDialog(self, '¡No se pudo eliminar el elemento!', str(err))
            return
        
        qm.information(self, 'Éxito', 'Se eliminó el elemento seleccionado.', qm.Ok)
        self.update_display(rescan=True)
    
    def enviarLote(self):
        ...
    
    def recibirLote(self):
        ...
    
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
class App_EditarInventario(QtWidgets.QMainWindow):
    """
    Backend para la ventana para editar un material del inventario.
    """
    def __init__(self, first, idx: int = None):
        from AdministrarInventario.Ui_EditarInventario import Ui_EditarInventario
        
        super().__init__(first)

        self.ui = Ui_EditarInventario()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)
        
        self.first = first # ventana de administrar inventario
        self.session = first.session # conexión a la base de datos y usuario actual
        self.idx = idx  # id del elemento a editar
        
        if idx:     # elemento existente
            crsr = first.session['conn'].cursor()
            
            # datos de la primera página
            crsr.execute('SELECT * FROM Inventario WHERE idInventario = ?;', (idx,))
            
            _, nombre, precio, existencia, minimo = crsr.fetchone()
            
            self.ui.txtNombre.setText(nombre)
            self.ui.txtPrecioCompra.setText(f'{precio:.2f}')
            self.ui.txtExistencia.setText(f'{existencia:.2f}')
            self.ui.txtMinimo.setText(f'{minimo:.2f}')
            
            # agregar productos de la segunda página
            crsr.execute('''
            SELECT	codigo,
                    utilizaInventario
            FROM	ProductosUtilizaInventario AS PUI
                    LEFT JOIN Productos AS P
                           ON PUI.idProductos = P.idProductos
            WHERE 	idInventario = ?;
            ''', (idx,))
            
            productos = crsr.fetchall()
                    
            for codigo, cantidad in productos:
                self.agregarProductoALista(codigo, cantidad)
        
        # validadores para datos numéricos
        regexp_numero = QRegExp(r'\d*\.?\d*')
        validador = QtGui.QRegExpValidator(regexp_numero)
        
        self.ui.txtPrecioCompra.setValidator(validador)
        self.ui.txtExistencia.setValidator(validador)
        self.ui.txtMinimo.setValidator(validador)
        self.ui.txtCantidadAgregar.setValidator(validador)

        # evento para botón de regresar
        self.ui.btAceptar.clicked.connect(self.done)
        self.ui.btAgregar.clicked.connect(lambda _: self.agregarProductoALista())
        self.ui.btSumar.clicked.connect(self.sumar_existencia)
        self.ui.btRestar.clicked.connect(self.restar_existencia)
        self.ui.lbRegresar.mousePressEvent = self.closeEvent

        self.show()
    
    ##################################
    # WIDGET PARA LISTA DE PRODUCTOS #
    ##################################
    def widgetProducto(self):
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
        lbContador.setPixmap(QtGui.QPixmap(":/img/resources/images/package_2.png"))
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
        label.setText("utiliza              unidades de este elemento.")
        txtProductoUtiliza = QtWidgets.QLineEdit(frameProducto)
        txtProductoUtiliza.setGeometry(QtCore.QRect(80, 40, 41, 20))
        txtProductoUtiliza.setMinimumSize(QtCore.QSize(41, 20))
        txtProductoUtiliza.setFont(font)
        QtCore.QMetaObject.connectSlotsByName(frameProducto)
        
        return frameProducto
    
    ####################
    # FUNCIONES ÚTILES #
    ####################
    def sumar_existencia(self):
        try:
            nueva_existencia = float(self.ui.txtExistencia.text()) \
                               + float(self.ui.txtCantidadAgregar.text())
                            
            self.ui.txtExistencia.setText(f'{nueva_existencia:.2f}')
        except ValueError:
            return
    
    def restar_existencia(self):
        try:
            nueva_existencia = float(self.ui.txtExistencia.text()) \
                               - float(self.ui.txtCantidadAgregar.text())
                            
            self.ui.txtExistencia.setText(f'{nueva_existencia:.2f}')
        except ValueError:
            return
    
    def agregarProductoALista(self, codigo: str = '', cantidad: int = 1):
        # crear widget y agregar a la lista
        nuevo = self.widgetProducto()
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
        
        crsr.execute('SELECT codigo FROM Productos;')
        box.addItems([codigo for codigo, in crsr])
        
        # modificar valores a los de la base de datos
        box.setCurrentText(codigo)
        line.setText(f'{cantidad}')
        
        self.ui.layoutScroll.addWidget(nuevo)
    
    def done(self):
        """
        Actualiza la base de datos y sale de la ventana.
        """
        qm = QtWidgets.QMessageBox
        
        # <tabla Inventario>
        try:
            inventario_db_parametros = (
                self.ui.txtNombre.text().strip() or None,
                float(self.ui.txtPrecioCompra.text()),
                float(self.ui.txtExistencia.text()),
                float(self.ui.txtMinimo.text())
            )
        except ValueError:
            qm.warning(self, 'Atención', '¡Verifique que los datos numéricos sean correctos!', qm.Ok)
            return
        
        conn = self.session['conn']
        crsr = conn.cursor()

        try:
            if self.idx:        # el elemento no existe
                crsr.execute('''
                UPDATE  Inventario
                SET     nombre = ?,
                        precioCompra = ?,
                        enExistencia = ?,
                        minimo = ?
                WHERE   idInventario = ?;
                ''', (*inventario_db_parametros, self.idx))
            else:                   # actualizar elemento
                crsr.execute('''
                INSERT INTO Inventario (
                    nombre, precioCompra,
                    enExistencia, minimo
                )
                VALUES
                    (?,?,?,?)
                RETURNING
                    idInventario;
                ''', inventario_db_parametros)
                
                self.idx, = crsr.fetchone()
        except fdb.Error as err:
            WarningDialog(self, '¡No se pudo editar el elemento!', str(err))
            return
        # </tabla Inventario>
        
        # <tabla ProductosUtilizaInventario>
        productos = self.ui.scrollAreaLista.children()[1:]  # QFrames
        productos = [prod.children() for prod in productos] # hijos de cada QFrame
        
        try:
            productos = [(box.currentText(), float(line.text()))    # codigo y cantidad
                         for (box, _, _, _, line) in productos]
        except ValueError:
            qm.warning(self, 'Atención', '¡Verifique que los datos numéricos sean correctos!', qm.Ok)
            return
        
        PUI_db_parametros = []
            
        for codigo, cantidad in productos:
            if not codigo or cantidad < 1:
                return
            
            crsr.execute('SELECT idProductos FROM Productos WHERE codigo = ?;', (codigo,))
            idProducto, = crsr.fetchone()
            
            PUI_db_parametros.append((idProducto, self.idx, cantidad))

        try:
            # primero borrar las entradas existentes
            crsr.execute('''
            DELETE  FROM ProductosUtilizaInventario
            WHERE   idInventario = ?;
            ''', (self.idx,))
            
            # nuevas entradas, introducidas por el usuario
            crsr.executemany('''
            INSERT INTO ProductosUtilizaInventario (
                idProductos, idInventario, utilizaInventario
            )
            VALUES
                (?,?,?);
            ''', PUI_db_parametros)
            
            conn.commit()
        except fdb.Error as err:
            conn.rollback()
            
            WarningDialog(self, '¡No se pudo editar el elemento!', str(err))
            return
        # </tabla ProductosUtilizaInventario>
        
        qm.information(self, 'Éxito', '¡Se editó el elemento!', qm.Ok)
        
        self.first.update_display(rescan=True)
        self.close()
