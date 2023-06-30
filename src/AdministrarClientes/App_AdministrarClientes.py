from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QDateTime, QRegExp, pyqtSignal

from myutils import (exportarXlsx, formatDate, ColorsEnum, son_similar)
from mydecorators import con_fondo
from mywidgets import LabelAdvertencia, WarningDialog

import fdb

class App_AdministrarClientes(QtWidgets.QMainWindow):
    """
    Backend para la ventana de administración de clientes.
    """
    def __init__(self, parent=None):
        from AdministrarClientes.Ui_AdministrarClientes import Ui_AdministrarClientes
        
        super().__init__()

        self.ui = Ui_AdministrarClientes()
        self.ui.setupUi(self)

        self.session = parent.session  # conexión y usuario actual
        self.filtro = 1
        
        LabelAdvertencia(self.ui.tabla_clientes, '¡No se encontró ningún cliente!')

        # añadir menú de opciones al botón para filtrar
        popup = QtWidgets.QMenu()

        default = popup.addAction(
            'Nombre',lambda: self.cambiar_filtro('nombre', 1))
        popup.addAction(
            'Teléfono', lambda: self.cambiar_filtro('teléfono', 2))
        popup.addAction(
            'Correo', lambda: self.cambiar_filtro('correo', 3))
        popup.addAction(
            'Dirección', lambda: self.cambiar_filtro('dirección', 4))
        popup.addAction(
            'RFC', lambda: self.cambiar_filtro('RFC', 5))
        popup.setDefaultAction(default)

        self.ui.btFiltrar.setMenu(popup)
        self.ui.btFiltrar.clicked.connect(lambda: self.cambiar_filtro('nombre', 1))

        # dar formato a la tabla principal
        header = self.ui.tabla_clientes.horizontalHeader()
        
        for col in range(self.ui.tabla_clientes.columnCount()):
            if col in {0, 2, 5}:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
            else:
                header.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
        
        # restringir botón de eliminar cliente
        if not self.session['user'].administrador:
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
    
    def cambiar_filtro(self, filtro, idx):
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
            crsr = self.session['conn'].cursor()

            crsr.execute('''
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

            self.all = crsr.fetchall()
            self.ui.lbContador.setText(f'{len(self.all)} clientes en la base de datos.')

        tabla = self.ui.tabla_clientes
        tabla.setRowCount(0)
        
        bold = QtGui.QFont()
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
                color = QtGui.QColor(ColorsEnum.ROJO)
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
        self.new = App_EditarCliente(self)
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
                          'Los clientes seleccionados se eliminarán de la base de datos. ¿Desea continuar?',
                          qm.Yes | qm.No)

        if ret != qm.Yes:
            return
        
        values = [(item.text(),) for item in selected if item.column() == 0]

        conn = self.session['conn']
        crsr = conn.cursor()

        # crea un cuadro que notifica el resultado de la operación
        try:
            crsr.executemany('DELETE FROM Clientes WHERE id_clientes = ?;', values)
            conn.commit()
        except fdb.Error as err:
            conn.rollback()
            
            WarningDialog(self, '¡No se pudo eliminar el cliente!', str(err))
            return
        
        qm.information(self, 'Éxito', 'Se eliminaron los clientes seleccionados.', qm.Ok)
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
# VENTANAS PARA EDITAR LA VENTA #
#################################
@con_fondo
class App_EditarCliente(QtWidgets.QMainWindow):
    """
    Backend para la función de editar cliente.
    """
    success = pyqtSignal()
    
    def __init__(self, first, idx = None, 
                 nombre = '', celular = '999', correo = ''):
        from AdministrarClientes.Ui_EditarCliente import Ui_EditarCliente
        
        super().__init__(first)

        self.ui = Ui_EditarCliente()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)

        self.first = first # referencia a la ventana de crear venta
        self.session = first.session # conexión a la base de datos y usuario actual
        self.idx = idx  # id del cliente a editar

        # datos por defecto
        if idx:
            crsr = self.session['conn'].cursor()
            crsr.execute('SELECT * FROM Clientes WHERE id_clientes = ?;', (idx,))
            cliente = crsr.fetchone()
            
            nombre = cliente[1]
            celular = cliente[2].replace(' ', '')
            correo = cliente[3]
            especial = bool(cliente[6])
            
            self.ui.txtDireccion.setPlainText(cliente[4])
            self.ui.txtRFC.setText(cliente[5])
            self.ui.txtDescuentos.setPlainText(cliente[7])
        else:
            celular = celular.replace(' ', '')
            especial = False
        
        self.ui.txtNombre.setText(nombre)
        self.ui.txtLada.setText(celular[1:-10] or '52')
        self.ui.txtCelular.setText(celular[-10:])
        self.ui.txtCorreo.setText(correo)
        
        self.ui.checkDescuentos.setChecked(especial)
        self.ui.txtDescuentos.setEnabled(especial)
        
        # validador clave de país
        regexp = QRegExp(r'[0-9]{1,}')
        validador = QtGui.QRegExpValidator(regexp)
        self.ui.txtLada.setValidator(validador)

        # crear eventos para los botones
        self.ui.lbRegresar.mousePressEvent = self.closeEvent
        self.ui.btRegistrar.clicked.connect(self.done)
        self.ui.checkDescuentos.clicked.connect(
            lambda estado: self.ui.txtDescuentos.setEnabled(estado))
        
        # deshabilitar modificación de descuentos para usuarios normales
        if not first.session['user'].administrador:
            self.ui.checkDescuentos.setEnabled(False)
            self.ui.txtDescuentos.setEnabled(False)

        self.show()
    
    ####################
    # FUNCIONES ÚTILES #
    ####################
    @property
    def numeroTelefono(self) -> str:
        return f'+{self.ui.txtLada.text()} {self.ui.txtCelular.displayText()}'
    
    def done(self):
        """
        Intenta agregar datos ingresados a la tabla Clientes y
        se notifica al usuario del resultado de la operación.
        """
        clientes_db_parametros = (v.strip() or None if isinstance(v, str)
                                  else v for v in (
            self.ui.txtNombre.text(),
            self.numeroTelefono,
            self.ui.txtCorreo.text(),
            self.ui.txtDireccion.toPlainText(),
            self.ui.txtRFC.text(),
            int(self.ui.checkDescuentos.isChecked()),
            self.ui.txtDescuentos.toPlainText()
        ))
        
        conn = self.session['conn']
        crsr = conn.cursor()

        try:
            if self.idx:        # editar cliente
                crsr.execute('''
                UPDATE  Clientes
                SET     nombre = ?,
                        telefono = ?,
                        correo = ?,
                        direccion = ?,
                        RFC = ?,
                        cliente_especial = ?,
                        descuentos = ?
                WHERE   id_clientes = ?;
                ''', (*clientes_db_parametros, self.idx))
            else:               # crear nuevo cliente
                crsr.execute('''
                INSERT INTO Clientes (
                    nombre, telefono, correo, direccion,
                    RFC, cliente_especial, descuentos
                ) 
                VALUES 
                    (?,?,?,?,?,?,?);
                ''', tuple(clientes_db_parametros))

            conn.commit()
        except fdb.Error as err:
            conn.rollback()

            WarningDialog(self, '¡No se pudo editar el cliente!', str(err))
            return
        
        qm = QtWidgets.QMessageBox
        qm.information(self, 'Éxito', '¡Se editó el cliente!', qm.Ok)
        
        self.success.emit()
        self.close()
