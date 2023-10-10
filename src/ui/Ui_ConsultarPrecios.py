# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_ConsultarPrecios.ui'
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
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QRadioButton, QSizePolicy,
    QSpacerItem, QTabWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

from utils.mywidgets import TablaDatos
from . import resources_rc
from . import resources_rc

class Ui_ConsultarPrecios(object):
    def setupUi(self, ConsultarPrecios):
        if not ConsultarPrecios.objectName():
            ConsultarPrecios.setObjectName(u"ConsultarPrecios")
        ConsultarPrecios.resize(1066, 640)
        icon = QIcon()
        icon.addFile(u":/img/icon.ico", QSize(), QIcon.Normal, QIcon.Off)
        ConsultarPrecios.setWindowIcon(icon)
        self.verticalLayout_5 = QVBoxLayout(ConsultarPrecios)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(ConsultarPrecios)
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
        self.horizontalLayout.setContentsMargins(18, 18, 18, 18)
        self.label_5 = QLabel(self.frame_4)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(41, 41))
        self.label_5.setMaximumSize(QSize(41, 41))
        self.label_5.setCursor(QCursor(Qt.PointingHandCursor))
        self.label_5.setStyleSheet(u"")
        self.label_5.setPixmap(QPixmap(u":/img/resources/images/package.png"))
        self.label_5.setScaledContents(True)

        self.horizontalLayout.addWidget(self.label_5)

        self.label = QLabel(self.frame_4)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(201, 41))
        font = QFont()
        font.setPointSize(18)
        self.label.setFont(font)
        self.label.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.horizontalLayout.addWidget(self.label)


        self.verticalLayout_2.addWidget(self.frame_4)


        self.verticalLayout_5.addWidget(self.frame)

        self.frame_5 = QFrame(ConsultarPrecios)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(18, 20, -1, 10)
        self.label_2 = QLabel(self.frame_5)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(51, 31))
        self.label_2.setMaximumSize(QSize(51, 31))
        self.label_2.setStyleSheet(u"image: url(:/img/resources/images/magnifier.png);\n"
"background-color: rgb(255, 255, 255);")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.searchBar = QLineEdit(self.frame_5)
        self.searchBar.setObjectName(u"searchBar")
        self.searchBar.setMinimumSize(QSize(500, 31))
        self.searchBar.setMaximumSize(QSize(500, 31))
        font1 = QFont()
        font1.setPointSize(11)
        self.searchBar.setFont(font1)
        self.searchBar.setFrame(False)

        self.horizontalLayout_2.addWidget(self.searchBar)

        self.horizontalSpacer = QSpacerItem(25, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.btCodigo = QRadioButton(self.frame_5)
        self.groupButtonFiltro = QButtonGroup(ConsultarPrecios)
        self.groupButtonFiltro.setObjectName(u"groupButtonFiltro")
        self.groupButtonFiltro.addButton(self.btCodigo)
        self.btCodigo.setObjectName(u"btCodigo")
        font2 = QFont()
        font2.setPointSize(10)
        self.btCodigo.setFont(font2)
        self.btCodigo.setChecked(False)

        self.horizontalLayout_2.addWidget(self.btCodigo)

        self.horizontalSpacer_2 = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.btDescripcion = QRadioButton(self.frame_5)
        self.groupButtonFiltro.addButton(self.btDescripcion)
        self.btDescripcion.setObjectName(u"btDescripcion")
        self.btDescripcion.setFont(font2)
        self.btDescripcion.setChecked(True)

        self.horizontalLayout_2.addWidget(self.btDescripcion)


        self.verticalLayout_5.addWidget(self.frame_5, 0, Qt.AlignHCenter)

        self.frame_2 = QFrame(ConsultarPrecios)
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
        self.verticalLayout_3.setContentsMargins(18, -1, 18, 0)
        self.tabWidget = QTabWidget(self.frame_2)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setFont(font2)
        self.tabWidget.setDocumentMode(True)
        self.tab_productos = QWidget()
        self.tab_productos.setObjectName(u"tab_productos")
        self.verticalLayout = QVBoxLayout(self.tab_productos)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, -1, 0, -1)
        self.tabla_seleccionar = TablaDatos(self.tab_productos)
        if (self.tabla_seleccionar.columnCount() < 3):
            self.tabla_seleccionar.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.tabla_seleccionar.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tabla_seleccionar.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tabla_seleccionar.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.tabla_seleccionar.setObjectName(u"tabla_seleccionar")
        self.tabla_seleccionar.setMinimumSize(QSize(0, 301))

        self.verticalLayout.addWidget(self.tabla_seleccionar)

        self.frame_3 = QFrame(self.tab_productos)
        self.frame_3.setObjectName(u"frame_3")
        sizePolicy2.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy2)
        self.frame_3.setFont(font2)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.frame_3)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(90)
        self.gridLayout.setVerticalSpacing(10)
        self.groupBox = QGroupBox(self.frame_3)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy3 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy3)
        self.groupBox.setMinimumSize(QSize(191, 61))
        self.groupBox.setFont(font1)
        self.txtCantidad = QLineEdit(self.groupBox)
        self.txtCantidad.setObjectName(u"txtCantidad")
        self.txtCantidad.setGeometry(QRect(10, 30, 151, 20))
        self.txtCantidad.setFont(font1)
        self.txtCantidad.setReadOnly(False)

        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.checkDuplex = QCheckBox(self.frame_3)
        self.checkDuplex.setObjectName(u"checkDuplex")
        self.checkDuplex.setFont(font1)

        self.gridLayout.addWidget(self.checkDuplex, 1, 0, 1, 1)

        self.lbTotalSimple = QLabel(self.frame_3)
        self.lbTotalSimple.setObjectName(u"lbTotalSimple")
        self.lbTotalSimple.setMinimumSize(QSize(0, 40))
        self.lbTotalSimple.setFont(font)

        self.gridLayout.addWidget(self.lbTotalSimple, 0, 1, 2, 1)


        self.verticalLayout.addWidget(self.frame_3, 0, Qt.AlignLeft|Qt.AlignBottom)

        self.tabWidget.addTab(self.tab_productos, "")
        self.tab_granformato = QWidget()
        self.tab_granformato.setObjectName(u"tab_granformato")
        self.verticalLayout_4 = QVBoxLayout(self.tab_granformato)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, -1, 0, -1)
        self.tabla_granformato = TablaDatos(self.tab_granformato)
        if (self.tabla_granformato.columnCount() < 4):
            self.tabla_granformato.setColumnCount(4)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tabla_granformato.setHorizontalHeaderItem(0, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tabla_granformato.setHorizontalHeaderItem(1, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tabla_granformato.setHorizontalHeaderItem(2, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tabla_granformato.setHorizontalHeaderItem(3, __qtablewidgetitem6)
        self.tabla_granformato.setObjectName(u"tabla_granformato")
        self.tabla_granformato.setMinimumSize(QSize(0, 301))

        self.verticalLayout_4.addWidget(self.tabla_granformato)

        self.frame_6 = QFrame(self.tab_granformato)
        self.frame_6.setObjectName(u"frame_6")
        sizePolicy2.setHeightForWidth(self.frame_6.sizePolicy().hasHeightForWidth())
        self.frame_6.setSizePolicy(sizePolicy2)
        self.frame_6.setFont(font2)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.frame_6)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(90)
        self.gridLayout_2.setContentsMargins(-1, -1, 0, 5)
        self.groupBox_4 = QGroupBox(self.frame_6)
        self.groupBox_4.setObjectName(u"groupBox_4")
        sizePolicy3.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy3)
        self.groupBox_4.setMinimumSize(QSize(245, 89))
        self.groupBox_4.setFont(font1)
        self.gridLayout_3 = QGridLayout(self.groupBox_4)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_3 = QLabel(self.groupBox_4)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font1)

        self.gridLayout_3.addWidget(self.label_3, 0, 0, 1, 1)

        self.txtAncho = QLineEdit(self.groupBox_4)
        self.txtAncho.setObjectName(u"txtAncho")
        self.txtAncho.setFont(font1)

        self.gridLayout_3.addWidget(self.txtAncho, 0, 1, 1, 1)

        self.btAnchoCm = QRadioButton(self.groupBox_4)
        self.groupButtonAncho = QButtonGroup(ConsultarPrecios)
        self.groupButtonAncho.setObjectName(u"groupButtonAncho")
        self.groupButtonAncho.addButton(self.btAnchoCm)
        self.btAnchoCm.setObjectName(u"btAnchoCm")
        self.btAnchoCm.setFont(font1)
        self.btAnchoCm.setChecked(False)
        self.btAnchoCm.setAutoExclusive(True)

        self.gridLayout_3.addWidget(self.btAnchoCm, 0, 2, 1, 1)

        self.btAnchoM = QRadioButton(self.groupBox_4)
        self.groupButtonAncho.addButton(self.btAnchoM)
        self.btAnchoM.setObjectName(u"btAnchoM")
        self.btAnchoM.setFont(font1)
        self.btAnchoM.setChecked(True)
        self.btAnchoM.setAutoExclusive(True)

        self.gridLayout_3.addWidget(self.btAnchoM, 0, 3, 1, 1)

        self.label_4 = QLabel(self.groupBox_4)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font1)

        self.gridLayout_3.addWidget(self.label_4, 1, 0, 1, 1)

        self.txtAlto = QLineEdit(self.groupBox_4)
        self.txtAlto.setObjectName(u"txtAlto")
        self.txtAlto.setFont(font1)

        self.gridLayout_3.addWidget(self.txtAlto, 1, 1, 1, 1)

        self.btAltoCm = QRadioButton(self.groupBox_4)
        self.groupButtonAlto = QButtonGroup(ConsultarPrecios)
        self.groupButtonAlto.setObjectName(u"groupButtonAlto")
        self.groupButtonAlto.addButton(self.btAltoCm)
        self.btAltoCm.setObjectName(u"btAltoCm")
        self.btAltoCm.setFont(font1)
        self.btAltoCm.setChecked(False)
        self.btAltoCm.setAutoExclusive(True)

        self.gridLayout_3.addWidget(self.btAltoCm, 1, 2, 1, 1)

        self.btAltoM = QRadioButton(self.groupBox_4)
        self.groupButtonAlto.addButton(self.btAltoM)
        self.btAltoM.setObjectName(u"btAltoM")
        self.btAltoM.setFont(font1)
        self.btAltoM.setChecked(True)
        self.btAltoM.setAutoExclusive(True)

        self.gridLayout_3.addWidget(self.btAltoM, 1, 3, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox_4, 0, 0, 1, 1)

        self.lbTotalGranFormato = QLabel(self.frame_6)
        self.lbTotalGranFormato.setObjectName(u"lbTotalGranFormato")
        self.lbTotalGranFormato.setMinimumSize(QSize(0, 40))
        self.lbTotalGranFormato.setMaximumSize(QSize(16777215, 40))
        self.lbTotalGranFormato.setFont(font)

        self.gridLayout_2.addWidget(self.lbTotalGranFormato, 0, 1, 1, 1)


        self.verticalLayout_4.addWidget(self.frame_6, 0, Qt.AlignLeft|Qt.AlignBottom)

        self.tabWidget.addTab(self.tab_granformato, "")

        self.verticalLayout_3.addWidget(self.tabWidget)


        self.verticalLayout_5.addWidget(self.frame_2)


        self.retranslateUi(ConsultarPrecios)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ConsultarPrecios)
    # setupUi

    def retranslateUi(self, ConsultarPrecios):
        ConsultarPrecios.setWindowTitle(QCoreApplication.translate("ConsultarPrecios", u"Consultar precios", None))
        self.label.setText(QCoreApplication.translate("ConsultarPrecios", u"Consultar precios", None))
        self.label_2.setText("")
        self.searchBar.setPlaceholderText(QCoreApplication.translate("ConsultarPrecios", u"Busque producto por descripci\u00f3n...", None))
        self.btCodigo.setText(QCoreApplication.translate("ConsultarPrecios", u"Por c\u00f3digo", None))
        self.btDescripcion.setText(QCoreApplication.translate("ConsultarPrecios", u"Por descripci\u00f3n", None))
        ___qtablewidgetitem = self.tabla_seleccionar.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("ConsultarPrecios", u"C\u00f3digo", None));
        ___qtablewidgetitem1 = self.tabla_seleccionar.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("ConsultarPrecios", u"Descripci\u00f3n", None));
        ___qtablewidgetitem2 = self.tabla_seleccionar.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("ConsultarPrecios", u"Precio", None));
        self.groupBox.setTitle(QCoreApplication.translate("ConsultarPrecios", u"Cantidad", None))
        self.txtCantidad.setPlaceholderText(QCoreApplication.translate("ConsultarPrecios", u"1", None))
        self.checkDuplex.setText(QCoreApplication.translate("ConsultarPrecios", u"Producto a doble cara", None))
        self.lbTotalSimple.setText(QCoreApplication.translate("ConsultarPrecios", u"Total: $0.00", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_productos), QCoreApplication.translate("ConsultarPrecios", u"Productos simples", None))
        ___qtablewidgetitem3 = self.tabla_granformato.horizontalHeaderItem(0)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("ConsultarPrecios", u"C\u00f3digo", None));
        ___qtablewidgetitem4 = self.tabla_granformato.horizontalHeaderItem(1)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("ConsultarPrecios", u"Descripci\u00f3n", None));
        ___qtablewidgetitem5 = self.tabla_granformato.horizontalHeaderItem(2)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("ConsultarPrecios", u"M\u00ednimo m\u00b2", None));
        ___qtablewidgetitem6 = self.tabla_granformato.horizontalHeaderItem(3)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("ConsultarPrecios", u"Precio (m\u00b2)", None));
        self.groupBox_4.setTitle(QCoreApplication.translate("ConsultarPrecios", u"Medidas", None))
        self.label_3.setText(QCoreApplication.translate("ConsultarPrecios", u"Ancho:", None))
        self.btAnchoCm.setText(QCoreApplication.translate("ConsultarPrecios", u"cm", None))
        self.btAnchoM.setText(QCoreApplication.translate("ConsultarPrecios", u"m", None))
        self.label_4.setText(QCoreApplication.translate("ConsultarPrecios", u"Alto:", None))
        self.btAltoCm.setText(QCoreApplication.translate("ConsultarPrecios", u"cm", None))
        self.btAltoM.setText(QCoreApplication.translate("ConsultarPrecios", u"m", None))
        self.lbTotalGranFormato.setText(QCoreApplication.translate("ConsultarPrecios", u"Total: $0.00", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_granformato), QCoreApplication.translate("ConsultarPrecios", u"Gran formato", None))
    # retranslateUi

