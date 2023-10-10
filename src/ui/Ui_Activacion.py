# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_Activacion.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QWidget)
from . import resources_rc

class Ui_Activacion(object):
    def setupUi(self, Activacion):
        if not Activacion.objectName():
            Activacion.setObjectName(u"Activacion")
        Activacion.setWindowModality(Qt.ApplicationModal)
        Activacion.resize(491, 330)
        icon = QIcon()
        icon.addFile(u":/img/icon.ico", QSize(), QIcon.Normal, QIcon.Off)
        Activacion.setWindowIcon(icon)
        self.frame = QFrame(Activacion)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(0, 0, 541, 81))
        self.frame.setStyleSheet(u"background-color: rgb(52, 172, 224);")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(140, 20, 321, 41))
        font = QFont()
        font.setPointSize(18)
        self.label.setFont(font)
        self.label.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_3 = QLabel(self.frame)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(25, 15, 60, 60))
        self.label_3.setPixmap(QPixmap(u":/img/resources/images/key-set.png"))
        self.label_3.setScaledContents(True)
        self.label_2 = QLabel(Activacion)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(40, 100, 411, 51))
        font1 = QFont()
        font1.setPointSize(12)
        self.label_2.setFont(font1)
        self.label_2.setWordWrap(True)
        self.lineLicencia = QLineEdit(Activacion)
        self.lineLicencia.setObjectName(u"lineLicencia")
        self.lineLicencia.setGeometry(QRect(70, 210, 351, 31))
        font2 = QFont()
        font2.setPointSize(11)
        self.lineLicencia.setFont(font2)
        self.lineLicencia.setAlignment(Qt.AlignCenter)
        self.btActivar = QPushButton(Activacion)
        self.btActivar.setObjectName(u"btActivar")
        self.btActivar.setGeometry(QRect(260, 280, 75, 24))
        self.btCerrar = QPushButton(Activacion)
        self.btCerrar.setObjectName(u"btCerrar")
        self.btCerrar.setGeometry(QRect(160, 280, 75, 24))
        self.label_4 = QLabel(Activacion)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(40, 165, 411, 31))
        self.label_4.setFont(font1)
        self.label_4.setWordWrap(True)

        self.retranslateUi(Activacion)

        QMetaObject.connectSlotsByName(Activacion)
    # setupUi

    def retranslateUi(self, Activacion):
        Activacion.setWindowTitle(QCoreApplication.translate("Activacion", u"Form", None))
        self.label.setText(QCoreApplication.translate("Activacion", u"\u00a1PrintPOS no est\u00e1 activado!", None))
        self.label_3.setText("")
        self.label_2.setText(QCoreApplication.translate("Activacion", u"Para tener acceso a PrintPOS, debe adquirir una licencia de activaci\u00f3n con la duraci\u00f3n que m\u00e1s le convenga. ", None))
        self.lineLicencia.setText("")
        self.btActivar.setText(QCoreApplication.translate("Activacion", u"Activar", None))
        self.btCerrar.setText(QCoreApplication.translate("Activacion", u"Cerrar", None))
        self.label_4.setText(QCoreApplication.translate("Activacion", u"Al tenerla, por favor ingr\u00e9sela en el siguiente recuadro.", None))
    # retranslateUi

