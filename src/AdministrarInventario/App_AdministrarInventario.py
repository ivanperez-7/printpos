import fdb

from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QColor, QPixmap, QIcon, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp, pyqtSignal

from mydecorators import con_fondo
from myutils import ColorsEnum, DatabaseManager, son_similar
from mywidgets import LabelAdvertencia, VentanaPrincipal


###########################################
# CLASE PARA MANEJAR OPERACIONES EN LA DB #
###########################################
class ManejadorInventario(DatabaseManager):
    """ Clase para manejar sentencias hacia/desde la tabla Inventario. """
    def __init__(self, conn: fdb.Connection, error_txt: str = ''):
        super().__init__(conn, error_txt)
    
    def obtenerTablaPrincipal(self):
        """ Sentencia para alimentar tabla principal de elementos. """
        return self.fetchall('''
            SELECT  id_inventario,
                    nombre,
                    tamano_lote,
                    precio_lote,
                    minimo_lotes,
                    unidades_restantes,
                    lotes_restantes
            FROM    Inventario;
        ''')
    
    def obtenerInformacionPrincipal(self, id_inventario: int):
        """ Regresa información principal de un elemento. """
        return self.fetchone('''
            SELECT  nombre,
                    tamano_lote, 
                    precio_lote,
                    minimo_lotes,
                    unidades_restantes
            FROM    Inventario 
            WHERE   id_inventario = ?;
        ''', (id_inventario,))
    
    def obtenerProdUtilizaInv(self, id_inventario: int):
        """ Obtener relación con productos en la tabla productos_utiliza_inventario. """
        return self.fetchall('''
            SELECT	codigo,
                    utiliza_inventario
            FROM	Productos_Utiliza_Inventario AS PUI
                    LEFT JOIN Productos AS P
                           ON PUI.id_productos = P.id_productos
            WHERE 	id_inventario = ?;
        ''', (id_inventario,))
    
    def agregarLotes(self, id_inventario: int, num_lotes: float):
        """ Agrega lotes a existencia del elemento. Hace commit automáticamente. """
        return self.execute('''
            UPDATE  Inventario
            SET     unidades_restantes = unidades_restantes + tamano_lote * ?
            WHERE   id_inventario = ?;
        ''', (num_lotes, id_inventario), commit=True)
    
    def registrarElemento(self, datos_elemento: tuple):
        """ Intenta registrar un elemento en la tabla y regresar 
            tupla con el índice recién insertado. No hace commit. """
        return self.fetchone('''
            INSERT INTO Inventario (
                nombre, tamano_lote, precio_lote,
                minimo_lotes, unidades_restantes
            )
            VALUES
                (?,?,?,?,?)
            RETURNING
                id_inventario;
        ''', datos_elemento)
    
    def editarElemento(self, id_inventario: int, datos_elemento: tuple):
        """ Intenta editar datos de un elemento en la tabla y regresar
            tupla con el índice recién editado. No hace commit. """
        return self.fetchone('''
            UPDATE  Inventario
            SET     nombre = ?,
                    tamano_lote = ?,
                    precio_lote = ?,
                    minimo_lotes = ?,
                    unidades_restantes = ?
            WHERE   id_inventario = ?
            RETURNING id_inventario;
        ''', (*datos_elemento, id_inventario))
    
    def eliminarElemento(self, id_inventario: int):
        """ Elimina un elemento de la tabla. Hace commit automáticamente. """
        return self.execute('''
            DELETE  FROM Inventario 
            WHERE   id_inventario = ?;
        ''', (id_inventario,), commit=True)
    
    def eliminarProdUtilizaInv(self, id_inventario: int):
        """ Elimina elemento de la tabla productos_utiliza_inventario.
            No hace commit, al ser parte inicial del proceso de registro/modificación. """
        return self.execute('''
            DELETE  FROM productos_utiliza_inventario
            WHERE   id_inventario = ?;
        ''', (id_inventario,), commit=False)
    
    def insertarProdUtilizaInv(self, id_inventario: int, params: list[tuple]):
        """ Inserta elemento en la tabla productos_utiliza_inventario.
            Hace commit, al ser parte final del proceso de registro/modificación. """
        params = [(id_inventario,) + param for param in params]
        
        return self.executemany('''
            INSERT INTO productos_utiliza_inventario (
                id_inventario, id_productos, utiliza_inventario
            )
            VALUES
                (?,?,?);
        ''', params, commit=True)


#####################
# VENTANA PRINCIPAL #
#####################
class App_AdministrarInventario(QtWidgets.QMainWindow):
    """ Backend para la ventana de administración de inventario. """
    def __init__(self, parent: VentanaPrincipal):
        from AdministrarInventario.Ui_AdministrarInventario import Ui_AdministrarInventario
        
        super().__init__()

        self.ui = Ui_AdministrarInventario()
        self.ui.setupUi(self)
        
        LabelAdvertencia(self.ui.tabla_inventario, '¡No se encontró ningún elemento!')

        # guardar conexión y usuarios como atributos
        self.conn = parent.conn
        self.user = parent.user

        # dar formato a la tabla principal
        header = self.ui.tabla_inventario.horizontalHeader()
        
        for col in range(self.ui.tabla_inventario.columnCount()):
            if col > 1:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)

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
    def update_display(self, rescan: bool = False):
        """
        Actualiza la tabla y el contador de elementos.
        Acepta una cadena de texto para la búsqueda de elementos.
        También lee de nuevo la tabla de elementos, si se desea.
        """
        if rescan:
            manejador = ManejadorInventario(self.conn)
            self.all = manejador.obtenerTablaPrincipal()
            self.ui.lbContador.setText(f'{len(self.all)} elementos en la base de datos.')
        
        tabla = self.ui.tabla_inventario
        tabla.setRowCount(0)
        
        bold = QFont()
        bold.setBold(True)
        
        # texto introducido por el usuario
        txt_busqueda = self.ui.searchBar.text().strip()
        
        found = self.all if not txt_busqueda else \
                filter(
                    lambda c: c[1] 
                              and son_similar(txt_busqueda, c[1]), 
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
                
                if col in {2, 5}: cell += ' unidades'
                if col in {4, 6}: cell += ' lotes'
                tabla.setItem(row, col, QtWidgets.QTableWidgetItem(cell))
            
            tabla.item(row, 1).setFont(bold)
            
            btSurtir = QtWidgets.QPushButton('Surtir existencias')
            btSurtir.clicked.connect(self.surtirExistencias)
            tabla.setCellWidget(row, col+1, btSurtir)
            
            # resaltar si hay menos cantidad que el mínimo
            if item[6] < item[4]:
                color = QColor(ColorsEnum.ROJO)
                tabla.item(row, 6).setBackground(color)

        tabla.resizeRowsToContents()
    
    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def surtirExistencias(self):
        Dialog = ExistenciasWidget(self)
        
        def accept_handle():
            selected = self.ui.tabla_inventario.selectedItems()
            
            try:
                idx = int(selected[0].text())
                num_lotes = float(Dialog.cantidadLotes)
            except ValueError:
                return
            
            manejador = ManejadorInventario(self.conn)
            if not manejador.agregarLotes(idx, num_lotes):
                return
     
            self.update_display(rescan=True)
            Dialog.close()
            
        Dialog.accept = accept_handle
        Dialog.show()
    
    def agregarInventario(self, _):
        self.new = App_RegistrarInventario(self)
        self.new.success.connect(
            lambda: self.update_display(rescan=True))
    
    def editarInventario(self, _):
        selected = self.ui.tabla_inventario.selectedItems()
        
        if selected:        
            self.new = App_EditarInventario(self, selected[0].text())
            self.new.success.connect(
                lambda: self.update_display(rescan=True))
    
    def quitarInventario(self, _):
        """ Elimina un material de la base de datos.
            Primero se verifica si hay productos que lo utilizan. """
        try:
            id_inventario = self.ui.tabla_inventario.selectedItems()[0].text()
        except IndexError:
            return
        
        qm = QtWidgets.QMessageBox
        
        manejador = ManejadorInventario(self.conn, '¡No se pudo eliminar el elemento!')
        result = manejador.obtenerProdUtilizaInv(id_inventario)
        
        if result:
            qm.warning(self, 'Atención', 
                       'No se puede eliminar este elemento debido '
                       'a que hay productos que lo utilizan. Haga doble '
                       'click en algún elemento para ver estos productos.')
            return
        
        # abrir pregunta
        ret = qm.question(self, 'Atención',
                          'El elemento seleccionado se eliminará de la base de datos. '
                          '¿Desea continuar?',
                          qm.Yes | qm.No)
        
        if ret != qm.Yes:
            return
        
        if not manejador.eliminarElemento(id_inventario):
            return
        
        qm.information(self, 'Éxito', 'Se eliminó el elemento seleccionado.')
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
class Base_EditarInventario(QtWidgets.QMainWindow):
    """Clase base para módulo de registrar o modificar elemento."""
    MENSAJE_EXITO: str
    MENSAJE_ERROR: str
    
    success = pyqtSignal()
    
    def __init__(self, first: App_AdministrarInventario):
        from AdministrarInventario.Ui_EditarInventario import Ui_EditarInventario
        
        super().__init__(first)

        self.ui = Ui_EditarInventario()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)
        
        # guardar conexión y usuarios como atributos
        self.conn = first.conn
        self.user = first.user
        
        # validadores para datos numéricos
        regexp_numero = QRegExp(r'\d*\.?\d*')
        validador = QRegExpValidator(regexp_numero)
        
        self.ui.txtPrecioCompra.setValidator(validador)
        self.ui.txtExistencia.setValidator(validador)
        self.ui.txtMinimo.setValidator(validador)
        self.ui.txtTamano.setValidator(validador)

        # evento para botón de regresar
        self.ui.btAceptar.clicked.connect(self.done)
        self.ui.btAgregar.clicked.connect(lambda _: self.agregarProductoALista())
        self.ui.lbRegresar.mousePressEvent = self.closeEvent

        self.show()
     
    ####################
    # FUNCIONES ÚTILES #
    ####################
    def agregarProductoALista(self, codigo: str = '', cantidad: int = 1):
        # crear widget y agregar a la lista
        nuevo = WidgetProducto()
        
        # evento para eliminar la entrada
        nuevo.lbEliminar.mousePressEvent = \
            lambda _: self.ui.layoutScroll.removeWidget(nuevo) \
                      or nuevo.setParent(None)
        
        # validador para datos numéricos
        regexp_numero = QRegExp(r'\d*\.?\d*')
        validador = QRegExpValidator(regexp_numero)
        nuevo.txtProductoUtiliza.setValidator(validador)
        
        # llenar caja de opciones con productos
        crsr = self.conn.cursor()
        
        crsr.execute('SELECT codigo FROM Productos;')
        nuevo.boxProducto.addItems([codigo for codigo, in crsr])
        
        # modificar valores a los de la base de datos
        nuevo.boxProducto.setCurrentText(codigo)
        nuevo.txtProductoUtiliza.setText(f'{cantidad}')
        
        self.ui.layoutScroll.addWidget(nuevo)
        
    def obtenerParametrosInventario(self):
        """ Parámetros para la tabla inventario. """
        try:
            if not (tamanoLote := float(self.ui.txtTamano.text())):
                return None
            
            return (self.ui.txtNombre.text().strip() or None,
                    tamanoLote,
                    float(self.ui.txtPrecioCompra.text()),
                    float(self.ui.txtMinimo.text()),
                    float(self.ui.txtExistencia.text()))
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self, 'Atención', 
                '¡Verifique que los datos numéricos sean correctos!')
            return None
    
    def obtenerParametrosProdUtilizaInv(self):
        """ Parámetros para la tabla productos_utiliza_inventario. """
        productos: list[WidgetProducto] = self.ui.scrollAreaLista.children()[1:]
        
        try:
            productos = [(p.productoSeleccionado, float(p.cantidadProducto))
                         for p in productos]
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self, 'Atención', 
                '¡Verifique que los datos numéricos sean correctos!')
            return None
        
        PUI_db_parametros = []
        manejador = DatabaseManager(self.conn, '')
            
        for codigo, cantidad in productos:
            if not codigo or cantidad < 1:
                return None
            
            idProducto, = manejador.fetchone(
                'SELECT id_productos FROM Productos WHERE codigo = ?;', (codigo,))
            
            PUI_db_parametros.append((idProducto, cantidad))
        
        return PUI_db_parametros
        
    def done(self):
        """Función donde se registrará o actualizará elemento del inventario."""
        qm = QtWidgets.QMessageBox
        
        #### obtención de parámetros ####
        inventario_db_parametros = self.obtenerParametrosInventario()
        PUI_db_parametros = self.obtenerParametrosProdUtilizaInv()
        
        if inventario_db_parametros == None or PUI_db_parametros == None:
            return
        
        # ejecuta internamente un fetchone, por lo que se desempaca luego
        result = self.ejecutarOperacion(self.conn, inventario_db_parametros)
        if not result:
            return
        
        idx, = result
        manejador = ManejadorInventario(self.conn, self.MENSAJE_ERROR)
        
        # transacción principal, se checa si cada operación fue exitosa
        if not manejador.eliminarProdUtilizaInv(idx):
            return
        if not manejador.insertarProdUtilizaInv(idx, PUI_db_parametros):
            return
        
        qm.information(self, 'Éxito', self.MENSAJE_EXITO)
        self.success.emit()
        self.close()
    
    def ejecutarOperacion(self, conn: fdb.Connection, params: tuple) -> tuple:
        """ Devuelve tupla con índice del elemento registrado o editado. """
        pass


class App_RegistrarInventario(Base_EditarInventario):
    """Backend para la ventana para registrar un material del inventario."""
    MENSAJE_EXITO = '¡Se registró el elemento!'
    MENSAJE_ERROR = '¡No se pudo registrar el elemento!'
    
    def __init__(self, first: App_AdministrarInventario):
        super().__init__(first)
        
        self.ui.lbTitulo.setText('Registrar elemento')
        self.ui.btAceptar.setText(' Registrar elemento')
        self.ui.btAceptar.setIcon(QIcon(QPixmap(':/img/resources/images/plus.png')))
    
    ####################
    # FUNCIONES ÚTILES #
    ####################
    def ejecutarOperacion(self, conn, params):
        manejador = ManejadorInventario(conn, self.MENSAJE_ERROR)
        return manejador.registrarElemento(params)


class App_EditarInventario(Base_EditarInventario):
    """Backend para la ventana para editar un material del inventario."""
    MENSAJE_EXITO = '¡Se editó el elemento!'
    MENSAJE_ERROR = '¡No se pudo editar el elemento!'
    
    def __init__(self, first: App_AdministrarInventario, idx: int = None):
        super().__init__(first)
        
        self.idx = idx  # id del elemento a editar
        
        manejador = ManejadorInventario(self.conn)
        
        # datos de la primera página
        nombre, tamano, precio, minimo, existencia \
            = manejador.obtenerInformacionPrincipal(idx)
        
        self.ui.txtNombre.setText(nombre)
        self.ui.txtTamano.setText(f'{tamano:,.2f}')
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
    def ejecutarOperacion(self, conn, params):
        manejador = ManejadorInventario(conn, self.MENSAJE_ERROR)
        return manejador.editarElemento(self.idx, params)


#########################################
# WIDGETS PERSONALIZADOS PARA EL MÓDULO #
#########################################
class WidgetProducto(QtWidgets.QWidget):
    def __init__(self):
        from PyQt5 import QtCore, QtWidgets, QtGui
        
        super().__init__()
        
        self.resize(390, 70)
        self.setMinimumSize(390, 70)
        boxProducto = QtWidgets.QComboBox(self)
        boxProducto.setGeometry(QtCore.QRect(35, 10, 271, 22))
        boxProducto.setMinimumSize(QtCore.QSize(271, 22))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        boxProducto.setFont(font)
        lbContador = QtWidgets.QLabel(self)
        lbContador.setGeometry(QtCore.QRect(5, 10, 21, 21))
        lbContador.setMinimumSize(QtCore.QSize(21, 21))
        lbContador.setPixmap(QtGui.QPixmap(":/img/resources/images/package_2.png"))
        lbContador.setScaledContents(True)
        lbEliminar = QtWidgets.QLabel(self)
        lbEliminar.setGeometry(QtCore.QRect(343, 12, 35, 35))
        lbEliminar.setMinimumSize(QtCore.QSize(35, 35))
        lbEliminar.setPixmap(QtGui.QPixmap(":/img/resources/images/cancel.png"))
        lbEliminar.setScaledContents(True)
        lbEliminar.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        label = QtWidgets.QLabel(self)
        label.setGeometry(QtCore.QRect(35, 40, 271, 21))
        label.setMinimumSize(QtCore.QSize(271, 21))
        label.setFont(font)
        label.setText("utiliza              unidades de este elemento.")
        txtProductoUtiliza = QtWidgets.QLineEdit(self)
        txtProductoUtiliza.setGeometry(QtCore.QRect(80, 40, 41, 20))
        txtProductoUtiliza.setMinimumSize(QtCore.QSize(41, 20))
        txtProductoUtiliza.setFont(font)
        QtCore.QMetaObject.connectSlotsByName(self)
        
        # guardar widgets importantes como atributos
        self.boxProducto = boxProducto
        self.lbEliminar = lbEliminar
        self.txtProductoUtiliza = txtProductoUtiliza
    
    @property
    def productoSeleccionado(self):
        return self.boxProducto.currentText()
    
    @property
    def cantidadProducto(self):
        return self.txtProductoUtiliza.text()


class ExistenciasWidget(QtWidgets.QDialog):
    def __init__(self, first: App_AdministrarInventario):
        from PyQt5 import QtCore
        
        super().__init__(parent=first)
        
        self.resize(354, 84)
        self.setWindowTitle("Surtir existencias")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        gridLayout = QtWidgets.QGridLayout(self)
        gridLayout.setContentsMargins(-1, -1, -1, 9)
        label = QtWidgets.QLabel(self)
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        label.setFont(font)
        label.setText("Suministrar ")
        gridLayout.addWidget(label, 0, 0, 1, 1)
        txtCantidad = QtWidgets.QLineEdit(self)
        txtCantidad.setFont(font)
        gridLayout.addWidget(txtCantidad, 0, 1, 1, 1)
        label_2 = QtWidgets.QLabel(self)
        label_2.setFont(font)
        label_2.setText(" lotes para este elemento.")
        gridLayout.addWidget(label_2, 0, 2, 1, 1)
        buttonBox = QtWidgets.QDialogButtonBox(self)
        buttonBox.setFont(font)
        buttonBox.setOrientation(Qt.Horizontal)
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        buttonBox.setCenterButtons(True)
        gridLayout.addWidget(buttonBox, 1, 0, 1, 3, Qt.AlignBottom)

        buttonBox.accepted.connect(self.accept) # type: ignore
        buttonBox.rejected.connect(self.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(self)
        
        # guardar widgets importantes como atributos
        self.txtCantidad = txtCantidad
    
    @property
    def cantidadLotes(self):
        return self.txtCantidad.text()
