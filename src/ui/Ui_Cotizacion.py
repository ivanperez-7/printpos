# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_Cotizacion.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QPushButton,
    QSizePolicy, QWidget)
from . import resources_rc
from . import resources_rc

class Ui_EnviarCotizacion(object):
    def setupUi(self, EnviarCotizacion):
        if not EnviarCotizacion.objectName():
            EnviarCotizacion.setObjectName(u"EnviarCotizacion")
        EnviarCotizacion.setWindowModality(Qt.ApplicationModal)
        EnviarCotizacion.resize(511, 355)
        icon = QIcon()
        icon.addFile(u":/img/icon.ico", QSize(), QIcon.Normal, QIcon.Off)
        EnviarCotizacion.setWindowIcon(icon)
        self.frame = QFrame(EnviarCotizacion)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(0, 0, 511, 81))
        self.frame.setStyleSheet(u"background-color: rgb(52, 172, 224);")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(80, 20, 281, 41))
        font = QFont()
        font.setPointSize(18)
        self.label.setFont(font)
        self.label.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.btRegresar = QPushButton(self.frame)
        self.btRegresar.setObjectName(u"btRegresar")
        self.btRegresar.setGeometry(QRect(20, 20, 40, 40))
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
        self.label_2 = QLabel(EnviarCotizacion)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(125, 105, 261, 21))
        font1 = QFont()
        font1.setPointSize(16)
        self.label_2.setFont(font1)
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_62 = QLabel(EnviarCotizacion)
        self.label_62.setObjectName(u"label_62")
        self.label_62.setGeometry(QRect(95, 170, 80, 80))
        self.label_62.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.label_62.setFrameShadow(QFrame.Plain)
        self.label_62.setText(u"")
        self.label_62.setPixmap(QPixmap(u":/img/resources/images/whatsapp.png"))
        self.label_62.setScaledContents(True)
        self.label_62.setTextInteractionFlags(Qt.NoTextInteraction)
        self.label_63 = QLabel(EnviarCotizacion)
        self.label_63.setObjectName(u"label_63")
        self.label_63.setGeometry(QRect(50, 265, 170, 41))
        font2 = QFont()
        font2.setPointSize(12)
        font2.setBold(False)
        self.label_63.setFont(font2)
        self.label_63.setText(u"Enviar cotizaci\u00f3n por WhatsApp")
        self.label_63.setAlignment(Qt.AlignCenter)
        self.label_63.setWordWrap(True)
        self.btWhatsapp = QPushButton(EnviarCotizacion)
        self.btWhatsapp.setObjectName(u"btWhatsapp")
        self.btWhatsapp.setGeometry(QRect(50, 150, 170, 170))
        self.btTicket = QPushButton(EnviarCotizacion)
        self.btTicket.setObjectName(u"btTicket")
        self.btTicket.setGeometry(QRect(290, 150, 170, 170))
        self.label_64 = QLabel(EnviarCotizacion)
        self.label_64.setObjectName(u"label_64")
        self.label_64.setGeometry(QRect(305, 265, 141, 41))
        self.label_64.setFont(font2)
        self.label_64.setText(u"Imprimir cotizaci\u00f3n en ticket")
        self.label_64.setAlignment(Qt.AlignCenter)
        self.label_64.setWordWrap(True)
        self.label_65 = QLabel(EnviarCotizacion)
        self.label_65.setObjectName(u"label_65")
        self.label_65.setGeometry(QRect(335, 170, 80, 80))
        self.label_65.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.label_65.setFrameShadow(QFrame.Plain)
        self.label_65.setText(u"")
        self.label_65.setPixmap(QPixmap(u":/img/resources/images/bill.png"))
        self.label_65.setScaledContents(True)
        self.label_65.setTextInteractionFlags(Qt.NoTextInteraction)
        self.btWhatsapp.raise_()
        self.frame.raise_()
        self.label_2.raise_()
        self.label_62.raise_()
        self.label_63.raise_()
        self.btTicket.raise_()
        self.label_64.raise_()
        self.label_65.raise_()

        self.retranslateUi(EnviarCotizacion)

        self.btWhatsapp.setDefault(True)
        self.btTicket.setDefault(True)


        QMetaObject.connectSlotsByName(EnviarCotizacion)
    # setupUi

    def retranslateUi(self, EnviarCotizacion):
        EnviarCotizacion.setWindowTitle(QCoreApplication.translate("EnviarCotizacion", u"Form", None))
        self.label.setText(QCoreApplication.translate("EnviarCotizacion", u"Cotizaci\u00f3n de venta", None))
        self.label_2.setText(QCoreApplication.translate("EnviarCotizacion", u"Seleccione una opci\u00f3n:", None))
        self.btWhatsapp.setText("")
        self.btTicket.setText("")
    # retranslateUi

