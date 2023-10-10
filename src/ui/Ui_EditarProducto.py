# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_EditarProducto.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QPlainTextEdit, QPushButton, QScrollArea, QSizePolicy,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)
from . import resources_rc

class Ui_EditarProducto(object):
    def setupUi(self, EditarProducto):
        if not EditarProducto.objectName():
            EditarProducto.setObjectName(u"EditarProducto")
        EditarProducto.resize(926, 733)
        self.verticalLayout_3 = QVBoxLayout(EditarProducto)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, -1)
        self.frame_4 = QFrame(EditarProducto)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setStyleSheet(u"QFrame { background-color: rgb(52, 172, 224); border: none}")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_4)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame_5 = QFrame(self.frame_4)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setMinimumSize(QSize(294, 63))
        self.frame_5.setMaximumSize(QSize(294, 63))
        self.frame_5.setStyleSheet(u"QFrame {border: none}")
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.btRegresar = QPushButton(self.frame_5)
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

        self.horizontalLayout_2.addWidget(self.btRegresar)

        self.lbTitulo = QLabel(self.frame_5)
        self.lbTitulo.setObjectName(u"lbTitulo")
        self.lbTitulo.setMinimumSize(QSize(211, 41))
        font = QFont()
        font.setPointSize(18)
        self.lbTitulo.setFont(font)
        self.lbTitulo.setStyleSheet(u"color: rgb(255, 255, 255);")

        self.horizontalLayout_2.addWidget(self.lbTitulo)


        self.horizontalLayout.addWidget(self.frame_5, 0, Qt.AlignLeft)


        self.verticalLayout_3.addWidget(self.frame_4)

        self.frame = QFrame(EditarProducto)
        self.frame.setObjectName(u"frame")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.horizontalLayout_3 = QHBoxLayout(self.frame)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.frame_2 = QFrame(self.frame)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setMinimumSize(QSize(451, 469))
        self.frame_2.setFrameShape(QFrame.Box)
        self.frame_2.setFrameShadow(QFrame.Plain)
        self.frame_2.setLineWidth(1)
        self.groupBox_3 = QGroupBox(self.frame_2)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(59, 210, 331, 101))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(11)
        self.groupBox_3.setFont(font1)
        self.txtDescripcion = QPlainTextEdit(self.groupBox_3)
        self.txtDescripcion.setObjectName(u"txtDescripcion")
        self.txtDescripcion.setGeometry(QRect(10, 30, 291, 61))
        self.txtDescripcion.setFont(font1)
        self.groupBox_4 = QGroupBox(self.frame_2)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setGeometry(QRect(125, 130, 201, 61))
        self.groupBox_4.setFont(font1)
        self.txtNombre = QLineEdit(self.groupBox_4)
        self.txtNombre.setObjectName(u"txtNombre")
        self.txtNombre.setGeometry(QRect(10, 30, 171, 20))
        self.txtNombre.setFont(font1)
        self.groupBox = QGroupBox(self.frame_2)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(30, 50, 391, 61))
        self.groupBox.setFont(font1)
        self.txtCodigo = QLineEdit(self.groupBox)
        self.txtCodigo.setObjectName(u"txtCodigo")
        self.txtCodigo.setGeometry(QRect(10, 30, 351, 20))
        self.txtCodigo.setFont(font1)
        self.label_3 = QLabel(self.frame_2)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 17, 431, 25))
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        font2.setPointSize(14)
        self.label_3.setFont(font2)
        self.label_3.setAlignment(Qt.AlignCenter)
        self.label = QLabel(self.frame_2)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 340, 431, 21))
        font3 = QFont()
        font3.setPointSize(14)
        self.label.setFont(font3)
        self.label.setAlignment(Qt.AlignCenter)
        self.tabWidget = QTabWidget(self.frame_2)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(60, 370, 361, 181))
        self.tabWidget.setDocumentMode(True)
        self.tab_simples = QWidget()
        self.tab_simples.setObjectName(u"tab_simples")
        self.tabla_precios = QTableWidget(self.tab_simples)
        if (self.tabla_precios.columnCount() < 3):
            self.tabla_precios.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.tabla_precios.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tabla_precios.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tabla_precios.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.tabla_precios.setObjectName(u"tabla_precios")
        self.tabla_precios.setGeometry(QRect(0, 0, 330, 141))
        font4 = QFont()
        font4.setFamilies([u"Segoe UI"])
        font4.setPointSize(10)
        self.tabla_precios.setFont(font4)
        self.tabla_precios.setStyleSheet(u"QHeaderView::section {\n"
"	font: bold 10pt;\n"
"	color: rgb(255, 255, 255);\n"
"	background-color: rgb(0, 170, 0);\n"
"\n"
"	padding: 7px;\n"
"}\n"
"\n"
"QTableWidget {\n"
"	alternate-background-color: rgb(240, 240, 240);\n"
"}\n"
"\n"
"QTableView {\n"
"    selection-background-color: rgb(85, 85, 255);\n"
"    selection-color: rgb(255, 255, 255);\n"
"}\n"
"QTableView:active {\n"
"    selection-background-color: rgb(85, 85, 255);\n"
"    selection-color: rgb(255, 255, 255);\n"
"}")
        self.tabla_precios.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tabla_precios.setAlternatingRowColors(True)
        self.tabla_precios.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla_precios.horizontalHeader().setMinimumSectionSize(20)
        self.tabla_precios.horizontalHeader().setStretchLastSection(True)
        self.tabla_precios.verticalHeader().setVisible(False)
        self.btAgregarIntervalo = QPushButton(self.tab_simples)
        self.btAgregarIntervalo.setObjectName(u"btAgregarIntervalo")
        self.btAgregarIntervalo.setGeometry(QRect(340, 40, 20, 20))
        font5 = QFont()
        font5.setFamilies([u"Segoe UI"])
        self.btAgregarIntervalo.setFont(font5)
        self.btAgregarIntervalo.setCursor(QCursor(Qt.PointingHandCursor))
        self.btAgregarIntervalo.setStyleSheet(u"QPushButton {\n"
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
        icon1.addFile(u":/img/resources/images/plus2.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btAgregarIntervalo.setIcon(icon1)
        self.btAgregarIntervalo.setIconSize(QSize(20, 20))
        self.btAgregarIntervalo.setFlat(True)
        self.btEliminarIntervalo = QPushButton(self.tab_simples)
        self.btEliminarIntervalo.setObjectName(u"btEliminarIntervalo")
        self.btEliminarIntervalo.setGeometry(QRect(340, 80, 20, 20))
        self.btEliminarIntervalo.setFont(font5)
        self.btEliminarIntervalo.setCursor(QCursor(Qt.PointingHandCursor))
        self.btEliminarIntervalo.setStyleSheet(u"QPushButton {\n"
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
        icon2 = QIcon()
        icon2.addFile(u":/img/resources/images/minus2.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btEliminarIntervalo.setIcon(icon2)
        self.btEliminarIntervalo.setIconSize(QSize(20, 20))
        self.btEliminarIntervalo.setFlat(True)
        self.tabWidget.addTab(self.tab_simples, "")
        self.tab_granformato = QWidget()
        self.tab_granformato.setObjectName(u"tab_granformato")
        self.label_5 = QLabel(self.tab_granformato)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(20, 38, 201, 16))
        self.label_5.setFont(font1)
        self.txtMinM2 = QLineEdit(self.tab_granformato)
        self.txtMinM2.setObjectName(u"txtMinM2")
        self.txtMinM2.setGeometry(QRect(232, 40, 91, 20))
        self.txtMinM2.setFont(font1)
        self.label_6 = QLabel(self.tab_granformato)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(20, 78, 181, 21))
        self.label_6.setFont(font1)
        self.txtPrecio = QLineEdit(self.tab_granformato)
        self.txtPrecio.setObjectName(u"txtPrecio")
        self.txtPrecio.setGeometry(QRect(210, 80, 113, 20))
        self.txtPrecio.setFont(font1)
        self.tabWidget.addTab(self.tab_granformato, "")

        self.horizontalLayout_3.addWidget(self.frame_2)

        self.frame_6 = QFrame(self.frame)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.Box)
        self.frame_6.setFrameShadow(QFrame.Plain)
        self.frame_6.setLineWidth(1)
        self.verticalLayout_2 = QVBoxLayout(self.frame_6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, 15, -1, 15)
        self.label_2 = QLabel(self.frame_6)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font3)
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_2)

        self.scrollArea = QScrollArea(self.frame_6)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaLista = QWidget()
        self.scrollAreaLista.setObjectName(u"scrollAreaLista")
        self.scrollAreaLista.setGeometry(QRect(0, 0, 431, 453))
        self.layoutScroll = QVBoxLayout(self.scrollAreaLista)
        self.layoutScroll.setObjectName(u"layoutScroll")
        self.layoutScroll.setContentsMargins(-1, -1, 0, -1)
        self.scrollArea.setWidget(self.scrollAreaLista)

        self.verticalLayout_2.addWidget(self.scrollArea)

        self.btAgregar = QPushButton(self.frame_6)
        self.btAgregar.setObjectName(u"btAgregar")
        self.btAgregar.setMinimumSize(QSize(160, 31))
        font6 = QFont()
        font6.setPointSize(10)
        self.btAgregar.setFont(font6)
        icon3 = QIcon()
        icon3.addFile(u":/img/resources/images/add.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btAgregar.setIcon(icon3)

        self.verticalLayout_2.addWidget(self.btAgregar, 0, Qt.AlignHCenter)


        self.horizontalLayout_3.addWidget(self.frame_6)


        self.verticalLayout_3.addWidget(self.frame)

        self.frame_3 = QFrame(EditarProducto)
        self.frame_3.setObjectName(u"frame_3")
        self.verticalLayout = QVBoxLayout(self.frame_3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.btAceptar = QPushButton(self.frame_3)
        self.btAceptar.setObjectName(u"btAceptar")
        self.btAceptar.setMinimumSize(QSize(170, 41))
        self.btAceptar.setFont(font1)
        self.btAceptar.setText(u" Aceptar cambios")
        icon4 = QIcon()
        icon4.addFile(u":/img/resources/images/edit.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btAceptar.setIcon(icon4)

        self.verticalLayout.addWidget(self.btAceptar, 0, Qt.AlignHCenter)


        self.verticalLayout_3.addWidget(self.frame_3)

        QWidget.setTabOrder(self.txtCodigo, self.txtNombre)
        QWidget.setTabOrder(self.txtNombre, self.txtDescripcion)
        QWidget.setTabOrder(self.txtDescripcion, self.tabWidget)
        QWidget.setTabOrder(self.tabWidget, self.tabla_precios)
        QWidget.setTabOrder(self.tabla_precios, self.scrollArea)
        QWidget.setTabOrder(self.scrollArea, self.btAgregar)
        QWidget.setTabOrder(self.btAgregar, self.btAceptar)
        QWidget.setTabOrder(self.btAceptar, self.btRegresar)
        QWidget.setTabOrder(self.btRegresar, self.btAgregarIntervalo)
        QWidget.setTabOrder(self.btAgregarIntervalo, self.btEliminarIntervalo)
        QWidget.setTabOrder(self.btEliminarIntervalo, self.txtMinM2)
        QWidget.setTabOrder(self.txtMinM2, self.txtPrecio)

        self.retranslateUi(EditarProducto)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(EditarProducto)
    # setupUi

    def retranslateUi(self, EditarProducto):
        EditarProducto.setWindowTitle(QCoreApplication.translate("EditarProducto", u"Form", None))
        self.lbTitulo.setText(QCoreApplication.translate("EditarProducto", u"Editar producto", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("EditarProducto", u"Descripci\u00f3n", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("EditarProducto", u"Nombre para tickets", None))
        self.txtNombre.setText("")
        self.txtNombre.setPlaceholderText(QCoreApplication.translate("EditarProducto", u"Impresi\u00f3n B/N", None))
        self.groupBox.setTitle(QCoreApplication.translate("EditarProducto", u"C\u00f3digo", None))
        self.txtCodigo.setText("")
        self.txtCodigo.setPlaceholderText(QCoreApplication.translate("EditarProducto", u"IMP. ByN 1-15", None))
        self.label_3.setText(QCoreApplication.translate("EditarProducto", u"Datos generales", None))
        self.label.setText(QCoreApplication.translate("EditarProducto", u"Precio del producto", None))
        ___qtablewidgetitem = self.tabla_precios.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("EditarProducto", u"A partir de", None));
        ___qtablewidgetitem1 = self.tabla_precios.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("EditarProducto", u"Cuesta", None));
        ___qtablewidgetitem2 = self.tabla_precios.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("EditarProducto", u"\u00bfEs precio d\u00faplex?", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_simples), QCoreApplication.translate("EditarProducto", u"Productos simples", None))
        self.label_5.setText(QCoreApplication.translate("EditarProducto", u"M\u00ednimo de metros cuadrados", None))
        self.label_6.setText(QCoreApplication.translate("EditarProducto", u"Precio del metro cuadrado", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_granformato), QCoreApplication.translate("EditarProducto", u"Gran formato", None))
        self.label_2.setText(QCoreApplication.translate("EditarProducto", u"Materia prima utilizada", None))
        self.btAgregar.setText(QCoreApplication.translate("EditarProducto", u"Agregar elemento", None))
    # retranslateUi

