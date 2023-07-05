import fdb

from PySide6 import QtWidgets
from PySide6.QtGui import QFont, QColor, QIcon, QPixmap, QRegularExpressionValidator
from PySide6.QtCore import Qt, QDateTime, QRegularExpression, Signal

from mydecorators import con_fondo
from myutils import DatabaseManager, exportarXlsx, formatDate, ColorsEnum, son_similar
from mywidgets import LabelAdvertencia, VentanaPrincipal


###########################################
# CLASE PARA MANEJAR OPERACIONES EN LA DB #
###########################################
class ManejadorClientes(DatabaseManager):
    """ Clase para manejar sentencias hacia/desde la tabla Clientes. """
    def __init__(self, conn: fdb.Connection, error_txt: str = ''):
        super().__init__(conn, error_txt)
    
    def obtenerTablaPrincipal(self):
        """ Sentencia para alimentar la tabla principal de clientes. """
        return self.fetchall('''
            SELECT  C.id_clientes,
                    nombre,
                    telefono,
                    correo,
                    direccion,
                    RFC,
                    MAX(fecha_hora_creacion) AS ultimaVenta
            FROM    Clientes AS C
                    LEFT JOIN Ventas AS V
                           ON C.id_clientes = V.id_clientes
            GROUP   BY 1, 2, 3, 4, 5, 6
            ORDER   BY C.id_clientes;
        ''')
    
    def obtenerCliente(self, idx):
        """ Sentencia para obtener un cliente. """
        return self.fetchone('''
            SELECT  * 
            FROM    Clientes 
            WHERE id_clientes = ?;
        ''', (idx,))
    
    def registrarCliente(self, datosCliente: tuple):
        """ Sentencia para registrar cliente. Hace commit automáticamente. """
        return self.execute('''
            INSERT INTO Clientes (
                nombre, telefono, correo, direccion,
                RFC, cliente_especial, descuentos
            )
            VALUES
                (?,?,?,?,?,?,?);
        ''', datosCliente, commit=True)
    
    def actualizarCliente(self, idCliente, datosCliente: tuple):
        """ Sentencia para actualizar cliente. Hace commit automáticamente. """
        return self.execute('''
            UPDATE  Clientes
            SET     nombre = ?,
                    telefono = ?,
                    correo = ?,
                    direccion = ?,
                    RFC = ?,
                    cliente_especial = ?,
                    descuentos = ?
            WHERE   id_clientes = ?;
        ''', (*datosCliente, idCliente), commit=True)
    
    def eliminarCliente(self, idCliente):
        """ Sentencia para eliminar cliente. Hace commit automáticamente. """
        return self.execute('''
            DELETE  FROM Clientes
            WHERE   id_clientes = ?;
        ''', (idCliente,), commit=True)


#####################
# VENTANA PRINCIPAL #
#####################
class App_AdministrarClientes(QtWidgets.QMainWindow):
    """
    Backend para la ventana de administración de clientes.
    """
    def __init__(self, parent: VentanaPrincipal):
        from AdministrarClientes.Ui_AdministrarClientes import Ui_AdministrarClientes
        
        super().__init__()

        self.ui = Ui_AdministrarClientes()
        self.ui.setupUi(self)
        
        LabelAdvertencia(self.ui.tabla_clientes, '¡No se encontró ningún cliente!')

        # otras variables importantes
        self.filtro = 1
        
        # guardar conexión y usuarios como atributos
        self.conn = parent.conn
        self.user = parent.user

        # añadir menú de opciones al botón para filtrar
        popup = QtWidgets.QMenu(self.ui.btFiltrar)

        default = popup.addAction(
            'Nombre',lambda: self.cambiarFiltro('nombre', 1))
        popup.addAction(
            'Teléfono', lambda: self.cambiarFiltro('teléfono', 2))
        popup.addAction(
            'Correo', lambda: self.cambiarFiltro('correo', 3))
        popup.addAction(
            'Dirección', lambda: self.cambiarFiltro('dirección', 4))
        popup.addAction(
            'RFC', lambda: self.cambiarFiltro('RFC', 5))
        popup.setDefaultAction(default)

        self.ui.btFiltrar.setMenu(popup)
        self.ui.btFiltrar.clicked.connect(lambda: self.cambiarFiltro('nombre', 1))

        # dar formato a la tabla principal
        header = self.ui.tabla_clientes.horizontalHeader()
        
        for col in range(self.ui.tabla_clientes.columnCount()):
            if col in {0, 2, 5}:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
        
        # restringir botón de eliminar cliente
        if not self.user.administrador:
            self.ui.lbQuitar.hide()

        # añade eventos para los botones
        self.ui.lbAgregar.mousePressEvent = self.registrarCliente
        self.ui.lbEditar.mousePressEvent = self.editarCliente
        self.ui.lbQuitar.mousePressEvent = self.quitarCliente
        self.ui.lbRegresar.mousePressEvent = self.goHome
        self.ui.searchBar.textChanged.connect(lambda: self.update_display())
        self.ui.resaltarCheck.stateChanged.connect(lambda: self.update_display())
        self.ui.resaltarDias.textChanged.connect(self.resaltarTrigger)
        self.ui.btExportar.clicked.connect(self.exportarExcel)
    
    def showEvent(self, event):
        self.update_display(rescan=True)
    
    def resizeEvent(self, event):
        if self.isVisible():
            self.ui.tabla_clientes.resizeRowsToContents()
    
    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def resaltarTrigger(self, *args):
        """
        Recolorea la tabla para resaltar clientes que no han
        visitado en una cantidad escogida de días.
        """
        if self.ui.resaltarCheck.isChecked():
            self.update_display()
    
    def cambiarFiltro(self, filtro, idx):
        """
        Modifica el filtro de búsqueda.
        """
        self.filtro = idx
        self.ui.searchBar.setPlaceholderText(f'Busque cliente por {filtro}...')
        self.update_display()

    def update_display(self, rescan: bool = False):
        """
        Actualiza la tabla y el contador de clientes.
        Acepta una cadena de texto para la búsqueda de clientes.
        También lee de nuevo la tabla de clientes, si se desea.
        """
        if rescan:
            manejador = ManejadorClientes(self.conn)
            self.all = manejador.obtenerTablaPrincipal()
            self.ui.lbContador.setText(f'{len(self.all)} clientes en la base de datos.')

        tabla = self.ui.tabla_clientes
        tabla.setRowCount(0)
        
        bold = QFont()
        bold.setBold(True)
        
        # texto introducido por el usuario
        txt_busqueda = self.ui.searchBar.text().strip()
        
        # resalta si un cliente no ha venido en _ días
        dias = int(self.ui.resaltarDias.text())
        # timestamp UNIX de ahora mismo
        timestamp_now = QDateTime.currentSecsSinceEpoch()
        
        found = self.all if not txt_busqueda else \
                filter(
                    lambda c: c[self.filtro] 
                              and son_similar(txt_busqueda, c[self.filtro]), 
                    self.all)
    
        for row, cliente in enumerate(found):
            tabla.insertRow(row)

            for col, dato in enumerate(cliente):
                if isinstance(dato, int) and col > 0:
                    cell = formatDate(dato)
                else:
                    cell = str(dato or '')
                tabla.setItem(row, col, QtWidgets.QTableWidgetItem(cell))
            # al salir del ciclo, todos los usos subsecuentes de `col`
            # apuntan a la última columna de la tabla.
            
            tabla.item(row, 1).setFont(bold)
            
            if not self.ui.resaltarCheck.isChecked():
                continue
            
            if cliente[-1] and timestamp_now-cliente[-1] >= 86400*dias:
                color = QColor(ColorsEnum.ROJO)
                tabla.item(row, col).setBackground(color)
        
        tabla.resizeRowsToContents()
    
    def exportarExcel(self):
        """
        Exportar clientes a un archivo .xlsx.
        """      
        # abrir widget para determinar ubicación de archivo
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Guardar archivo...',
                                                            filter='Libro de Excel (*.xlsx)')
        
        if not fileName:
            return
        
        titulos = [self.ui.tabla_clientes.horizontalHeaderItem(section).text()
                    for section in range(1,self.ui.tabla_clientes.columnCount())]
        datos = []
        
        for cliente in self.all:
            cliente = list(cliente)[1:]   # lista mutable
            
            for col, dato in enumerate(cliente):
                if isinstance(dato, int):
                    cell = formatDate(dato)
                else:
                    cell = str(dato or '')
                cliente[col] = cell
                
            datos.append(cliente)
        
        exportarXlsx(fileName, titulos, datos)
    
    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def registrarCliente(self, _):
        """
        Abre ventana para registrar un cliente.
        """
        self.new = App_RegistrarCliente(self)
        self.new.success.connect(
            lambda: self.update_display(rescan=True))

    def editarCliente(self, _):
        """
        Abre ventana para editar un cliente seleccionado.
        """
        selected = self.ui.tabla_clientes.selectedItems()
        
        if not selected or selected[0].text() == '1':
            return

        self.new = App_EditarCliente(self, int(selected[0].text()))
        self.new.success.connect(
            lambda: self.update_display(rescan=True))
    
    def quitarCliente(self, _):
        """
        Pide confirmación para eliminar clientes de la base de datos.
        """
        selected = self.ui.tabla_clientes.selectedItems()

        if not selected or selected[0].text() == '1':
            return
        
        # abrir pregunta
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Atención',
                          'Los clientes seleccionados se eliminarán de la base de datos. '
                          '¿Desea continuar?',
                          qm.Yes | qm.No)

        if ret != qm.Yes:
            return

        manejador = ManejadorClientes(self.conn, '¡No se pudo eliminar el cliente!')
        
        if not manejador.eliminarCliente(selected[0].text()):
            return

        qm.information(self, 'Éxito', 'Se eliminaron los clientes seleccionados.')
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
# VENTANAS PARA EDITAR CLIENTES #
#################################
@con_fondo
class Base_EditarCliente(QtWidgets.QMainWindow):
    """Clase base para registrar o editar cliente."""
    MENSAJE_EXITO: str
    MENSAJE_ERROR: str
    
    success = Signal(str, str, str)
    
    def __init__(self, first: App_AdministrarClientes):
        from AdministrarClientes.Ui_EditarCliente import Ui_EditarCliente
        
        super().__init__(first)

        self.ui = Ui_EditarCliente()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)

        # guardar conexión y usuarios como atributos
        self.conn = first.conn
        self.user = first.user
        
        # validador clave de país
        regexp = QRegularExpression(r'[0-9]{1,}')
        validador = QRegularExpressionValidator(regexp)
        self.ui.txtLada.setValidator(validador)

        # crear eventos para los botones
        self.ui.lbRegresar.mousePressEvent = self.closeEvent
        self.ui.btRegistrar.clicked.connect(self.done)
        self.ui.checkDescuentos.clicked.connect(
            lambda estado: self.ui.txtDescuentos.setEnabled(estado))
        
        # deshabilitar modificación de descuentos para usuarios normales
        if not first.user.administrador:
            self.ui.checkDescuentos.setEnabled(False)
            self.ui.txtDescuentos.setEnabled(False)

        self.show()
    
    ####################
    # FUNCIONES ÚTILES #
    ####################
    @property
    def numeroTelefono(self) -> str:
        return f'+{self.ui.txtLada.text()} {self.ui.txtCelular.displayText()}'
    
    def agregarDatosPorDefecto(self, nombre: str, celular: str, correo: str):
        """Datos por defecto, proveído por ambas clases heredadas."""
        celular = celular.replace(' ', '')
        
        self.ui.txtNombre.setText(nombre)
        self.ui.txtLada.setText(celular[1:-10] or '52')
        self.ui.txtCelular.setText(celular[-10:])
        self.ui.txtCorreo.setText(correo)
    
    def done(self):
        """Método en el que se modificará o insertará un cliente."""
        clientes_db_parametros = tuple(v.strip() or None if isinstance(v, str)
                                       else v for v in (
            self.ui.txtNombre.text(),
            self.numeroTelefono,
            self.ui.txtCorreo.text(),
            self.ui.txtDireccion.toPlainText(),
            self.ui.txtRFC.text(),
            int(self.ui.checkDescuentos.isChecked()),
            self.ui.txtDescuentos.toPlainText()
        ))

        if not self.ejecutarOperacion(self.conn, clientes_db_parametros):
            return
        
        QtWidgets.QMessageBox.information(
            self, 'Éxito', self.MENSAJE_EXITO)
        
        self.success.emit(self.ui.txtNombre.text(), 
                          self.numeroTelefono, 
                          self.ui.txtCorreo.text())
        self.close()
    
    def ejecutarOperacion(self, conn: fdb.Connection, params: tuple):
        """Función a sobreescribir donde se realiza consulta SQL."""
        pass


class App_RegistrarCliente(Base_EditarCliente):
    """Backend para la función de registrar cliente."""
    MENSAJE_EXITO = '¡Se registró el cliente!'
    MENSAJE_ERROR = '¡No se pudo registrar el cliente!'
    
    def __init__(self, first: App_AdministrarClientes,
                 nombre = '', celular = '999', correo = ''):        
        super().__init__(first)
        
        self.ui.lbTitulo.setText('Registrar cliente')
        self.ui.btRegistrar.setText(' Registrar cliente')
        self.ui.btRegistrar.setIcon(QIcon(QPixmap(':/img/resources/images/plus.png')))
        
        self.agregarDatosPorDefecto(nombre, celular, correo)
    
    ####################
    # FUNCIONES ÚTILES #
    ####################
    def ejecutarOperacion(self, conn, params):
        """Insertar nuevo cliente a la base de datos."""
        manejador = ManejadorClientes(conn, self.MENSAJE_ERROR)
        return manejador.registrarCliente(params)


class App_EditarCliente(Base_EditarCliente):
    """Backend para la función de editar cliente."""
    MENSAJE_EXITO = '¡Se editó el cliente!'
    MENSAJE_ERROR = '¡No se pudo editar el cliente!'
    
    def __init__(self, first: App_AdministrarClientes, idx: int):        
        super().__init__(first)
        
        self.idx = idx  # id del cliente a editar

        # obtener datos del cliente
        manejador = ManejadorClientes(self.conn)
        cliente = manejador.obtenerCliente(idx)
        
        nombre = cliente[1]
        celular = cliente[2].replace(' ', '')
        correo = cliente[3]
        especial = bool(cliente[6])
        
        self.agregarDatosPorDefecto(nombre, celular, correo)
        
        self.ui.txtDireccion.setPlainText(cliente[4])
        self.ui.txtRFC.setText(cliente[5])
        
        self.ui.checkDescuentos.setChecked(especial)
        self.ui.txtDescuentos.setEnabled(especial)
        self.ui.txtDescuentos.setPlainText(cliente[7])
    
    ####################
    # FUNCIONES ÚTILES #
    ####################
    def ejecutarOperacion(self, conn, params):
        """Actualizar datos del cliente en la base de datos."""
        manejador = ManejadorClientes(conn, self.MENSAJE_ERROR)
        return manejador.actualizarCliente(self.idx, params)
