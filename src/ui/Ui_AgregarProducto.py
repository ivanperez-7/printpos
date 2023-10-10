# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_AgregarProducto.ui'
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
    QLabel, QLineEdit, QPushButton, QRadioButton,
    QSizePolicy, QTabWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

from utils.mywidgets import TablaDatos
from . import resources_rc

class Ui_AgregarProducto(object):
    def setupUi(self, AgregarProducto):
        if not AgregarProducto.objectName():
            AgregarProducto.setObjectName(u"AgregarProducto")
        AgregarProducto.resize(951, 623)
        self.verticalLayout_5 = QVBoxLayout(AgregarProducto)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(AgregarProducto)
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
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(20, 15, 20, 15)
        self.btRegresar = QPushButton(self.frame_4)
        self.btRegresar.setObjectName(u"btRegresar")
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

        self.horizontalLayout.addWidget(self.btRegresar)

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

        self.frame_5 = QFrame(AgregarProducto)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_4.setSpacing(20)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(18, 15, 18, 8)
        self.frame_7 = QFrame(self.frame_5)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_7)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.btAgregar = QPushButton(self.frame_7)
        self.btAgregar.setObjectName(u"btAgregar")
        self.btAgregar.setMinimumSize(QSize(171, 31))
        font1 = QFont()
        font1.setPointSize(11)
        self.btAgregar.setFont(font1)
        icon1 = QIcon()
        icon1.addFile(u":/img/resources/images/accept.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btAgregar.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.btAgregar)


        self.horizontalLayout_4.addWidget(self.frame_7)

        self.frame_8 = QFrame(self.frame_5)
        self.frame_8.setObjectName(u"frame_8")
        sizePolicy.setHeightForWidth(self.frame_8.sizePolicy().hasHeightForWidth())
        self.frame_8.setSizePolicy(sizePolicy)
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_8)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.frame_8)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(51, 31))
        self.label_2.setMaximumSize(QSize(51, 31))
        self.label_2.setStyleSheet(u"image: url(:/img/resources/images/magnifier.png);\n"
"background-color: rgb(255, 255, 255);")

        self.horizontalLayout_3.addWidget(self.label_2)

        self.searchBar = QLineEdit(self.frame_8)
        self.searchBar.setObjectName(u"searchBar")
        self.searchBar.setMinimumSize(QSize(0, 31))
        self.searchBar.setMaximumSize(QSize(16777215, 31))
        self.searchBar.setFont(font1)
        self.searchBar.setFrame(False)

        self.horizontalLayout_3.addWidget(self.searchBar)


        self.horizontalLayout_4.addWidget(self.frame_8)

        self.btCodigo = QRadioButton(self.frame_5)
        self.groupFiltro = QButtonGroup(AgregarProducto)
        self.groupFiltro.setObjectName(u"groupFiltro")
        self.groupFiltro.addButton(self.btCodigo)
        self.btCodigo.setObjectName(u"btCodigo")
        font2 = QFont()
        font2.setPointSize(10)
        self.btCodigo.setFont(font2)
        self.btCodigo.setChecked(False)

        self.horizontalLayout_4.addWidget(self.btCodigo, 0, Qt.AlignRight)

        self.btDescripcion = QRadioButton(self.frame_5)
        self.groupFiltro.addButton(self.btDescripcion)
        self.btDescripcion.setObjectName(u"btDescripcion")
        self.btDescripcion.setFont(font2)
        self.btDescripcion.setChecked(True)

        self.horizontalLayout_4.addWidget(self.btDescripcion, 0, Qt.AlignRight)


        self.verticalLayout_5.addWidget(self.frame_5)

        self.frame_2 = QFrame(AgregarProducto)
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
        self.tabla_seleccionar.horizontalHeader().setMinimumSectionSize(80)

        self.verticalLayout.addWidget(self.tabla_seleccionar)

        self.frame_3 = QFrame(self.tab_productos)
        self.frame_3.setObjectName(u"frame_3")
        sizePolicy2.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy2)
        self.frame_3.setFont(font2)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.frame_3)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(20)
        self.gridLayout.setVerticalSpacing(12)
        self.gridLayout.setContentsMargins(-1, -1, 0, 5)
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

        self.groupBox_2 = QGroupBox(self.frame_3)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy2.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy2)
        self.groupBox_2.setMinimumSize(QSize(611, 61))
        self.groupBox_2.setFont(font1)
        self.txtNotas = QLineEdit(self.groupBox_2)
        self.txtNotas.setObjectName(u"txtNotas")
        self.txtNotas.setGeometry(QRect(10, 30, 571, 20))
        sizePolicy.setHeightForWidth(self.txtNotas.sizePolicy().hasHeightForWidth())
        self.txtNotas.setSizePolicy(sizePolicy)
        self.txtNotas.setFont(font1)
        self.txtNotas.setReadOnly(False)

        self.gridLayout.addWidget(self.groupBox_2, 0, 1, 1, 1, Qt.AlignLeft)

        self.checkDuplex = QCheckBox(self.frame_3)
        self.checkDuplex.setObjectName(u"checkDuplex")
        self.checkDuplex.setFont(font1)

        self.gridLayout.addWidget(self.checkDuplex, 1, 0, 1, 1)


        self.verticalLayout.addWidget(self.frame_3, 0, Qt.AlignBottom)

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
        self.tabla_granformato.horizontalHeader().setMinimumSectionSize(80)

        self.verticalLayout_4.addWidget(self.tabla_granformato)

        self.frame_6 = QFrame(self.tab_granformato)
        self.frame_6.setObjectName(u"frame_6")
        sizePolicy2.setHeightForWidth(self.frame_6.sizePolicy().hasHeightForWidth())
        self.frame_6.setSizePolicy(sizePolicy2)
        self.frame_6.setFont(font2)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.frame_6)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(20)
        self.gridLayout_2.setContentsMargins(-1, -1, 0, 12)
        self.groupBox_3 = QGroupBox(self.frame_6)
        self.groupBox_3.setObjectName(u"groupBox_3")
        sizePolicy2.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy2)
        self.groupBox_3.setMinimumSize(QSize(611, 61))
        self.groupBox_3.setFont(font1)
        self.txtNotas_2 = QLineEdit(self.groupBox_3)
        self.txtNotas_2.setObjectName(u"txtNotas_2")
        self.txtNotas_2.setGeometry(QRect(10, 30, 571, 20))
        sizePolicy.setHeightForWidth(self.txtNotas_2.sizePolicy().hasHeightForWidth())
        self.txtNotas_2.setSizePolicy(sizePolicy)
        self.txtNotas_2.setFont(font1)
        self.txtNotas_2.setReadOnly(False)

        self.gridLayout_2.addWidget(self.groupBox_3, 0, 1, 1, 1, Qt.AlignLeft|Qt.AlignTop)

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
        self.buttonGroup = QButtonGroup(AgregarProducto)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.btAnchoCm)
        self.btAnchoCm.setObjectName(u"btAnchoCm")
        self.btAnchoCm.setFont(font1)
        self.btAnchoCm.setChecked(False)
        self.btAnchoCm.setAutoExclusive(True)

        self.gridLayout_3.addWidget(self.btAnchoCm, 0, 2, 1, 1)

        self.btAnchoM = QRadioButton(self.groupBox_4)
        self.buttonGroup.addButton(self.btAnchoM)
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
        self.buttonGroup_2 = QButtonGroup(AgregarProducto)
        self.buttonGroup_2.setObjectName(u"buttonGroup_2")
        self.buttonGroup_2.addButton(self.btAltoCm)
        self.btAltoCm.setObjectName(u"btAltoCm")
        self.btAltoCm.setFont(font1)
        self.btAltoCm.setChecked(False)
        self.btAltoCm.setAutoExclusive(True)

        self.gridLayout_3.addWidget(self.btAltoCm, 1, 2, 1, 1)

        self.btAltoM = QRadioButton(self.groupBox_4)
        self.buttonGroup_2.addButton(self.btAltoM)
        self.btAltoM.setObjectName(u"btAltoM")
        self.btAltoM.setFont(font1)
        self.btAltoM.setChecked(True)
        self.btAltoM.setAutoExclusive(True)

        self.gridLayout_3.addWidget(self.btAltoM, 1, 3, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox_4, 0, 0, 1, 1)


        self.verticalLayout_4.addWidget(self.frame_6, 0, Qt.AlignBottom)

        self.tabWidget.addTab(self.tab_granformato, "")

        self.verticalLayout_3.addWidget(self.tabWidget)


        self.verticalLayout_5.addWidget(self.frame_2)

        QWidget.setTabOrder(self.searchBar, self.txtCantidad)
        QWidget.setTabOrder(self.txtCantidad, self.txtNotas)
        QWidget.setTabOrder(self.txtNotas, self.checkDuplex)
        QWidget.setTabOrder(self.checkDuplex, self.btAgregar)
        QWidget.setTabOrder(self.btAgregar, self.btCodigo)
        QWidget.setTabOrder(self.btCodigo, self.tabla_seleccionar)
        QWidget.setTabOrder(self.tabla_seleccionar, self.btDescripcion)
        QWidget.setTabOrder(self.btDescripcion, self.tabWidget)
        QWidget.setTabOrder(self.tabWidget, self.btRegresar)
        QWidget.setTabOrder(self.btRegresar, self.tabla_granformato)
        QWidget.setTabOrder(self.tabla_granformato, self.txtNotas_2)
        QWidget.setTabOrder(self.txtNotas_2, self.txtAncho)
        QWidget.setTabOrder(self.txtAncho, self.btAnchoCm)
        QWidget.setTabOrder(self.btAnchoCm, self.btAnchoM)
        QWidget.setTabOrder(self.btAnchoM, self.txtAlto)
        QWidget.setTabOrder(self.txtAlto, self.btAltoCm)
        QWidget.setTabOrder(self.btAltoCm, self.btAltoM)

        self.retranslateUi(AgregarProducto)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(AgregarProducto)
    # setupUi

    def retranslateUi(self, AgregarProducto):
        AgregarProducto.setWindowTitle(QCoreApplication.translate("AgregarProducto", u"Form", None))
        self.label.setText(QCoreApplication.translate("AgregarProducto", u"Agregar producto", None))
        self.btAgregar.setText(QCoreApplication.translate("AgregarProducto", u"Agregar a la venta", None))
        self.label_2.setText("")
        self.searchBar.setPlaceholderText(QCoreApplication.translate("AgregarProducto", u"Busque producto por descripci\u00f3n...", None))
        self.btCodigo.setText(QCoreApplication.translate("AgregarProducto", u"Por c\u00f3digo", None))
        self.btDescripcion.setText(QCoreApplication.translate("AgregarProducto", u"Por descripci\u00f3n", None))
        ___qtablewidgetitem = self.tabla_seleccionar.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("AgregarProducto", u"C\u00f3digo", None));
        ___qtablewidgetitem1 = self.tabla_seleccionar.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("AgregarProducto", u"Descripci\u00f3n", None));
        ___qtablewidgetitem2 = self.tabla_seleccionar.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("AgregarProducto", u"Precio", None));
        self.groupBox.setTitle(QCoreApplication.translate("AgregarProducto", u"Cantidad", None))
        self.txtCantidad.setPlaceholderText(QCoreApplication.translate("AgregarProducto", u"1", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("AgregarProducto", u"Especificaciones", None))
        self.txtNotas.setText("")
        self.checkDuplex.setText(QCoreApplication.translate("AgregarProducto", u"Producto a doble cara", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_productos), QCoreApplication.translate("AgregarProducto", u"Productos simples", None))
        ___qtablewidgetitem3 = self.tabla_granformato.horizontalHeaderItem(0)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("AgregarProducto", u"C\u00f3digo", None));
        ___qtablewidgetitem4 = self.tabla_granformato.horizontalHeaderItem(1)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("AgregarProducto", u"Descripci\u00f3n", None));
        ___qtablewidgetitem5 = self.tabla_granformato.horizontalHeaderItem(2)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("AgregarProducto", u"M\u00ednimo m\u00b2", None));
        ___qtablewidgetitem6 = self.tabla_granformato.horizontalHeaderItem(3)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("AgregarProducto", u"Precio (m\u00b2)", None));
        self.groupBox_3.setTitle(QCoreApplication.translate("AgregarProducto", u"Especificaciones", None))
        self.txtNotas_2.setText("")
        self.groupBox_4.setTitle(QCoreApplication.translate("AgregarProducto", u"Medidas", None))
        self.label_3.setText(QCoreApplication.translate("AgregarProducto", u"Ancho:", None))
        self.btAnchoCm.setText(QCoreApplication.translate("AgregarProducto", u"cm", None))
        self.btAnchoM.setText(QCoreApplication.translate("AgregarProducto", u"m", None))
        self.label_4.setText(QCoreApplication.translate("AgregarProducto", u"Alto:", None))
        self.btAltoCm.setText(QCoreApplication.translate("AgregarProducto", u"cm", None))
        self.btAltoM.setText(QCoreApplication.translate("AgregarProducto", u"m", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_granformato), QCoreApplication.translate("AgregarProducto", u"Gran formato", None))
    # retranslateUi

