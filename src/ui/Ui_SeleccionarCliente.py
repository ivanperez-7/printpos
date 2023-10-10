# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_SeleccionarCliente.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QTableWidgetItem, QVBoxLayout, QWidget)

from utils.mywidgets import TablaDatos
from . import resources_rc

class Ui_SeleccionarCliente(object):
    def setupUi(self, SeleccionarCliente):
        if not SeleccionarCliente.objectName():
            SeleccionarCliente.setObjectName(u"SeleccionarCliente")
        SeleccionarCliente.setWindowModality(Qt.ApplicationModal)
        SeleccionarCliente.resize(921, 570)
        self.verticalLayout = QVBoxLayout(SeleccionarCliente)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(SeleccionarCliente)
        self.frame.setObjectName(u"frame")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setStyleSheet(u"background-color: rgb(52, 172, 224);")
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_4 = QFrame(self.frame)
        self.frame_4.setObjectName(u"frame_4")
        sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_4.sizePolicy().hasHeightForWidth())
        self.frame_4.setSizePolicy(sizePolicy1)
        self.frame_4.setStyleSheet(u"QFrame { border:none; }\n"
"background-color: rgb(52, 172, 224);")
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_4)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(18, 18, 15, 18)
        self.btRegresar = QPushButton(self.frame_4)
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
        icon = QIcon()
        icon.addFile(u":/img/resources/images/leftarrow.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btRegresar.setIcon(icon)
        self.btRegresar.setIconSize(QSize(40, 40))
        self.btRegresar.setFlat(True)

        self.horizontalLayout.addWidget(self.btRegresar)

        self.label = QLabel(self.frame_4)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(201, 41))
        font = QFont()
        font.setPointSize(18)
        self.label.setFont(font)
        self.label.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.horizontalLayout.addWidget(self.label)


        self.verticalLayout_2.addWidget(self.frame_4)


        self.verticalLayout.addWidget(self.frame)

        self.frame_2 = QFrame(SeleccionarCliente)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy2)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_2)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(-1, -1, -1, 0)
        self.frame_5 = QFrame(self.frame_2)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_4.setSpacing(20)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(-1, -1, -1, 15)
        self.frame_7 = QFrame(self.frame_5)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_7)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.btAgregar = QPushButton(self.frame_7)
        self.btAgregar.setObjectName(u"btAgregar")
        self.btAgregar.setMinimumSize(QSize(171, 31))
        font1 = QFont()
        font1.setPointSize(11)
        self.btAgregar.setFont(font1)
        icon1 = QIcon()
        icon1.addFile(u":/img/resources/images/accept.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btAgregar.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.btAgregar)


        self.horizontalLayout_4.addWidget(self.frame_7)

        self.frame_8 = QFrame(self.frame_5)
        self.frame_8.setObjectName(u"frame_8")
        sizePolicy.setHeightForWidth(self.frame_8.sizePolicy().hasHeightForWidth())
        self.frame_8.setSizePolicy(sizePolicy)
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_8)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.frame_8)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(51, 31))
        self.label_2.setMaximumSize(QSize(51, 31))
        self.label_2.setStyleSheet(u"image: url(:/img/resources/images/magnifier.png);\n"
"background-color: rgb(255, 255, 255);")

        self.horizontalLayout_3.addWidget(self.label_2)

        self.searchBar = QLineEdit(self.frame_8)
        self.searchBar.setObjectName(u"searchBar")
        self.searchBar.setMinimumSize(QSize(0, 31))
        self.searchBar.setMaximumSize(QSize(16777215, 31))
        self.searchBar.setFont(font1)
        self.searchBar.setFrame(False)

        self.horizontalLayout_3.addWidget(self.searchBar)


        self.horizontalLayout_4.addWidget(self.frame_8)


        self.verticalLayout_3.addWidget(self.frame_5, 0, Qt.AlignTop)

        self.frame_6 = QFrame(self.frame_2)
        self.frame_6.setObjectName(u"frame_6")
        sizePolicy2.setHeightForWidth(self.frame_6.sizePolicy().hasHeightForWidth())
        self.frame_6.setSizePolicy(sizePolicy2)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(-1, -1, -1, 20)
        self.tabla_seleccionar = TablaDatos(self.frame_6)
        if (self.tabla_seleccionar.columnCount() < 5):
            self.tabla_seleccionar.setColumnCount(5)
        __qtablewidgetitem = QTableWidgetItem()
        self.tabla_seleccionar.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tabla_seleccionar.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tabla_seleccionar.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tabla_seleccionar.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tabla_seleccionar.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        self.tabla_seleccionar.setObjectName(u"tabla_seleccionar")

        self.horizontalLayout_5.addWidget(self.tabla_seleccionar)


        self.verticalLayout_3.addWidget(self.frame_6)


        self.verticalLayout.addWidget(self.frame_2)


        self.retranslateUi(SeleccionarCliente)

        QMetaObject.connectSlotsByName(SeleccionarCliente)
    # setupUi

    def retranslateUi(self, SeleccionarCliente):
        SeleccionarCliente.setWindowTitle(QCoreApplication.translate("SeleccionarCliente", u"Form", None))
        self.label.setText(QCoreApplication.translate("SeleccionarCliente", u"Seleccionar cliente", None))
        self.btAgregar.setText(QCoreApplication.translate("SeleccionarCliente", u"Seleccionar", None))
        self.label_2.setText("")
        self.searchBar.setPlaceholderText(QCoreApplication.translate("SeleccionarCliente", u"Busque cliente por nombre...", None))
        ___qtablewidgetitem = self.tabla_seleccionar.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("SeleccionarCliente", u"Nombre", None));
        ___qtablewidgetitem1 = self.tabla_seleccionar.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("SeleccionarCliente", u"Tel\u00e9fono", None));
        ___qtablewidgetitem2 = self.tabla_seleccionar.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("SeleccionarCliente", u"Correo", None));
        ___qtablewidgetitem3 = self.tabla_seleccionar.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("SeleccionarCliente", u"Direcci\u00f3n", None));
        ___qtablewidgetitem4 = self.tabla_seleccionar.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("SeleccionarCliente", u"RFC", None));
    # retranslateUi

