from dataclasses import dataclass
from datetime import datetime

from PySide6 import QtWidgets
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QDateTime

from utils.databasemanagers import ManejadorCaja
from utils.mydecorators import run_in_thread
from utils.myinterfaces import InterfazFechas
from utils.myutils import enviarAImpresora, formatDate, generarPDFTemporal
from utils.mywidgets import LabelAdvertencia, VentanaPrincipal


##################
# CLASE AUXILIAR #
##################
@dataclass
class Movimiento:
    """ Clase para mantener registro de un movimiento en la caja. """
    fecha_hora: datetime    # tipo de dato recibido por la DB
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
        return iter((self.fecha_hora, self.monto, self.descripcion,
                     self.metodo, self.usuario))


@dataclass
class Caja:
    """ Clase para manejar todos los movimientos en caja. """
    movimientos: list[Movimiento]
    
    def todoIngresos(self):
        """ Regresa lista de movimientos que son ingresos. """
        return [m for m in self.movimientos if m.esIngreso]
    
    def todoEgresos(self):
        """ Regresa lista de movimientos que son egresos. """
        return [m for m in self.movimientos if not m.esIngreso]
    
    def _total(self, iter: list[Movimiento], metodo: str = None) -> float:
        if metodo:
            return sum(m.monto for m in iter if m.metodo.startswith(metodo))
        else:
            return sum(m.monto for m in iter)
    
    def totalIngresos(self, metodo: str = None):
        return self._total(self.todoIngresos(), metodo)
    
    def totalEgresos(self, metodo: str = None):
        return self._total(self.todoEgresos(), metodo)
    
    def totalCorte(self, metodo: str = None):
        return self._total(self.movimientos, metodo)


#####################
# VENTANA PRINCIPAL #
#####################
class App_Caja(QtWidgets.QMainWindow):
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
        self.all_movimientos = Caja([Movimiento(*m) for m in movimientos])
        
        self.llenar_ingresos()
        self.llenar_egresos()
        
        total = self.all_movimientos.totalCorte()
                
        self.ui.lbTotal.setText(
            f'Total del corte: ${total:,.2f}')

    def llenar_ingresos(self):
        bold = QFont()
        bold.setBold(True)
        
        tabla = self.ui.tabla_ingresos
        tabla.setRowCount(0)
        
        movimientos = self.all_movimientos
        
        self.ui.lbTotalIngresos.setText(
            'Total de ingresos: ${:,.2f}'.format(movimientos.totalIngresos()))
        self.ui.lbIngresosEfectivo.setText(
            'Efectivo: ${:,.2f}'.format(movimientos.totalIngresos('Efectivo')))
        self.ui.lbIngresosTarjeta.setText(
            'Tarjeta de crédito/débito: ${:,.2f}'.format(movimientos.totalIngresos('Tarjeta')))
        self.ui.lbIngresosTransferencia.setText(
            'Transferencias bancarias: ${:,.2f}'.format(movimientos.totalIngresos('Transferencia')))

        for row, movimiento in enumerate(movimientos.todoIngresos()):
            tabla.insertRow(row)

            for col, dato in enumerate(movimiento):
                if isinstance(dato, datetime):
                    cell = formatDate(dato)
                elif isinstance(dato, float):
                    cell = f'{dato:,.2f}'
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
            'Total de egresos: ${:,.2f}'.format(-movimientos.totalEgresos()))
        self.ui.lbEgresosEfectivo.setText(
            'Efectivo: ${:,.2f}'.format(-movimientos.totalEgresos('Efectivo')))
        self.ui.lbEgresosTarjeta.setText(
            'Tarjeta de crédito/débito: ${:,.2f}'.format(-movimientos.totalEgresos('Tarjeta')))
        self.ui.lbEgresosTransferencia.setText(
            'Transferencias bancarias: ${:,.2f}'.format(-movimientos.totalEgresos('Transferencia')))

        for row, movimiento in enumerate(movimientos.todoEgresos()):
            tabla.insertRow(row)

            for col, dato in enumerate(movimiento):
                if isinstance(dato, datetime):
                    cell = formatDate(dato)
                elif isinstance(dato, float):
                    cell = f'{dato:,.2f}'
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
                          'las fechas proporcionadas. \n¿Desea continuar?',
                          qm.Yes | qm.No)
        
        if ret == qm.Yes:
            self.generarCortePDF()
    
    @run_in_thread
    def generarCortePDF(self):
        """ Función para generar el corte de caja, comprendido entre fechas dadas.
            Contiene:
                - Realizado el: (fecha)
                - Nombre del usuario activo
                - Fecha inicial y final
                - Fondo inicial de caja
                - Tabla de movimientos 
                    Fecha y hora | Descripción | Método de pago | Cantidad
                - Tabla de resumen de movimientos
                    Método de pago -> Ingresos | Egresos """
        from reportlab.lib.units import mm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_LEFT

        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        
        filename = generarPDFTemporal()

        doc = SimpleDocTemplate(filename, pagesize=(80*mm, 297*mm),
                                topMargin=0., bottomMargin=0.,
                                leftMargin=0., rightMargin=0.)

        # estilos de párrafos
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Left', fontName='Helvetica',
                                  fontSize=9, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='Foot', fontName='Helvetica',
                                  fontSize=11, alignment=TA_LEFT))
        
        # cálculos extra de ingresos
        ingresos_credito = self.all_movimientos.totalIngresos('Tarjeta de crédito')
        ingresos_debito = self.all_movimientos.totalIngresos('Tarjeta de débito')
        
        # cálculos extra de egresos
        egresos_credito = -self.all_movimientos.totalEgresos('Tarjeta de crédito')
        egresos_debito = -self.all_movimientos.totalEgresos('Tarjeta de débito')
        
        # totales (todos los métodos)
        total_efectivo = self.all_movimientos.totalCorte('Efectivo')
        total_transferencia = self.all_movimientos.totalCorte('Transferencia')
        total_credito = ingresos_credito - egresos_credito
        total_debito = ingresos_debito - egresos_debito
        
        esperado = self.all_movimientos.totalCorte()
        
        # elementos para constuir el PDF
        elements = [
            Paragraph('Resumen de movimientos de caja', styles['Heading1']),
            Spacer(1, 6),
            
            Paragraph('Realizado por: ' + self.user.nombre, styles['Left']),
            Paragraph('Fecha y hora: ' + formatDate(QDateTime.currentDateTime()), styles['Left']),
            Spacer(1, 6),
            
            Paragraph('Resumen de ingresos', styles['Heading3']),
            Paragraph(self.ui.lbIngresosEfectivo.text(), styles['Left'], bulletText='•'),
            Paragraph(f'Tarjeta de crédito: ${ingresos_credito:,.2f}', styles['Left'], bulletText='•'),
            Paragraph(f'Tarjeta de débito: ${ingresos_debito:,.2f}', styles['Left'], bulletText='•'),
            Paragraph(self.ui.lbIngresosTransferencia.text(), styles['Left'], bulletText='•'),
            Spacer(1, 6),
            
            Paragraph('Resumen de egresos', styles['Heading3']),
            Paragraph(self.ui.lbEgresosEfectivo.text(), styles['Left'], bulletText='•'),
            Paragraph(f'Tarjeta de crédito: ${egresos_credito:,.2f}', styles['Left'], bulletText='•'),
            Paragraph(f'Tarjeta de débito: ${egresos_debito:,.2f}', styles['Left'], bulletText='•'),
            Paragraph(self.ui.lbEgresosTransferencia.text(), styles['Left'], bulletText='•'),
            Spacer(1, 6),
            
            Paragraph('Esperado', styles['Heading3']),
            Paragraph(f'Efectivo: ${total_efectivo:,.2f}', styles['Left'], bulletText='•'),
            Paragraph(f'Tarjeta de crédito: ${total_credito:,.2f}', styles['Left'], bulletText='•'),
            Paragraph(f'Tarjeta de débito: ${total_debito:,.2f}', styles['Left'], bulletText='•'),
            Paragraph(f'Transferencias bancarias: ${total_transferencia:,.2f}', styles['Left'], bulletText='•'),
            Spacer(1, 20),
            
            Paragraph('<b>' + self.ui.lbTotalIngresos.text() + '</b>', styles['Foot']),
            Paragraph('<b>' + self.ui.lbTotalEgresos.text() + '</b>', styles['Foot']),
            Paragraph(f'<b>Esperado en caja: ${esperado:,.2f}</b>', styles['Foot']),
        ]

        # Build the PDF document
        doc.build(elements)
        
        # ????? asegurar archivo cerrado
        with open(filename, 'rb') as f:
            pass
        
        # imprimir archivo temporal        
        enviarAImpresora(filename, False)
    
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
        from Home import App_Home

        parent = self.parentWidget()       # QMainWindow
        new = App_Home(parent)
        parent.setCentralWidget(new)



#################################
# VENTANAS USADAS POR EL MÓDULO #
#################################

class Dialog_Registrar(QtWidgets.QDialog):
    def __init__(self, parent: App_Caja, egreso = False):
        from PySide6 import QtCore, QtGui
        
        super().__init__(parent)
        
        self.egreso = egreso # es egreso o no
        
        self.conn = parent.conn
        self.user = parent.user
        self.parent_ = parent
        
        if egreso:
            self.setWindowTitle("Registrar egreso")
        else:
            self.setWindowTitle("Registrar ingreso")

        self.setFixedSize(525, 160)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
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
        horizontalLayout.addWidget(btEfectivo, 0, Qt.AlignHCenter|Qt.AlignVCenter)
        btTarjetaCredito = QtWidgets.QRadioButton(frame)
        btTarjetaCredito.setFont(font)
        btTarjetaCredito.setText("Tarjeta de crédito")
        groupMetodo.addButton(btTarjetaCredito)
        horizontalLayout.addWidget(btTarjetaCredito, 0, Qt.AlignHCenter|Qt.AlignVCenter)
        btTarjetaDebito = QtWidgets.QRadioButton(frame)
        btTarjetaDebito.setFont(font)
        btTarjetaDebito.setText("Tarjeta de débito")
        groupMetodo.addButton(btTarjetaDebito)
        horizontalLayout.addWidget(btTarjetaDebito, 0, Qt.AlignHCenter|Qt.AlignVCenter)
        btTransferencia = QtWidgets.QRadioButton(frame)
        btTransferencia.setFont(font)
        btTransferencia.setText("Transferencia bancaria")
        btTransferencia.setObjectName("btTransferencia")
        groupMetodo.addButton(btTransferencia)
        horizontalLayout.addWidget(btTransferencia, 0, Qt.AlignHCenter|Qt.AlignVCenter)
        formLayout.setWidget(2, QtWidgets.QFormLayout.SpanningRole, frame)
        buttonBox = QtWidgets.QDialogButtonBox(self)
        buttonBox.setFont(font)
        buttonBox.setOrientation(Qt.Horizontal)
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        buttonBox.setCenterButtons(True)
        buttonBox.setObjectName("buttonBox")
        formLayout.setWidget(3, QtWidgets.QFormLayout.SpanningRole, buttonBox)

        buttonBox.accepted.connect(self.accept) # type: ignore
        buttonBox.rejected.connect(self.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(self)
        
        # guardar algunos widgets como atributos
        self.txtCantidad = txtCantidad
        self.groupMetodo = groupMetodo
        self.txtMotivo = txtMotivo
        
        # validadores para datos numéricos
        regexp_numero = QtCore.QRegularExpression(r'\d*\.?\d*')
        validador = QtGui.QRegularExpressionValidator(regexp_numero)
        txtCantidad.setValidator(validador)
        
        self.show()
    
    def accept(self):
        if self.monto == 0. or not self.motivo:
            return
        
        caja_db_parametros = (
            QDateTime.currentDateTime().toPython(),
            self.monto,
            self.motivo,
            self.metodo,
            self.user.id
        )
        manejador = ManejadorCaja(self.conn, 
                                  '¡No se pudo registrar el movimiento!')
        
        if not manejador.insertarMovimiento(caja_db_parametros):
            return
        
        QtWidgets.QMessageBox.information(
            self, 'Éxito', '¡Movimiento registrado!')
        
        self.parent_.update_display()
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
