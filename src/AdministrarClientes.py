from datetime import datetime

import fdb

from PySide6 import QtWidgets
from PySide6.QtGui import QFont, QColor, QIcon, QPixmap, QRegularExpressionValidator
from PySide6.QtCore import Qt, QDate, QRegularExpression, Signal

from utils.databasemanagers import ManejadorClientes
from utils.mydecorators import con_fondo
from utils.myinterfaces import InterfazFiltro
from utils.myutils import (configurarCabecera, exportarXlsx, formatDate,
                           ColorsEnum, son_similar)
from utils.mywidgets import LabelAdvertencia, VentanaPrincipal


#####################
# VENTANA PRINCIPAL #
#####################
class App_AdministrarClientes(QtWidgets.QMainWindow):
    """ Backend para la ventana de administración de clientes. """
    def __init__(self, parent: VentanaPrincipal):
        from ui.Ui_AdministrarClientes import Ui_AdministrarClientes
        
        super().__init__()

        self.ui = Ui_AdministrarClientes()
        self.ui.setupUi(self)
        
        LabelAdvertencia(self.ui.tabla_clientes, '¡No se encontró ningún cliente!')
        
        # guardar conexión y usuarios como atributos
        self.conn = parent.conn
        self.user = parent.user

        # añadir menú de opciones al botón para filtrar
        self.filtro = InterfazFiltro(self.ui.btFiltrar, [
            ('Nombre', 'nombre', 1),
            ('Teléfono', 'teléfono', 2),
            ('Correo', 'correo', 3),
            ('Dirección', 'dirección', 4),
            ('RFC', 'RFC', 5)
        ])
        self.filtro.filtroCambiado.connect(
            lambda txt: self.ui.searchBar.setPlaceholderText(f'Busque cliente por {txt}...')
                        or self.update_display())
        
        # restringir botón de eliminar cliente
        if not self.user.administrador:
            self.ui.btEliminar.hide()

        # añade eventos para los botones
        self.ui.btAgregar.clicked.connect(self.insertarCliente)
        self.ui.btEditar.clicked.connect(self.editarCliente)
        self.ui.btEliminar.clicked.connect(self.quitarCliente)
        self.ui.btRegresar.clicked.connect(self.goHome)
        
        self.ui.searchBar.textChanged.connect(lambda: self.update_display())
        self.ui.resaltarCheck.stateChanged.connect(lambda: self.update_display())
        self.ui.resaltarDias.textChanged.connect(self.resaltarTrigger)
        self.ui.btExportar.clicked.connect(self.exportarExcel)

        configurarCabecera(self.ui.tabla_clientes,
                           lambda col: col in [0, 2, 5, 6])
        self.update_display(rescan=True)
    
    def showEvent(self, event):
        self.ui.tabla_clientes.resizeRowsToContents()
    
    def resizeEvent(self, event):
        if self.isVisible():
            self.ui.tabla_clientes.resizeRowsToContents()
    
    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def resaltarTrigger(self, *args):
        """ Recolorea la tabla para resaltar clientes que no han
        visitado en una cantidad escogida de días. """
        if self.ui.resaltarCheck.isChecked():
            self.update_display()

    def update_display(self, rescan: bool = False):
        """ Actualiza la tabla y el contador de clientes.
            Acepta una cadena de texto para la búsqueda de clientes.
            También lee de nuevo la tabla de clientes, si se desea. """
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
        # timestamp ahora mismo
        timestamp_now = QDate.currentDate().dayOfYear()
        
        found = self.all if not txt_busqueda else \
                filter(
                    lambda c: c[self.filtro.filtro] 
                              and son_similar(txt_busqueda, c[self.filtro.filtro]), 
                    self.all)
    
        for row, cliente in enumerate(found):
            tabla.insertRow(row)

            for col, dato in enumerate(cliente):
                if isinstance(dato, datetime):
                    cell = formatDate(dato)
                else:
                    cell = str(dato or '')
                tabla.setItem(row, col, QtWidgets.QTableWidgetItem(cell))
            # al salir del ciclo, todos los usos subsecuentes de `col`
            # apuntan a la última columna de la tabla.
            
            tabla.item(row, 1).setFont(bold)
            
            if not self.ui.resaltarCheck.isChecked():
                continue
            
            ultimaVisita = QDate(cliente[-1])
            
            if ultimaVisita and timestamp_now-ultimaVisita.dayOfYear() >= dias:
                color = QColor(ColorsEnum.ROJO)
                tabla.item(row, col).setBackground(color)
        
        tabla.resizeRowsToContents()
    
    def exportarExcel(self):
        """ Exportar clientes a un archivo .xlsx. """      
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
                if isinstance(dato, datetime):
                    cell = formatDate(dato)
                else:
                    cell = str(dato or '')
                cliente[col] = cell
                
            datos.append(cliente)
        
        exportarXlsx(fileName, titulos, datos)
    
    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def insertarCliente(self):
        """ Abre ventana para registrar un cliente. """
        self.new = App_RegistrarCliente(self)
        self.new.success.connect(
            lambda: self.update_display(rescan=True))

    def editarCliente(self):
        """ Abre ventana para editar un cliente seleccionado. """
        selected = self.ui.tabla_clientes.selectedItems()
        
        if not selected or selected[0].text() == '1':
            return

        self.new = App_EditarCliente(self, int(selected[0].text()))
        self.new.success.connect(
            lambda: self.update_display(rescan=True))
    
    def quitarCliente(self):
        """ Pide confirmación para eliminar clientes de la base de datos. """
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
    
    def goHome(self):
        """ Cierra la ventana y regresa al inicio. """
        from Home import App_Home

        parent = self.parentWidget()       # QMainWindow
        new = App_Home(parent)
        parent.setCentralWidget(new)


#################################
# VENTANAS PARA EDITAR CLIENTES #
#################################
@con_fondo
class Base_EditarCliente(QtWidgets.QMainWindow):
    """ Clase base para registrar o editar cliente. """
    MENSAJE_EXITO: str
    MENSAJE_ERROR: str
    
    success = Signal(str, str, str)
    
    def __init__(self, first: App_AdministrarClientes):
        from ui.Ui_EditarCliente import Ui_EditarCliente
        
        super().__init__(first)

        self.ui = Ui_EditarCliente()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)

        # guardar conexión y usuarios como atributos
        self.conn = first.conn
        self.user = first.user
        
        # validador clave de país
        regexp = QRegularExpression(r'[0-9]{1,}')
        validador = QRegularExpressionValidator(regexp)
        self.ui.txtLada.setValidator(validador)

        # crear eventos para los botones
        self.ui.btRegresar.clicked.connect(self.close)
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
        """ Datos por defecto, proveído por ambas clases heredadas. """
        celular = celular.replace(' ', '')
        
        self.ui.txtNombre.setText(nombre)
        self.ui.txtLada.setText(celular[1:-10] or '52')
        self.ui.txtCelular.setText(celular[-10:])
        self.ui.txtCorreo.setText(correo)
    
    def done(self):
        """ Método en el que se modificará o insertará un cliente. """
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
        """ Función a sobreescribir donde se realiza consulta SQL. """
        pass


class App_RegistrarCliente(Base_EditarCliente):
    """ Backend para la función de registrar cliente. """
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
        """ Insertar nuevo cliente a la base de datos. """
        manejador = ManejadorClientes(conn, self.MENSAJE_ERROR)
        return manejador.insertarCliente(params)


class App_EditarCliente(Base_EditarCliente):
    """ Backend para la función de editar cliente. """
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
        """ Actualizar datos del cliente en la base de datos. """
        manejador = ManejadorClientes(conn, self.MENSAJE_ERROR)
        return manejador.actualizarCliente(self.idx, params)
