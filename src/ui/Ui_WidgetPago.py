# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_WidgetPago.ui'
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
from PySide6.QtWidgets import (QApplication, QButtonGroup, QFrame, QGridLayout,
    QLabel, QRadioButton, QSizePolicy, QWidget)

from utils.mywidgets import NumberEdit

class Ui_WidgetPago(object):
    def setupUi(self, WidgetPago):
        if not WidgetPago.objectName():
            WidgetPago.setObjectName(u"WidgetPago")
        WidgetPago.resize(441, 139)
        self.gridLayout = QGridLayout(WidgetPago)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(60, -1, -1, 0)
        self.label_13 = QLabel(WidgetPago)
        self.label_13.setObjectName(u"label_13")
        font = QFont()
        font.setPointSize(14)
        self.label_13.setFont(font)

        self.gridLayout.addWidget(self.label_13, 0, 0, 1, 1)

        self.lbCambio = QLabel(WidgetPago)
        self.lbCambio.setObjectName(u"lbCambio")
        font1 = QFont()
        font1.setPointSize(15)
        self.lbCambio.setFont(font1)
        self.lbCambio.setStyleSheet(u"color: rgb(249, 0, 0);")
        self.lbCambio.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.lbCambio, 1, 2, 1, 1)

        self.frame_9 = QFrame(WidgetPago)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setMaximumSize(QSize(469, 62))
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        self.frame_9.setFont(font2)
        self.gridLayout_2 = QGridLayout(self.frame_9)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(20)
        self.gridLayout_2.setContentsMargins(-1, 12, -1, -1)
        self.radioButton = QRadioButton(self.frame_9)
        self.buttonGroup = QButtonGroup(WidgetPago)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.radioButton)
        self.radioButton.setObjectName(u"radioButton")
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(11)
        self.radioButton.setFont(font3)
        self.radioButton.setChecked(True)

        self.gridLayout_2.addWidget(self.radioButton, 0, 0, 1, 1)

        self.radioButton_2 = QRadioButton(self.frame_9)
        self.buttonGroup.addButton(self.radioButton_2)
        self.radioButton_2.setObjectName(u"radioButton_2")
        self.radioButton_2.setFont(font3)

        self.gridLayout_2.addWidget(self.radioButton_2, 0, 1, 1, 1)

        self.radioButton_4 = QRadioButton(self.frame_9)
        self.buttonGroup.addButton(self.radioButton_4)
        self.radioButton_4.setObjectName(u"radioButton_4")
        self.radioButton_4.setMinimumSize(QSize(0, 22))
        self.radioButton_4.setFont(font3)

        self.gridLayout_2.addWidget(self.radioButton_4, 1, 0, 1, 1)

        self.radioButton_3 = QRadioButton(self.frame_9)
        self.buttonGroup.addButton(self.radioButton_3)
        self.radioButton_3.setObjectName(u"radioButton_3")
        self.radioButton_3.setMinimumSize(QSize(0, 22))
        self.radioButton_3.setFont(font3)

        self.gridLayout_2.addWidget(self.radioButton_3, 1, 1, 1, 1)


        self.gridLayout.addWidget(self.frame_9, 2, 0, 1, 3)

        self.txtPago = NumberEdit(WidgetPago)
        self.txtPago.setObjectName(u"txtPago")
        self.txtPago.setMinimumSize(QSize(200, 28))
        self.txtPago.setMaximumSize(QSize(16777215, 28))
        self.txtPago.setStyleSheet(u"color: rgb(0, 170, 255)")

        self.gridLayout.addWidget(self.txtPago, 0, 2, 1, 1)

        self.label_19 = QLabel(WidgetPago)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setMinimumSize(QSize(0, 28))
        self.label_19.setFont(font1)

        self.gridLayout.addWidget(self.label_19, 0, 1, 1, 1)

        self.label_25 = QLabel(WidgetPago)
        self.label_25.setObjectName(u"label_25")
        self.label_25.setMinimumSize(QSize(0, 28))
        self.label_25.setFont(font1)
        self.label_25.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label_25, 1, 1, 1, 1)

        self.label_26 = QLabel(WidgetPago)
        self.label_26.setObjectName(u"label_26")
        self.label_26.setFont(font)

        self.gridLayout.addWidget(self.label_26, 1, 0, 1, 1)


        self.retranslateUi(WidgetPago)

        QMetaObject.connectSlotsByName(WidgetPago)
    # setupUi

    def retranslateUi(self, WidgetPago):
        self.label_13.setText(QCoreApplication.translate("WidgetPago", u"Cantidad recibida", None))
        self.lbCambio.setText(QCoreApplication.translate("WidgetPago", u"0.00", None))
        self.radioButton.setText(QCoreApplication.translate("WidgetPago", u"Efectivo", None))
        self.radioButton_2.setText(QCoreApplication.translate("WidgetPago", u"Tarjeta de cr\u00e9dito", None))
        self.radioButton_4.setText(QCoreApplication.translate("WidgetPago", u"Tarjeta de d\u00e9bito", None))
        self.radioButton_3.setText(QCoreApplication.translate("WidgetPago", u"Transferencia bancaria", None))
        self.label_19.setText(QCoreApplication.translate("WidgetPago", u"$", None))
        self.label_25.setText(QCoreApplication.translate("WidgetPago", u"$", None))
        self.label_26.setText(QCoreApplication.translate("WidgetPago", u"Cambio", None))
        pass
    # retranslateUi

