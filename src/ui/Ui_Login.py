# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_Login.ui'
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
from PySide6.QtWidgets import (QApplication, QButtonGroup, QLabel, QLineEdit,
    QRadioButton, QSizePolicy, QWidget)

from backends.Login import LoginButton
from . import resources_rc

class Ui_Login(object):
    def setupUi(self, Login):
        if not Login.objectName():
            Login.setObjectName(u"Login")
        Login.resize(461, 506)
        icon = QIcon()
        icon.addFile(u":/img/icon.ico", QSize(), QIcon.Normal, QIcon.Off)
        Login.setWindowIcon(icon)
        Login.setStyleSheet(u"QLineEdit {\n"
"	border-radius: 8px;\n"
"	border: 1px solid #e0e4e7;\n"
"	padding: 5px 15px;\n"
"}\n"
"\n"
"QLineEdit:focus {\n"
"	border: 1px solid #d0e3ff;\n"
"}")
        self.lbEstado = QLabel(Login)
        self.lbEstado.setObjectName(u"lbEstado")
        self.lbEstado.setGeometry(QRect(28, 430, 191, 55))
        font = QFont()
        font.setPointSize(10)
        self.lbEstado.setFont(font)
        self.lbEstado.setStyleSheet(u"color: rgb(255, 0, 0);")
        self.lbEstado.setAlignment(Qt.AlignCenter)
        self.lbEstado.setWordWrap(True)
        self.btIngresar = LoginButton(Login)
        self.btIngresar.setObjectName(u"btIngresar")
        self.btIngresar.setGeometry(QRect(248, 435, 181, 41))
        self.btIngresar.setCursor(QCursor(Qt.PointingHandCursor))
        self.lbUsuario = QLabel(Login)
        self.lbUsuario.setObjectName(u"lbUsuario")
        self.lbUsuario.setGeometry(QRect(61, 160, 81, 16))
        font1 = QFont()
        font1.setPointSize(11)
        self.lbUsuario.setFont(font1)
        self.radioButton = QRadioButton(Login)
        self.groupRol = QButtonGroup(Login)
        self.groupRol.setObjectName(u"groupRol")
        self.groupRol.addButton(self.radioButton)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setGeometry(QRect(108, 388, 111, 20))
        self.radioButton.setFont(font1)
        self.radioButton.setChecked(True)
        self.lbSubtitulo = QLabel(Login)
        self.lbSubtitulo.setObjectName(u"lbSubtitulo")
        self.lbSubtitulo.setGeometry(QRect(50, 80, 161, 16))
        self.lbSubtitulo.setFont(font1)
        self.inputUsuario = QLineEdit(Login)
        self.inputUsuario.setObjectName(u"inputUsuario")
        self.inputUsuario.setGeometry(QRect(61, 180, 331, 41))
        font2 = QFont()
        font2.setPointSize(12)
        self.inputUsuario.setFont(font2)
        self.inputUsuario.setAlignment(Qt.AlignCenter)
        self.inputUsuario.setClearButtonEnabled(True)
        self.lbContrasenia = QLabel(Login)
        self.lbContrasenia.setObjectName(u"lbContrasenia")
        self.lbContrasenia.setGeometry(QRect(61, 260, 91, 16))
        self.lbContrasenia.setFont(font1)
        self.lbContrasenia_2 = QLabel(Login)
        self.lbContrasenia_2.setObjectName(u"lbContrasenia_2")
        self.lbContrasenia_2.setGeometry(QRect(61, 356, 111, 21))
        self.lbContrasenia_2.setFont(font1)
        self.radioButton_2 = QRadioButton(Login)
        self.groupRol.addButton(self.radioButton_2)
        self.radioButton_2.setObjectName(u"radioButton_2")
        self.radioButton_2.setGeometry(QRect(238, 388, 121, 20))
        self.radioButton_2.setFont(font1)
        self.inputContrasenia = QLineEdit(Login)
        self.inputContrasenia.setObjectName(u"inputContrasenia")
        self.inputContrasenia.setGeometry(QRect(61, 280, 331, 41))
        self.inputContrasenia.setFont(font2)
        self.inputContrasenia.setEchoMode(QLineEdit.Password)
        self.inputContrasenia.setAlignment(Qt.AlignCenter)
        self.inputContrasenia.setClearButtonEnabled(True)
        self.label = QLabel(Login)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(248, 30, 171, 91))
        self.label.setStyleSheet(u"image: url(:/img/resources/images/logo.png);")
        self.lbTitulo = QLabel(Login)
        self.lbTitulo.setObjectName(u"lbTitulo")
        self.lbTitulo.setGeometry(QRect(50, 40, 101, 41))
        font3 = QFont()
        font3.setPointSize(18)
        font3.setBold(True)
        self.lbTitulo.setFont(font3)
        QWidget.setTabOrder(self.inputUsuario, self.inputContrasenia)
        QWidget.setTabOrder(self.inputContrasenia, self.radioButton)
        QWidget.setTabOrder(self.radioButton, self.radioButton_2)
        QWidget.setTabOrder(self.radioButton_2, self.btIngresar)

        self.retranslateUi(Login)

        QMetaObject.connectSlotsByName(Login)
    # setupUi

    def retranslateUi(self, Login):
        Login.setWindowTitle(QCoreApplication.translate("Login", u"Iniciar sesi\u00f3n", None))
        self.lbEstado.setText("")
        self.btIngresar.setText(QCoreApplication.translate("Login", u"INGRESAR", None))
        self.lbUsuario.setText(QCoreApplication.translate("Login", u"Usuario:", None))
        self.radioButton.setText(QCoreApplication.translate("Login", u"Vendedor", None))
        self.lbSubtitulo.setText(QCoreApplication.translate("Login", u"\u00a1Bienvenido de vuelta!", None))
        self.inputUsuario.setPlaceholderText(QCoreApplication.translate("Login", u"Ingrese su nombre de usuario...", None))
        self.lbContrasenia.setText(QCoreApplication.translate("Login", u"Contrase\u00f1a:", None))
        self.lbContrasenia_2.setText(QCoreApplication.translate("Login", u"Ingresar como:", None))
        self.radioButton_2.setText(QCoreApplication.translate("Login", u"Administrador", None))
        self.inputContrasenia.setPlaceholderText(QCoreApplication.translate("Login", u"Ingrese su contrase\u00f1a...", None))
        self.label.setText("")
        self.lbTitulo.setText(QCoreApplication.translate("Login", u"Ingresar", None))
    # retranslateUi

