# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_Caja.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDateEdit, QFrame, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QPushButton,
    QSizePolicy, QTableWidgetItem, QVBoxLayout, QWidget)

from utils.mywidgets import TablaDatos
from . import resources_rc

class Ui_Caja(object):
    def setupUi(self, Caja):
        if not Caja.objectName():
            Caja.setObjectName(u"Caja")
        Caja.resize(1273, 718)
        self.verticalLayout = QVBoxLayout(Caja)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(Caja)
        self.frame.setObjectName(u"frame")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        self.frame.setFont(font)
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(19, 15, 19, -1)
        self.btRegresar = QPushButton(self.frame)
        self.btRegresar.setObjectName(u"btRegresar")
        self.btRegresar.setFont(font)
        self.btRegresar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btRegresar.setStyleSheet(u"QPushButton {\n"
"        background-color: transparent;\n"
"        border: none;\n"
"        padding: 0px;\n"
"    }\n"
"    QPushButton:hover {\n"
"        background-color: rgba(255, 255, 255, 0);\n"
"    }\n"
"    QPushButton:pressed {\n"
"        background-color: rgba(255, 255, 255, 0);\n"
"    }")
        icon = QIcon()
        icon.addFile(u":/img/resources/images/leftarrow.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btRegresar.setIcon(icon)
        self.btRegresar.setIconSize(QSize(40, 40))
        self.btRegresar.setFlat(True)

        self.horizontalLayout.addWidget(self.btRegresar)

        self.lbTitulo = QLabel(self.frame)
        self.lbTitulo.setObjectName(u"lbTitulo")
        self.lbTitulo.setMinimumSize(QSize(261, 41))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(18)
        self.lbTitulo.setFont(font1)

        self.horizontalLayout.addWidget(self.lbTitulo)


        self.verticalLayout.addWidget(self.frame, 0, Qt.AlignLeft)

        self.frame_2 = QFrame(Caja)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFont(font)
        self.frame_2.setFrameShape(QFrame.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.frame_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setVerticalSpacing(0)
        self.frame_5 = QFrame(self.frame_2)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFont(font)
        self.frame_5.setFrameShape(QFrame.NoFrame)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.gridLayout_3 = QGridLayout(self.frame_5)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setHorizontalSpacing(20)
        self.gridLayout_3.setVerticalSpacing(12)
        self.btImprimir = QPushButton(self.frame_5)
        self.btImprimir.setObjectName(u"btImprimir")
        self.btImprimir.setMinimumSize(QSize(0, 35))
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        font2.setPointSize(11)
        self.btImprimir.setFont(font2)

        self.gridLayout_3.addWidget(self.btImprimir, 0, 0, 1, 2)

        self.btIngreso = QPushButton(self.frame_5)
        self.btIngreso.setObjectName(u"btIngreso")
        self.btIngreso.setMinimumSize(QSize(140, 35))
        self.btIngreso.setFont(font2)
        self.btIngreso.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(0, 190, 0);\n"
"border: 0px;")

        self.gridLayout_3.addWidget(self.btIngreso, 1, 0, 1, 1)

        self.btEgreso = QPushButton(self.frame_5)
        self.btEgreso.setObjectName(u"btEgreso")
        self.btEgreso.setMinimumSize(QSize(140, 35))
        self.btEgreso.setFont(font2)
        self.btEgreso.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"background-color: rgb(210, 0, 0);\n"
"border: 0px;")

        self.gridLayout_3.addWidget(self.btEgreso, 1, 1, 1, 1)


        self.gridLayout.addWidget(self.frame_5, 0, 1, 1, 1, Qt.AlignRight|Qt.AlignVCenter)

        self.frame_6 = QFrame(self.frame_2)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFont(font)
        self.frame_6.setFrameShape(QFrame.NoFrame)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_6)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.frame_7 = QFrame(self.frame_6)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setFont(font)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_7)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(self.frame_7)
        self.label.setObjectName(u"label")
        self.label.setFont(font2)

        self.horizontalLayout_3.addWidget(self.label)

        self.dateDesde = QDateEdit(self.frame_7)
        self.dateDesde.setObjectName(u"dateDesde")
        self.dateDesde.setMinimumSize(QSize(220, 0))
        self.dateDesde.setMaximumSize(QSize(220, 16777215))
        self.dateDesde.setFont(font2)
        self.dateDesde.setCalendarPopup(True)

        self.horizontalLayout_3.addWidget(self.dateDesde)

        self.label_2 = QLabel(self.frame_7)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font2)

        self.horizontalLayout_3.addWidget(self.label_2)

        self.dateHasta = QDateEdit(self.frame_7)
        self.dateHasta.setObjectName(u"dateHasta")
        self.dateHasta.setMinimumSize(QSize(220, 0))
        self.dateHasta.setMaximumSize(QSize(220, 16777215))
        self.dateHasta.setFont(font2)
        self.dateHasta.setCalendarPopup(True)

        self.horizontalLayout_3.addWidget(self.dateHasta)


        self.verticalLayout_2.addWidget(self.frame_7)

        self.frame_13 = QFrame(self.frame_6)
        self.frame_13.setObjectName(u"frame_13")
        self.frame_13.setFont(font)
        self.horizontalLayout_9 = QHBoxLayout(self.frame_13)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.btHoy = QPushButton(self.frame_13)
        self.btHoy.setObjectName(u"btHoy")
        self.btHoy.setMinimumSize(QSize(115, 30))
        self.btHoy.setFont(font2)

        self.horizontalLayout_9.addWidget(self.btHoy)

        self.btEstaSemana = QPushButton(self.frame_13)
        self.btEstaSemana.setObjectName(u"btEstaSemana")
        self.btEstaSemana.setMinimumSize(QSize(115, 30))
        self.btEstaSemana.setFont(font2)

        self.horizontalLayout_9.addWidget(self.btEstaSemana)

        self.btEsteMes = QPushButton(self.frame_13)
        self.btEsteMes.setObjectName(u"btEsteMes")
        self.btEsteMes.setMinimumSize(QSize(115, 30))
        self.btEsteMes.setFont(font2)

        self.horizontalLayout_9.addWidget(self.btEsteMes)


        self.verticalLayout_2.addWidget(self.frame_13, 0, Qt.AlignHCenter)


        self.gridLayout.addWidget(self.frame_6, 0, 0, 1, 1, Qt.AlignLeft)

        self.frame_4 = QFrame(self.frame_2)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFont(font)
        self.frame_4.setFrameShape(QFrame.NoFrame)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.frame_4)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(20)
        self.lbTotalIngresos = QLabel(self.frame_4)
        self.lbTotalIngresos.setObjectName(u"lbTotalIngresos")
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(16)
        self.lbTotalIngresos.setFont(font3)

        self.gridLayout_2.addWidget(self.lbTotalIngresos, 0, 0, 1, 1)

        self.lbTotalEgresos = QLabel(self.frame_4)
        self.lbTotalEgresos.setObjectName(u"lbTotalEgresos")
        self.lbTotalEgresos.setFont(font3)

        self.gridLayout_2.addWidget(self.lbTotalEgresos, 0, 1, 1, 1)

        self.tabla_ingresos = TablaDatos(self.frame_4)
        if (self.tabla_ingresos.columnCount() < 5):
            self.tabla_ingresos.setColumnCount(5)
        __qtablewidgetitem = QTableWidgetItem()
        self.tabla_ingresos.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tabla_ingresos.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tabla_ingresos.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tabla_ingresos.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tabla_ingresos.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        self.tabla_ingresos.setObjectName(u"tabla_ingresos")

        self.gridLayout_2.addWidget(self.tabla_ingresos, 1, 0, 1, 1)

        self.tabla_egresos = TablaDatos(self.frame_4)
        if (self.tabla_egresos.columnCount() < 5):
            self.tabla_egresos.setColumnCount(5)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tabla_egresos.setHorizontalHeaderItem(0, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tabla_egresos.setHorizontalHeaderItem(1, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tabla_egresos.setHorizontalHeaderItem(2, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tabla_egresos.setHorizontalHeaderItem(3, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tabla_egresos.setHorizontalHeaderItem(4, __qtablewidgetitem9)
        self.tabla_egresos.setObjectName(u"tabla_egresos")

        self.gridLayout_2.addWidget(self.tabla_egresos, 1, 1, 1, 1)

        self.frame_8 = QFrame(self.frame_4)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setFont(font)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_8)
        self.horizontalLayout_5.setSpacing(30)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.lbIngresosEfectivo = QLabel(self.frame_8)
        self.lbIngresosEfectivo.setObjectName(u"lbIngresosEfectivo")
        self.lbIngresosEfectivo.setMinimumSize(QSize(47, 13))
        self.lbIngresosEfectivo.setFont(font2)

        self.horizontalLayout_5.addWidget(self.lbIngresosEfectivo)

        self.lbIngresosTarjeta = QLabel(self.frame_8)
        self.lbIngresosTarjeta.setObjectName(u"lbIngresosTarjeta")
        self.lbIngresosTarjeta.setMinimumSize(QSize(47, 13))
        self.lbIngresosTarjeta.setFont(font2)

        self.horizontalLayout_5.addWidget(self.lbIngresosTarjeta)

        self.lbIngresosTransferencia = QLabel(self.frame_8)
        self.lbIngresosTransferencia.setObjectName(u"lbIngresosTransferencia")
        self.lbIngresosTransferencia.setMinimumSize(QSize(47, 13))
        self.lbIngresosTransferencia.setFont(font2)

        self.horizontalLayout_5.addWidget(self.lbIngresosTransferencia)


        self.gridLayout_2.addWidget(self.frame_8, 2, 0, 1, 1, Qt.AlignHCenter)

        self.frame_9 = QFrame(self.frame_4)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setFont(font)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_9)
        self.horizontalLayout_6.setSpacing(30)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.lbEgresosEfectivo = QLabel(self.frame_9)
        self.lbEgresosEfectivo.setObjectName(u"lbEgresosEfectivo")
        self.lbEgresosEfectivo.setMinimumSize(QSize(47, 13))
        self.lbEgresosEfectivo.setFont(font2)

        self.horizontalLayout_6.addWidget(self.lbEgresosEfectivo)

        self.lbEgresosTarjeta = QLabel(self.frame_9)
        self.lbEgresosTarjeta.setObjectName(u"lbEgresosTarjeta")
        self.lbEgresosTarjeta.setMinimumSize(QSize(47, 13))
        self.lbEgresosTarjeta.setFont(font2)

        self.horizontalLayout_6.addWidget(self.lbEgresosTarjeta)

        self.lbEgresosTransferencia = QLabel(self.frame_9)
        self.lbEgresosTransferencia.setObjectName(u"lbEgresosTransferencia")
        self.lbEgresosTransferencia.setMinimumSize(QSize(47, 13))
        self.lbEgresosTransferencia.setFont(font2)

        self.horizontalLayout_6.addWidget(self.lbEgresosTransferencia)


        self.gridLayout_2.addWidget(self.frame_9, 2, 1, 1, 1, Qt.AlignHCenter)


        self.gridLayout.addWidget(self.frame_4, 1, 0, 1, 2)


        self.verticalLayout.addWidget(self.frame_2)

        self.frame_3 = QFrame(Caja)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFont(font)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(19, -1, -1, -1)
        self.lbTotal = QLabel(self.frame_3)
        self.lbTotal.setObjectName(u"lbTotal")
        font4 = QFont()
        font4.setFamilies([u"Segoe UI"])
        font4.setPointSize(18)
        font4.setBold(True)
        self.lbTotal.setFont(font4)

        self.horizontalLayout_2.addWidget(self.lbTotal, 0, Qt.AlignHCenter)


        self.verticalLayout.addWidget(self.frame_3)


        self.retranslateUi(Caja)

        QMetaObject.connectSlotsByName(Caja)
    # setupUi

    def retranslateUi(self, Caja):
        Caja.setWindowTitle(QCoreApplication.translate("Caja", u"Form", None))
        self.lbTitulo.setText(QCoreApplication.translate("Caja", u"Movimientos de la caja", None))
        self.btImprimir.setText(QCoreApplication.translate("Caja", u"Imprimir corte de caja", None))
        self.btIngreso.setText(QCoreApplication.translate("Caja", u"Registrar ingreso", None))
        self.btEgreso.setText(QCoreApplication.translate("Caja", u"Registrar egreso", None))
        self.label.setText(QCoreApplication.translate("Caja", u"Ver desde:", None))
        self.dateDesde.setDisplayFormat(QCoreApplication.translate("Caja", u"d 'de' MMMM 'de' yyyy", None))
        self.label_2.setText(QCoreApplication.translate("Caja", u"         Hasta:", None))
        self.dateHasta.setDisplayFormat(QCoreApplication.translate("Caja", u"d 'de' MMMM 'de' yyyy", None))
        self.btHoy.setText(QCoreApplication.translate("Caja", u"Hoy", None))
        self.btEstaSemana.setText(QCoreApplication.translate("Caja", u"Esta semana", None))
        self.btEsteMes.setText(QCoreApplication.translate("Caja", u"Este mes", None))
        self.lbTotalIngresos.setText(QCoreApplication.translate("Caja", u"Total de ingresos: $0.00", None))
        self.lbTotalEgresos.setText(QCoreApplication.translate("Caja", u"Total de egresos: $0.00", None))
        ___qtablewidgetitem = self.tabla_ingresos.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Caja", u"Fecha y hora", None));
        ___qtablewidgetitem1 = self.tabla_ingresos.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Caja", u"Monto", None));
        ___qtablewidgetitem2 = self.tabla_ingresos.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Caja", u"Descripci\u00f3n", None));
        ___qtablewidgetitem3 = self.tabla_ingresos.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Caja", u"M\u00e9todo", None));
        ___qtablewidgetitem4 = self.tabla_ingresos.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("Caja", u"Usuario", None));
        ___qtablewidgetitem5 = self.tabla_egresos.horizontalHeaderItem(0)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("Caja", u"Fecha y hora", None));
        ___qtablewidgetitem6 = self.tabla_egresos.horizontalHeaderItem(1)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("Caja", u"Monto", None));
        ___qtablewidgetitem7 = self.tabla_egresos.horizontalHeaderItem(2)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("Caja", u"Descripci\u00f3n", None));
        ___qtablewidgetitem8 = self.tabla_egresos.horizontalHeaderItem(3)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("Caja", u"M\u00e9todo", None));
        ___qtablewidgetitem9 = self.tabla_egresos.horizontalHeaderItem(4)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("Caja", u"Usuario", None));
        self.lbIngresosEfectivo.setText(QCoreApplication.translate("Caja", u"Efectivo: $", None))
        self.lbIngresosTarjeta.setText(QCoreApplication.translate("Caja", u"Tarjeta de cr\u00e9dito/d\u00e9bito: $", None))
        self.lbIngresosTransferencia.setText(QCoreApplication.translate("Caja", u"Transferencias bancarias: $", None))
        self.lbEgresosEfectivo.setText(QCoreApplication.translate("Caja", u"Efectivo: $", None))
        self.lbEgresosTarjeta.setText(QCoreApplication.translate("Caja", u"Tarjeta de cr\u00e9dito/d\u00e9bito: $", None))
        self.lbEgresosTransferencia.setText(QCoreApplication.translate("Caja", u"Transferencias bancarias: $", None))
        self.lbTotal.setText(QCoreApplication.translate("Caja", u"Total del corte: $0.00", None))
    # retranslateUi

