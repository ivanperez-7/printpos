# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_EditarUsuario.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGroupBox, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QWidget)
from . import resources_rc
from . import resources_rc

class Ui_EditarUsuario(object):
    def setupUi(self, EditarUsuario):
        if not EditarUsuario.objectName():
            EditarUsuario.setObjectName(u"EditarUsuario")
        EditarUsuario.setWindowModality(Qt.ApplicationModal)
        EditarUsuario.resize(413, 527)
        icon = QIcon()
        icon.addFile(u":/img/icon.ico", QSize(), QIcon.Normal, QIcon.Off)
        EditarUsuario.setWindowIcon(icon)
        self.frame = QFrame(EditarUsuario)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(0, 0, 501, 81))
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        self.frame.setFont(font)
        self.frame.setStyleSheet(u"background-color: rgb(52, 172, 224);")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.lbTitulo = QLabel(self.frame)
        self.lbTitulo.setObjectName(u"lbTitulo")
        self.lbTitulo.setGeometry(QRect(80, 20, 181, 41))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(18)
        self.lbTitulo.setFont(font1)
        self.lbTitulo.setStyleSheet(u"color: rgb(255, 255, 255);")
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
        icon1 = QIcon()
        icon1.addFile(u":/img/resources/images/leftarrow.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btRegresar.setIcon(icon1)
        self.btRegresar.setIconSize(QSize(40, 40))
        self.btRegresar.setFlat(True)
        self.label_aceptar = QLabel(EditarUsuario)
        self.label_aceptar.setObjectName(u"label_aceptar")
        self.label_aceptar.setGeometry(QRect(290, 484, 100, 21))
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        font2.setPointSize(11)
        font2.setBold(False)
        self.label_aceptar.setFont(font2)
        self.label_aceptar.setAlignment(Qt.AlignCenter)
        self.label_icono = QLabel(EditarUsuario)
        self.label_icono.setObjectName(u"label_icono")
        self.label_icono.setGeometry(QRect(320, 440, 40, 40))
        self.label_icono.setFont(font)
        self.label_icono.setPixmap(QPixmap(u":/img/resources/images/edit.png"))
        self.label_icono.setScaledContents(True)
        self.btRegistrar = QPushButton(EditarUsuario)
        self.btRegistrar.setObjectName(u"btRegistrar")
        self.btRegistrar.setGeometry(QRect(290, 430, 100, 81))
        self.btRegistrar.setFont(font)
        self.groupBox = QGroupBox(EditarUsuario)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(20, 110, 371, 61))
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(11)
        self.groupBox.setFont(font3)
        self.txtUsuario = QLineEdit(self.groupBox)
        self.txtUsuario.setObjectName(u"txtUsuario")
        self.txtUsuario.setGeometry(QRect(10, 30, 321, 20))
        self.txtUsuario.setFont(font3)
        self.groupBox_2 = QGroupBox(EditarUsuario)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(20, 190, 371, 61))
        self.groupBox_2.setFont(font3)
        self.txtNombre = QLineEdit(self.groupBox_2)
        self.txtNombre.setObjectName(u"txtNombre")
        self.txtNombre.setGeometry(QRect(10, 30, 321, 20))
        self.txtNombre.setFont(font3)
        self.groupPsswd = QGroupBox(EditarUsuario)
        self.groupPsswd.setObjectName(u"groupPsswd")
        self.groupPsswd.setEnabled(False)
        self.groupPsswd.setGeometry(QRect(60, 270, 281, 61))
        self.groupPsswd.setFont(font3)
        self.txtPsswd = QLineEdit(self.groupPsswd)
        self.txtPsswd.setObjectName(u"txtPsswd")
        self.txtPsswd.setGeometry(QRect(10, 30, 241, 20))
        self.txtPsswd.setFont(font3)
        self.txtPsswd.setEchoMode(QLineEdit.Password)
        self.groupPsswdConf = QGroupBox(EditarUsuario)
        self.groupPsswdConf.setObjectName(u"groupPsswdConf")
        self.groupPsswdConf.setEnabled(False)
        self.groupPsswdConf.setGeometry(QRect(60, 350, 281, 61))
        self.groupPsswdConf.setFont(font3)
        self.txtPsswdConf = QLineEdit(self.groupPsswdConf)
        self.txtPsswdConf.setObjectName(u"txtPsswdConf")
        self.txtPsswdConf.setGeometry(QRect(10, 30, 241, 20))
        self.txtPsswdConf.setFont(font3)
        self.txtPsswdConf.setEchoMode(QLineEdit.Password)
        self.groupBox_6 = QGroupBox(EditarUsuario)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.groupBox_6.setGeometry(QRect(20, 440, 241, 61))
        self.groupBox_6.setFont(font3)
        self.boxPermisos = QComboBox(self.groupBox_6)
        self.boxPermisos.addItem("")
        self.boxPermisos.addItem("")
        self.boxPermisos.setObjectName(u"boxPermisos")
        self.boxPermisos.setGeometry(QRect(10, 30, 201, 20))
        font4 = QFont()
        font4.setFamilies([u"Segoe UI"])
        font4.setPointSize(10)
        self.boxPermisos.setFont(font4)
        self.boxPermisos.setStyleSheet(u"QFrame {border: 1px solid black;}")
        self.cambiarPsswd = QCheckBox(EditarUsuario)
        self.cambiarPsswd.setObjectName(u"cambiarPsswd")
        self.cambiarPsswd.setGeometry(QRect(30, 340, 16, 17))
        self.cambiarPsswd.setFont(font)
        self.btRegistrar.raise_()
        self.frame.raise_()
        self.label_aceptar.raise_()
        self.label_icono.raise_()
        self.groupBox.raise_()
        self.groupBox_2.raise_()
        self.groupPsswd.raise_()
        self.groupPsswdConf.raise_()
        self.groupBox_6.raise_()
        self.cambiarPsswd.raise_()
        QWidget.setTabOrder(self.txtUsuario, self.txtNombre)
        QWidget.setTabOrder(self.txtNombre, self.txtPsswd)
        QWidget.setTabOrder(self.txtPsswd, self.txtPsswdConf)
        QWidget.setTabOrder(self.txtPsswdConf, self.boxPermisos)
        QWidget.setTabOrder(self.boxPermisos, self.btRegistrar)
        QWidget.setTabOrder(self.btRegistrar, self.cambiarPsswd)
        QWidget.setTabOrder(self.cambiarPsswd, self.btRegresar)

        self.retranslateUi(EditarUsuario)

        QMetaObject.connectSlotsByName(EditarUsuario)
    # setupUi

    def retranslateUi(self, EditarUsuario):
        EditarUsuario.setWindowTitle(QCoreApplication.translate("EditarUsuario", u"Form", None))
        self.lbTitulo.setText(QCoreApplication.translate("EditarUsuario", u"Editar usuario", None))
        self.label_aceptar.setText(QCoreApplication.translate("EditarUsuario", u"Editar", None))
        self.btRegistrar.setText("")
        self.groupBox.setTitle(QCoreApplication.translate("EditarUsuario", u"Usuario", None))
        self.txtUsuario.setText("")
        self.txtUsuario.setPlaceholderText(QCoreApplication.translate("EditarUsuario", u"juan_perez.023", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("EditarUsuario", u"Nombre(s) y apellido(s)", None))
        self.txtNombre.setText("")
        self.txtNombre.setPlaceholderText(QCoreApplication.translate("EditarUsuario", u"Juan P\u00e9rez", None))
        self.groupPsswd.setTitle(QCoreApplication.translate("EditarUsuario", u"Contrase\u00f1a", None))
        self.txtPsswd.setText("")
        self.groupPsswdConf.setTitle(QCoreApplication.translate("EditarUsuario", u"Confirmar contrase\u00f1a", None))
        self.txtPsswdConf.setText("")
        self.groupBox_6.setTitle(QCoreApplication.translate("EditarUsuario", u"Permisos", None))
        self.boxPermisos.setItemText(0, QCoreApplication.translate("EditarUsuario", u"Vendedor", None))
        self.boxPermisos.setItemText(1, QCoreApplication.translate("EditarUsuario", u"Administrador", None))

        self.cambiarPsswd.setText("")
    # retranslateUi

