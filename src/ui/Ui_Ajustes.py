# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_Ajustes.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QSizePolicy, QTabWidget, QVBoxLayout, QWidget)
from . import resources_rc

class Ui_Ajustes(object):
    def setupUi(self, Ajustes):
        if not Ajustes.objectName():
            Ajustes.setObjectName(u"Ajustes")
        Ajustes.resize(1181, 685)
        self.verticalLayout = QVBoxLayout(Ajustes)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(Ajustes)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"QFrame { border: none; }")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(19, 19, -1, -1)
        self.lbRegresar = QLabel(self.frame)
        self.lbRegresar.setObjectName(u"lbRegresar")
        self.lbRegresar.setMinimumSize(QSize(41, 41))
        self.lbRegresar.setCursor(QCursor(Qt.PointingHandCursor))
        self.lbRegresar.setStyleSheet(u"image: url(:/img/resources/images/leftarrow.png);")

        self.horizontalLayout.addWidget(self.lbRegresar)

        self.lbTitulo = QLabel(self.frame)
        self.lbTitulo.setObjectName(u"lbTitulo")
        self.lbTitulo.setMinimumSize(QSize(321, 41))
        font = QFont()
        font.setPointSize(18)
        self.lbTitulo.setFont(font)

        self.horizontalLayout.addWidget(self.lbTitulo)


        self.verticalLayout.addWidget(self.frame, 0, Qt.AlignLeft)

        self.frame_2 = QFrame(Ajustes)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(18, -1, 18, 18)
        self.tabWidget = QTabWidget(self.frame_2)
        self.tabWidget.setObjectName(u"tabWidget")
        font1 = QFont()
        font1.setPointSize(11)
        self.tabWidget.setFont(font1)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.tabWidget.addTab(self.tab, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.tabWidget.addTab(self.tab_4, "")
        self.tab_5 = QWidget()
        self.tab_5.setObjectName(u"tab_5")
        self.tabWidget.addTab(self.tab_5, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.tabWidget.addTab(self.tab_2, "")

        self.horizontalLayout_2.addWidget(self.tabWidget)


        self.verticalLayout.addWidget(self.frame_2)


        self.retranslateUi(Ajustes)

        QMetaObject.connectSlotsByName(Ajustes)
    # setupUi

    def retranslateUi(self, Ajustes):
        Ajustes.setWindowTitle(QCoreApplication.translate("Ajustes", u"Form", None))
#if QT_CONFIG(tooltip)
        self.lbRegresar.setToolTip(QCoreApplication.translate("Ajustes", u"Regresar al men\u00fa de inicio", None))
#endif // QT_CONFIG(tooltip)
        self.lbRegresar.setText("")
        self.lbTitulo.setText(QCoreApplication.translate("Ajustes", u"Ajustes del sistema", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Ajustes", u"Tab 1", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("Ajustes", u"Page", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("Ajustes", u"Page", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), QCoreApplication.translate("Ajustes", u"Page", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("Ajustes", u"Tab 2", None))
    # retranslateUi

