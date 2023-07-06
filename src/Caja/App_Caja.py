from datetime import datetime

import fdb

from PySide6 import QtWidgets
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QDateTime, QDate

from databasemanagers import ManejadorCaja
from mydecorators import run_in_thread
from myutils import enviarAImpresora, formatDate
from mywidgets import LabelAdvertencia, VentanaPrincipal, WarningDialog


#####################
# VENTANA PRINCIPAL #
#####################
class App_Caja(QtWidgets.QMainWindow):
    """
    Backend para la ventana de movimientos de la caja.
    TODO:
    -   exportar corte a archivo
    """
    def __init__(self, parent: VentanaPrincipal):
        from Caja.Ui_Caja import Ui_Caja
        
        super().__init__()

        self.ui = Ui_Caja()
        self.ui.setupUi(self)
        
        LabelAdvertencia(self.ui.tabla_ingresos, '¡No se encontró ningún movimiento!')
        LabelAdvertencia(self.ui.tabla_egresos, '¡No se encontró ningún movimiento!')

        # guardar conexión y usuario como atributos
        self.conn = parent.conn
        self.user = parent.user
        
        # fechas por defecto
        hoy = QDate.currentDate()
        fechaMin, = self.conn \
                    .cursor() \
                    .execute('SELECT MIN(fecha_hora) FROM Caja;') \
                    .fetchone()
        fechaMin = QDateTime(fechaMin).date() if fechaMin else hoy
        
        self.ui.dateDesde.setDate(hoy)
        self.ui.dateDesde.setMaximumDate(hoy)
        self.ui.dateDesde.setMinimumDate(fechaMin)
        
        self.ui.dateHasta.setDate(hoy)
        self.ui.dateHasta.setMaximumDate(hoy)
        self.ui.dateHasta.setMinimumDate(fechaMin)

        # dar formato a la tabla principal
        header_i = self.ui.tabla_ingresos.horizontalHeader()
        header_e = self.ui.tabla_egresos.horizontalHeader()

        for col in range(self.ui.tabla_ingresos.columnCount()):
            if col not in {0, 2}:
                header_i.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
                header_e.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
            else:
                header_i.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
                header_e.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)

        # añade eventos para los botones
        self.ui.btRegresar.clicked.connect(self.goHome)
        self.ui.btIngreso.clicked.connect(self.registrarIngreso)
        self.ui.btEgreso.clicked.connect(self.registrarEgreso)
        
        self.ui.dateDesde.dateChanged.connect(lambda: self.update_display())
        self.ui.dateHasta.dateChanged.connect(lambda: self.update_display())
        self.ui.btHoy.clicked.connect(self.hoy_handle)
        self.ui.btEstaSemana.clicked.connect(self.semana_handle)
        self.ui.btEsteMes.clicked.connect(self.mes_handle)
        self.ui.btImprimir.clicked.connect(self.confirmarImprimir)

    def showEvent(self, event):
        self.update_display(rescan=True)
    
    def resizeEvent(self, event):
        if self.isVisible():
            self.ui.tabla_egresos.resizeRowsToContents()
            self.ui.tabla_ingresos.resizeRowsToContents()
    
    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def hoy_handle(self):
        hoy = QDate.currentDate()
        self.ui.dateDesde.setDate(hoy)
        self.ui.dateHasta.setDate(hoy)
        
    def semana_handle(self):
        hoy = QDate.currentDate()
        
        start = hoy.addDays(-hoy.dayOfWeek())
        end = hoy.addDays(6 - hoy.dayOfWeek())
        
        self.ui.dateDesde.setDate(start)
        self.ui.dateHasta.setDate(end)
    
    def mes_handle(self):
        hoy = QDate.currentDate()
        
        start = QDate(hoy.year(), hoy.month(), 1)
        end = QDate(hoy.year(), hoy.month(), hoy.daysInMonth())
        
        self.ui.dateDesde.setDate(start)
        self.ui.dateHasta.setDate(end)
        
    def update_display(self, rescan: bool = False):
        """ Actualiza la tabla y el contador de usuarios.
            Acepta una cadena de texto para la búsqueda de usuarios.
            También lee de nuevo la tabla de usuarios, si se desea. """
        if rescan:
            manejador = ManejadorCaja(self.conn)

            all_movimientos = manejador.obtenerMovimientos()
            self.all_ingresos = []
            self.all_egresos  = []
            
            for m in all_movimientos:
                lista = self.all_ingresos if m[1] > 0 else self.all_egresos
                lista.append(m)

        bold = QFont()
        bold.setBold(True)
        
        fechaDesde = self.ui.dateDesde.date()
        fechaHasta = self.ui.dateHasta.date()
        
        # <tabla de ingresos>
        tabla = self.ui.tabla_ingresos
        tabla.setRowCount(0)
        
        movimientos = [m for m in self.all_ingresos
                       if fechaDesde <= QDate(m[0]) <= fechaHasta]
        
        ingresos_efectivo = sum(m[1] for m in movimientos if m[3] == 'Efectivo')
        ingresos_transferencia = sum(m[1] for m in movimientos if m[3] == 'Transferencia bancaria')
        ingresos_tarjeta = sum(m[1] for m in movimientos if m[3].startswith('Tarjeta'))
        
        self.ui.lbTotalIngresos.setText(
            f'Total de ingresos: ${sum(m[1] for m in movimientos):,.2f}')
        self.ui.lbIngresosEfectivo.setText(
            f'Efectivo: ${ingresos_efectivo:,.2f}')
        self.ui.lbIngresosTarjeta.setText(
            f'Tarjeta de crédito/débito: ${ingresos_tarjeta:,.2f}')
        self.ui.lbIngresosTransferencia.setText(
            f'Transferencias bancarias: ${ingresos_transferencia:,.2f}')

        for row, movimiento in enumerate(movimientos):
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
        # </tabla de ingresos>
        
        # <tabla de egresos>
        tabla = self.ui.tabla_egresos
        tabla.setRowCount(0)
        
        movimientos = [m for m in self.all_egresos
                       if fechaDesde <= QDate(m[0]) <= fechaHasta]
        
        egresos_efectivo = sum(-m[1] for m in movimientos if m[3] == 'Efectivo')
        egresos_transferencia = sum(-m[1] for m in movimientos if m[3] == 'Transferencia bancaria')
        egresos_tarjeta = sum(-m[1] for m in movimientos if m[3].startswith('Tarjeta'))
        
        self.ui.lbTotalEgresos.setText(
            f'Total de egresos: ${-sum(m[1] for m in movimientos):,.2f}')
        self.ui.lbEgresosEfectivo.setText(
            f'Efectivo: ${egresos_efectivo:,.2f}')
        self.ui.lbEgresosTarjeta.setText(
            f'Tarjeta de crédito/débito: ${egresos_tarjeta:,.2f}')
        self.ui.lbEgresosTransferencia.setText(
            f'Transferencias bancarias: ${egresos_transferencia:,.2f}')

        for row, movimiento in enumerate(movimientos):
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
        # </tabla de egresos>
        
        total = ingresos_tarjeta + ingresos_efectivo + ingresos_transferencia \
              - (egresos_efectivo + egresos_tarjeta + egresos_transferencia)
                
        self.ui.lbTotal.setText(
            f'Total del corte: ${total:,.2f}')
    
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
        """
        Función para generar el corte de caja, comprendido entre fechas dadas.
        Contiene:
            - Realizado el: (fecha)
            - Nombre del usuario activo
            - Fecha inicial y final
            - Fondo inicial de caja
            - Tabla de movimientos 
                Fecha y hora | Descripción | Método de pago | Cantidad
            - Tabla de resumen de movimientos
                Método de pago -> Ingresos | Egresos
        """
        from reportlab.lib.units import mm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_LEFT

        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        import os
        import uuid
        
        # archivo y directorio temporales
        os.makedirs('./tmp/', exist_ok=True)
        
        filename = f'.\\tmp\\{uuid.uuid4().hex[:10]}.pdf'

        doc = SimpleDocTemplate(filename, pagesize=(80*mm, 297*mm),
                                topMargin=0., bottomMargin=0.,
                                leftMargin=0., rightMargin=0.)

        # Define styles for the document
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Left', fontName='Helvetica',
                                  fontSize=9, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='Foot', fontName='Helvetica',
                                  fontSize=11, alignment=TA_LEFT))

        # contenido del PDF
        fechaDesde = self.ui.dateDesde.date()
        fechaHasta = self.ui.dateHasta.date()
        
        # cálculos extra de ingresos
        movimientos = [m for m in self.all_ingresos
                       if fechaDesde <= QDate(m[0]) <= fechaHasta]
        
        ingresos_credito = sum(m[1] for m in movimientos if m[3].endswith('crédito'))
        ingresos_debito = sum(m[1] for m in movimientos if m[3].endswith('débito'))
        
        # cálculos extra de egresos
        movimientos = [m for m in self.all_egresos
                       if fechaDesde <= QDate(m[0]) <= fechaHasta]
        
        egresos_credito = -sum(m[1] for m in movimientos if m[3].endswith('crédito'))
        egresos_debito = -sum(m[1] for m in movimientos if m[3].endswith('débito'))
        
        # totales (todos los métodos)
        movimientos = [m for m in self.all_ingresos + self.all_egresos
                       if fechaDesde <= QDate(m[0]) <= fechaHasta]
        
        total_efectivo = sum(m[1] for m in movimientos if m[3] == 'Efectivo')
        total_transferencia = sum(m[1] for m in movimientos if m[3] == 'Transferencia bancaria')
        total_credito = ingresos_credito - egresos_credito
        total_debito = ingresos_debito - egresos_debito
        
        esperado = sum(m[1] for m in self.all_egresos + self.all_ingresos)
        
        # elementos para constuir el PDF
        elements = [
            Paragraph('Resumen de movimientos de caja', styles['Heading1']),
            Spacer(1, 6),
            
            Paragraph('Realizado por: ' + self.user.nombre, styles['Left']),
            Paragraph(f'Fecha y hora: {formatDate(QDateTime.currentDateTime())}', styles['Left']),
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
            
            Paragraph('Total', styles['Heading3']),
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
        
        # imprimir archivo temporal        
        enviarAImpresora(filename, True)
    
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
        font.setFamily("MS Shell Dlg 2")
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
        
        self.parent_.update_display(rescan=True)
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
