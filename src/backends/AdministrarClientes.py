from datetime import datetime

from PySide6 import QtWidgets
from PySide6.QtGui import QFont, QColor, QIcon, QRegularExpressionValidator
from PySide6.QtCore import Qt, QDate, Signal, QMutex

from core import ROJO
from context import user_context
from interfaces import IModuloPrincipal
from sql import ManejadorClientes
from utils.mydecorators import fondo_oscuro, run_in_thread
from utils.myinterfaces import InterfazFiltro
from utils.myutils import daysTo, exportarXlsx, formatdate, son_similar
from utils.mywidgets import LabelAdvertencia


#####################
# VENTANA PRINCIPAL #
#####################
class App_AdministrarClientes(QtWidgets.QWidget, IModuloPrincipal):
    """Backend para la ventana de administración de clientes."""

    rescanned = Signal()

    def crear(self):
        from ui.Ui_AdministrarClientes import Ui_AdministrarClientes

        self.ui = Ui_AdministrarClientes()
        self.ui.setupUi(self)

        self.mutex = QMutex()

        LabelAdvertencia(self.ui.tabla_clientes, '¡No se encontró ningún cliente!')

        # guardar conexión y usuarios como atributos
        self.conn = user_context.conn
        self.user = user_context.user

        self.all = []

        # añadir menú de opciones al botón para filtrar
        self.filtro = InterfazFiltro(
            self.ui.btFiltrar,
            self.ui.searchBar,
            [('Nombre', 1), ('Teléfono', 2), ('Correo', 3), ('Dirección', 4), ('RFC', 5),],
        )
        self.filtro.cambiado.connect(self.update_display)

        # restringir botón de eliminar cliente
        if not self.user.rol == 'ADMINISTRADOR':
            self.ui.btEliminar.hide()

        # añade eventos para los botones
        self.ui.btAgregar.clicked.connect(self.insertarCliente)
        self.ui.btEditar.clicked.connect(self.editarCliente)
        self.ui.btEliminar.clicked.connect(self.quitarCliente)
        self.ui.btRegresar.clicked.connect(self.go_back.emit)

        self.ui.searchBar.textChanged.connect(self.update_display)
        self.ui.resaltarCheck.stateChanged.connect(self.update_display)
        self.ui.resaltarDias.textChanged.connect(self.resaltarTrigger)
        self.ui.btExportar.clicked.connect(self.exportarExcel)
        self.rescanned.connect(self.update_display)

        self.ui.tabla_clientes.configurarCabecera(lambda col: col in {0, 2, 5, 6})

    def showEvent(self, event):
        self.rescan_update()

    def resizeEvent(self, event):
        if self.isVisible():
            self.ui.tabla_clientes.resizeRowsToContents()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def resaltarTrigger(self):
        """Recolorea la tabla para resaltar clientes que no han
        visitado en una cantidad escogida de días."""
        if self.ui.resaltarCheck.isChecked():
            self.update_display()

    @run_in_thread
    def rescan_update(self, *args):
        if not self.mutex.try_lock():
            return

        self.ui.lbContador.setText('Recuperando información...')

        manejador = ManejadorClientes(self.conn)
        self.all = manejador.obtener_vista('view_all_clientes') or []
        self.ui.lbContador.setText(f'{len(self.all)} clientes en la base de datos.')

        self.rescanned.emit()

    def update_display(self):
        """Actualiza la tabla y el contador de clientes.
        Acepta una cadena de texto para la búsqueda de clientes.
        También lee de nuevo la tabla de clientes, si se desea."""
        tabla = self.ui.tabla_clientes
        tabla.setRowCount(0)

        bold = QFont()
        bold.setBold(True)

        # resalta si un cliente no ha venido en _ días
        dias = int(self.ui.resaltarDias.text())
        # timestamp ahora mismo
        timestamp_now = QDate.currentDate()

        if txt_busqueda := self.ui.searchBar.text().strip():
            found = [c for c in self.all if son_similar(txt_busqueda, c[self.filtro.idx])]
        else:
            found = self.all

        tabla.setRowCount(len(found))

        for row, cliente in enumerate(found):
            for col, dato in enumerate(cliente):
                if isinstance(dato, datetime):
                    delta = QDate(dato).daysTo(timestamp_now)
                    cell = '{} ({})'.format(formatdate(dato), daysTo(delta))
                else:
                    cell = str(dato or '')
                tabla.setItem(row, col, QtWidgets.QTableWidgetItem(cell))

            tabla.item(row, 1).setFont(bold)

            if self.ui.resaltarCheck.isChecked():
                ultimaVisita = QDate(cliente[6])

                if ultimaVisita and ultimaVisita.daysTo(timestamp_now) >= dias:
                    color = QColor(ROJO)
                    tabla.item(row, 6).setBackground(color)

        tabla.resizeRowsToContents()
        self.mutex.unlock()

    def exportarExcel(self):
        """Exportar clientes a un archivo .xlsx."""
        # abrir widget para determinar ubicación de archivo
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Guardar archivo...', filter='Libro de Excel (*.xlsx)'
        )
        if fileName:
            self.generar_xlsx(fileName)

    @run_in_thread
    def generar_xlsx(self, fileName: str):
        titulos = [
            self.ui.tabla_clientes.horizontalHeaderItem(section).text()
            for section in range(1, self.ui.tabla_clientes.columnCount())
        ]
        datos = []

        for cliente in self.all:
            cliente = list(cliente)[1:]  # lista mutable

            for col, dato in enumerate(cliente):
                if isinstance(dato, datetime):
                    cell = formatdate(dato)
                else:
                    cell = str(dato or '')
                cliente[col] = cell
            datos.append(cliente)

        exportarXlsx(fileName, titulos, datos)

    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def insertarCliente(self):
        """Abre ventana para registrar un cliente."""
        widget = App_RegistrarCliente(self)
        widget.success.connect(self.rescan_update)

    def editarCliente(self):
        """Abre ventana para editar un cliente seleccionado."""
        if not (selected := self.ui.tabla_clientes.selectedItems()) or selected[0].text() == '1':
            return

        widget = App_EditarCliente(selected[0].text(), self)
        widget.success.connect(self.rescan_update)

    def quitarCliente(self):
        """Pide confirmación para eliminar clientes de la base de datos."""
        if not (selected := self.ui.tabla_clientes.selectedItems()) or selected[0].text() == '1':
            return

        # abrir pregunta
        qm = QtWidgets.QMessageBox
        manejador = ManejadorClientes(self.conn, '¡No se pudo eliminar el cliente!')

        ret = qm.question(
            self,
            'Atención',
            'Los clientes seleccionados se eliminarán de la base de datos. ¿Desea continuar?',
        )

        if ret == qm.Yes and manejador.eliminarCliente(selected[0].text()):
            qm.information(self, 'Éxito', 'Se eliminaron los clientes seleccionados.')
            self.rescan_update()


#################################
# VENTANAS PARA EDITAR CLIENTES #
#################################
@fondo_oscuro
class Base_EditarCliente(QtWidgets.QWidget):
    """Clase base para registrar o editar cliente."""

    MENSAJE_EXITO: str
    MENSAJE_ERROR: str

    success = Signal(str, str, str)

    def __init__(self, parent=None):
        from ui.Ui_EditarCliente import Ui_EditarCliente

        super().__init__(parent)

        self.ui = Ui_EditarCliente()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.Window)

        # guardar conexión y usuarios como atributos
        self.conn = user_context.conn
        self.user = user_context.user

        # validador clave de país
        self.ui.txtLada.setValidator(QRegularExpressionValidator(r'[0-9]{1,}'))

        # crear eventos para los botones
        self.ui.btRegresar.clicked.connect(self.close)
        self.ui.btRegistrar.clicked.connect(self.done)
        self.ui.checkDescuentos.clicked.connect(lambda estado: self.ui.txtDescuentos.setEnabled(estado))

        # deshabilitar modificación de descuentos para usuarios normales
        if not self.user.administrador:
            self.ui.checkDescuentos.setEnabled(False)
            self.ui.txtDescuentos.setEnabled(False)

        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    ####################
    # FUNCIONES ÚTILES #
    ####################
    def numeroTelefono(self):
        return '+{} {}'.format(self.ui.txtLada.displayText(), self.ui.txtCelular.displayText())

    def agregarDatosPorDefecto(self, nombre: str, celular: str, correo: str):
        """Datos por defecto, proveído por ambas clases heredadas."""
        if correo and correo.startswith('N/A'):
            correo = ''
        celular = celular.replace(' ', '') # quitar espacios

        self.ui.txtNombre.setText(nombre)
        self.ui.txtLada.setText(celular[1:-10] or '52')
        self.ui.txtCelular.setText(celular[-10:])
        self.ui.txtCorreo.setText(correo)

    def done(self):
        """Método en el que se modificará o insertará un cliente."""
        params = (
            self.ui.txtNombre.text(),
            self.numeroTelefono(),
            self.ui.txtCorreo.text(),
            self.ui.txtDireccion.toPlainText(),
            self.ui.txtRFC.text(),
            self.ui.checkDescuentos.isChecked(),
            self.ui.txtDescuentos.toPlainText(),
        )
        clientes_db_parametros = tuple(v.strip() or None if isinstance(v, str) else v for v in params)

        if self.insertar_o_modificar(clientes_db_parametros):
            QtWidgets.QMessageBox.information(self, 'Éxito', self.MENSAJE_EXITO)

            self.success.emit(
                self.ui.txtNombre.text(), self.numeroTelefono(), self.ui.txtCorreo.text(),
            )
            self.close()

    def insertar_o_modificar(self, clientes_db_parametros: tuple):
        """Función a sobreescribir donde se realiza consulta SQL."""
        raise NotImplementedError('BEIS CLASSSSSSS')


class App_RegistrarCliente(Base_EditarCliente):
    """Backend para la función de registrar cliente."""

    MENSAJE_EXITO = '¡Se registró el cliente!'
    MENSAJE_ERROR = '¡No se pudo registrar el cliente!'

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui.lbTitulo.setText('Registrar cliente')
        self.ui.btRegistrar.setText(' Registrar cliente')
        self.ui.btRegistrar.setIcon(QIcon(':/img/resources/images/plus.png'))

        self.agregarDatosPorDefecto('', '999', '')

    ####################
    # FUNCIONES ÚTILES #
    ####################
    def insertar_o_modificar(self, clientes_db_parametros):
        """Insertar nuevo cliente a la base de datos."""
        manejador = ManejadorClientes(self.conn, self.MENSAJE_ERROR)
        return manejador.insertarCliente(clientes_db_parametros)


class App_EditarCliente(Base_EditarCliente):
    """Backend para la función de editar cliente."""

    MENSAJE_EXITO = '¡Se editó el cliente!'
    MENSAJE_ERROR = '¡No se pudo editar el cliente!'

    def __init__(self, idx: int, parent=None):
        super().__init__(parent)

        self.idx = idx  # id del cliente a editar

        # obtener datos del cliente
        manejador = ManejadorClientes(self.conn)
        cliente = manejador.obtenerCliente(idx)

        self.agregarDatosPorDefecto(cliente.nombre, cliente.telefono, cliente.correo)

        self.ui.txtDireccion.setPlainText(cliente.direccion)
        self.ui.txtRFC.setText(cliente.rfc)

        self.ui.checkDescuentos.setChecked(cliente.cliente_especial)
        self.ui.txtDescuentos.setEnabled(cliente.cliente_especial)
        self.ui.txtDescuentos.setPlainText(cliente.descuentos)

    ####################
    # FUNCIONES ÚTILES #
    ####################
    def insertar_o_modificar(self, clientes_db_parametros):
        """Actualizar datos del cliente en la base de datos."""
        manejador = ManejadorClientes(self.conn, self.MENSAJE_ERROR)
        return manejador.actualizarCliente(self.idx, clientes_db_parametros)
