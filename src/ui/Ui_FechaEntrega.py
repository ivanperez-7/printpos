# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_FechaEntrega.ui'
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
from PySide6.QtWidgets import (QApplication, QCalendarWidget, QFrame, QLabel,
    QPushButton, QSizePolicy, QTimeEdit, QWidget)
from . import resources_rc

class Ui_FechaEntrega(object):
    def setupUi(self, FechaEntrega):
        if not FechaEntrega.objectName():
            FechaEntrega.setObjectName(u"FechaEntrega")
        FechaEntrega.setWindowModality(Qt.ApplicationModal)
        FechaEntrega.resize(420, 414)
        self.frame = QFrame(FechaEntrega)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(0, 0, 421, 81))
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
        icon = QIcon()
        icon.addFile(u":/img/resources/images/leftarrow.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btRegresar.setIcon(icon)
        self.btRegresar.setIconSize(QSize(40, 40))
        self.btRegresar.setFlat(True)
        self.btListo = QPushButton(FechaEntrega)
        self.btListo.setObjectName(u"btListo")
        self.btListo.setGeometry(QRect(280, 360, 111, 31))
        font1 = QFont()
        font1.setPointSize(11)
        self.btListo.setFont(font1)
        icon1 = QIcon()
        icon1.addFile(u":/img/resources/images/accept.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btListo.setIcon(icon1)
        self.calendario = QCalendarWidget(FechaEntrega)
        self.calendario.setObjectName(u"calendario")
        self.calendario.setGeometry(QRect(30, 110, 361, 221))
        self.calendario.setFont(font1)
        self.calendario.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.horaEdit = QTimeEdit(FechaEntrega)
        self.horaEdit.setObjectName(u"horaEdit")
        self.horaEdit.setGeometry(QRect(30, 360, 121, 31))
        self.horaEdit.setFont(font1)
        self.horaEdit.setAlignment(Qt.AlignCenter)
        self.horaEdit.setDisplayFormat(u"h:mm ap")
        self.btListo.raise_()
        self.frame.raise_()
        self.calendario.raise_()
        self.horaEdit.raise_()
        QWidget.setTabOrder(self.calendario, self.horaEdit)
        QWidget.setTabOrder(self.horaEdit, self.btListo)
        QWidget.setTabOrder(self.btListo, self.btRegresar)

        self.retranslateUi(FechaEntrega)

        QMetaObject.connectSlotsByName(FechaEntrega)
    # setupUi

    def retranslateUi(self, FechaEntrega):
        FechaEntrega.setWindowTitle(QCoreApplication.translate("FechaEntrega", u"Form", None))
        self.label.setText(QCoreApplication.translate("FechaEntrega", u"Fecha y hora de entrega", None))
        self.btListo.setText(QCoreApplication.translate("FechaEntrega", u"Listo", None))
    # retranslateUi

