# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_Reportes.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QPushButton, QRadioButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QVBoxLayout, QWidget)
from . import resources_rc

class Ui_Reportes(object):
    def setupUi(self, Reportes):
        if not Reportes.objectName():
            Reportes.setObjectName(u"Reportes")
        Reportes.resize(1368, 658)
        self.verticalLayout_2 = QVBoxLayout(Reportes)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.frame = QFrame(Reportes)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(0, 71))
        self.frame.setStyleSheet(u"QFrame { border: none; }")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(27, -1, 18, -1)
        self.btRegresar = QPushButton(self.frame)
        self.btRegresar.setObjectName(u"btRegresar")
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
        self.btRegresar.setText(u"")
        icon = QIcon()
        icon.addFile(u":/img/resources/images/leftarrow.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btRegresar.setIcon(icon)
        self.btRegresar.setIconSize(QSize(40, 40))
        self.btRegresar.setFlat(True)

        self.horizontalLayout.addWidget(self.btRegresar)

        self.lbTitulo = QLabel(self.frame)
        self.lbTitulo.setObjectName(u"lbTitulo")
        self.lbTitulo.setMinimumSize(QSize(211, 41))
        font = QFont()
        font.setPointSize(18)
        self.lbTitulo.setFont(font)

        self.horizontalLayout.addWidget(self.lbTitulo)


        self.verticalLayout_2.addWidget(self.frame, 0, Qt.AlignLeft|Qt.AlignTop)

        self.frame1 = QFrame(Reportes)
        self.frame1.setObjectName(u"frame1")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame1.sizePolicy().hasHeightForWidth())
        self.frame1.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QHBoxLayout(self.frame1)
        self.horizontalLayout_2.setSpacing(26)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.frameBotones = QFrame(self.frame1)
        self.frameBotones.setObjectName(u"frameBotones")
        self.verticalLayout = QVBoxLayout(self.frameBotones)
        self.verticalLayout.setSpacing(50)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, 50, 0, -1)
        self.btTablero = QPushButton(self.frameBotones)
        self.btTablero.setObjectName(u"btTablero")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.btTablero.sizePolicy().hasHeightForWidth())
        self.btTablero.setSizePolicy(sizePolicy1)
        self.btTablero.setMinimumSize(QSize(270, 52))
        self.btTablero.setMaximumSize(QSize(16777215, 50))
        font1 = QFont()
        font1.setPointSize(13)
        self.btTablero.setFont(font1)
        self.btTablero.setCursor(QCursor(Qt.PointingHandCursor))
        self.btTablero.setStyleSheet(u"QPushButton {\n"
"	background-color: transparent;\n"
"	border-radius: 10px;\n"
"	text-align: left;\n"
"	padding-left: 20px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: rgba(2,123,255,255);\n"
"	color: white;\n"
"}\n"
"QPushButton:pressed {\n"
"	background-color: rgba(0,95,160,255);\n"
"	color: white;\n"
"}\n"
"QPushButton:checked {\n"
"	background-color: rgba(2,123,255,255);\n"
"	color: white;\n"
"}")
        icon1 = QIcon()
        icon1.addFile(u":/img/resources/images/blocks.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btTablero.setIcon(icon1)
        self.btTablero.setIconSize(QSize(25, 25))
        self.btTablero.setCheckable(True)
        self.btTablero.setChecked(True)
        self.btTablero.setAutoExclusive(True)
        self.btTablero.setFlat(True)

        self.verticalLayout.addWidget(self.btTablero, 0, Qt.AlignTop)

        self.btVentas = QPushButton(self.frameBotones)
        self.btVentas.setObjectName(u"btVentas")
        sizePolicy1.setHeightForWidth(self.btVentas.sizePolicy().hasHeightForWidth())
        self.btVentas.setSizePolicy(sizePolicy1)
        self.btVentas.setMinimumSize(QSize(270, 52))
        self.btVentas.setMaximumSize(QSize(16777215, 50))
        self.btVentas.setFont(font1)
        self.btVentas.setCursor(QCursor(Qt.PointingHandCursor))
        self.btVentas.setStyleSheet(u"QPushButton {\n"
"	background-color: transparent;\n"
"	border-radius: 10px;\n"
"	text-align: left;\n"
"	padding-left: 20px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: rgba(2,123,255,255);\n"
"	color: white;\n"
"}\n"
"QPushButton:pressed {\n"
"	background-color: rgba(0,95,160,255);\n"
"	color: white;\n"
"}\n"
"QPushButton:checked {\n"
"	background-color: rgba(2,123,255,255);\n"
"	color: white;\n"
"}")
        icon2 = QIcon()
        icon2.addFile(u":/img/resources/images/crecimiento.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btVentas.setIcon(icon2)
        self.btVentas.setIconSize(QSize(25, 25))
        self.btVentas.setCheckable(True)
        self.btVentas.setAutoExclusive(True)
        self.btVentas.setFlat(True)

        self.verticalLayout.addWidget(self.btVentas, 0, Qt.AlignTop)

        self.btVendedores = QPushButton(self.frameBotones)
        self.btVendedores.setObjectName(u"btVendedores")
        sizePolicy1.setHeightForWidth(self.btVendedores.sizePolicy().hasHeightForWidth())
        self.btVendedores.setSizePolicy(sizePolicy1)
        self.btVendedores.setMinimumSize(QSize(270, 52))
        self.btVendedores.setMaximumSize(QSize(16777215, 50))
        self.btVendedores.setFont(font1)
        self.btVendedores.setCursor(QCursor(Qt.PointingHandCursor))
        self.btVendedores.setStyleSheet(u"QPushButton {\n"
"	background-color: transparent;\n"
"	border-radius: 10px;\n"
"	text-align: left;\n"
"	padding-left: 20px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: rgba(2,123,255,255);\n"
"	color: white;\n"
"}\n"
"QPushButton:pressed {\n"
"	background-color: rgba(0,95,160,255);\n"
"	color: white;\n"
"}\n"
"QPushButton:checked {\n"
"	background-color: rgba(2,123,255,255);\n"
"	color: white;\n"
"}")
        icon3 = QIcon()
        icon3.addFile(u":/img/resources/images/grupo.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btVendedores.setIcon(icon3)
        self.btVendedores.setIconSize(QSize(25, 25))
        self.btVendedores.setCheckable(True)
        self.btVendedores.setAutoExclusive(True)
        self.btVendedores.setFlat(True)

        self.verticalLayout.addWidget(self.btVendedores, 0, Qt.AlignTop)

        self.btProductos = QPushButton(self.frameBotones)
        self.btProductos.setObjectName(u"btProductos")
        sizePolicy1.setHeightForWidth(self.btProductos.sizePolicy().hasHeightForWidth())
        self.btProductos.setSizePolicy(sizePolicy1)
        self.btProductos.setMinimumSize(QSize(270, 52))
        self.btProductos.setMaximumSize(QSize(16777215, 50))
        self.btProductos.setFont(font1)
        self.btProductos.setCursor(QCursor(Qt.PointingHandCursor))
        self.btProductos.setStyleSheet(u"QPushButton {\n"
"	background-color: transparent;\n"
"	border-radius: 10px;\n"
"	text-align: left;\n"
"	padding-left: 20px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: rgba(2,123,255,255);\n"
"	color: white;\n"
"}\n"
"QPushButton:pressed {\n"
"	background-color: rgba(0,95,160,255);\n"
"	color: white;\n"
"}\n"
"QPushButton:checked {\n"
"	background-color: rgba(2,123,255,255);\n"
"	color: white;\n"
"}")
        icon4 = QIcon()
        icon4.addFile(u":/img/resources/images/paquete.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btProductos.setIcon(icon4)
        self.btProductos.setIconSize(QSize(25, 25))
        self.btProductos.setCheckable(True)
        self.btProductos.setAutoExclusive(True)
        self.btProductos.setFlat(True)

        self.verticalLayout.addWidget(self.btProductos, 0, Qt.AlignTop)


        self.horizontalLayout_2.addWidget(self.frameBotones, 0, Qt.AlignTop)

        self.stackedWidget = QStackedWidget(self.frame1)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.horizontalLayout_3 = QHBoxLayout(self.page)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.widget = QWidget(self.page)
        self.widget.setObjectName(u"widget")
        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(38)
        self.ingresosW = QWidget(self.widget)
        self.ingresosW.setObjectName(u"ingresosW")
        self.ingresosW.setStyleSheet(u"QWidget#ingresosW {\n"
"	background-color: rgb(255, 255, 255);\n"
"	border-radius: 15px;\n"
"	border: 2px solid #ddd;\n"
"}")
        self.horizontalLayout_5 = QHBoxLayout(self.ingresosW)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, -1, 0)
        self.label_4 = QLabel(self.ingresosW)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMaximumSize(QSize(80, 80))
        self.label_4.setStyleSheet(u"")
        self.label_4.setPixmap(QPixmap(u":/img/resources/images/dolar.png"))
        self.label_4.setScaledContents(True)

        self.horizontalLayout_5.addWidget(self.label_4)

        self.widgett = QWidget(self.ingresosW)
        self.widgett.setObjectName(u"widgett")
        self.gridLayout_2 = QGridLayout(self.widgett)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(-1, 15, -1, 15)
        self.lbIngresosBrutos = QLabel(self.widgett)
        self.lbIngresosBrutos.setObjectName(u"lbIngresosBrutos")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lbIngresosBrutos.sizePolicy().hasHeightForWidth())
        self.lbIngresosBrutos.setSizePolicy(sizePolicy2)
        font2 = QFont()
        font2.setPointSize(12)
        self.lbIngresosBrutos.setFont(font2)

        self.gridLayout_2.addWidget(self.lbIngresosBrutos, 1, 0, 1, 1)

        self.lbCountVentas = QLabel(self.widgett)
        self.lbCountVentas.setObjectName(u"lbCountVentas")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.lbCountVentas.sizePolicy().hasHeightForWidth())
        self.lbCountVentas.setSizePolicy(sizePolicy3)
        self.lbCountVentas.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)

        self.gridLayout_2.addWidget(self.lbCountVentas, 1, 1, 1, 1)

        self.label = QLabel(self.widgett)
        self.label.setObjectName(u"label")
        font3 = QFont()
        font3.setPointSize(13)
        font3.setBold(True)
        self.label.setFont(font3)

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 2)


        self.horizontalLayout_5.addWidget(self.widgett)


        self.gridLayout.addWidget(self.ingresosW, 1, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 2, 1, 1, 1)

        self.vendedorW = QWidget(self.widget)
        self.vendedorW.setObjectName(u"vendedorW")
        self.vendedorW.setStyleSheet(u"QWidget#vendedorW {\n"
"	background-color: rgb(255, 255, 255);\n"
"	border-radius: 15px;\n"
"	border: 2px solid #ddd;\n"
"}")
        self.horizontalLayout_6 = QHBoxLayout(self.vendedorW)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, -1, 0)
        self.label_5 = QLabel(self.vendedorW)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMaximumSize(QSize(80, 80))
        self.label_5.setStyleSheet(u"")
        self.label_5.setPixmap(QPixmap(u":/img/resources/images/user_block.png"))
        self.label_5.setScaledContents(True)

        self.horizontalLayout_6.addWidget(self.label_5)

        self.widget2 = QWidget(self.vendedorW)
        self.widget2.setObjectName(u"widget2")
        self.gridLayout_3 = QGridLayout(self.widget2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(-1, 15, -1, 15)
        self.lbVendedorBrutos = QLabel(self.widget2)
        self.lbVendedorBrutos.setObjectName(u"lbVendedorBrutos")
        sizePolicy2.setHeightForWidth(self.lbVendedorBrutos.sizePolicy().hasHeightForWidth())
        self.lbVendedorBrutos.setSizePolicy(sizePolicy2)
        self.lbVendedorBrutos.setFont(font2)

        self.gridLayout_3.addWidget(self.lbVendedorBrutos, 1, 0, 1, 1)

        self.lbVendedorTotal = QLabel(self.widget2)
        self.lbVendedorTotal.setObjectName(u"lbVendedorTotal")
        sizePolicy3.setHeightForWidth(self.lbVendedorTotal.sizePolicy().hasHeightForWidth())
        self.lbVendedorTotal.setSizePolicy(sizePolicy3)
        self.lbVendedorTotal.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)

        self.gridLayout_3.addWidget(self.lbVendedorTotal, 1, 1, 1, 1)

        self.label_2 = QLabel(self.widget2)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font3)

        self.gridLayout_3.addWidget(self.label_2, 0, 0, 1, 2)


        self.horizontalLayout_6.addWidget(self.widget2)


        self.gridLayout.addWidget(self.vendedorW, 1, 1, 1, 1)

        self.widget_4 = QWidget(self.widget)
        self.widget_4.setObjectName(u"widget_4")
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.widget_4.sizePolicy().hasHeightForWidth())
        self.widget_4.setSizePolicy(sizePolicy4)
        self.widget_4.setMinimumSize(QSize(0, 250))
        self.widget_4.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-radius: 15px;")

        self.gridLayout.addWidget(self.widget_4, 3, 0, 1, 3)

        self.productoW = QWidget(self.widget)
        self.productoW.setObjectName(u"productoW")
        self.productoW.setStyleSheet(u"QWidget#productoW {\n"
"	background-color: rgb(255, 255, 255);\n"
"	border-radius: 15px;\n"
"	border: 2px solid #ddd;\n"
"}")
        self.horizontalLayout_7 = QHBoxLayout(self.productoW)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, -1, 0)
        self.label_6 = QLabel(self.productoW)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMaximumSize(QSize(80, 80))
        self.label_6.setStyleSheet(u"")
        self.label_6.setPixmap(QPixmap(u":/img/resources/images/paq_block.png"))
        self.label_6.setScaledContents(True)

        self.horizontalLayout_7.addWidget(self.label_6)

        self.widget3 = QWidget(self.productoW)
        self.widget3.setObjectName(u"widget3")
        self.gridLayout_4 = QGridLayout(self.widget3)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(-1, 15, -1, 15)
        self.lbProdVendidos = QLabel(self.widget3)
        self.lbProdVendidos.setObjectName(u"lbProdVendidos")
        sizePolicy2.setHeightForWidth(self.lbProdVendidos.sizePolicy().hasHeightForWidth())
        self.lbProdVendidos.setSizePolicy(sizePolicy2)
        self.lbProdVendidos.setFont(font2)

        self.gridLayout_4.addWidget(self.lbProdVendidos, 1, 0, 1, 1)

        self.lbProdCount = QLabel(self.widget3)
        self.lbProdCount.setObjectName(u"lbProdCount")
        sizePolicy3.setHeightForWidth(self.lbProdCount.sizePolicy().hasHeightForWidth())
        self.lbProdCount.setSizePolicy(sizePolicy3)
        self.lbProdCount.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)

        self.gridLayout_4.addWidget(self.lbProdCount, 1, 1, 1, 1)

        self.label_3 = QLabel(self.widget3)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font3)

        self.gridLayout_4.addWidget(self.label_3, 0, 0, 1, 2)


        self.horizontalLayout_7.addWidget(self.widget3)


        self.gridLayout.addWidget(self.productoW, 1, 2, 1, 1)

        self.widget_2 = QWidget(self.widget)
        self.widget_2.setObjectName(u"widget_2")
        self.horizontalLayout_4 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_4.setSpacing(20)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.radioButton = QRadioButton(self.widget_2)
        self.radioButton.setObjectName(u"radioButton")
        font4 = QFont()
        font4.setPointSize(11)
        self.radioButton.setFont(font4)
        self.radioButton.setChecked(True)

        self.horizontalLayout_4.addWidget(self.radioButton)

        self.radioButton_2 = QRadioButton(self.widget_2)
        self.radioButton_2.setObjectName(u"radioButton_2")
        self.radioButton_2.setFont(font4)

        self.horizontalLayout_4.addWidget(self.radioButton_2)

        self.radioButton_3 = QRadioButton(self.widget_2)
        self.radioButton_3.setObjectName(u"radioButton_3")
        self.radioButton_3.setFont(font4)

        self.horizontalLayout_4.addWidget(self.radioButton_3)


        self.gridLayout.addWidget(self.widget_2, 0, 0, 1, 3, Qt.AlignRight)


        self.horizontalLayout_3.addWidget(self.widget, 0, Qt.AlignTop)

        self.stackedWidget.addWidget(self.page)

        self.horizontalLayout_2.addWidget(self.stackedWidget)


        self.verticalLayout_2.addWidget(self.frame1)


        self.retranslateUi(Reportes)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Reportes)
    # setupUi

    def retranslateUi(self, Reportes):
        Reportes.setWindowTitle(QCoreApplication.translate("Reportes", u"Form", None))
        self.lbTitulo.setText(QCoreApplication.translate("Reportes", u"Reportes del negocio", None))
        self.btTablero.setText(QCoreApplication.translate("Reportes", u"   Tablero", None))
        self.btVentas.setText(QCoreApplication.translate("Reportes", u"   Reportes de ventas", None))
        self.btVendedores.setText(QCoreApplication.translate("Reportes", u"   Reportes de vendedores", None))
        self.btProductos.setText(QCoreApplication.translate("Reportes", u"   Reportes de productos", None))
        self.label_4.setText("")
        self.lbIngresosBrutos.setText(QCoreApplication.translate("Reportes", u"$59,124.57", None))
        self.lbCountVentas.setText(QCoreApplication.translate("Reportes", u"a trav\u00e9s de 5,123 ventas", None))
        self.label.setText(QCoreApplication.translate("Reportes", u"Ingresos brutos", None))
        self.label_5.setText("")
        self.lbVendedorBrutos.setText(QCoreApplication.translate("Reportes", u"Johnny", None))
        self.lbVendedorTotal.setText(QCoreApplication.translate("Reportes", u"$4,123.23", None))
        self.label_2.setText(QCoreApplication.translate("Reportes", u"Vendedor m\u00e1s productivo", None))
        self.label_6.setText("")
        self.lbProdVendidos.setText(QCoreApplication.translate("Reportes", u"Ejemplo", None))
        self.lbProdCount.setText(QCoreApplication.translate("Reportes", u"14,123 unidades", None))
        self.label_3.setText(QCoreApplication.translate("Reportes", u"Producto m\u00e1s vendido", None))
        self.radioButton.setText(QCoreApplication.translate("Reportes", u"Esta quincena", None))
        self.radioButton_2.setText(QCoreApplication.translate("Reportes", u"Este mes", None))
        self.radioButton_3.setText(QCoreApplication.translate("Reportes", u"Este a\u00f1o", None))
    # retranslateUi

