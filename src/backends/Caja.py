from PySide6 import QtWidgets
from PySide6.QtCore import QDateTime, QMutex, Signal
from PySide6.QtGui import QFont

from pdf import ImpresoraTickets
from sql import ManejadorCaja, ManejadorMetodosPago
from utils import Moneda
from utils.mydataclasses import Caja
from utils.mydecorators import run_in_thread
from utils.myinterfaces import InterfazFechas
from utils.myutils import FabricaValidadores
from utils.mywidgets import LabelAdvertencia


#####################
# VENTANA PRINCIPAL #
#####################
class App_Caja(QtWidgets.QWidget):
    """ Backend para la ventana de movimientos de la caja. """
    rescanned = Signal()

    def __init__(self, conn, user):
        from ui.Ui_Caja import Ui_Caja

        super().__init__()
        self.ui = Ui_Caja()
        self.ui.setupUi(self)

        self.mutex = QMutex()

        LabelAdvertencia(self.ui.tabla_ingresos, '¡No se encontró ningún movimiento!')
        LabelAdvertencia(self.ui.tabla_egresos, '¡No se encontró ningún movimiento!')

        # guardar conexión y usuario como atributos
        self.conn = conn
        self.user = user

        self.all_movimientos = Caja()

        # interfaz de widgets de fechas
        manejador = ManejadorCaja(self.conn)
        fechaMin = manejador.obtenerFechaPrimerMov()

        InterfazFechas(self.ui.btHoy, self.ui.btEstaSemana, self.ui.btEsteMes,
                       self.ui.dateDesde, self.ui.dateHasta, fechaMin)

        # añade eventos para los botones
        self.ui.btRegresar.clicked.connect(self.goHome)
        self.ui.btIngreso.clicked.connect(self.registrarIngreso)
        self.ui.btEgreso.clicked.connect(self.registrarEgreso)

        self.ui.dateDesde.dateChanged.connect(self.rescan_update)
        self.ui.dateHasta.dateChanged.connect(self.rescan_update)
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

        fechaDesde = self.ui.dateDesde.date()
        fechaHasta = self.ui.dateHasta.date()
        manejador = ManejadorCaja(self.conn)

        movimientos = manejador.obtenerMovimientos(fechaDesde, fechaHasta)
        self.all_movimientos = Caja(movimientos)

        self.rescanned.emit()

    def update_display(self):
        """ Actualiza las tablas de ingresos y egresos.

            Relee base de datos en cualquier evento (en este caso, al mover fechas). """
        total = self.all_movimientos.totalCorte()
        self.ui.lbTotal.setText(f'Total del corte: ${total}')

        self.llenar_ingresos()
        self.llenar_egresos()
        self.mutex.unlock()

    def llenar_ingresos(self):
        bold = QFont()
        bold.setBold(True)

        movimientos = self.all_movimientos

        self.ui.lbTotalIngresos.setText(
            'Total de ingresos: ${}'.format(movimientos.totalIngresos()))
        self.ui.lbIngresosEfectivo.setText(
            'Efectivo: ${}'.format(movimientos.totalIngresos('Efectivo')))
        self.ui.lbIngresosTarjeta.setText(
            'Tarjeta de crédito/débito: ${}'.format(movimientos.totalIngresos('Tarjeta')))
        self.ui.lbIngresosTransferencia.setText(
            'Transferencias bancarias: ${}'.format(movimientos.totalIngresos('Transferencia')))

        tabla = self.ui.tabla_ingresos
        tabla.modelo = tabla.Modelos.RESALTAR_SEGUNDA
        tabla.llenar(movimientos.todoIngresos)
        tabla.resizeRowsToContents()

    def llenar_egresos(self):
        bold = QFont()
        bold.setBold(True)

        movimientos = self.all_movimientos

        self.ui.lbTotalEgresos.setText(
            'Total de egresos: ${}'.format(-movimientos.totalEgresos()))
        self.ui.lbEgresosEfectivo.setText(
            'Efectivo: ${}'.format(-movimientos.totalEgresos('Efectivo')))
        self.ui.lbEgresosTarjeta.setText(
            'Tarjeta de crédito/débito: ${}'.format(-movimientos.totalEgresos('Tarjeta')))
        self.ui.lbEgresosTransferencia.setText(
            'Transferencias bancarias: ${}'.format(-movimientos.totalEgresos('Transferencia')))

        tabla = self.ui.tabla_egresos
        tabla.modelo = tabla.Modelos.RESALTAR_SEGUNDA
        tabla.llenar(movimientos.todoEgresos)
        tabla.resizeRowsToContents()

    def confirmar_imprimir(self):
        """ Ventana de confirmación para imprimir corte. """
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, 'Atención',
                          'Se procederá a imprimir el corte de caja entre '
                          'las fechas proporcionadas.\n¿Desea continuar?')

        if ret == qm.Yes:
            impresora = ImpresoraTickets(self.conn)
            impresora.imprimirCorteCaja(self.all_movimientos, self.user.nombre)

    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def registrarIngreso(self):
        """ Registrar ingreso en movimientos. """
        self.Dialog = Dialog_Registrar(self, self.conn, self.user)
        self.Dialog.success.connect(self.rescan_update)

    def registrarEgreso(self):
        """ Registrar egreso en movimientos. """
        self.Dialog = Dialog_Registrar(self, self.conn, self.user, egreso=True)
        self.Dialog.success.connect(self.rescan_update)

    def goHome(self):
        """ Cierra la ventana y regresa al inicio. """
        self.parentWidget().goHome()


#################################
# VENTANAS USADAS POR EL MÓDULO #
#################################
class Dialog_Registrar(QtWidgets.QDialog):
    success = Signal()

    def __init__(self, parent, conn, user, *, egreso=False):
        from ui.Ui_RegistrarMovimiento import Ui_RegistrarMovimiento

        super().__init__(parent)
        self.ui = Ui_RegistrarMovimiento()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())

        ttl = 'Registrar ' + ('egreso' if egreso else 'ingreso')
        self.setWindowTitle(ttl)

        self.egreso = egreso
        self.conn = conn
        self.user = user

        # validadores para datos numéricos
        self.ui.txtCantidad.setValidator(
            FabricaValidadores.NumeroDecimal)

        self.show()

    def accept(self):
        motivo = self.ui.txtMotivo.text()
        if not (self.monto and motivo):
            return

        id_metodo = ManejadorMetodosPago(self.conn).obtenerIdMetodo(self.metodo)
        caja_db_parametros = (
            QDateTime.currentDateTime().toPython(),
            Moneda(self.monto),
            motivo,
            id_metodo,
            self.user.id
        )

        manejador = ManejadorCaja(self.conn, '¡No se pudo registrar el movimiento!')

        if manejador.insertarMovimiento(caja_db_parametros):
            self.close()
            QtWidgets.QMessageBox.information(self, 'Éxito', '¡Movimiento registrado!')
            self.success.emit()

    @property
    def monto(self):
        try:
            return float(self.ui.txtCantidad.text()) * (-1 if self.egreso else 1)
        except ValueError:
            return 0.

    @property
    def metodo(self):
        if (out := self.ui.groupMetodo.checkedButton().text()) == 'Transferencia':
            out += ' bancaria'
        return out
