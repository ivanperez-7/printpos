# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_AgregarDescuento.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTableWidgetItem,
    QWidget)

from utils.mywidgets import TablaDatos
from . import resources_rc

class Ui_AgregarDescuento(object):
    def setupUi(self, AgregarDescuento):
        if not AgregarDescuento.objectName():
            AgregarDescuento.setObjectName(u"AgregarDescuento")
        AgregarDescuento.setWindowModality(Qt.ApplicationModal)
        AgregarDescuento.resize(781, 470)
        self.frame = QFrame(AgregarDescuento)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(0, 0, 911, 81))
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        self.frame.setFont(font)
        self.frame.setStyleSheet(u"background-color: rgb(52, 172, 224);")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(80, 20, 251, 41))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(18)
        self.label.setFont(font1)
        self.label.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.btRegresar = QPushButton(self.frame)
        self.btRegresar.setObjectName(u"btRegresar")
        self.btRegresar.setGeometry(QRect(20, 20, 41, 41))
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
        self.label_2 = QLabel(AgregarDescuento)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 100, 271, 21))
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        font2.setPointSize(12)
        self.label_2.setFont(font2)
        self.tabla_productos = TablaDatos(AgregarDescuento)
        if (self.tabla_productos.columnCount() < 5):
            self.tabla_productos.setColumnCount(5)
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
        self.tabla_productos.setObjectName(u"tabla_productos")
        self.tabla_productos.setGeometry(QRect(20, 130, 741, 251))
        self.tabla_productos.horizontalHeader().setMinimumSectionSize(80)
        self.label_3 = QLabel(AgregarDescuento)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 415, 311, 21))
        self.label_3.setFont(font2)
        self.btListo = QPushButton(AgregarDescuento)
        self.btListo.setObjectName(u"btListo")
        self.btListo.setGeometry(QRect(660, 400, 101, 51))
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(11)
        self.btListo.setFont(font3)
        icon1 = QIcon()
        icon1.addFile(u":/img/resources/images/accept.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btListo.setIcon(icon1)
        self.txtPrecio = QLineEdit(AgregarDescuento)
        self.txtPrecio.setObjectName(u"txtPrecio")
        self.txtPrecio.setGeometry(QRect(300, 416, 171, 20))
        self.txtPrecio.setFont(font2)
        QWidget.setTabOrder(self.tabla_productos, self.txtPrecio)
        QWidget.setTabOrder(self.txtPrecio, self.btListo)
        QWidget.setTabOrder(self.btListo, self.btRegresar)

        self.retranslateUi(AgregarDescuento)

        QMetaObject.connectSlotsByName(AgregarDescuento)
    # setupUi

    def retranslateUi(self, AgregarDescuento):
        AgregarDescuento.setWindowTitle(QCoreApplication.translate("AgregarDescuento", u"Form", None))
        self.label.setText(QCoreApplication.translate("AgregarDescuento", u"Agregar descuento", None))
        self.label_2.setText(QCoreApplication.translate("AgregarDescuento", u"1. Seleccionar producto a descontar:", None))
        ___qtablewidgetitem = self.tabla_productos.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("AgregarDescuento", u"Cantidad", None));
        ___qtablewidgetitem1 = self.tabla_productos.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("AgregarDescuento", u"Producto", None));
        ___qtablewidgetitem2 = self.tabla_productos.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("AgregarDescuento", u"Especificaciones", None));
        ___qtablewidgetitem3 = self.tabla_productos.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("AgregarDescuento", u"Precio", None));
        ___qtablewidgetitem4 = self.tabla_productos.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("AgregarDescuento", u"Descuento $", None));
        self.label_3.setText(QCoreApplication.translate("AgregarDescuento", u"2. Ingresar nuevo precio por unidad:", None))
        self.btListo.setText(QCoreApplication.translate("AgregarDescuento", u" Listo", None))
        self.txtPrecio.setPlaceholderText(QCoreApplication.translate("AgregarDescuento", u"0.70", None))
    # retranslateUi

