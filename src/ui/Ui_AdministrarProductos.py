# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_AdministrarProductos.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QTableWidgetItem, QToolButton, QVBoxLayout,
    QWidget)

from utils.mywidgets import TablaDatos
from . import resources_rc

class Ui_AdministrarProductos(object):
    def setupUi(self, AdministrarProductos):
        if not AdministrarProductos.objectName():
            AdministrarProductos.setObjectName(u"AdministrarProductos")
        AdministrarProductos.resize(1085, 650)
        self.verticalLayout = QVBoxLayout(AdministrarProductos)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(AdministrarProductos)
        self.frame.setObjectName(u"frame")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        self.frame.setFont(font)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(19, 15, 19, 15)
        self.btRegresar = QPushButton(self.frame)
        self.btRegresar.setObjectName(u"btRegresar")
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
        icon = QIcon()
        icon.addFile(u":/img/resources/images/leftarrow.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btRegresar.setIcon(icon)
        self.btRegresar.setIconSize(QSize(40, 40))
        self.btRegresar.setFlat(True)

        self.horizontalLayout.addWidget(self.btRegresar)

        self.lbTitulo = QLabel(self.frame)
        self.lbTitulo.setObjectName(u"lbTitulo")
        self.lbTitulo.setMinimumSize(QSize(211, 41))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(18)
        self.lbTitulo.setFont(font1)

        self.horizontalLayout.addWidget(self.lbTitulo)


        self.verticalLayout.addWidget(self.frame, 0, Qt.AlignLeft)

        self.frame_3 = QFrame(AdministrarProductos)
        self.frame_3.setObjectName(u"frame_3")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setFont(font)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_3)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(8, -1, 8, -1)
        self.frame_2 = QFrame(self.frame_3)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFont(font)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_5 = QFrame(self.frame_2)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFont(font)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.btFiltrar = QToolButton(self.frame_5)
        self.btFiltrar.setObjectName(u"btFiltrar")
        self.btFiltrar.setMinimumSize(QSize(41, 31))
        self.btFiltrar.setFont(font)
        icon1 = QIcon()
        icon1.addFile(u":/img/resources/images/filter.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btFiltrar.setIcon(icon1)
        self.btFiltrar.setPopupMode(QToolButton.MenuButtonPopup)

        self.horizontalLayout_5.addWidget(self.btFiltrar)

        self.horizontalSpacer = QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer)

        self.label_2 = QLabel(self.frame_5)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(51, 31))
        self.label_2.setMaximumSize(QSize(51, 31))
        self.label_2.setFont(font)
        self.label_2.setStyleSheet(u"image: url(:/img/resources/images/magnifier.png);\n"
"background-color: rgb(255, 255, 255);")

        self.horizontalLayout_5.addWidget(self.label_2)

        self.searchBar = QLineEdit(self.frame_5)
        self.searchBar.setObjectName(u"searchBar")
        self.searchBar.setMinimumSize(QSize(481, 31))
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        font2.setPointSize(11)
        self.searchBar.setFont(font2)
        self.searchBar.setFrame(False)

        self.horizontalLayout_5.addWidget(self.searchBar)


        self.horizontalLayout_2.addWidget(self.frame_5)

        self.frame_6 = QFrame(self.frame_2)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFont(font)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_3.setSpacing(30)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.btAgregar = QPushButton(self.frame_6)
        self.btAgregar.setObjectName(u"btAgregar")
        self.btAgregar.setFont(font)
        self.btAgregar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btAgregar.setStyleSheet(u"QPushButton {\n"
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
        icon2.addFile(u":/img/resources/images/plus.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btAgregar.setIcon(icon2)
        self.btAgregar.setIconSize(QSize(40, 40))
        self.btAgregar.setFlat(True)

        self.horizontalLayout_3.addWidget(self.btAgregar)

        self.btEditar = QPushButton(self.frame_6)
        self.btEditar.setObjectName(u"btEditar")
        self.btEditar.setFont(font)
        self.btEditar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btEditar.setStyleSheet(u"QPushButton {\n"
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
        icon3 = QIcon()
        icon3.addFile(u":/img/resources/images/edit.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btEditar.setIcon(icon3)
        self.btEditar.setIconSize(QSize(40, 40))
        self.btEditar.setFlat(True)

        self.horizontalLayout_3.addWidget(self.btEditar)

        self.btEliminar = QPushButton(self.frame_6)
        self.btEliminar.setObjectName(u"btEliminar")
        self.btEliminar.setFont(font)
        self.btEliminar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btEliminar.setStyleSheet(u"QPushButton {\n"
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
        icon4 = QIcon()
        icon4.addFile(u":/img/resources/images/trash.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btEliminar.setIcon(icon4)
        self.btEliminar.setIconSize(QSize(40, 40))
        self.btEliminar.setFlat(True)

        self.horizontalLayout_3.addWidget(self.btEliminar)


        self.horizontalLayout_2.addWidget(self.frame_6)


        self.verticalLayout_3.addWidget(self.frame_2, 0, Qt.AlignTop)

        self.frame_7 = QFrame(self.frame_3)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setFont(font)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_7)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(-1, 0, -1, -1)
        self.tabla_productos = TablaDatos(self.frame_7)
        if (self.tabla_productos.columnCount() < 8):
            self.tabla_productos.setColumnCount(8)
        __qtablewidgetitem = QTableWidgetItem()
        self.tabla_productos.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tabla_productos.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tabla_productos.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tabla_productos.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tabla_productos.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tabla_productos.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tabla_productos.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tabla_productos.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        self.tabla_productos.setObjectName(u"tabla_productos")

        self.horizontalLayout_4.addWidget(self.tabla_productos)


        self.verticalLayout_3.addWidget(self.frame_7)


        self.verticalLayout.addWidget(self.frame_3)

        self.frame_4 = QFrame(AdministrarProductos)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFont(font)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(-1, 0, -1, 0)
        self.frame_8 = QFrame(self.frame_4)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setFont(font)
        self.frame_8.setStyleSheet(u"QFrame { border: none; }")
        self.frame_8.setFrameShape(QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_8)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.lbContador = QLabel(self.frame_8)
        self.lbContador.setObjectName(u"lbContador")
        self.lbContador.setMinimumSize(QSize(271, 21))
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(11)
        font3.setBold(True)
        self.lbContador.setFont(font3)

        self.verticalLayout_2.addWidget(self.lbContador)

        self.label_3 = QLabel(self.frame_8)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(561, 21))
        font4 = QFont()
        font4.setFamilies([u"Segoe UI"])
        font4.setPointSize(11)
        font4.setBold(False)
        self.label_3.setFont(font4)

        self.verticalLayout_2.addWidget(self.label_3)


        self.horizontalLayout_6.addWidget(self.frame_8)


        self.verticalLayout.addWidget(self.frame_4)


        self.retranslateUi(AdministrarProductos)

        QMetaObject.connectSlotsByName(AdministrarProductos)
    # setupUi

    def retranslateUi(self, AdministrarProductos):
        AdministrarProductos.setWindowTitle(QCoreApplication.translate("AdministrarProductos", u"Form", None))
        self.lbTitulo.setText(QCoreApplication.translate("AdministrarProductos", u"Administrar productos", None))
#if QT_CONFIG(tooltip)
        self.btFiltrar.setToolTip(QCoreApplication.translate("AdministrarProductos", u"Filtrar b\u00fasqueda por...", None))
#endif // QT_CONFIG(tooltip)
        self.btFiltrar.setText(QCoreApplication.translate("AdministrarProductos", u"...", None))
        self.label_2.setText("")
        self.searchBar.setPlaceholderText(QCoreApplication.translate("AdministrarProductos", u"Busque producto por c\u00f3digo...", None))
        ___qtablewidgetitem = self.tabla_productos.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("AdministrarProductos", u"ID", None));
        ___qtablewidgetitem1 = self.tabla_productos.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("AdministrarProductos", u"C\u00f3digo", None));
        ___qtablewidgetitem2 = self.tabla_productos.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("AdministrarProductos", u"Descripci\u00f3n", None));
        ___qtablewidgetitem3 = self.tabla_productos.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("AdministrarProductos", u"Nombre para tickets y notas", None));
        ___qtablewidgetitem4 = self.tabla_productos.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("AdministrarProductos", u"Precio con I.V.A.", None));
        ___qtablewidgetitem5 = self.tabla_productos.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("AdministrarProductos", u"Precio sin I.V.A.", None));
        ___qtablewidgetitem6 = self.tabla_productos.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("AdministrarProductos", u"Costo de producci\u00f3n", None));
        ___qtablewidgetitem7 = self.tabla_productos.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("AdministrarProductos", u"Utilidad", None));
        self.lbContador.setText(QCoreApplication.translate("AdministrarProductos", u"0 productos en la base de datos.", None))
        self.label_3.setText(QCoreApplication.translate("AdministrarProductos", u"Haga doble click en alguno de los productos para consultar detalles.", None))
    # retranslateUi

