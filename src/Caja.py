from dataclasses import dataclass
from datetime import datetime
from typing import overload

from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QFont

from utils.moneda import Moneda
from utils.myinterfaces import InterfazFechas
from utils.myutils import *
from utils.mywidgets import LabelAdvertencia, VentanaPrincipal
from utils.sql import ManejadorCaja, ManejadorMetodosPago


##################
# CLASE AUXILIAR #
##################
@dataclass
class Movimiento:
    """ Clase para mantener registro de un movimiento en la caja. """
    fecha_hora: datetime
    monto: float
    descripcion: str
    metodo: str
    usuario: str
    
    @property
    def esIngreso(self):
        return self.monto > 0
    
    def __iter__(self):
        """ Alimenta las tablas principales:
        
            Fecha y hora | Monto | Descripción | Método | Usuario. """
        yield from (self.fecha_hora, self.monto, self.descripcion,
                    self.metodo, self.usuario)


class Caja:
    """ Clase para manejar todos los movimientos en caja. """
    movimientos: list[Movimiento]
    
    @overload
    def __init__(self, movimientos: list[tuple]) -> None: ...
    @overload
    def __init__(self, movimientos: list[Movimiento]) -> None: ...
    
    def __init__(self, movimientos: list[tuple] | list[Movimiento]):
        try:
            mov = movimientos[0]
        except IndexError:
            self.movimientos = []
            return
        
        if isinstance(mov, Movimiento):
            self.movimientos = movimientos
        elif isinstance(mov, tuple):
            self.movimientos = [Movimiento(*m) for m in movimientos]
        else:
            raise TypeError('Lista debe ser de tuplas o Movimiento.')
    
    def todoIngresos(self):
        """ Regresa lista de movimientos que son ingresos. """
        return filter(lambda m: m.esIngreso, self.movimientos)
    
    def todoEgresos(self):
        """ Regresa lista de movimientos que son egresos. """
        return filter(lambda m: not m.esIngreso, self.movimientos)
    
    def __total(self, _iter: list[Movimiento], metodo: str = None):
        if metodo:
            _iter = filter(lambda m: m.metodo.startswith(metodo), _iter)
        return Moneda.sum(m.monto for m in _iter)
    
    def totalIngresos(self, metodo: str = None):
        return self.__total(self.todoIngresos(), metodo)
    
    def totalEgresos(self, metodo: str = None):
        return self.__total(self.todoEgresos(), metodo)
    
    def totalCorte(self, metodo: str = None):
        return self.__total(self.movimientos, metodo)


#####################
# VENTANA PRINCIPAL #
#####################
class App_Caja(QtWidgets.QWidget):
    """ Backend para la ventana de movimientos de la caja. """
    
    def __init__(self, parent: VentanaPrincipal):
        from ui.Ui_Caja import Ui_Caja
        
        super().__init__()
        
        self.ui = Ui_Caja()
        self.ui.setupUi(self)
        
        LabelAdvertencia(self.ui.tabla_ingresos, '¡No se encontró ningún movimiento!')
        LabelAdvertencia(self.ui.tabla_egresos, '¡No se encontró ningún movimiento!')
        
        # guardar conexión y usuario como atributos
        self.conn = parent.conn
        self.user = parent.user
        
        # interfaz de widgets de fechas
        manejador = ManejadorCaja(self.conn)
        fechaMin = manejador.obtenerFechaPrimerMov()
        
        InterfazFechas(self.ui.btHoy, self.ui.btEstaSemana, self.ui.btEsteMes,
                       self.ui.dateDesde, self.ui.dateHasta, fechaMin)
        
        # añade eventos para los botones
        self.ui.btRegresar.clicked.connect(self.goHome)
        self.ui.btIngreso.clicked.connect(self.registrarIngreso)
        self.ui.btEgreso.clicked.connect(self.registrarEgreso)
        
        self.ui.dateDesde.dateChanged.connect(self.update_display)
        self.ui.dateHasta.dateChanged.connect(self.update_display)
        self.ui.btImprimir.clicked.connect(self.confirmarImprimir)
        
        self.ui.tabla_ingresos.configurarCabecera(lambda col: col not in [0, 2])
        self.ui.tabla_egresos.configurarCabecera(lambda col: col not in [0, 2])
    
    def showEvent(self, event):
        self.update_display()
    
    def resizeEvent(self, event):
        if self.isVisible():
            self.ui.tabla_egresos.resizeRowsToContents()
            self.ui.tabla_ingresos.resizeRowsToContents()
    
    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def update_display(self):
        """ Actualiza las tablas de ingresos y egresos.

            Relee base de datos en cualquier evento (en este caso, al mover fechas). """
        fechaDesde = self.ui.dateDesde.date()
        fechaHasta = self.ui.dateHasta.date()
        manejador = ManejadorCaja(self.conn)
        
        movimientos = manejador.obtenerMovimientos(fechaDesde, fechaHasta)
        self.all_movimientos = Caja(movimientos)
        
        self.llenar_ingresos()
        self.llenar_egresos()
        
        total = self.all_movimientos.totalCorte()
        
        self.ui.lbTotal.setText(f'Total del corte: ${total}')
    
    def llenar_ingresos(self):
        bold = QFont()
        bold.setBold(True)
        
        tabla = self.ui.tabla_ingresos
        tabla.setRowCount(0)
        
        movimientos = self.all_movimientos
        
        self.ui.lbTotalIngresos.setText(
            'Total de ingresos: ${}'.format(movimientos.totalIngresos()))
        self.ui.lbIngresosEfectivo.setText(
            'Efectivo: ${}'.format(movimientos.totalIngresos('Efectivo')))
        self.ui.lbIngresosTarjeta.setText(
            'Tarjeta de crédito/débito: ${}'.format(movimientos.totalIngresos('Tarjeta')))
        self.ui.lbIngresosTransferencia.setText(
            'Transferencias bancarias: ${}'.format(movimientos.totalIngresos('Transferencia')))
        
        for row, movimiento in enumerate(movimientos.todoIngresos()):
            tabla.insertRow(row)
            
            for col, dato in enumerate(movimiento):
                if isinstance(dato, datetime):
                    cell = formatDate(dato)
                elif isinstance(dato, float):
                    cell = f'${dato:,.2f}'
                else:
                    cell = str(dato or '')
                tabla.setItem(row, col, QtWidgets.QTableWidgetItem(cell))
            
            tabla.item(row, 1).setFont(bold)
        
        tabla.resizeRowsToContents()
    
    def llenar_egresos(self):
        bold = QFont()
        bold.setBold(True)
        
        tabla = self.ui.tabla_egresos
        tabla.setRowCount(0)
        
        movimientos = self.all_movimientos
        
        self.ui.lbTotalEgresos.setText(
            'Total de egresos: ${}'.format(-movimientos.totalEgresos()))
        self.ui.lbEgresosEfectivo.setText(
            'Efectivo: ${}'.format(-movimientos.totalEgresos('Efectivo')))
        self.ui.lbEgresosTarjeta.setText(
            'Tarjeta de crédito/débito: ${}'.format(-movimientos.totalEgresos('Tarjeta')))
        self.ui.lbEgresosTransferencia.setText(
            'Transferencias bancarias: ${}'.format(-movimientos.totalEgresos('Transferencia')))
        
        for row, movimiento in enumerate(movimientos.todoEgresos()):
            tabla.insertRow(row)
            
            for col, dato in enumerate(movimiento):
                if isinstance(dato, datetime):
                    cell = formatDate(dato)
                elif isinstance(dato, float):
                    cell = f'${dato:,.2f}'
                else:
                    cell = str(dato or '')
                tabla.setItem(row, col, QtWidgets.QTableWidgetItem(cell))
            
            tabla.item(row, 1).setFont(bold)
        
        tabla.resizeRowsToContents()
    
    def confirmarImprimir(self):
        """ Ventana de confirmación para imprimir corte. """
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Atención',
                          'Se procederá a imprimir el corte de caja entre '
                          'las fechas proporcionadas. \n¿Desea continuar?')
        
        if ret == qm.Yes:
            from utils.pdf import ImpresoraTickets
            
            impresora = ImpresoraTickets(self)
            impresora.imprimirCorteCaja(self.all_movimientos, self.user)
    
    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def registrarIngreso(self):
        """ Registrar ingreso en movimientos. """
        self.Dialog = Dialog_Registrar(self)
    
    def registrarEgreso(self):
        """ Registrar egreso en movimientos. """
        self.Dialog = Dialog_Registrar(self, egreso=True)
    
    def goHome(self):
        """ Cierra la ventana y regresa al inicio. """
        parent: VentanaPrincipal = self.parentWidget()
        parent.goHome()


#################################
# VENTANAS USADAS POR EL MÓDULO #
#################################

class Dialog_Registrar(QtWidgets.QDialog):
    def __init__(self, parent: App_Caja, egreso=False):
        from PySide6 import QtCore
        
        super().__init__(parent)
        
        self.egreso = egreso  # es egreso o no
        self.conn = parent.conn
        self.user = parent.user
        
        ttl = 'Registrar ' + ('egreso' if egreso else 'ingreso')
        self.setWindowTitle(ttl)
        
        self.setFixedSize(525, 160)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setModal(True)
        self.setWindowModality(Qt.ApplicationModal)
        formLayout = QtWidgets.QFormLayout(self)
        formLayout.setHorizontalSpacing(25)
        formLayout.setVerticalSpacing(9)
        formLayout.setObjectName("formLayout")
        label = QtWidgets.QLabel(self)
        font = QFont()
        font.setPointSize(10)
        label.setFont(font)
        label.setText("Monto:")
        label.setObjectName("label")
        formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, label)
        txtCantidad = QtWidgets.QLineEdit(self)
        txtCantidad.setFont(font)
        txtCantidad.setText("")
        txtCantidad.setObjectName("txtCantidad")
        formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, txtCantidad)
        label_2 = QtWidgets.QLabel(self)
        label_2.setFont(font)
        label_2.setText("Descripción:")
        label_2.setObjectName("label_2")
        formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, label_2)
        txtMotivo = QtWidgets.QLineEdit(self)
        txtMotivo.setFont(font)
        txtMotivo.setObjectName("txtMotivo")
        formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, txtMotivo)
        frame = QtWidgets.QFrame(self)
        frame.setObjectName("frame")
        horizontalLayout = QtWidgets.QHBoxLayout(frame)
        horizontalLayout.setObjectName("horizontalLayout")
        btEfectivo = QtWidgets.QRadioButton(frame)
        btEfectivo.setFont(font)
        btEfectivo.setText("Efectivo")
        btEfectivo.setObjectName("btEfectivo")
        btEfectivo.setChecked(True)
        groupMetodo = QtWidgets.QButtonGroup(self)
        groupMetodo.setObjectName("groupMetodo")
        groupMetodo.addButton(btEfectivo)
        horizontalLayout.addWidget(btEfectivo, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        btTarjetaCredito = QtWidgets.QRadioButton(frame)
        btTarjetaCredito.setFont(font)
        btTarjetaCredito.setText("Tarjeta de crédito")
        groupMetodo.addButton(btTarjetaCredito)
        horizontalLayout.addWidget(btTarjetaCredito, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        btTarjetaDebito = QtWidgets.QRadioButton(frame)
        btTarjetaDebito.setFont(font)
        btTarjetaDebito.setText("Tarjeta de débito")
        groupMetodo.addButton(btTarjetaDebito)
        horizontalLayout.addWidget(btTarjetaDebito, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        btTransferencia = QtWidgets.QRadioButton(frame)
        btTransferencia.setFont(font)
        btTransferencia.setText("Transferencia bancaria")
        btTransferencia.setObjectName("btTransferencia")
        groupMetodo.addButton(btTransferencia)
        horizontalLayout.addWidget(btTransferencia, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        formLayout.setWidget(2, QtWidgets.QFormLayout.SpanningRole, frame)
        buttonBox = QtWidgets.QDialogButtonBox(self)
        buttonBox.setFont(font)
        buttonBox.setOrientation(Qt.Horizontal)
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        buttonBox.setCenterButtons(True)
        buttonBox.setObjectName("buttonBox")
        formLayout.setWidget(3, QtWidgets.QFormLayout.SpanningRole, buttonBox)
        
        buttonBox.accepted.connect(self.accept)  # type: ignore
        buttonBox.rejected.connect(self.reject)  # type: ignore
        QtCore.QMetaObject.connectSlotsByName(self)
        
        # guardar algunos widgets como atributos
        self.txtCantidad = txtCantidad
        self.groupMetodo = groupMetodo
        self.txtMotivo = txtMotivo
        
        # validadores para datos numéricos
        txtCantidad.setValidator(
            FabricaValidadores.NumeroDecimal)
        
        self.show()
    
    def accept(self):
        if self.monto == 0 or not self.motivo:
            return
        
        id_metodo = ManejadorMetodosPago(self.conn).obtenerIdMetodo(self.metodo)
        caja_db_parametros = (
            QDateTime.currentDateTime().toPython(),
            Moneda(self.monto),
            self.motivo,
            id_metodo,
            self.user.id
        )
        
        manejador = ManejadorCaja(self.conn, '¡No se pudo registrar el movimiento!')
        if not manejador.insertarMovimiento(caja_db_parametros):
            return
        
        QtWidgets.QMessageBox.information(
            self, 'Éxito', '¡Movimiento registrado!')
        
        self.parentWidget().update_display()
        self.close()
    
    @property
    def monto(self):
        try:
            return float(self.txtCantidad.text()) * (-1 if self.egreso else 1)
        except ValueError:
            return 0.
    
    @property
    def metodo(self):
        return self.groupMetodo.checkedButton().text()
    
    @property
    def motivo(self):
        return self.txtMotivo.text()
