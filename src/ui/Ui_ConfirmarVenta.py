# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_ConfirmarVenta.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QTableWidgetItem,
    QVBoxLayout, QWidget)

from utils.mywidgets import (NumberEdit, StackPagos, TablaDatos)
from . import resources_rc

class Ui_ConfirmarVenta(object):
    def setupUi(self, ConfirmarVenta):
        if not ConfirmarVenta.objectName():
            ConfirmarVenta.setObjectName(u"ConfirmarVenta")
        ConfirmarVenta.setWindowModality(Qt.ApplicationModal)
        ConfirmarVenta.resize(833, 793)
        self.verticalLayout = QVBoxLayout(ConfirmarVenta)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, -1)
        self.frame = QFrame(ConfirmarVenta)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"QFrame { background-color: rgb(52, 172, 224); }")
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 5, -1, 5)
        self.frame_5 = QFrame(self.frame)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.frame_5)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(45, 45))
        font = QFont()
        font.setPointSize(18)
        self.label.setFont(font)
        self.label.setStyleSheet(u"image: url(:/img/resources/images/shopping-cart.png);")

        self.horizontalLayout_2.addWidget(self.label)

        self.label_17 = QLabel(self.frame_5)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setMinimumSize(QSize(211, 41))
        self.label_17.setFont(font)
        self.label_17.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.horizontalLayout_2.addWidget(self.label_17)


        self.horizontalLayout.addWidget(self.frame_5, 0, Qt.AlignLeft|Qt.AlignTop)

        self.frame_6 = QFrame(self.frame)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_5 = QLabel(self.frame_6)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(41, 21))
        font1 = QFont()
        font1.setPointSize(11)
        self.label_5.setFont(font1)
        self.label_5.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.label_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.verticalLayout_2.addWidget(self.label_5)

        self.lbFolio = QLabel(self.frame_6)
        self.lbFolio.setObjectName(u"lbFolio")
        self.lbFolio.setMinimumSize(QSize(61, 21))
        font2 = QFont()
        font2.setPointSize(11)
        font2.setBold(True)
        self.lbFolio.setFont(font2)
        self.lbFolio.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.lbFolio.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.verticalLayout_2.addWidget(self.lbFolio)


        self.horizontalLayout.addWidget(self.frame_6, 0, Qt.AlignRight|Qt.AlignTop)


        self.verticalLayout.addWidget(self.frame)

        self.frame_2 = QFrame(ConfirmarVenta)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(18, -1, 18, -1)
        self.frame_7 = QFrame(self.frame_2)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_7)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(-1, -1, 50, -1)
        self.groupBox = QGroupBox(self.frame_7)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMinimumSize(QSize(361, 131))
        self.groupBox.setFont(font2)
        self.groupBox.setFlat(True)
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(25)
        self.gridLayout.setVerticalSpacing(20)
        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")
        font3 = QFont()
        font3.setPointSize(11)
        font3.setBold(False)
        self.label_6.setFont(font3)

        self.gridLayout.addWidget(self.label_6, 0, 0, 1, 1)

        self.txtCliente = QLineEdit(self.groupBox)
        self.txtCliente.setObjectName(u"txtCliente")
        font4 = QFont()
        font4.setPointSize(11)
        font4.setBold(False)
        font4.setItalic(False)
        self.txtCliente.setFont(font4)
        self.txtCliente.setStyleSheet(u"color: rgb(0, 147, 220);")
        self.txtCliente.setFrame(False)
        self.txtCliente.setReadOnly(True)
        self.txtCliente.setClearButtonEnabled(False)

        self.gridLayout.addWidget(self.txtCliente, 0, 1, 1, 1)

        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setFont(font3)

        self.gridLayout.addWidget(self.label_7, 1, 0, 1, 1)

        self.txtCorreo = QLineEdit(self.groupBox)
        self.txtCorreo.setObjectName(u"txtCorreo")
        self.txtCorreo.setFont(font3)
        self.txtCorreo.setStyleSheet(u"color: rgb(0, 147, 220);")
        self.txtCorreo.setFrame(False)
        self.txtCorreo.setReadOnly(True)
        self.txtCorreo.setClearButtonEnabled(False)

        self.gridLayout.addWidget(self.txtCorreo, 1, 1, 1, 1)

        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setFont(font3)

        self.gridLayout.addWidget(self.label_8, 2, 0, 1, 1)

        self.txtTelefono = QLineEdit(self.groupBox)
        self.txtTelefono.setObjectName(u"txtTelefono")
        self.txtTelefono.setFont(font3)
        self.txtTelefono.setStyleSheet(u"color: rgb(0, 147, 220);")
        self.txtTelefono.setFrame(False)
        self.txtTelefono.setReadOnly(True)
        self.txtTelefono.setClearButtonEnabled(False)

        self.gridLayout.addWidget(self.txtTelefono, 2, 1, 1, 1)


        self.horizontalLayout_5.addWidget(self.groupBox)


        self.horizontalLayout_3.addWidget(self.frame_7, 0, Qt.AlignTop)

        self.frame_8 = QFrame(self.frame_2)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_8)
        self.verticalLayout_4.setSpacing(20)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBox_2 = QGroupBox(self.frame_8)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setMinimumSize(QSize(291, 61))
        self.groupBox_2.setFont(font2)
        self.groupBox_2.setFlat(True)
        self.txtCreacion = QLineEdit(self.groupBox_2)
        self.txtCreacion.setObjectName(u"txtCreacion")
        self.txtCreacion.setGeometry(QRect(10, 30, 261, 20))
        self.txtCreacion.setFont(font3)
        self.txtCreacion.setStyleSheet(u"")
        self.txtCreacion.setFrame(False)
        self.txtCreacion.setReadOnly(True)
        self.txtCreacion.setClearButtonEnabled(False)

        self.verticalLayout_4.addWidget(self.groupBox_2)

        self.boxFechaEntrega = QGroupBox(self.frame_8)
        self.boxFechaEntrega.setObjectName(u"boxFechaEntrega")
        self.boxFechaEntrega.setMinimumSize(QSize(291, 61))
        self.boxFechaEntrega.setFont(font2)
        self.boxFechaEntrega.setFlat(True)
        self.txtEntrega = QLineEdit(self.boxFechaEntrega)
        self.txtEntrega.setObjectName(u"txtEntrega")
        self.txtEntrega.setGeometry(QRect(10, 30, 261, 20))
        self.txtEntrega.setFont(font3)
        self.txtEntrega.setStyleSheet(u"")
        self.txtEntrega.setFrame(False)
        self.txtEntrega.setReadOnly(True)
        self.txtEntrega.setClearButtonEnabled(False)

        self.verticalLayout_4.addWidget(self.boxFechaEntrega)


        self.horizontalLayout_3.addWidget(self.frame_8, 0, Qt.AlignRight|Qt.AlignTop)


        self.verticalLayout.addWidget(self.frame_2)

        self.frame_3 = QFrame(ConfirmarVenta)
        self.frame_3.setObjectName(u"frame_3")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(18, 0, 18, 0)
        self.tabla_productos = TablaDatos(self.frame_3)
        if (self.tabla_productos.columnCount() < 6):
            self.tabla_productos.setColumnCount(6)
        __qtablewidgetitem = QTableWidgetItem()
        self.tabla_productos.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tabla_productos.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tabla_productos.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tabla_productos.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tabla_productos.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tabla_productos.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        self.tabla_productos.setObjectName(u"tabla_productos")
        self.tabla_productos.setMinimumSize(QSize(791, 238))
        self.tabla_productos.horizontalHeader().setMinimumSectionSize(80)

        self.horizontalLayout_8.addWidget(self.tabla_productos)


        self.verticalLayout.addWidget(self.frame_3)

        self.frame_4 = QFrame(ConfirmarVenta)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.frame_4)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(20)
        self.gridLayout_2.setContentsMargins(-1, -1, 60, 0)
        self.frame_12 = QFrame(self.frame_4)
        self.frame_12.setObjectName(u"frame_12")
        self.horizontalLayout_4 = QHBoxLayout(self.frame_12)
        self.horizontalLayout_4.setSpacing(2)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(-1, 0, -1, 4)
        self.btQuitar = QPushButton(self.frame_12)
        self.btQuitar.setObjectName(u"btQuitar")
        self.btQuitar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btQuitar.setStyleSheet(u"QPushButton {\n"
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
        self.btQuitar.setText(u"")
        icon = QIcon()
        icon.addFile(u":/img/resources/images/minus2.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btQuitar.setIcon(icon)
        self.btQuitar.setIconSize(QSize(20, 20))
        self.btQuitar.setFlat(True)

        self.horizontalLayout_4.addWidget(self.btQuitar)

        self.horizontalSpacer = QSpacerItem(6, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.btAnterior = QPushButton(self.frame_12)
        self.btAnterior.setObjectName(u"btAnterior")
        self.btAnterior.setCursor(QCursor(Qt.PointingHandCursor))
        self.btAnterior.setStyleSheet(u"QPushButton {\n"
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
        self.btAnterior.setText(u"")
        icon1 = QIcon()
        icon1.addFile(u":/img/resources/images/back.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btAnterior.setIcon(icon1)
        self.btAnterior.setIconSize(QSize(20, 20))
        self.btAnterior.setFlat(True)

        self.horizontalLayout_4.addWidget(self.btAnterior)

        self.lbContador = QLabel(self.frame_12)
        self.lbContador.setObjectName(u"lbContador")
        font5 = QFont()
        font5.setPointSize(13)
        self.lbContador.setFont(font5)

        self.horizontalLayout_4.addWidget(self.lbContador)

        self.btSiguiente = QPushButton(self.frame_12)
        self.btSiguiente.setObjectName(u"btSiguiente")
        self.btSiguiente.setCursor(QCursor(Qt.PointingHandCursor))
        self.btSiguiente.setStyleSheet(u"QPushButton {\n"
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
        self.btSiguiente.setText(u"")
        icon2 = QIcon()
        icon2.addFile(u":/img/resources/images/next.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btSiguiente.setIcon(icon2)
        self.btSiguiente.setIconSize(QSize(20, 20))
        self.btSiguiente.setFlat(True)

        self.horizontalLayout_4.addWidget(self.btSiguiente)

        self.horizontalSpacer_2 = QSpacerItem(6, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)

        self.btAgregar = QPushButton(self.frame_12)
        self.btAgregar.setObjectName(u"btAgregar")
        self.btAgregar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btAgregar.setStyleSheet(u"QPushButton {\n"
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
        self.btAgregar.setText(u"")
        icon3 = QIcon()
        icon3.addFile(u":/img/resources/images/plus2.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btAgregar.setIcon(icon3)
        self.btAgregar.setIconSize(QSize(20, 20))
        self.btAgregar.setFlat(True)

        self.horizontalLayout_4.addWidget(self.btAgregar)


        self.gridLayout_2.addWidget(self.frame_12, 0, 0, 1, 1, Qt.AlignLeft)

        self.frame_10 = QFrame(self.frame_4)
        self.frame_10.setObjectName(u"frame_10")
        self.gridLayout_3 = QGridLayout(self.frame_10)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setVerticalSpacing(0)
        self.gridLayout_3.setContentsMargins(60, 4, -1, -1)
        self.lbTotal = QLabel(self.frame_10)
        self.lbTotal.setObjectName(u"lbTotal")
        self.lbTotal.setMinimumSize(QSize(180, 28))
        font6 = QFont()
        font6.setPointSize(15)
        font6.setBold(True)
        self.lbTotal.setFont(font6)
        self.lbTotal.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_3.addWidget(self.lbTotal, 0, 2, 1, 1)

        self.lbAnticipo1 = QLabel(self.frame_10)
        self.lbAnticipo1.setObjectName(u"lbAnticipo1")
        self.lbAnticipo1.setMinimumSize(QSize(0, 28))
        font7 = QFont()
        font7.setPointSize(14)
        font7.setBold(True)
        self.lbAnticipo1.setFont(font7)

        self.gridLayout_3.addWidget(self.lbAnticipo1, 1, 0, 2, 1)

        self.label_20 = QLabel(self.frame_10)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setMinimumSize(QSize(149, 0))
        self.label_20.setFont(font7)

        self.gridLayout_3.addWidget(self.label_20, 0, 0, 1, 1)

        self.label_24 = QLabel(self.frame_10)
        self.label_24.setObjectName(u"label_24")
        self.label_24.setMinimumSize(QSize(0, 28))
        self.label_24.setFont(font6)

        self.gridLayout_3.addWidget(self.label_24, 0, 1, 1, 1)

        self.lbCincuenta = QLabel(self.frame_10)
        self.lbCincuenta.setObjectName(u"lbCincuenta")
        self.lbCincuenta.setFont(font1)
        self.lbCincuenta.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_3.addWidget(self.lbCincuenta, 3, 0, 1, 1)

        self.txtAnticipo = NumberEdit(self.frame_10)
        self.txtAnticipo.setObjectName(u"txtAnticipo")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.txtAnticipo.sizePolicy().hasHeightForWidth())
        self.txtAnticipo.setSizePolicy(sizePolicy1)
        self.txtAnticipo.setMinimumSize(QSize(180, 28))
        self.txtAnticipo.setStyleSheet(u"color: rgb(0, 170, 0);")

        self.gridLayout_3.addWidget(self.txtAnticipo, 1, 2, 3, 1)

        self.lbAnticipo2 = QLabel(self.frame_10)
        self.lbAnticipo2.setObjectName(u"lbAnticipo2")
        self.lbAnticipo2.setMinimumSize(QSize(0, 28))
        self.lbAnticipo2.setFont(font6)

        self.gridLayout_3.addWidget(self.lbAnticipo2, 1, 1, 3, 1)


        self.gridLayout_2.addWidget(self.frame_10, 1, 0, 1, 1)

        self.stackedWidget = StackPagos(self.frame_4)
        self.stackedWidget.setObjectName(u"stackedWidget")

        self.gridLayout_2.addWidget(self.stackedWidget, 2, 0, 1, 1)

        self.frame_16 = QFrame(self.frame_4)
        self.frame_16.setObjectName(u"frame_16")
        self.frame_16.setMinimumSize(QSize(230, 0))
        self.frame_16.setFrameShadow(QFrame.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.frame_16)
        self.verticalLayout_8.setSpacing(30)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.btListo = QPushButton(self.frame_16)
        self.btListo.setObjectName(u"btListo")
        self.btListo.setMinimumSize(QSize(130, 40))
        self.btListo.setFont(font1)
        icon4 = QIcon()
        icon4.addFile(u":/img/resources/images/accept.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btListo.setIcon(icon4)
        self.btListo.setIconSize(QSize(25, 25))

        self.verticalLayout_8.addWidget(self.btListo)

        self.btCancelar = QPushButton(self.frame_16)
        self.btCancelar.setObjectName(u"btCancelar")
        self.btCancelar.setMinimumSize(QSize(130, 40))
        self.btCancelar.setFont(font1)
        icon5 = QIcon()
        icon5.addFile(u":/img/resources/images/trash.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btCancelar.setIcon(icon5)
        self.btCancelar.setIconSize(QSize(25, 25))

        self.verticalLayout_8.addWidget(self.btCancelar)


        self.gridLayout_2.addWidget(self.frame_16, 0, 1, 3, 1, Qt.AlignVCenter)


        self.verticalLayout.addWidget(self.frame_4)


        self.retranslateUi(ConfirmarVenta)

        QMetaObject.connectSlotsByName(ConfirmarVenta)
    # setupUi

    def retranslateUi(self, ConfirmarVenta):
        ConfirmarVenta.setWindowTitle(QCoreApplication.translate("ConfirmarVenta", u"Form", None))
        self.label.setText("")
        self.label_17.setText(QCoreApplication.translate("ConfirmarVenta", u"Resumen de venta", None))
        self.label_5.setText(QCoreApplication.translate("ConfirmarVenta", u"Folio", None))
        self.lbFolio.setText(QCoreApplication.translate("ConfirmarVenta", u"20", None))
        self.groupBox.setTitle(QCoreApplication.translate("ConfirmarVenta", u"Cliente", None))
        self.label_6.setText(QCoreApplication.translate("ConfirmarVenta", u"Nombre", None))
        self.txtCliente.setText(QCoreApplication.translate("ConfirmarVenta", u"P\u00fablico general", None))
        self.label_7.setText(QCoreApplication.translate("ConfirmarVenta", u"E-mail", None))
        self.txtCorreo.setText(QCoreApplication.translate("ConfirmarVenta", u"N/A", None))
        self.label_8.setText(QCoreApplication.translate("ConfirmarVenta", u"Tel\u00e9fono", None))
        self.txtTelefono.setText(QCoreApplication.translate("ConfirmarVenta", u"N/A", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("ConfirmarVenta", u"Fecha de creaci\u00f3n", None))
        self.txtCreacion.setText(QCoreApplication.translate("ConfirmarVenta", u"02 de febrero 2023, 5:00 p.m.", None))
        self.boxFechaEntrega.setTitle(QCoreApplication.translate("ConfirmarVenta", u"Fecha de entrega", None))
        self.txtEntrega.setText(QCoreApplication.translate("ConfirmarVenta", u"02 de febrero 2023, 5:00 p.m.", None))
        ___qtablewidgetitem = self.tabla_productos.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("ConfirmarVenta", u"Cantidad", None));
        ___qtablewidgetitem1 = self.tabla_productos.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("ConfirmarVenta", u"Producto", None));
        ___qtablewidgetitem2 = self.tabla_productos.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("ConfirmarVenta", u"Especificaciones", None));
        ___qtablewidgetitem3 = self.tabla_productos.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("ConfirmarVenta", u"Precio", None));
        ___qtablewidgetitem4 = self.tabla_productos.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("ConfirmarVenta", u"Descuento $", None));
        ___qtablewidgetitem5 = self.tabla_productos.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("ConfirmarVenta", u"Importe", None));
#if QT_CONFIG(tooltip)
        self.btQuitar.setToolTip(QCoreApplication.translate("ConfirmarVenta", u"Quitar este pago de la venta", None))
#endif // QT_CONFIG(tooltip)
        self.lbContador.setText(QCoreApplication.translate("ConfirmarVenta", u"Pago 1/1", None))
#if QT_CONFIG(tooltip)
        self.btAgregar.setToolTip(QCoreApplication.translate("ConfirmarVenta", u"Agregar pago a la venta", None))
#endif // QT_CONFIG(tooltip)
        self.lbTotal.setText(QCoreApplication.translate("ConfirmarVenta", u"0.00", None))
        self.lbAnticipo1.setText(QCoreApplication.translate("ConfirmarVenta", u"Anticipo (m\u00ednimo 50%)", None))
        self.label_20.setText(QCoreApplication.translate("ConfirmarVenta", u"Total", None))
        self.label_24.setText(QCoreApplication.translate("ConfirmarVenta", u"$", None))
        self.lbCincuenta.setText(QCoreApplication.translate("ConfirmarVenta", u"($250.00)", None))
        self.lbAnticipo2.setText(QCoreApplication.translate("ConfirmarVenta", u"$", None))
        self.btListo.setText(QCoreApplication.translate("ConfirmarVenta", u" Terminar", None))
        self.btCancelar.setText(QCoreApplication.translate("ConfirmarVenta", u" Abortar", None))
    # retranslateUi

