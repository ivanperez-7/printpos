from PySide6 import QtWidgets
from PySide6.QtCore import QMutex, Signal
from PySide6.QtGui import QFont

from context import user_context
from core import Moneda, NumeroDecimal
from interfaces import IModuloPrincipal
from pdf import ImpresoraTickets
from sql import ManejadorCaja
from utils.mydataclasses import Caja
from utils.mydecorators import run_in_thread
from utils.myinterfaces import InterfazFechas
from utils.mywidgets import LabelAdvertencia


#####################
# VENTANA PRINCIPAL #
#####################
class App_Caja(QtWidgets.QWidget, IModuloPrincipal):
    """Backend para la ventana de movimientos de la caja."""

    rescanned = Signal()

    def crear(self):
        from ui.Ui_Caja import Ui_Caja

        self.ui = Ui_Caja()
        self.ui.setupUi(self)

        self.mutex = QMutex()

        LabelAdvertencia(self.ui.tabla_ingresos, '¡No se encontró ningún movimiento!')
        LabelAdvertencia(self.ui.tabla_egresos, '¡No se encontró ningún movimiento!')

        # guardar conexión y usuario como atributos
        self.conn = user_context.conn
        self.user = user_context.user

        self.all_movimientos = Caja()

        # interfaz de widgets de fechas
        manejador = ManejadorCaja(self.conn)
        fechaMin = manejador.obtenerFechaPrimerMov()

        self.iFechas = InterfazFechas(
            self.ui.btHoy,
            self.ui.btEstaSemana,
            self.ui.btEsteMes,
            self.ui.dateDesde,
            self.ui.dateHasta,
            fechaMin,
        )
        self.iFechas.dateChanged.connect(self.rescan_update)

        # añade eventos para los botones
        self.ui.btRegresar.clicked.connect(self.go_back.emit)
        self.ui.btIngreso.clicked.connect(self.registrarIngreso)
        self.ui.btEgreso.clicked.connect(self.registrarEgreso)

        self.ui.btImprimir.clicked.connect(self.confirmar_imprimir)
        self.rescanned.connect(self.update_display)

        self.ui.tabla_ingresos.configurarCabecera(lambda col: col not in {0, 2})
        self.ui.tabla_egresos.configurarCabecera(lambda col: col not in {0, 2})

    def showEvent(self, event):
        self.rescan_update()

    def resizeEvent(self, event):
        if self.isVisible():
            self.ui.tabla_egresos.resizeRowsToContents()
            self.ui.tabla_ingresos.resizeRowsToContents()

    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @run_in_thread
    def rescan_update(self, *args):
        if not self.mutex.try_lock():
            return

        self.ui.lbTotal.setText('Recuperando información...')

        manejador = ManejadorCaja(self.conn)
        fechas = self.iFechas.rango_fechas
        movimientos = manejador.obtenerMovimientos(fechas) or []

        self.all_movimientos = Caja(movimientos)
        self.rescanned.emit()

    def update_display(self):
        """Actualiza las tablas de ingresos y egresos.

        Relee base de datos en cualquier evento (en este caso, al mover fechas)."""
        total = self.all_movimientos.totalCorte()
        self.ui.lbTotal.setText(f'Total del corte: ${total}')

        self.llenar_ingresos()
        self.llenar_egresos()
        self.mutex.unlock()

    def llenar_ingresos(self):
        bold = QFont()
        bold.setBold(True)

        movimientos = self.all_movimientos

        self.ui.lbTotalIngresos.setText('Total de ingresos: ${}'.format(movimientos.totalIngresos()))
        self.ui.lbIngresosEfectivo.setText('Efectivo: ${}'.format(movimientos.totalIngresos('Efectivo')))
        self.ui.lbIngresosTarjeta.setText(
            'Tarjeta de crédito/débito: ${}'.format(movimientos.totalIngresos('Tarjeta'))
        )
        self.ui.lbIngresosTransferencia.setText(
            'Transferencias bancarias: ${}'.format(movimientos.totalIngresos('Transferencia'))
        )

        tabla = self.ui.tabla_ingresos
        tabla.modelo = tabla.Modelos.RESALTAR_SEGUNDA
        tabla.llenar(movimientos.todoIngresos)
        tabla.resizeRowsToContents()

    def llenar_egresos(self):
        bold = QFont()
        bold.setBold(True)

        movimientos = self.all_movimientos

        self.ui.lbTotalEgresos.setText('Total de egresos: ${}'.format(-movimientos.totalEgresos()))
        self.ui.lbEgresosEfectivo.setText('Efectivo: ${}'.format(-movimientos.totalEgresos('Efectivo')))
        self.ui.lbEgresosTarjeta.setText(
            'Tarjeta de crédito/débito: ${}'.format(-movimientos.totalEgresos('Tarjeta'))
        )
        self.ui.lbEgresosTransferencia.setText(
            'Transferencias bancarias: ${}'.format(-movimientos.totalEgresos('Transferencia'))
        )

        tabla = self.ui.tabla_egresos
        tabla.modelo = tabla.Modelos.RESALTAR_SEGUNDA
        tabla.llenar(movimientos.todoEgresos)
        tabla.resizeRowsToContents()

    def confirmar_imprimir(self):
        """Ventana de confirmación para imprimir corte."""
        qm = QtWidgets.QMessageBox
        ret = qm.question(
            self,
            'Atención',
            'Se procederá a imprimir el corte de caja entre ' 'las fechas proporcionadas.\n¿Desea continuar?',
        )

        if ret == qm.Yes:
            impresora = ImpresoraTickets(self.conn)
            impresora.imprimirCorteCaja(self.all_movimientos, self.user.nombre)

    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def registrarIngreso(self):
        """Registrar ingreso en movimientos."""
        self.Dialog = Dialog_Registrar()
        self.Dialog.success.connect(self.rescan_update)

    def registrarEgreso(self):
        """Registrar egreso en movimientos."""
        self.Dialog = Dialog_Registrar(egreso=True)
        self.Dialog.success.connect(self.rescan_update)


#################################
# VENTANAS USADAS POR EL MÓDULO #
#################################
class Dialog_Registrar(QtWidgets.QDialog):
    success = Signal()

    def __init__(self, *, egreso=False):
        from ui.Ui_RegistrarMovimiento import Ui_RegistrarMovimiento

        super().__init__()
        self.ui = Ui_RegistrarMovimiento()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())

        ttl = 'Registrar ' + ('egreso' if egreso else 'ingreso')
        self.setWindowTitle(ttl)

        self.egreso = egreso
        self.conn = user_context.conn
        self.user = user_context.user

        # validadores para datos numéricos
        self.ui.txtCantidad.setValidator(NumeroDecimal)

        self.show()

    def accept(self):
        try:
            monto = float(self.ui.txtCantidad.text()) * (-1 if self.egreso else 1)
        except ValueError:
            monto = 0.0
        motivo = self.ui.txtMotivo.text()

        if not (monto and motivo):
            return
        manejador = ManejadorCaja(self.conn, '¡No se pudo registrar el movimiento!')
        id_metodo = manejador.obtenerIdMetodoPago(self.metodo)

        caja_db_parametros = (Moneda(monto), motivo, id_metodo, self.user.id)
        if manejador.insertarMovimiento(caja_db_parametros):
            self.close()
            QtWidgets.QMessageBox.information(self, 'Éxito', '¡Movimiento registrado!')
            self.success.emit()

    @property
    def metodo(self):
        if (out := self.ui.groupMetodo.checkedButton().text()) == 'Transferencia':
            out += ' bancaria'
        return out
