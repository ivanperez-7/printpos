# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_EditarInventario.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget)
from . import resources_rc

class Ui_EditarInventario(object):
    def setupUi(self, EditarInventario):
        if not EditarInventario.objectName():
            EditarInventario.setObjectName(u"EditarInventario")
        EditarInventario.resize(946, 684)
        self.verticalLayout_3 = QVBoxLayout(EditarInventario)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, -1)
        self.frame_4 = QFrame(EditarInventario)
        self.frame_4.setObjectName(u"frame_4")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        self.frame_4.setFont(font)
        self.frame_4.setStyleSheet(u"QFrame { background-color: rgb(52, 172, 224); border: none}")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_4)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame_5 = QFrame(self.frame_4)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setMinimumSize(QSize(294, 63))
        self.frame_5.setMaximumSize(QSize(294, 63))
        self.frame_5.setFont(font)
        self.frame_5.setStyleSheet(u"QFrame {border: none}")
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_5)
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

        self.horizontalLayout_2.addWidget(self.btRegresar, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.lbTitulo = QLabel(self.frame_5)
        self.lbTitulo.setObjectName(u"lbTitulo")
        self.lbTitulo.setMinimumSize(QSize(211, 41))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(18)
        self.lbTitulo.setFont(font1)
        self.lbTitulo.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.horizontalLayout_2.addWidget(self.lbTitulo, 0, Qt.AlignHCenter|Qt.AlignVCenter)


        self.horizontalLayout.addWidget(self.frame_5, 0, Qt.AlignLeft)


        self.verticalLayout_3.addWidget(self.frame_4)

        self.frame = QFrame(EditarInventario)
        self.frame.setObjectName(u"frame")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFont(font)
        self.horizontalLayout_3 = QHBoxLayout(self.frame)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(-1, -1, -1, 0)
        self.frame_2 = QFrame(self.frame)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setMinimumSize(QSize(451, 469))
        self.frame_2.setFont(font)
        self.frame_2.setFrameShape(QFrame.Box)
        self.frame_2.setFrameShadow(QFrame.Plain)
        self.frame_2.setLineWidth(1)
        self.label_3 = QLabel(self.frame_2)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 12, 431, 30))
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        font2.setPointSize(14)
        self.label_3.setFont(font2)
        self.label_3.setAlignment(Qt.AlignCenter)
        self.groupBox_3 = QGroupBox(self.frame_2)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(250, 330, 161, 61))
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(11)
        self.groupBox_3.setFont(font3)
        self.txtMinimo = QLineEdit(self.groupBox_3)
        self.txtMinimo.setObjectName(u"txtMinimo")
        self.txtMinimo.setGeometry(QRect(10, 30, 101, 20))
        self.txtMinimo.setFont(font3)
        self.label_4 = QLabel(self.groupBox_3)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(120, 30, 71, 16))
        self.label_4.setFont(font3)
        self.groupBox_2 = QGroupBox(self.frame_2)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(40, 330, 191, 61))
        self.groupBox_2.setFont(font3)
        self.txtPrecioCompra = QLineEdit(self.groupBox_2)
        self.txtPrecioCompra.setObjectName(u"txtPrecioCompra")
        self.txtPrecioCompra.setGeometry(QRect(25, 30, 101, 20))
        self.txtPrecioCompra.setFont(font3)
        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 32, 21, 16))
        self.label.setFont(font3)
        self.groupBox = QGroupBox(self.frame_2)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(30, 110, 391, 61))
        self.groupBox.setFont(font3)
        self.txtNombre = QLineEdit(self.groupBox)
        self.txtNombre.setObjectName(u"txtNombre")
        self.txtNombre.setGeometry(QRect(10, 30, 351, 20))
        self.txtNombre.setFont(font3)
        self.groupBox_4 = QGroupBox(self.frame_2)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setGeometry(QRect(230, 220, 181, 61))
        font4 = QFont()
        font4.setFamilies([u"Segoe UI"])
        font4.setPointSize(11)
        font4.setBold(False)
        self.groupBox_4.setFont(font4)
        self.txtExistencia = QLineEdit(self.groupBox_4)
        self.txtExistencia.setObjectName(u"txtExistencia")
        self.txtExistencia.setGeometry(QRect(10, 30, 91, 20))
        self.txtExistencia.setFont(font4)
        self.txtExistencia.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.label_5 = QLabel(self.groupBox_4)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(110, 30, 71, 16))
        self.label_5.setFont(font4)
        self.groupBox_5 = QGroupBox(self.frame_2)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.groupBox_5.setGeometry(QRect(40, 220, 171, 61))
        self.groupBox_5.setFont(font3)
        self.txtTamano = QLineEdit(self.groupBox_5)
        self.txtTamano.setObjectName(u"txtTamano")
        self.txtTamano.setGeometry(QRect(10, 30, 81, 20))
        self.txtTamano.setFont(font3)
        self.label_7 = QLabel(self.groupBox_5)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(100, 30, 71, 16))
        self.label_7.setFont(font3)

        self.horizontalLayout_3.addWidget(self.frame_2)

        self.frame_6 = QFrame(self.frame)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFont(font)
        self.frame_6.setFrameShape(QFrame.Box)
        self.frame_6.setFrameShadow(QFrame.Plain)
        self.frame_6.setLineWidth(1)
        self.verticalLayout_2 = QVBoxLayout(self.frame_6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, 15, -1, 15)
        self.label_2 = QLabel(self.frame_6)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font2)
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_2)

        self.scrollArea = QScrollArea(self.frame_6)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFont(font)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaLista = QWidget()
        self.scrollAreaLista.setObjectName(u"scrollAreaLista")
        self.scrollAreaLista.setGeometry(QRect(0, 0, 451, 413))
        self.layoutScroll = QVBoxLayout(self.scrollAreaLista)
        self.layoutScroll.setObjectName(u"layoutScroll")
        self.layoutScroll.setContentsMargins(-1, -1, 0, -1)
        self.scrollArea.setWidget(self.scrollAreaLista)

        self.verticalLayout_2.addWidget(self.scrollArea)

        self.btAgregar = QPushButton(self.frame_6)
        self.btAgregar.setObjectName(u"btAgregar")
        self.btAgregar.setMinimumSize(QSize(160, 31))
        font5 = QFont()
        font5.setFamilies([u"Segoe UI"])
        font5.setPointSize(10)
        self.btAgregar.setFont(font5)
        icon1 = QIcon()
        icon1.addFile(u":/img/resources/images/add.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btAgregar.setIcon(icon1)

        self.verticalLayout_2.addWidget(self.btAgregar, 0, Qt.AlignHCenter)


        self.horizontalLayout_3.addWidget(self.frame_6)


        self.verticalLayout_3.addWidget(self.frame)

        self.frame_3 = QFrame(EditarInventario)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFont(font)
        self.verticalLayout = QVBoxLayout(self.frame_3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.btAceptar = QPushButton(self.frame_3)
        self.btAceptar.setObjectName(u"btAceptar")
        self.btAceptar.setMinimumSize(QSize(170, 41))
        self.btAceptar.setFont(font3)
        self.btAceptar.setText(u" Aceptar cambios")
        icon2 = QIcon()
        icon2.addFile(u":/img/resources/images/edit.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btAceptar.setIcon(icon2)

        self.verticalLayout.addWidget(self.btAceptar, 0, Qt.AlignHCenter)


        self.verticalLayout_3.addWidget(self.frame_3)

        QWidget.setTabOrder(self.txtNombre, self.txtTamano)
        QWidget.setTabOrder(self.txtTamano, self.txtExistencia)
        QWidget.setTabOrder(self.txtExistencia, self.txtPrecioCompra)
        QWidget.setTabOrder(self.txtPrecioCompra, self.txtMinimo)
        QWidget.setTabOrder(self.txtMinimo, self.scrollArea)
        QWidget.setTabOrder(self.scrollArea, self.btAgregar)
        QWidget.setTabOrder(self.btAgregar, self.btAceptar)
        QWidget.setTabOrder(self.btAceptar, self.btRegresar)

        self.retranslateUi(EditarInventario)

        QMetaObject.connectSlotsByName(EditarInventario)
    # setupUi

    def retranslateUi(self, EditarInventario):
        EditarInventario.setWindowTitle(QCoreApplication.translate("EditarInventario", u"Form", None))
        self.lbTitulo.setText(QCoreApplication.translate("EditarInventario", u"Editar elemento", None))
        self.label_3.setText(QCoreApplication.translate("EditarInventario", u"Datos generales", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("EditarInventario", u"M\u00ednimo", None))
        self.txtMinimo.setText("")
        self.label_4.setText(QCoreApplication.translate("EditarInventario", u"lotes", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("EditarInventario", u"Precio de compra de lote", None))
        self.txtPrecioCompra.setText("")
        self.label.setText(QCoreApplication.translate("EditarInventario", u"$", None))
        self.groupBox.setTitle(QCoreApplication.translate("EditarInventario", u"Nombre", None))
        self.txtNombre.setText("")
        self.groupBox_4.setTitle(QCoreApplication.translate("EditarInventario", u"En existencia", None))
        self.txtExistencia.setText("")
        self.label_5.setText(QCoreApplication.translate("EditarInventario", u"unidades", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("EditarInventario", u"Tama\u00f1o del lote", None))
        self.txtTamano.setText("")
        self.label_7.setText(QCoreApplication.translate("EditarInventario", u"unidades", None))
        self.label_2.setText(QCoreApplication.translate("EditarInventario", u"Se utiliza en los productos...", None))
        self.btAgregar.setText(QCoreApplication.translate("EditarInventario", u"Agregar elemento", None))
    # retranslateUi

