# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_DetallesVenta.ui'
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
    QPlainTextEdit, QPushButton, QSizePolicy, QSpacerItem,
    QTableWidgetItem, QVBoxLayout, QWidget)

from utils.mywidgets import TablaDatos
from . import resources_rc

class Ui_DetallesVenta(object):
    def setupUi(self, DetallesVenta):
        if not DetallesVenta.objectName():
            DetallesVenta.setObjectName(u"DetallesVenta")
        DetallesVenta.resize(827, 685)
        self.verticalLayout = QVBoxLayout(DetallesVenta)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, -1)
        self.frame = QFrame(DetallesVenta)
        self.frame.setObjectName(u"frame")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        self.frame.setFont(font)
        self.frame.setStyleSheet(u"QFrame { background-color: rgb(52, 172, 224); }")
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 5, -1, 5)
        self.frame_5 = QFrame(self.frame)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFont(font)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_2.setSpacing(20)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.btRegresar = QPushButton(self.frame_5)
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

        self.horizontalLayout_2.addWidget(self.btRegresar)

        self.label_17 = QLabel(self.frame_5)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setMinimumSize(QSize(211, 41))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(18)
        self.label_17.setFont(font1)
        self.label_17.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.horizontalLayout_2.addWidget(self.label_17)


        self.horizontalLayout.addWidget(self.frame_5, 0, Qt.AlignLeft|Qt.AlignVCenter)

        self.frame_6 = QFrame(self.frame)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFont(font)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_5 = QLabel(self.frame_6)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(41, 21))
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        font2.setPointSize(11)
        self.label_5.setFont(font2)
        self.label_5.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.label_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.verticalLayout_2.addWidget(self.label_5)

        self.lbFolio = QLabel(self.frame_6)
        self.lbFolio.setObjectName(u"lbFolio")
        self.lbFolio.setMinimumSize(QSize(61, 21))
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(11)
        font3.setBold(True)
        self.lbFolio.setFont(font3)
        self.lbFolio.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.lbFolio.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.verticalLayout_2.addWidget(self.lbFolio)


        self.horizontalLayout.addWidget(self.frame_6, 0, Qt.AlignRight|Qt.AlignTop)


        self.verticalLayout.addWidget(self.frame)

        self.frame_2 = QFrame(DetallesVenta)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFont(font)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(18, -1, 18, -1)
        self.frame_7 = QFrame(self.frame_2)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setFont(font)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_7)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(-1, -1, 50, -1)
        self.groupBox = QGroupBox(self.frame_7)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMinimumSize(QSize(361, 131))
        self.groupBox.setFont(font3)
        self.groupBox.setFlat(True)
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(25)
        self.gridLayout.setVerticalSpacing(20)
        self.txtTelefono = QLineEdit(self.groupBox)
        self.txtTelefono.setObjectName(u"txtTelefono")
        font4 = QFont()
        font4.setFamilies([u"Segoe UI"])
        font4.setPointSize(11)
        font4.setBold(False)
        self.txtTelefono.setFont(font4)
        self.txtTelefono.setStyleSheet(u"color: rgb(0, 147, 220);")
        self.txtTelefono.setFrame(False)
        self.txtTelefono.setReadOnly(True)
        self.txtTelefono.setClearButtonEnabled(False)

        self.gridLayout.addWidget(self.txtTelefono, 2, 1, 1, 1)

        self.txtCliente = QLineEdit(self.groupBox)
        self.txtCliente.setObjectName(u"txtCliente")
        font5 = QFont()
        font5.setFamilies([u"Segoe UI"])
        font5.setPointSize(11)
        font5.setBold(False)
        font5.setItalic(False)
        self.txtCliente.setFont(font5)
        self.txtCliente.setStyleSheet(u"color: rgb(0, 147, 220);")
        self.txtCliente.setFrame(False)
        self.txtCliente.setReadOnly(True)
        self.txtCliente.setClearButtonEnabled(False)

        self.gridLayout.addWidget(self.txtCliente, 0, 1, 1, 1)

        self.txtCorreo = QLineEdit(self.groupBox)
        self.txtCorreo.setObjectName(u"txtCorreo")
        self.txtCorreo.setFont(font4)
        self.txtCorreo.setStyleSheet(u"color: rgb(0, 147, 220);")
        self.txtCorreo.setFrame(False)
        self.txtCorreo.setReadOnly(True)
        self.txtCorreo.setClearButtonEnabled(False)

        self.gridLayout.addWidget(self.txtCorreo, 1, 1, 1, 1)

        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setFont(font4)

        self.gridLayout.addWidget(self.label_7, 1, 0, 1, 1)

        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setFont(font4)

        self.gridLayout.addWidget(self.label_8, 2, 0, 1, 1)

        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font4)

        self.gridLayout.addWidget(self.label_6, 0, 0, 1, 1)


        self.horizontalLayout_5.addWidget(self.groupBox)


        self.horizontalLayout_3.addWidget(self.frame_7, 0, Qt.AlignTop)

        self.frame_8 = QFrame(self.frame_2)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setFont(font)
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_8)
        self.verticalLayout_4.setSpacing(20)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBox_2 = QGroupBox(self.frame_8)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setMinimumSize(QSize(291, 61))
        self.groupBox_2.setFont(font3)
        self.groupBox_2.setFlat(True)
        self.txtCreacion = QLineEdit(self.groupBox_2)
        self.txtCreacion.setObjectName(u"txtCreacion")
        self.txtCreacion.setGeometry(QRect(10, 30, 261, 20))
        self.txtCreacion.setFont(font4)
        self.txtCreacion.setStyleSheet(u"")
        self.txtCreacion.setFrame(False)
        self.txtCreacion.setReadOnly(True)
        self.txtCreacion.setClearButtonEnabled(False)

        self.verticalLayout_4.addWidget(self.groupBox_2)

        self.boxEntrega = QGroupBox(self.frame_8)
        self.boxEntrega.setObjectName(u"boxEntrega")
        self.boxEntrega.setMinimumSize(QSize(291, 61))
        self.boxEntrega.setFont(font3)
        self.boxEntrega.setFlat(True)
        self.txtEntrega = QLineEdit(self.boxEntrega)
        self.txtEntrega.setObjectName(u"txtEntrega")
        self.txtEntrega.setGeometry(QRect(10, 30, 261, 20))
        self.txtEntrega.setFont(font4)
        self.txtEntrega.setStyleSheet(u"")
        self.txtEntrega.setFrame(False)
        self.txtEntrega.setReadOnly(True)
        self.txtEntrega.setClearButtonEnabled(False)

        self.verticalLayout_4.addWidget(self.boxEntrega)


        self.horizontalLayout_3.addWidget(self.frame_8, 0, Qt.AlignRight|Qt.AlignTop)


        self.verticalLayout.addWidget(self.frame_2)

        self.frame_3 = QFrame(DetallesVenta)
        self.frame_3.setObjectName(u"frame_3")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setMinimumSize(QSize(0, 210))
        self.frame_3.setFont(font)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.frame_3)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(18, 0, 18, 0)
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
        self.tabla_productos.setMinimumSize(QSize(791, 210))
        self.tabla_productos.horizontalHeader().setMinimumSectionSize(80)

        self.verticalLayout_6.addWidget(self.tabla_productos)


        self.verticalLayout.addWidget(self.frame_3)

        self.frame_4 = QFrame(DetallesVenta)
        self.frame_4.setObjectName(u"frame_4")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_4.sizePolicy().hasHeightForWidth())
        self.frame_4.setSizePolicy(sizePolicy1)
        self.frame_4.setFont(font)
        self.frame_4.setStyleSheet(u"QFrame { border:none; }")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_4)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(-1, 0, -1, -1)
        self.frame_10 = QFrame(self.frame_4)
        self.frame_10.setObjectName(u"frame_10")
        self.frame_10.setFont(font)
        self.frame_10.setStyleSheet(u"QFrame { border:none; }")
        self.frame_10.setFrameShape(QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.frame_10)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setVerticalSpacing(20)
        self.txtComentarios = QPlainTextEdit(self.frame_10)
        self.txtComentarios.setObjectName(u"txtComentarios")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.txtComentarios.sizePolicy().hasHeightForWidth())
        self.txtComentarios.setSizePolicy(sizePolicy2)
        self.txtComentarios.setMinimumSize(QSize(0, 51))
        self.txtComentarios.setMaximumSize(QSize(16777215, 51))
        self.txtComentarios.setFont(font2)
        self.txtComentarios.setReadOnly(True)

        self.gridLayout_2.addWidget(self.txtComentarios, 0, 0, 1, 2, Qt.AlignBottom)

        self.groupBox_4 = QGroupBox(self.frame_10)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setMinimumSize(QSize(231, 61))
        self.groupBox_4.setFont(font2)
        self.txtVendedor = QLineEdit(self.groupBox_4)
        self.txtVendedor.setObjectName(u"txtVendedor")
        self.txtVendedor.setGeometry(QRect(10, 30, 191, 20))
        self.txtVendedor.setFont(font2)
        self.txtVendedor.setReadOnly(True)

        self.gridLayout_2.addWidget(self.groupBox_4, 1, 0, 1, 1, Qt.AlignLeft|Qt.AlignBottom)

        self.frame_9 = QFrame(self.frame_10)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setFont(font)
        self.frame_9.setStyleSheet(u"")
        self.frame_9.setFrameShape(QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QFrame.Raised)
        self.gridLayout_3 = QGridLayout(self.frame_9)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setVerticalSpacing(6)
        self.gridLayout_3.setContentsMargins(-1, 0, -1, 0)
        self.label_16 = QLabel(self.frame_9)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setMinimumSize(QSize(0, 28))
        font6 = QFont()
        font6.setFamilies([u"Segoe UI"])
        font6.setPointSize(17)
        font6.setBold(True)
        self.label_16.setFont(font6)

        self.gridLayout_3.addWidget(self.label_16, 0, 2, 1, 1)

        self.label_18 = QLabel(self.frame_9)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setMinimumSize(QSize(0, 28))
        self.label_18.setFont(font6)
        self.label_18.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_3.addWidget(self.label_18, 0, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(70, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer, 0, 1, 1, 1)

        self.lbTotal = QLabel(self.frame_9)
        self.lbTotal.setObjectName(u"lbTotal")
        self.lbTotal.setMinimumSize(QSize(0, 28))
        self.lbTotal.setFont(font6)
        self.lbTotal.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_3.addWidget(self.lbTotal, 0, 3, 1, 1)

        self.lbSaldo = QLabel(self.frame_9)
        self.lbSaldo.setObjectName(u"lbSaldo")
        self.lbSaldo.setMinimumSize(QSize(0, 28))
        font7 = QFont()
        font7.setFamilies([u"Segoe UI"])
        font7.setPointSize(16)
        font7.setBold(False)
        self.lbSaldo.setFont(font7)
        self.lbSaldo.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_3.addWidget(self.lbSaldo, 2, 3, 1, 1)

        self.temp4 = QLabel(self.frame_9)
        self.temp4.setObjectName(u"temp4")
        self.temp4.setMinimumSize(QSize(0, 28))
        self.temp4.setFont(font7)

        self.gridLayout_3.addWidget(self.temp4, 2, 2, 1, 1)

        self.temp1 = QLabel(self.frame_9)
        self.temp1.setObjectName(u"temp1")
        self.temp1.setMinimumSize(QSize(0, 28))
        self.temp1.setFont(font7)
        self.temp1.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_3.addWidget(self.temp1, 1, 0, 1, 1)

        self.lbAnticipo = QLabel(self.frame_9)
        self.lbAnticipo.setObjectName(u"lbAnticipo")
        self.lbAnticipo.setMinimumSize(QSize(0, 28))
        self.lbAnticipo.setFont(font7)
        self.lbAnticipo.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_3.addWidget(self.lbAnticipo, 1, 3, 1, 1)

        self.temp2 = QLabel(self.frame_9)
        self.temp2.setObjectName(u"temp2")
        self.temp2.setMinimumSize(QSize(0, 28))
        self.temp2.setFont(font7)

        self.gridLayout_3.addWidget(self.temp2, 1, 2, 1, 1)

        self.temp3 = QLabel(self.frame_9)
        self.temp3.setObjectName(u"temp3")
        self.temp3.setMinimumSize(QSize(0, 28))
        self.temp3.setFont(font7)
        self.temp3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_3.addWidget(self.temp3, 2, 0, 1, 1)


        self.gridLayout_2.addWidget(self.frame_9, 1, 1, 1, 1, Qt.AlignRight|Qt.AlignBottom)


        self.verticalLayout_3.addWidget(self.frame_10, 0, Qt.AlignBottom)


        self.verticalLayout.addWidget(self.frame_4)


        self.retranslateUi(DetallesVenta)

        QMetaObject.connectSlotsByName(DetallesVenta)
    # setupUi

    def retranslateUi(self, DetallesVenta):
        DetallesVenta.setWindowTitle(QCoreApplication.translate("DetallesVenta", u"Form", None))
        self.label_17.setText(QCoreApplication.translate("DetallesVenta", u"Detalles de venta", None))
        self.label_5.setText(QCoreApplication.translate("DetallesVenta", u"Folio", None))
        self.lbFolio.setText(QCoreApplication.translate("DetallesVenta", u"123211", None))
        self.groupBox.setTitle(QCoreApplication.translate("DetallesVenta", u"Cliente", None))
        self.txtTelefono.setText(QCoreApplication.translate("DetallesVenta", u"N/A", None))
        self.txtCliente.setText(QCoreApplication.translate("DetallesVenta", u"P\u00fablico general", None))
        self.txtCorreo.setText(QCoreApplication.translate("DetallesVenta", u"N/A", None))
        self.label_7.setText(QCoreApplication.translate("DetallesVenta", u"E-mail", None))
        self.label_8.setText(QCoreApplication.translate("DetallesVenta", u"Tel\u00e9fono", None))
        self.label_6.setText(QCoreApplication.translate("DetallesVenta", u"Nombre", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("DetallesVenta", u"Fecha de creaci\u00f3n", None))
        self.txtCreacion.setText(QCoreApplication.translate("DetallesVenta", u"02 de febrero 2023, 5:00 p.m.", None))
        self.boxEntrega.setTitle(QCoreApplication.translate("DetallesVenta", u"Fecha de entrega", None))
        self.txtEntrega.setText(QCoreApplication.translate("DetallesVenta", u"02 de febrero 2023, 5:00 p.m.", None))
        ___qtablewidgetitem = self.tabla_productos.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("DetallesVenta", u"Cantidad", None));
        ___qtablewidgetitem1 = self.tabla_productos.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("DetallesVenta", u"Producto", None));
        ___qtablewidgetitem2 = self.tabla_productos.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("DetallesVenta", u"Especificaciones", None));
        ___qtablewidgetitem3 = self.tabla_productos.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("DetallesVenta", u"Precio", None));
        ___qtablewidgetitem4 = self.tabla_productos.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("DetallesVenta", u"Descuento $", None));
        ___qtablewidgetitem5 = self.tabla_productos.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("DetallesVenta", u"Importe", None));
        self.txtComentarios.setPlaceholderText(QCoreApplication.translate("DetallesVenta", u"Sin comentarios adicionales...", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("DetallesVenta", u"Vendedor", None))
        self.txtVendedor.setText(QCoreApplication.translate("DetallesVenta", u"default", None))
        self.label_16.setText(QCoreApplication.translate("DetallesVenta", u"$", None))
        self.label_18.setText(QCoreApplication.translate("DetallesVenta", u"Total", None))
        self.lbTotal.setText(QCoreApplication.translate("DetallesVenta", u"0.00", None))
        self.lbSaldo.setText(QCoreApplication.translate("DetallesVenta", u"0.00", None))
        self.temp4.setText(QCoreApplication.translate("DetallesVenta", u"$", None))
        self.temp1.setText(QCoreApplication.translate("DetallesVenta", u"Anticipo", None))
        self.lbAnticipo.setText(QCoreApplication.translate("DetallesVenta", u"0.00", None))
        self.temp2.setText(QCoreApplication.translate("DetallesVenta", u"$", None))
        self.temp3.setText(QCoreApplication.translate("DetallesVenta", u"Saldo", None))
    # retranslateUi

