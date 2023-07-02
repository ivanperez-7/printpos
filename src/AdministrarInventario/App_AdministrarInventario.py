import fdb

from PyQt5 import QtWidgets
from PyQt5.QtGui import (QFont, QColor, QPixmap,
                         QCursor, QIcon, QRegExpValidator)
from PyQt5.QtCore import Qt, QRegExp

from mydecorators import con_fondo
from myutils import ColorsEnum, son_similar
from mywidgets import LabelAdvertencia, WarningDialog


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
        
        LabelAdvertencia(self.ui.tabla_inventario, '¡No se encontró ningún elemento!')

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
            crsr = self.session['conn'].cursor()
            crsr.execute('''
            SELECT  id_inventario,
                    nombre,
                    tamano_lote,
                    precio_lote,
                    minimo_lotes,
                    unidades_restantes,
                    lotes_restantes
            FROM    Inventario;
            ''')

            self.all = crsr.fetchall()
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
        from PyQt5 import QtCore
        
        Dialog = QtWidgets.QDialog(self)
        Dialog.resize(354, 84)
        Dialog.setWindowTitle("Surtir existencias")
        Dialog.setWindowFlags(Dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        gridLayout = QtWidgets.QGridLayout(Dialog)
        gridLayout.setContentsMargins(-1, -1, -1, 9)
        label = QtWidgets.QLabel(Dialog)
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        label.setFont(font)
        label.setText("Suministrar ")
        gridLayout.addWidget(label, 0, 0, 1, 1)
        txtCantidad = QtWidgets.QLineEdit(Dialog)
        txtCantidad.setFont(font)
        gridLayout.addWidget(txtCantidad, 0, 1, 1, 1)
        label_2 = QtWidgets.QLabel(Dialog)
        label_2.setFont(font)
        label_2.setText(" lotes para este elemento.")
        gridLayout.addWidget(label_2, 0, 2, 1, 1)
        buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        buttonBox.setFont(font)
        buttonBox.setOrientation(Qt.Horizontal)
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        buttonBox.setCenterButtons(True)
        gridLayout.addWidget(buttonBox, 1, 0, 1, 3, Qt.AlignBottom)

        buttonBox.accepted.connect(Dialog.accept) # type: ignore
        buttonBox.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        
        def accept_handle():
            selected = self.ui.tabla_inventario.selectedItems()
            
            if not selected:
                return
            
            conn = self.session['conn']
            crsr = conn.cursor()
            
            try:
                surtir = float(txtCantidad.text())
                idx = selected[0].text()
                
                crsr.execute('''UPDATE  Inventario
                                SET     unidades_restantes = unidades_restantes + tamano_lote * ?
                                WHERE   id_inventario = ?;''', (surtir, idx))
                conn.commit()
                
                self.update_display(rescan=True)
                Dialog.close()
            except (ValueError, fdb.Error) as err:
                conn.rollback()
                print(str(err))
            
        Dialog.accept = accept_handle
        Dialog.show()
    
    def agregarInventario(self, _):
        self.new = App_RegistrarInventario(self)
    
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
            id_inventario = self.ui.tabla_inventario.selectedItems()[0].text()
        except IndexError:
            return
        
        qm = QtWidgets.QMessageBox
        
        conn = self.session['conn']
        crsr = conn.cursor()
        
        crsr.execute('''
        SELECT	id_productos
        FROM	Productos_Utiliza_Inventario
        WHERE	id_inventario = ?;
        ''', (id_inventario,))
        
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
            crsr.execute('DELETE FROM Inventario WHERE id_inventario = ?;', (id_inventario,))
            conn.commit()
        except fdb.Error as err:
            conn.rollback()

            WarningDialog(self, '¡No se pudo eliminar el elemento!', str(err))
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
    
    def __init__(self, first: App_AdministrarInventario):
        from AdministrarInventario.Ui_EditarInventario import Ui_EditarInventario
        
        super().__init__(first)

        self.ui = Ui_EditarInventario()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)
        
        self.first: App_AdministrarInventario = first
        self.session = first.session # conexión a la base de datos y usuario actual
        
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
    
    #######################
    # WIDGETS PARA LISTAS #
    #######################
    def widgetProducto(self) -> QtWidgets.QFrame:
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
        lbContador.setPixmap(QPixmap(":/img/resources/images/package_2.png"))
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
        label.setText("utiliza              unidades de este elemento.")
        txtProductoUtiliza = QtWidgets.QLineEdit(frameProducto)
        txtProductoUtiliza.setGeometry(QtCore.QRect(80, 40, 41, 20))
        txtProductoUtiliza.setMinimumSize(QtCore.QSize(41, 20))
        txtProductoUtiliza.setFont(font)
        QtCore.QMetaObject.connectSlotsByName(frameProducto)
        
        return frameProducto

    def agregarProductoALista(self, codigo: str = '', cantidad: int = 1):
        # crear widget y agregar a la lista
        nuevo = self.widgetProducto()
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
        
        crsr.execute('SELECT codigo FROM Productos;')
        box.addItems([codigo for codigo, in crsr])
        
        # modificar valores a los de la base de datos
        box.setCurrentText(codigo)
        line.setText(f'{cantidad}')
        
        self.ui.layoutScroll.addWidget(nuevo)
     
    ####################
    # FUNCIONES ÚTILES #
    ####################
    def done(self):
        """Función donde se registrará o actualizará elemento del inventario."""
        qm = QtWidgets.QMessageBox
        
        #### <tabla Inventario> ####
        try:
            if (tamanoLote := float(self.ui.txtTamano.text())) == 0:
                return
            
            inventario_db_parametros = (
                self.ui.txtNombre.text().strip() or None,
                tamanoLote,
                float(self.ui.txtPrecioCompra.text()),
                float(self.ui.txtMinimo.text()),
                float(self.ui.txtExistencia.text())
            )
        except ValueError:
            qm.warning(self, 'Atención', '¡Verifique que los datos numéricos sean correctos!')
            return
        
        conn = self.session['conn']
        crsr = conn.cursor()

        try:
            idx = self.ejecutarConsulta(crsr, inventario_db_parametros)
        except fdb.Error as err:
            conn.rollback()
            WarningDialog(self, self.MENSAJE_ERROR, str(err))
            return
        #### </tabla Inventario> ####
        
        #### <tabla Productos_Utiliza_Inventario> ####
        productos = self.ui.scrollAreaLista.children()[1:]  # QFrames
        productos = [prod.children() for prod in productos] # hijos de cada QFrame
        
        try:
            productos = [(box.currentText(), float(line.text()))    # codigo y cantidad
                         for (box, _, _, _, line) in productos]
        except ValueError:
            conn.rollback()
            qm.warning(self, 'Atención', '¡Verifique que los datos numéricos sean correctos!')
            return
        
        PUI_db_parametros = []
            
        for codigo, cantidad in productos:
            if not codigo or cantidad < 1:
                conn.rollback()
                return
            
            crsr.execute('SELECT id_productos FROM Productos WHERE codigo = ?;', (codigo,))
            idProducto, = crsr.fetchone()
            
            PUI_db_parametros.append((idProducto, idx, cantidad))

        try:
            # primero borrar las entradas existentes
            crsr.execute('''
            DELETE  FROM Productos_Utiliza_Inventario
            WHERE   id_inventario = ?;
            ''', (idx,))
            
            # nuevas entradas, introducidas por el usuario
            crsr.executemany('''
            INSERT INTO Productos_Utiliza_Inventario (
                id_productos, id_inventario, utiliza_inventario
            )
            VALUES
                (?,?,?);
            ''', PUI_db_parametros)
            
            conn.commit()
        except fdb.Error as err:
            conn.rollback()
            WarningDialog(self, self.MENSAJE_ERROR, str(err))
            return
        #### </tabla Productos_Utiliza_Inventario> ####
        
        qm.information(self, 'Éxito', self.MENSAJE_EXITO)
        
        self.first.update_display(rescan=True)
        self.close()
    
    def ejecutarConsulta(self, crsr: fdb.Cursor, params: tuple) -> int:
        """Devuelve índice del elemento registrado o editado."""
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
    def ejecutarConsulta(self, crsr, params):
        crsr.execute('''
        INSERT INTO Inventario (
            nombre, tamano_lote, precio_lote,
            minimo_lotes, unidades_restantes
        )
        VALUES
            (?,?,?,?,?)
        RETURNING
            id_inventario;
        ''', params)
            
        idx, = crsr.fetchone()
        return idx


class App_EditarInventario(Base_EditarInventario):
    """Backend para la ventana para editar un material del inventario."""
    MENSAJE_EXITO = '¡Se editó el elemento!'
    MENSAJE_ERROR = '¡No se pudo editar el elemento!'
    
    def __init__(self, first: App_AdministrarInventario, idx: int = None):
        super().__init__(first)
        
        self.idx = idx  # id del elemento a editar
        
        crsr = first.session['conn'].cursor()
        
        # datos de la primera página
        crsr.execute('''SELECT  nombre,
                                tamano_lote, 
                                precio_lote,
                                minimo_lotes,
                                unidades_restantes
                        FROM    Inventario 
                        WHERE   id_inventario = ?;''', (idx,))
        
        nombre, tamano, precio, minimo, existencia = crsr.fetchone()
        
        self.ui.txtNombre.setText(nombre)
        self.ui.txtTamano.setText(f'{tamano:,.2f}')
        self.ui.txtPrecioCompra.setText(f'{precio:.2f}')
        self.ui.txtExistencia.setText(f'{existencia:.2f}')
        self.ui.txtMinimo.setText(f'{minimo:.2f}')
        
        # agregar productos de la segunda página
        crsr.execute('''
        SELECT	codigo,
                utiliza_inventario
        FROM	Productos_Utiliza_Inventario AS PUI
                LEFT JOIN Productos AS P
                        ON PUI.id_productos = P.id_productos
        WHERE 	id_inventario = ?;
        ''', (idx,))
        
        productos = crsr.fetchall()
                
        for codigo, cantidad in productos:
            self.agregarProductoALista(codigo, cantidad)
    
    ####################
    # FUNCIONES ÚTILES #
    ####################
    def ejecutarConsulta(self, crsr, params):
        crsr.execute('''
        UPDATE  Inventario
        SET     nombre = ?,
                tamano_lote = ?,
                precio_lote = ?,
                minimo_lotes = ?,
                unidades_restantes = ?
        WHERE   id_inventario = ?;
        ''', (*params, self.idx))
        
        return self.idx
