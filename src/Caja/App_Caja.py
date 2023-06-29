from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QDateTime, QDate

from mydecorators import run_in_thread
from myutils import enviarAImpresora, formatDate
from mywidgets import LabelAdvertencia, WarningDialog

import fdb

#####################
# VENTANA PRINCIPAL #
#####################

class App_Caja(QtWidgets.QMainWindow):
    """
    Backend para la ventana de movimientos de la caja.
    TODO:
    -   exportar corte a archivo
    """
    def __init__(self, parent=None):
        from Caja.Ui_Caja import Ui_Caja
        
        super().__init__()

        self.ui = Ui_Caja()
        self.ui.setupUi(self)
    
        self.session = parent.session  # conexión y usuario actual
        
        LabelAdvertencia(self.ui.tabla_ingresos, '¡No se encontró ningún movimiento!')
        LabelAdvertencia(self.ui.tabla_egresos, '¡No se encontró ningún movimiento!')
        
        # fechas por defecto
        hoy = QDate.currentDate()
        fechaMin, = self.session['conn'] \
                    .cursor() \
                    .execute('SELECT MIN(fechaHora) FROM Caja;') \
                    .fetchone()
        fechaMin = QDateTime.fromSecsSinceEpoch(fechaMin).date() if fechaMin else hoy
        
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
        self.ui.lbRegresar.mousePressEvent = self.goHome
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
        """
        Actualiza la tabla y el contador de usuarios.
        Acepta una cadena de texto para la búsqueda de usuarios.
        También lee de nuevo la tabla de usuarios, si se desea.
        """
        if rescan:
            crsr = self.session['conn'].cursor()
            crsr.execute('''
            SELECT 	fechaHora,
                    monto,
                    descripcion,
                    metodo,
                    U.nombre
            FROM 	Caja AS C
                    LEFT JOIN Usuarios AS U
                           ON C.idUsuarios = U.idUsuarios
            ORDER   BY fechaHora DESC;
            ''')

            all_movimientos = crsr.fetchall()
            self.all_ingresos = []
            self.all_egresos  = []
            
            for m in all_movimientos:
                lista = self.all_ingresos if m[1] > 0 else self.all_egresos
                lista.append(m)

        bold = QtGui.QFont()
        bold.setBold(True)
        
        fechaDesde = self.ui.dateDesde.date()
        fechaHasta = self.ui.dateHasta.date()
        
        dateFromSecs = lambda s: QDateTime.fromSecsSinceEpoch(s).date()
        
        # <tabla de ingresos>
        tabla = self.ui.tabla_ingresos
        tabla.setRowCount(0)
        
        movimientos = [m for m in self.all_ingresos
                       if fechaDesde <= dateFromSecs(m[0]) <= fechaHasta]
        
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
                if isinstance(dato, int):
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
                       if fechaDesde <= dateFromSecs(m[0]) <= fechaHasta]
        
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
                if isinstance(dato, int):
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
        """
        Ventana de confirmación para imprimir corte.
        """
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
        from reportlab.lib.units import mm, inch
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        from reportlab.platypus import (Table, TableStyle, SimpleDocTemplate,
                                        Paragraph, Spacer)
        import os
        import uuid
        
        # archivo y directorio temporales
        os.makedirs('./tmp/', exist_ok=True)
        
        filename = f'.\\tmp\\{uuid.uuid4().hex}.pdf'

        doc = SimpleDocTemplate(filename, pagesize=(5.5*inch, 8.5*inch),
                                leftMargin=1*inch, rightMargin=1*inch)

        # Define styles for the document
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Left', fontName='Helvetica',
                                fontSize=8, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='Cell', fontName='Helvetica',
                                fontSize=8, alignment=TA_CENTER))

        # contenido del PDF
        fechaDesde = self.ui.dateDesde.date()
        fechaHasta = self.ui.dateHasta.date()
        
        dateFromSecs = lambda s: QDateTime.fromSecsSinceEpoch(s).date()
        
        movimientos = [m for m in self.all_ingresos + self.all_egresos
                       if fechaDesde <= dateFromSecs(m[0]) <= fechaHasta]

        data = [['Fecha y hora', 'Descripción', 'Forma de pago', 'Monto', 'Responsable']]

        for fechaHora, monto, descripcion, metodo, usuario in movimientos:
            data.append([
                formatDate(fechaHora),
                Paragraph(descripcion, styles['Cell']),
                Paragraph(metodo, styles['Cell']),
                monto,
                Paragraph(usuario, styles['Cell']),
            ])

        # productos de la compra
        tabla_productos = Table(data)

        tabla_productos.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONT', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('LINEBELOW', (0, 0), (-1, 0), 0.4, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 0.4, colors.black)
        ]))
        
        # elementos para constuir el PDF
        elements = [
            Paragraph('Resumen de corte de caja', styles['Title']),
            Paragraph('Fracc. Residencial Pensiones', styles['Left']),
            Spacer(1, 6),

            Paragraph('Teléfono: 999 649 0443', styles['Left']),
            Spacer(1, 6),

            Paragraph('* '*40, styles['Left']),
            Paragraph(f'<b>Fecha</b>: {formatDate(QDateTime.currentDateTime())}', styles['Left']),
            Spacer(1, 10),

            tabla_productos]

        # Build the PDF document
        doc.build(elements)
        
        # imprimir archivo temporal        
        enviarAImpresora(filename, True)
    
    # ====================================
    #  VENTANAS INVOCADAS POR LOS BOTONES
    # ====================================
    def registrarIngreso(self):
        dialogRegistrar = Dialog_Registrar(self)
        
        # callbacks para los botones
        def accepted_handle():
            try:
                cantidad = float(dialogRegistrar.txtCantidad.text())
                motivo = dialogRegistrar.txtMotivo.text().strip()
                metodo = dialogRegistrar.groupMetodo.checkedButton().text()
            except (ValueError, AttributeError):
                return
            
            if cantidad <= 0. or not motivo:
                return
            
            conn = self.session['conn']
            crsr = conn.cursor()
            caja_db_parametros = (
                QDateTime.currentDateTime().toSecsSinceEpoch(),
                cantidad,
                motivo,
                metodo,
                self.session['user'].id
            )
            
            try:
                crsr.execute('''
                INSERT INTO Caja (
                    fechaHora, monto,
                    descripcion, metodo, idUsuarios
                )
                VALUES
                    (?,?,?,?,?);
                ''', caja_db_parametros)
                
                conn.commit()
            except fdb.Error as err:
                conn.rollback()
                
                WarningDialog(self, '¡No pudo se registrar el movimiento!', str(err))
                return
            
            QtWidgets.QMessageBox.information(self, 'Éxito', '¡Movimiento registrado!')
            self.update_display(rescan=True)
            dialogRegistrar.close()
            
        dialogRegistrar.accept = accepted_handle
    
    def registrarEgreso(self):
        dialogRegistrar = Dialog_Registrar(self)
        dialogRegistrar.setWindowTitle('Registrar egreso')
        
        # callbacks para los botones
        def accepted_handle():
            try:
                cantidad = float(dialogRegistrar.txtCantidad.text())
                motivo = dialogRegistrar.txtMotivo.text().strip()
                metodo = dialogRegistrar.groupMetodo.checkedButton().text()
            except (ValueError, AttributeError):
                return
            
            if cantidad <= 0. or not motivo:
                return
            
            conn = self.session['conn']
            crsr = conn.cursor()
            caja_db_parametros = (
                QDateTime.currentDateTime().toSecsSinceEpoch(),
                -abs(cantidad),
                motivo,
                metodo,
                self.session['user'].id
            )
            
            try:
                crsr.execute('''
                INSERT INTO Caja (
                    fechaHora, monto,
                    descripcion, metodo, idUsuarios
                )
                VALUES
                    (?,?,?,?,?);
                ''', caja_db_parametros)
                
                conn.commit()
            except fdb.Error as err:
                conn.rollback()
                
                WarningDialog(self, '¡No pudo se registrar el movimiento!', str(err))
                return
            
            QtWidgets.QMessageBox.information(self, 'Éxito', '¡Movimiento registrado!')
            self.update_display(rescan=True)
            dialogRegistrar.close()
            
        dialogRegistrar.accept = accepted_handle
        
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

class Dialog_Registrar(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setupUi(self)
        
        self.show()
    
    def setupUi(self, DialogRegistrar):
        from PyQt5 import QtCore
        
        DialogRegistrar.setObjectName("DialogRegistrar")
        DialogRegistrar.setFixedSize(525, 160)
        DialogRegistrar.setWindowTitle("Registrar ingreso")
        DialogRegistrar.setWindowFlags(DialogRegistrar.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.formLayout = QtWidgets.QFormLayout(DialogRegistrar)
        self.formLayout.setHorizontalSpacing(25)
        self.formLayout.setVerticalSpacing(9)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(DialogRegistrar)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setText("Monto:")
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.txtCantidad = QtWidgets.QLineEdit(DialogRegistrar)
        self.txtCantidad.setFont(font)
        self.txtCantidad.setText("")
        self.txtCantidad.setObjectName("txtCantidad")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.txtCantidad)
        self.label_2 = QtWidgets.QLabel(DialogRegistrar)
        self.label_2.setFont(font)
        self.label_2.setText("Descripción:")
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.txtMotivo = QtWidgets.QLineEdit(DialogRegistrar)
        self.txtMotivo.setFont(font)
        self.txtMotivo.setObjectName("txtMotivo")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.txtMotivo)
        self.frame = QtWidgets.QFrame(DialogRegistrar)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btEfectivo = QtWidgets.QRadioButton(self.frame)
        self.btEfectivo.setFont(font)
        self.btEfectivo.setText("Efectivo")
        self.btEfectivo.setObjectName("btEfectivo")
        self.groupMetodo = QtWidgets.QButtonGroup(DialogRegistrar)
        self.groupMetodo.setObjectName("groupMetodo")
        self.groupMetodo.addButton(self.btEfectivo)
        self.horizontalLayout.addWidget(self.btEfectivo, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.btTarjetaCredito = QtWidgets.QRadioButton(self.frame)
        self.btTarjetaCredito.setFont(font)
        self.btTarjetaCredito.setText("Tarjeta de crédito")
        self.groupMetodo.addButton(self.btTarjetaCredito)
        self.horizontalLayout.addWidget(self.btTarjetaCredito, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.btTarjetaDebito = QtWidgets.QRadioButton(self.frame)
        self.btTarjetaDebito.setFont(font)
        self.btTarjetaDebito.setText("Tarjeta de débito")
        self.groupMetodo.addButton(self.btTarjetaDebito)
        self.horizontalLayout.addWidget(self.btTarjetaDebito, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.btTransferencia = QtWidgets.QRadioButton(self.frame)
        self.btTransferencia.setFont(font)
        self.btTransferencia.setText("Transferencia bancaria")
        self.btTransferencia.setObjectName("btTransferencia")
        self.groupMetodo.addButton(self.btTransferencia)
        self.horizontalLayout.addWidget(self.btTransferencia, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.SpanningRole, self.frame)
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogRegistrar)
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.SpanningRole, self.buttonBox)

        self.buttonBox.accepted.connect(DialogRegistrar.accept) # type: ignore
        self.buttonBox.rejected.connect(DialogRegistrar.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(DialogRegistrar)
