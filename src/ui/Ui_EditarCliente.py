# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_EditarCliente.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)
from . import resources_rc

class Ui_EditarCliente(object):
    def setupUi(self, EditarCliente):
        if not EditarCliente.objectName():
            EditarCliente.setObjectName(u"EditarCliente")
        EditarCliente.setWindowModality(Qt.ApplicationModal)
        EditarCliente.resize(946, 684)
        self.verticalLayout_3 = QVBoxLayout(EditarCliente)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, -1)
        self.frame_4 = QFrame(EditarCliente)
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

        self.horizontalLayout_2.addWidget(self.btRegresar)

        self.lbTitulo = QLabel(self.frame_5)
        self.lbTitulo.setObjectName(u"lbTitulo")
        self.lbTitulo.setMinimumSize(QSize(211, 41))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(18)
        self.lbTitulo.setFont(font1)
        self.lbTitulo.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.horizontalLayout_2.addWidget(self.lbTitulo)


        self.horizontalLayout.addWidget(self.frame_5, 0, Qt.AlignLeft)


        self.verticalLayout_3.addWidget(self.frame_4)

        self.frame = QFrame(EditarCliente)
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
        self.groupBox_2 = QGroupBox(self.frame_2)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(80, 150, 281, 61))
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(11)
        self.groupBox_2.setFont(font3)
        self.txtCelular = QLineEdit(self.groupBox_2)
        self.txtCelular.setObjectName(u"txtCelular")
        self.txtCelular.setGeometry(QRect(60, 30, 191, 20))
        self.txtCelular.setFont(font3)
        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 30, 30, 20))
        self.label_4.setFont(font3)
        self.txtLada = QLineEdit(self.groupBox_2)
        self.txtLada.setObjectName(u"txtLada")
        self.txtLada.setGeometry(QRect(20, 30, 31, 20))
        self.txtLada.setFont(font3)
        self.txtLada.setMaxLength(3)
        self.groupBox = QGroupBox(self.frame_2)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(40, 70, 371, 61))
        self.groupBox.setFont(font3)
        self.txtNombre = QLineEdit(self.groupBox)
        self.txtNombre.setObjectName(u"txtNombre")
        self.txtNombre.setGeometry(QRect(10, 30, 321, 20))
        self.txtNombre.setFont(font3)
        self.groupBox_5 = QGroupBox(self.frame_2)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.groupBox_5.setGeometry(QRect(80, 230, 281, 61))
        self.groupBox_5.setFont(font3)
        self.txtCorreo = QLineEdit(self.groupBox_5)
        self.txtCorreo.setObjectName(u"txtCorreo")
        self.txtCorreo.setGeometry(QRect(10, 30, 241, 20))
        self.txtCorreo.setFont(font3)
        self.groupBox_7 = QGroupBox(self.frame_2)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.groupBox_7.setGeometry(QRect(80, 310, 281, 61))
        self.groupBox_7.setFont(font3)
        self.txtRFC = QLineEdit(self.groupBox_7)
        self.txtRFC.setObjectName(u"txtRFC")
        self.txtRFC.setGeometry(QRect(10, 30, 241, 20))
        self.txtRFC.setFont(font3)
        self.txtRFC.setMaxLength(13)
        self.groupBox_6 = QGroupBox(self.frame_2)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.groupBox_6.setGeometry(QRect(40, 390, 371, 91))
        self.groupBox_6.setFont(font3)
        self.txtDireccion = QPlainTextEdit(self.groupBox_6)
        self.txtDireccion.setObjectName(u"txtDireccion")
        self.txtDireccion.setGeometry(QRect(10, 30, 331, 51))
        self.txtDireccion.setFont(font3)

        self.horizontalLayout_3.addWidget(self.frame_2)

        self.frame_6 = QFrame(self.frame)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setEnabled(True)
        self.frame_6.setFont(font)
        self.frame_6.setFrameShape(QFrame.Box)
        self.frame_6.setFrameShadow(QFrame.Plain)
        self.frame_6.setLineWidth(1)
        self.verticalLayout_2 = QVBoxLayout(self.frame_6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(20, 15, 20, 20)
        self.label_2 = QLabel(self.frame_6)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font2)
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_2)

        self.checkDescuentos = QCheckBox(self.frame_6)
        self.checkDescuentos.setObjectName(u"checkDescuentos")
        self.checkDescuentos.setEnabled(True)
        self.checkDescuentos.setFont(font3)

        self.verticalLayout_2.addWidget(self.checkDescuentos)

        self.txtDescuentos = QPlainTextEdit(self.frame_6)
        self.txtDescuentos.setObjectName(u"txtDescuentos")
        self.txtDescuentos.setFont(font3)

        self.verticalLayout_2.addWidget(self.txtDescuentos)


        self.horizontalLayout_3.addWidget(self.frame_6)


        self.verticalLayout_3.addWidget(self.frame)

        self.frame_3 = QFrame(EditarCliente)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFont(font)
        self.verticalLayout = QVBoxLayout(self.frame_3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.btRegistrar = QPushButton(self.frame_3)
        self.btRegistrar.setObjectName(u"btRegistrar")
        self.btRegistrar.setMinimumSize(QSize(170, 41))
        self.btRegistrar.setFont(font3)
        self.btRegistrar.setText(u" Aceptar cambios")
        icon1 = QIcon()
        icon1.addFile(u":/img/resources/images/edit.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btRegistrar.setIcon(icon1)

        self.verticalLayout.addWidget(self.btRegistrar, 0, Qt.AlignHCenter)


        self.verticalLayout_3.addWidget(self.frame_3)

        QWidget.setTabOrder(self.txtNombre, self.txtLada)
        QWidget.setTabOrder(self.txtLada, self.txtCelular)
        QWidget.setTabOrder(self.txtCelular, self.txtCorreo)
        QWidget.setTabOrder(self.txtCorreo, self.txtRFC)
        QWidget.setTabOrder(self.txtRFC, self.txtDireccion)
        QWidget.setTabOrder(self.txtDireccion, self.checkDescuentos)
        QWidget.setTabOrder(self.checkDescuentos, self.txtDescuentos)
        QWidget.setTabOrder(self.txtDescuentos, self.btRegistrar)
        QWidget.setTabOrder(self.btRegistrar, self.btRegresar)

        self.retranslateUi(EditarCliente)

        QMetaObject.connectSlotsByName(EditarCliente)
    # setupUi

    def retranslateUi(self, EditarCliente):
        EditarCliente.setWindowTitle(QCoreApplication.translate("EditarCliente", u"Form", None))
        self.lbTitulo.setText(QCoreApplication.translate("EditarCliente", u"Editar cliente", None))
        self.label_3.setText(QCoreApplication.translate("EditarCliente", u"Datos generales", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("EditarCliente", u"Tel\u00e9fono", None))
        self.txtCelular.setInputMask(QCoreApplication.translate("EditarCliente", u"999 999 9999;0", None))
        self.txtCelular.setText(QCoreApplication.translate("EditarCliente", u"999  ", None))
        self.label_4.setText(QCoreApplication.translate("EditarCliente", u"+", None))
        self.txtLada.setText(QCoreApplication.translate("EditarCliente", u"52", None))
        self.groupBox.setTitle(QCoreApplication.translate("EditarCliente", u"Nombre", None))
        self.txtNombre.setText("")
        self.groupBox_5.setTitle(QCoreApplication.translate("EditarCliente", u"E-mail", None))
        self.txtCorreo.setText("")
        self.groupBox_7.setTitle(QCoreApplication.translate("EditarCliente", u"RFC", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("EditarCliente", u"Direcci\u00f3n", None))
        self.label_2.setText(QCoreApplication.translate("EditarCliente", u"Descuentos especiales", None))
        self.checkDescuentos.setText(QCoreApplication.translate("EditarCliente", u"El cliente tiene descuentos especiales.", None))
    # retranslateUi

