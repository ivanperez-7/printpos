# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_CrearVenta.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QButtonGroup, QCheckBox,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QPlainTextEdit,
    QPushButton, QSizePolicy, QSpacerItem, QTableWidgetItem,
    QVBoxLayout, QWidget)

from utils.mywidgets import TablaDatos
from . import resources_rc

class Ui_CrearVenta(object):
    def setupUi(self, CrearVenta):
        if not CrearVenta.objectName():
            CrearVenta.setObjectName(u"CrearVenta")
        CrearVenta.resize(1271, 783)
        self.gridLayout_6 = QGridLayout(CrearVenta)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(-1, 0, 0, 0)
        self.frame = QFrame(CrearVenta)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.NoFrame)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(4, 9, 4, 9)
        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_7 = QFrame(self.frame_3)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_7)
        self.horizontalLayout_4.setSpacing(12)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.btRegresar = QPushButton(self.frame_7)
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

        self.horizontalLayout_4.addWidget(self.btRegresar)

        self.lbTitulo = QLabel(self.frame_7)
        self.lbTitulo.setObjectName(u"lbTitulo")
        self.lbTitulo.setMinimumSize(QSize(201, 41))
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(18)
        self.lbTitulo.setFont(font)

        self.horizontalLayout_4.addWidget(self.lbTitulo)


        self.horizontalLayout_2.addWidget(self.frame_7, 0, Qt.AlignLeft|Qt.AlignTop)

        self.frame_8 = QFrame(self.frame_3)
        self.frame_8.setObjectName(u"frame_8")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_8.sizePolicy().hasHeightForWidth())
        self.frame_8.setSizePolicy(sizePolicy)
        self.frame_8.setFrameShape(QFrame.NoFrame)
        self.gridLayout = QGridLayout(self.frame_8)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(9)
        self.btDeshacer = QPushButton(self.frame_8)
        self.btDeshacer.setObjectName(u"btDeshacer")
        self.btDeshacer.setCursor(QCursor(Qt.PointingHandCursor))
        self.btDeshacer.setStyleSheet(u"QPushButton {\n"
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
        self.btDeshacer.setText(u"")
        icon1 = QIcon()
        icon1.addFile(u":/img/resources/images/undo.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btDeshacer.setIcon(icon1)
        self.btDeshacer.setIconSize(QSize(20, 20))
        self.btDeshacer.setFlat(True)

        self.gridLayout.addWidget(self.btDeshacer, 0, 0, 2, 1)

        self.lbFecha = QLabel(self.frame_8)
        self.lbFecha.setObjectName(u"lbFecha")
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(11)
        font1.setBold(False)
        self.lbFecha.setFont(font1)
        self.lbFecha.setText(u"19/01/2023 12:00p.m.")
        self.lbFecha.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.lbFecha, 1, 1, 1, 1, Qt.AlignRight)

        self.btCalendario = QPushButton(self.frame_8)
        self.btCalendario.setObjectName(u"btCalendario")
        self.btCalendario.setCursor(QCursor(Qt.PointingHandCursor))
        self.btCalendario.setStyleSheet(u"QPushButton {\n"
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
        self.btCalendario.setText(u"")
        icon2 = QIcon()
        icon2.addFile(u":/img/resources/images/calendar.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btCalendario.setIcon(icon2)
        self.btCalendario.setIconSize(QSize(40, 40))
        self.btCalendario.setFlat(True)

        self.gridLayout.addWidget(self.btCalendario, 0, 3, 2, 1)

        self.label_5 = QLabel(self.frame_8)
        self.label_5.setObjectName(u"label_5")
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        font2.setPointSize(11)
        font2.setBold(True)
        self.label_5.setFont(font2)
        self.label_5.setText(u"Fecha y hora de entrega")
        self.label_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_5, 0, 1, 1, 1, Qt.AlignRight)

        self.horizontalSpacer_2 = QSpacerItem(8, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 0, 2, 1, 1)


        self.horizontalLayout_2.addWidget(self.frame_8, 0, Qt.AlignRight|Qt.AlignTop)


        self.verticalLayout.addWidget(self.frame_3, 0, Qt.AlignTop)

        self.frame_4 = QFrame(self.frame)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.NoFrame)
        self.verticalLayout_2 = QVBoxLayout(self.frame_4)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 15, 0, 0)
        self.frame_9 = QFrame(self.frame_4)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_9)
        self.horizontalLayout_5.setSpacing(30)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(-1, -1, -1, 0)
        self.btRegistrar = QPushButton(self.frame_9)
        self.btRegistrar.setObjectName(u"btRegistrar")
        self.btRegistrar.setMinimumSize(QSize(161, 30))
        self.btRegistrar.setMaximumSize(QSize(16777215, 30))
        font3 = QFont()
        font3.setPointSize(10)
        self.btRegistrar.setFont(font3)
        self.btRegistrar.setText(u"Registrar cliente")
        icon3 = QIcon()
        icon3.addFile(u":/img/resources/images/new-user.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btRegistrar.setIcon(icon3)

        self.horizontalLayout_5.addWidget(self.btRegistrar)

        self.btSeleccionar = QPushButton(self.frame_9)
        self.btSeleccionar.setObjectName(u"btSeleccionar")
        self.btSeleccionar.setMinimumSize(QSize(161, 30))
        self.btSeleccionar.setMaximumSize(QSize(16777215, 30))
        self.btSeleccionar.setFont(font3)
        self.btSeleccionar.setText(u"Seleccionar cliente")
        icon4 = QIcon()
        icon4.addFile(u":/img/resources/images/search.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btSeleccionar.setIcon(icon4)

        self.horizontalLayout_5.addWidget(self.btSeleccionar)

        self.btDescuentosCliente = QPushButton(self.frame_9)
        self.btDescuentosCliente.setObjectName(u"btDescuentosCliente")
        self.btDescuentosCliente.setMinimumSize(QSize(200, 30))
        self.btDescuentosCliente.setMaximumSize(QSize(16777215, 30))
        self.btDescuentosCliente.setFont(font3)
        self.btDescuentosCliente.setStyleSheet(u"background-color: rgb(255, 255, 0);")
        self.btDescuentosCliente.setText(u"Ver descuentos del cliente")
        icon5 = QIcon()
        icon5.addFile(u":/img/resources/images/tag.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btDescuentosCliente.setIcon(icon5)

        self.horizontalLayout_5.addWidget(self.btDescuentosCliente)


        self.verticalLayout_2.addWidget(self.frame_9, 0, Qt.AlignLeft)

        self.frame_10 = QFrame(self.frame_4)
        self.frame_10.setObjectName(u"frame_10")
        self.frame_10.setFrameShape(QFrame.NoFrame)
        self.gridLayout_4 = QGridLayout(self.frame_10)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setHorizontalSpacing(15)
        self.gridLayout_4.setVerticalSpacing(20)
        self.gridLayout_4.setContentsMargins(-1, 20, -1, 0)
        self.label_2 = QLabel(self.frame_10)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font2)

        self.gridLayout_4.addWidget(self.label_2, 1, 0, 1, 1)

        self.txtCorreo = QLineEdit(self.frame_10)
        self.txtCorreo.setObjectName(u"txtCorreo")
        self.txtCorreo.setMinimumSize(QSize(248, 19))
        font4 = QFont()
        font4.setFamilies([u"Segoe UI"])
        font4.setPointSize(11)
        self.txtCorreo.setFont(font4)
        self.txtCorreo.setStyleSheet(u"color: rgb(0, 147, 220);")
        self.txtCorreo.setFrame(True)
        self.txtCorreo.setClearButtonEnabled(False)

        self.gridLayout_4.addWidget(self.txtCorreo, 1, 1, 1, 1)

        self.label_3 = QLabel(self.frame_10)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font2)

        self.gridLayout_4.addWidget(self.label_3, 1, 3, 1, 1)

        self.txtTelefono = QLineEdit(self.frame_10)
        self.txtTelefono.setObjectName(u"txtTelefono")
        self.txtTelefono.setMinimumSize(QSize(247, 19))
        self.txtTelefono.setFont(font4)
        self.txtTelefono.setStyleSheet(u"color: rgb(0, 147, 220);")
        self.txtTelefono.setFrame(True)
        self.txtTelefono.setClearButtonEnabled(False)

        self.gridLayout_4.addWidget(self.txtTelefono, 1, 4, 1, 1)

        self.txtCliente = QLineEdit(self.frame_10)
        self.txtCliente.setObjectName(u"txtCliente")
        self.txtCliente.setMinimumSize(QSize(247, 19))
        self.txtCliente.setFont(font4)
        self.txtCliente.setStyleSheet(u"color: rgb(0, 147, 220);")
        self.txtCliente.setFrame(True)
        self.txtCliente.setClearButtonEnabled(False)

        self.gridLayout_4.addWidget(self.txtCliente, 0, 1, 1, 1)

        self.label = QLabel(self.frame_10)
        self.label.setObjectName(u"label")
        self.label.setFont(font2)

        self.gridLayout_4.addWidget(self.label, 0, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer, 1, 2, 1, 1)


        self.verticalLayout_2.addWidget(self.frame_10, 0, Qt.AlignLeft)


        self.verticalLayout.addWidget(self.frame_4, 0, Qt.AlignTop)

        self.frame_5 = QFrame(self.frame)
        self.frame_5.setObjectName(u"frame_5")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_5.sizePolicy().hasHeightForWidth())
        self.frame_5.setSizePolicy(sizePolicy1)
        self.frame_5.setFrameShape(QFrame.NoFrame)
        self.verticalLayout_3 = QVBoxLayout(self.frame_5)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(-1, -1, -1, 0)
        self.frame_11 = QFrame(self.frame_5)
        self.frame_11.setObjectName(u"frame_11")
        sizePolicy.setHeightForWidth(self.frame_11.sizePolicy().hasHeightForWidth())
        self.frame_11.setSizePolicy(sizePolicy)
        self.frame_11.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_11)
        self.horizontalLayout_6.setSpacing(20)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.btAgregar = QPushButton(self.frame_11)
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
        icon6 = QIcon()
        icon6.addFile(u":/img/resources/images/plus.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btAgregar.setIcon(icon6)
        self.btAgregar.setIconSize(QSize(40, 40))
        self.btAgregar.setFlat(True)

        self.horizontalLayout_6.addWidget(self.btAgregar)

        self.btEliminar = QPushButton(self.frame_11)
        self.btEliminar.setObjectName(u"btEliminar")
        self.btEliminar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btEliminar.setStyleSheet(u"QPushButton {\n"
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
        self.btEliminar.setText(u"")
        icon7 = QIcon()
        icon7.addFile(u":/img/resources/images/trash.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btEliminar.setIcon(icon7)
        self.btEliminar.setIconSize(QSize(40, 40))
        self.btEliminar.setFlat(True)

        self.horizontalLayout_6.addWidget(self.btEliminar)


        self.verticalLayout_3.addWidget(self.frame_11, 0, Qt.AlignRight|Qt.AlignTop)

        self.frame_12 = QFrame(self.frame_5)
        self.frame_12.setObjectName(u"frame_12")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame_12.sizePolicy().hasHeightForWidth())
        self.frame_12.setSizePolicy(sizePolicy2)
        self.frame_12.setMinimumSize(QSize(788, 180))
        self.frame_12.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_12)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(2, 2, 2, 10)
        self.tabla_productos = TablaDatos(self.frame_12)
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
        self.tabla_productos.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.tabla_productos.setSelectionMode(QAbstractItemView.MultiSelection)
        self.tabla_productos.horizontalHeader().setMinimumSectionSize(80)

        self.horizontalLayout_8.addWidget(self.tabla_productos)


        self.verticalLayout_3.addWidget(self.frame_12)

        self.frame_13 = QFrame(self.frame_5)
        self.frame_13.setObjectName(u"frame_13")
        sizePolicy.setHeightForWidth(self.frame_13.sizePolicy().hasHeightForWidth())
        self.frame_13.setSizePolicy(sizePolicy)
        self.frame_13.setMinimumSize(QSize(0, 55))
        self.frame_13.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_13)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.txtComentarios = QPlainTextEdit(self.frame_13)
        self.txtComentarios.setObjectName(u"txtComentarios")
        sizePolicy.setHeightForWidth(self.txtComentarios.sizePolicy().hasHeightForWidth())
        self.txtComentarios.setSizePolicy(sizePolicy)
        self.txtComentarios.setMinimumSize(QSize(0, 51))
        self.txtComentarios.setMaximumSize(QSize(16777215, 51))
        self.txtComentarios.setFont(font4)

        self.horizontalLayout_7.addWidget(self.txtComentarios)


        self.verticalLayout_3.addWidget(self.frame_13, 0, Qt.AlignBottom)


        self.verticalLayout.addWidget(self.frame_5)

        self.frame_6 = QFrame(self.frame)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 9, 0, 0)
        self.frame_14 = QFrame(self.frame_6)
        self.frame_14.setObjectName(u"frame_14")
        self.frame_14.setFrameShape(QFrame.NoFrame)
        self.gridLayout_2 = QGridLayout(self.frame_14)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.groupBox = QGroupBox(self.frame_14)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMinimumSize(QSize(231, 61))
        self.groupBox.setFont(font4)
        self.txtVendedor = QLineEdit(self.groupBox)
        self.txtVendedor.setObjectName(u"txtVendedor")
        self.txtVendedor.setGeometry(QRect(10, 30, 191, 20))
        self.txtVendedor.setFont(font4)
        self.txtVendedor.setReadOnly(True)

        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)


        self.horizontalLayout_3.addWidget(self.frame_14, 0, Qt.AlignLeft)

        self.frame_15 = QFrame(self.frame_6)
        self.frame_15.setObjectName(u"frame_15")
        self.frame_15.setFrameShape(QFrame.NoFrame)
        self.gridLayout_3 = QGridLayout(self.frame_15)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setHorizontalSpacing(30)
        self.boxFactura = QGroupBox(self.frame_15)
        self.boxFactura.setObjectName(u"boxFactura")
        self.boxFactura.setMinimumSize(QSize(142, 61))
        self.boxFactura.setFont(font4)
        self.boxFactura.setFlat(False)
        self.boxFactura.setCheckable(False)
        self.tickFacturaSi = QCheckBox(self.boxFactura)
        self.tickFacturaSi.setObjectName(u"tickFacturaSi")
        self.tickFacturaSi.setGeometry(QRect(10, 30, 70, 17))
        self.tickFacturaSi.setMinimumSize(QSize(70, 17))
        self.tickFacturaSi.setFont(font4)
        self.tickFacturaSi.setText(u"S\u00ed")
        self.tickFacturaSi.setChecked(False)
        self.tickFacturaSi.setAutoExclusive(True)
        self.tickFacturaNo = QCheckBox(self.boxFactura)
        self.tickFacturaNo.setObjectName(u"tickFacturaNo")
        self.tickFacturaNo.setGeometry(QRect(80, 30, 70, 17))
        self.tickFacturaNo.setMinimumSize(QSize(70, 17))
        self.tickFacturaNo.setFont(font4)
        self.tickFacturaNo.setText(u"No")
        self.tickFacturaNo.setChecked(True)
        self.tickFacturaNo.setAutoExclusive(True)

        self.gridLayout_3.addWidget(self.boxFactura, 0, 0, 1, 1)


        self.horizontalLayout_3.addWidget(self.frame_15, 0, Qt.AlignRight)


        self.verticalLayout.addWidget(self.frame_6, 0, Qt.AlignBottom)


        self.gridLayout_6.addWidget(self.frame, 0, 0, 1, 1)

        self.frame_2 = QFrame(CrearVenta)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy2.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy2)
        self.frame_2.setMinimumSize(QSize(330, 0))
        self.frame_2.setMaximumSize(QSize(320, 16777215))
        self.frame_2.setStyleSheet(u"QFrame{background-color: rgb(52, 172, 224);}")
        self.verticalLayout_4 = QVBoxLayout(self.frame_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, -1, 0, -1)
        self.frame_16 = QFrame(self.frame_2)
        self.frame_16.setObjectName(u"frame_16")
        self.verticalLayout_5 = QVBoxLayout(self.frame_16)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(15, 0, 15, 0)
        self.frame_19 = QFrame(self.frame_16)
        self.frame_19.setObjectName(u"frame_19")
        self.frame_19.setMinimumSize(QSize(0, 130))
        self.label_6 = QLabel(self.frame_19)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(10, 80, 31, 31))
        font5 = QFont()
        font5.setPointSize(22)
        font5.setBold(False)
        self.label_6.setFont(font5)
        self.label_6.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.label_6.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.lbTotal = QLabel(self.frame_19)
        self.lbTotal.setObjectName(u"lbTotal")
        self.lbTotal.setGeometry(QRect(60, 80, 171, 31))
        self.lbTotal.setFont(font5)
        self.lbTotal.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.lbTotal.setAlignment(Qt.AlignCenter)
        self.label_4 = QLabel(self.frame_19)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(14, 20, 261, 31))
        font6 = QFont()
        font6.setPointSize(22)
        font6.setBold(True)
        self.label_4.setFont(font6)
        self.label_4.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.label_4.setAlignment(Qt.AlignCenter)

        self.verticalLayout_5.addWidget(self.frame_19)

        self.frame_20 = QFrame(self.frame_16)
        self.frame_20.setObjectName(u"frame_20")
        self.gridLayout_5 = QGridLayout(self.frame_20)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setVerticalSpacing(20)
        self.gridLayout_5.setContentsMargins(-1, 25, -1, -1)
        self.label_8 = QLabel(self.frame_20)
        self.label_8.setObjectName(u"label_8")
        font7 = QFont()
        font7.setPointSize(13)
        self.label_8.setFont(font7)
        self.label_8.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.gridLayout_5.addWidget(self.label_8, 0, 0, 1, 1)

        self.label_11 = QLabel(self.frame_20)
        self.label_11.setObjectName(u"label_11")
        font8 = QFont()
        font8.setPointSize(13)
        font8.setBold(False)
        self.label_11.setFont(font8)
        self.label_11.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.label_11.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_5.addWidget(self.label_11, 0, 1, 1, 1)

        self.lbSubtotal = QLabel(self.frame_20)
        self.lbSubtotal.setObjectName(u"lbSubtotal")
        self.lbSubtotal.setFont(font8)
        self.lbSubtotal.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.lbSubtotal.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_5.addWidget(self.lbSubtotal, 0, 2, 1, 1)

        self.label_9 = QLabel(self.frame_20)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setFont(font7)
        self.label_9.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.gridLayout_5.addWidget(self.label_9, 1, 0, 1, 1)

        self.label_12 = QLabel(self.frame_20)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setFont(font8)
        self.label_12.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.label_12.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_5.addWidget(self.label_12, 1, 1, 1, 1)

        self.lbImpuestos = QLabel(self.frame_20)
        self.lbImpuestos.setObjectName(u"lbImpuestos")
        self.lbImpuestos.setFont(font8)
        self.lbImpuestos.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.lbImpuestos.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_5.addWidget(self.lbImpuestos, 1, 2, 1, 1)

        self.label_10 = QLabel(self.frame_20)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setFont(font7)
        self.label_10.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.gridLayout_5.addWidget(self.label_10, 2, 0, 1, 1)

        self.label_13 = QLabel(self.frame_20)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setFont(font8)
        self.label_13.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.label_13.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout_5.addWidget(self.label_13, 2, 1, 1, 1)

        self.lbDescuento = QLabel(self.frame_20)
        self.lbDescuento.setObjectName(u"lbDescuento")
        self.lbDescuento.setFont(font8)
        self.lbDescuento.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.lbDescuento.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_5.addWidget(self.lbDescuento, 2, 2, 1, 1)


        self.verticalLayout_5.addWidget(self.frame_20)


        self.verticalLayout_4.addWidget(self.frame_16)

        self.frame_17 = QFrame(self.frame_2)
        self.frame_17.setObjectName(u"frame_17")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.frame_17.sizePolicy().hasHeightForWidth())
        self.frame_17.setSizePolicy(sizePolicy3)
        self.horizontalLayout_9 = QHBoxLayout(self.frame_17)
        self.horizontalLayout_9.setSpacing(0)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, 20, 0, 25)
        self.btDescuento = QPushButton(self.frame_17)
        self.btDescuento.setObjectName(u"btDescuento")
        self.btDescuento.setMinimumSize(QSize(0, 70))
        font9 = QFont()
        font9.setPointSize(12)
        self.btDescuento.setFont(font9)
        self.btDescuento.setCursor(QCursor(Qt.PointingHandCursor))
        self.btDescuento.setStyleSheet(u"background-color: rgb(224, 52, 172);\n"
"color: rgb(255, 255, 255);\n"
"border-radius: 0px;")
        self.btDescuento.setText(u"Descuento")
        icon8 = QIcon()
        icon8.addFile(u":/img/resources/images/discounts.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btDescuento.setIcon(icon8)
        self.btDescuento.setIconSize(QSize(35, 35))

        self.horizontalLayout_9.addWidget(self.btDescuento)

        self.btCotizacion = QPushButton(self.frame_17)
        self.btCotizacion.setObjectName(u"btCotizacion")
        self.btCotizacion.setMinimumSize(QSize(0, 70))
        self.btCotizacion.setFont(font9)
        self.btCotizacion.setCursor(QCursor(Qt.PointingHandCursor))
        self.btCotizacion.setStyleSheet(u"background-color: rgb(0, 220, 0);\n"
"color: rgb(255, 255, 255);\n"
"border-radius: 0px;")
        self.btCotizacion.setText(u"Cotizaci\u00f3n")
        icon9 = QIcon()
        icon9.addFile(u":/img/resources/images/receipt.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btCotizacion.setIcon(icon9)
        self.btCotizacion.setIconSize(QSize(35, 35))

        self.horizontalLayout_9.addWidget(self.btCotizacion)


        self.verticalLayout_4.addWidget(self.frame_17, 0, Qt.AlignTop)

        self.frame_18 = QFrame(self.frame_2)
        self.frame_18.setObjectName(u"frame_18")
        sizePolicy3.setHeightForWidth(self.frame_18.sizePolicy().hasHeightForWidth())
        self.frame_18.setSizePolicy(sizePolicy3)
        self.verticalLayout_7 = QVBoxLayout(self.frame_18)
        self.verticalLayout_7.setSpacing(20)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(35, -1, 35, -1)
        self.groupMetodo = QGroupBox(self.frame_18)
        self.groupMetodo.setObjectName(u"groupMetodo")
        self.groupMetodo.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.groupMetodo.sizePolicy().hasHeightForWidth())
        self.groupMetodo.setSizePolicy(sizePolicy1)
        self.groupMetodo.setFont(font7)
        self.groupMetodo.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.groupMetodo.setFlat(True)
        self.groupMetodo.setCheckable(False)
        self.verticalLayout_6 = QVBoxLayout(self.groupMetodo)
        self.verticalLayout_6.setSpacing(20)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.btEfectivo = QPushButton(self.groupMetodo)
        self.btMetodoGrupo = QButtonGroup(CrearVenta)
        self.btMetodoGrupo.setObjectName(u"btMetodoGrupo")
        self.btMetodoGrupo.addButton(self.btEfectivo)
        self.btEfectivo.setObjectName(u"btEfectivo")
        self.btEfectivo.setMinimumSize(QSize(242, 40))
        font10 = QFont()
        font10.setPointSize(11)
        self.btEfectivo.setFont(font10)
        self.btEfectivo.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.btEfectivo.setText(u"Efectivo")
        icon10 = QIcon()
        icon10.addFile(u":/img/resources/images/money.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btEfectivo.setIcon(icon10)
        self.btEfectivo.setIconSize(QSize(27, 27))
        self.btEfectivo.setCheckable(True)
        self.btEfectivo.setChecked(True)
        self.btEfectivo.setAutoExclusive(True)

        self.verticalLayout_6.addWidget(self.btEfectivo)

        self.btTarjeta = QPushButton(self.groupMetodo)
        self.btMetodoGrupo.addButton(self.btTarjeta)
        self.btTarjeta.setObjectName(u"btTarjeta")
        self.btTarjeta.setMinimumSize(QSize(242, 40))
        self.btTarjeta.setFont(font10)
        self.btTarjeta.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.btTarjeta.setText(u"Tarjeta de cr\u00e9dito")
        icon11 = QIcon()
        icon11.addFile(u":/img/resources/images/pay.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btTarjeta.setIcon(icon11)
        self.btTarjeta.setIconSize(QSize(27, 27))
        self.btTarjeta.setCheckable(True)
        self.btTarjeta.setAutoExclusive(True)

        self.verticalLayout_6.addWidget(self.btTarjeta)

        self.btTarjeta_2 = QPushButton(self.groupMetodo)
        self.btMetodoGrupo.addButton(self.btTarjeta_2)
        self.btTarjeta_2.setObjectName(u"btTarjeta_2")
        self.btTarjeta_2.setMinimumSize(QSize(242, 40))
        self.btTarjeta_2.setFont(font10)
        self.btTarjeta_2.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.btTarjeta_2.setText(u"Tarjeta de d\u00e9bito")
        self.btTarjeta_2.setIcon(icon11)
        self.btTarjeta_2.setIconSize(QSize(27, 27))
        self.btTarjeta_2.setCheckable(True)
        self.btTarjeta_2.setAutoExclusive(True)

        self.verticalLayout_6.addWidget(self.btTarjeta_2)

        self.btTransferencia = QPushButton(self.groupMetodo)
        self.btMetodoGrupo.addButton(self.btTransferencia)
        self.btTransferencia.setObjectName(u"btTransferencia")
        self.btTransferencia.setMinimumSize(QSize(242, 40))
        self.btTransferencia.setFont(font10)
        self.btTransferencia.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.btTransferencia.setText(u"Transferencia bancaria")
        icon12 = QIcon()
        icon12.addFile(u":/img/resources/images/deposit.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btTransferencia.setIcon(icon12)
        self.btTransferencia.setIconSize(QSize(27, 27))
        self.btTransferencia.setCheckable(True)
        self.btTransferencia.setAutoExclusive(True)

        self.verticalLayout_6.addWidget(self.btTransferencia)


        self.verticalLayout_7.addWidget(self.groupMetodo)

        self.btListo = QPushButton(self.frame_18)
        self.btListo.setObjectName(u"btListo")
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.btListo.sizePolicy().hasHeightForWidth())
        self.btListo.setSizePolicy(sizePolicy4)
        self.btListo.setMaximumSize(QSize(16777215, 50))
        font11 = QFont()
        font11.setPointSize(14)
        font11.setBold(True)
        self.btListo.setFont(font11)
        self.btListo.setText(u"Listo")
        icon13 = QIcon()
        icon13.addFile(u":/img/resources/images/shopping-cart.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btListo.setIcon(icon13)
        self.btListo.setIconSize(QSize(40, 40))

        self.verticalLayout_7.addWidget(self.btListo, 0, Qt.AlignBottom)


        self.verticalLayout_4.addWidget(self.frame_18)


        self.gridLayout_6.addWidget(self.frame_2, 0, 1, 1, 1)


        self.retranslateUi(CrearVenta)

        QMetaObject.connectSlotsByName(CrearVenta)
    # setupUi

    def retranslateUi(self, CrearVenta):
        CrearVenta.setWindowTitle(QCoreApplication.translate("CrearVenta", u"Form", None))
        self.lbTitulo.setText(QCoreApplication.translate("CrearVenta", u"Realizar una venta", None))
#if QT_CONFIG(tooltip)
        self.btDeshacer.setToolTip(QCoreApplication.translate("CrearVenta", u"Deshacer fecha de entrega", None))
#endif // QT_CONFIG(tooltip)
        self.label_2.setText(QCoreApplication.translate("CrearVenta", u"E-mail", None))
        self.txtCorreo.setText(QCoreApplication.translate("CrearVenta", u"N/A", None))
        self.label_3.setText(QCoreApplication.translate("CrearVenta", u"Tel\u00e9fono", None))
        self.txtTelefono.setText(QCoreApplication.translate("CrearVenta", u"N/A", None))
        self.txtCliente.setText(QCoreApplication.translate("CrearVenta", u"P\u00fablico general", None))
        self.label.setText(QCoreApplication.translate("CrearVenta", u"Cliente", None))
        ___qtablewidgetitem = self.tabla_productos.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("CrearVenta", u"Cantidad", None));
        ___qtablewidgetitem1 = self.tabla_productos.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("CrearVenta", u"Producto", None));
        ___qtablewidgetitem2 = self.tabla_productos.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("CrearVenta", u"Especificaciones", None));
        ___qtablewidgetitem3 = self.tabla_productos.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("CrearVenta", u"Precio", None));
        ___qtablewidgetitem4 = self.tabla_productos.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("CrearVenta", u"Descuento $", None));
        ___qtablewidgetitem5 = self.tabla_productos.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("CrearVenta", u"Importe", None));
        self.txtComentarios.setPlaceholderText(QCoreApplication.translate("CrearVenta", u"Agregue comentarios adicionales aqu\u00ed...", None))
        self.groupBox.setTitle(QCoreApplication.translate("CrearVenta", u"Vendedor", None))
        self.txtVendedor.setText(QCoreApplication.translate("CrearVenta", u"default", None))
        self.boxFactura.setTitle(QCoreApplication.translate("CrearVenta", u"Requiere factura", None))
        self.label_6.setText(QCoreApplication.translate("CrearVenta", u"$", None))
        self.lbTotal.setText(QCoreApplication.translate("CrearVenta", u"0.00", None))
        self.label_4.setText(QCoreApplication.translate("CrearVenta", u"Total", None))
        self.label_8.setText(QCoreApplication.translate("CrearVenta", u"Subtotal ", None))
        self.label_11.setText(QCoreApplication.translate("CrearVenta", u"$", None))
        self.lbSubtotal.setText(QCoreApplication.translate("CrearVenta", u"0.00", None))
        self.label_9.setText(QCoreApplication.translate("CrearVenta", u"Impuestos", None))
        self.label_12.setText(QCoreApplication.translate("CrearVenta", u"$", None))
        self.lbImpuestos.setText(QCoreApplication.translate("CrearVenta", u"0.00", None))
        self.label_10.setText(QCoreApplication.translate("CrearVenta", u"Descuento", None))
        self.label_13.setText(QCoreApplication.translate("CrearVenta", u"$", None))
        self.lbDescuento.setText(QCoreApplication.translate("CrearVenta", u"0.00", None))
        self.groupMetodo.setTitle(QCoreApplication.translate("CrearVenta", u"Pagar", None))
    # retranslateUi

