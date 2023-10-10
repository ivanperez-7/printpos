# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_AdministrarVentas.ui'
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
from PySide6.QtWidgets import (QApplication, QDateEdit, QFrame, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
    QTableWidgetItem, QToolButton, QVBoxLayout, QWidget)

from utils.mywidgets import TablaDatos
from . import resources_rc

class Ui_AdministrarVentas(object):
    def setupUi(self, AdministrarVentas):
        if not AdministrarVentas.objectName():
            AdministrarVentas.setObjectName(u"AdministrarVentas")
        AdministrarVentas.resize(1161, 731)
        self.verticalLayout = QVBoxLayout(AdministrarVentas)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(AdministrarVentas)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"QFrame { border: none; }")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(19, 15, 19, 0)
        self.btRegresar = QPushButton(self.frame)
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
        self.btRegresar.setText(u"")
        icon = QIcon()
        icon.addFile(u":/img/resources/images/leftarrow.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btRegresar.setIcon(icon)
        self.btRegresar.setIconSize(QSize(40, 40))
        self.btRegresar.setFlat(True)

        self.horizontalLayout.addWidget(self.btRegresar)

        self.lbTitulo = QLabel(self.frame)
        self.lbTitulo.setObjectName(u"lbTitulo")
        self.lbTitulo.setMinimumSize(QSize(321, 41))
        font = QFont()
        font.setPointSize(18)
        self.lbTitulo.setFont(font)

        self.horizontalLayout.addWidget(self.lbTitulo)


        self.verticalLayout.addWidget(self.frame, 0, Qt.AlignLeft)

        self.frame_2 = QFrame(AdministrarVentas)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setStyleSheet(u"")
        self.verticalLayout_2 = QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.frame_4 = QFrame(self.frame_2)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setStyleSheet(u"QFrame { border: none; }")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_6 = QFrame(self.frame_4)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.btFiltrar = QToolButton(self.frame_6)
        self.btFiltrar.setObjectName(u"btFiltrar")
        self.btFiltrar.setMinimumSize(QSize(41, 31))
        self.btFiltrar.setText(u"...")
        icon1 = QIcon()
        icon1.addFile(u":/img/resources/images/filter.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btFiltrar.setIcon(icon1)
        self.btFiltrar.setPopupMode(QToolButton.MenuButtonPopup)

        self.horizontalLayout_4.addWidget(self.btFiltrar)

        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.label_2 = QLabel(self.frame_6)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(51, 31))
        self.label_2.setMaximumSize(QSize(51, 31))
        self.label_2.setStyleSheet(u"image: url(:/img/resources/images/magnifier.png);\n"
"background-color: rgb(255, 255, 255);")

        self.horizontalLayout_4.addWidget(self.label_2)

        self.searchBar = QLineEdit(self.frame_6)
        self.searchBar.setObjectName(u"searchBar")
        self.searchBar.setMinimumSize(QSize(0, 31))
        font1 = QFont()
        font1.setPointSize(11)
        self.searchBar.setFont(font1)
        self.searchBar.setFrame(False)

        self.horizontalLayout_4.addWidget(self.searchBar)


        self.horizontalLayout_2.addWidget(self.frame_6)

        self.frame_7 = QFrame(self.frame_4)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setStyleSheet(u"QFrame { border: none; }")
        self.frame_7.setFrameShape(QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_7)
        self.horizontalLayout_3.setSpacing(30)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.btTerminar = QPushButton(self.frame_7)
        self.btTerminar.setObjectName(u"btTerminar")
        self.btTerminar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btTerminar.setStyleSheet(u"QPushButton {\n"
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
        self.btTerminar.setText(u"")
        icon2 = QIcon()
        icon2.addFile(u":/img/resources/images/accept.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btTerminar.setIcon(icon2)
        self.btTerminar.setIconSize(QSize(40, 40))
        self.btTerminar.setFlat(True)

        self.horizontalLayout_3.addWidget(self.btTerminar)

        self.btCancelar = QPushButton(self.frame_7)
        self.btCancelar.setObjectName(u"btCancelar")
        self.btCancelar.setCursor(QCursor(Qt.PointingHandCursor))
        self.btCancelar.setStyleSheet(u"QPushButton {\n"
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
        self.btCancelar.setText(u"")
        icon3 = QIcon()
        icon3.addFile(u":/img/resources/images/cancel.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btCancelar.setIcon(icon3)
        self.btCancelar.setIconSize(QSize(40, 40))
        self.btCancelar.setFlat(True)

        self.horizontalLayout_3.addWidget(self.btCancelar)


        self.horizontalLayout_2.addWidget(self.frame_7)


        self.verticalLayout_2.addWidget(self.frame_4)

        self.frame_11 = QFrame(self.frame_2)
        self.frame_11.setObjectName(u"frame_11")
        self.horizontalLayout_10 = QHBoxLayout(self.frame_11)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(-1, 0, -1, 0)
        self.frame_12 = QFrame(self.frame_11)
        self.frame_12.setObjectName(u"frame_12")
        self.frame_12.setFrameShape(QFrame.NoFrame)
        self.frame_12.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_12)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(2, 0, -1, 0)
        self.label = QLabel(self.frame_12)
        self.label.setObjectName(u"label")
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        font2.setPointSize(11)
        self.label.setFont(font2)

        self.horizontalLayout_7.addWidget(self.label)

        self.dateDesde = QDateEdit(self.frame_12)
        self.dateDesde.setObjectName(u"dateDesde")
        self.dateDesde.setMinimumSize(QSize(220, 0))
        self.dateDesde.setMaximumSize(QSize(220, 16777215))
        self.dateDesde.setFont(font2)
        self.dateDesde.setCalendarPopup(True)

        self.horizontalLayout_7.addWidget(self.dateDesde)

        self.label_4 = QLabel(self.frame_12)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font2)

        self.horizontalLayout_7.addWidget(self.label_4)

        self.dateHasta = QDateEdit(self.frame_12)
        self.dateHasta.setObjectName(u"dateHasta")
        self.dateHasta.setMinimumSize(QSize(220, 0))
        self.dateHasta.setMaximumSize(QSize(220, 16777215))
        self.dateHasta.setFont(font2)
        self.dateHasta.setCalendarPopup(True)

        self.horizontalLayout_7.addWidget(self.dateHasta)


        self.horizontalLayout_10.addWidget(self.frame_12, 0, Qt.AlignLeft)

        self.frame_13 = QFrame(self.frame_11)
        self.frame_13.setObjectName(u"frame_13")
        self.horizontalLayout_9 = QHBoxLayout(self.frame_13)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(60, -1, -1, -1)
        self.btHoy = QPushButton(self.frame_13)
        self.btHoy.setObjectName(u"btHoy")
        self.btHoy.setMinimumSize(QSize(115, 30))
        self.btHoy.setFont(font2)
        self.btHoy.setText(u"Hoy")

        self.horizontalLayout_9.addWidget(self.btHoy)

        self.btEstaSemana = QPushButton(self.frame_13)
        self.btEstaSemana.setObjectName(u"btEstaSemana")
        self.btEstaSemana.setMinimumSize(QSize(115, 30))
        self.btEstaSemana.setFont(font2)
        self.btEstaSemana.setText(u"Esta semana")

        self.horizontalLayout_9.addWidget(self.btEstaSemana)

        self.btEsteMes = QPushButton(self.frame_13)
        self.btEsteMes.setObjectName(u"btEsteMes")
        self.btEsteMes.setMinimumSize(QSize(115, 30))
        self.btEsteMes.setFont(font2)
        self.btEsteMes.setText(u"Este mes")

        self.horizontalLayout_9.addWidget(self.btEsteMes)


        self.horizontalLayout_10.addWidget(self.frame_13, 0, Qt.AlignLeft)


        self.verticalLayout_2.addWidget(self.frame_11, 0, Qt.AlignLeft)


        self.verticalLayout.addWidget(self.frame_2)

        self.frame_5 = QFrame(AdministrarVentas)
        self.frame_5.setObjectName(u"frame_5")
        self.horizontalLayout_8 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(19, -1, 19, -1)
        self.tabWidget = QTabWidget(self.frame_5)
        self.tabWidget.setObjectName(u"tabWidget")
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(10)
        self.tabWidget.setFont(font3)
        self.tabWidget.setDocumentMode(True)
        self.tabDirectas = QWidget()
        self.tabDirectas.setObjectName(u"tabDirectas")
        self.horizontalLayout_5 = QHBoxLayout(self.tabDirectas)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.tabla_ventasDirectas = TablaDatos(self.tabDirectas)
        if (self.tabla_ventasDirectas.columnCount() < 9):
            self.tabla_ventasDirectas.setColumnCount(9)
        __qtablewidgetitem = QTableWidgetItem()
        self.tabla_ventasDirectas.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tabla_ventasDirectas.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tabla_ventasDirectas.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tabla_ventasDirectas.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tabla_ventasDirectas.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tabla_ventasDirectas.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tabla_ventasDirectas.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tabla_ventasDirectas.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tabla_ventasDirectas.setHorizontalHeaderItem(8, __qtablewidgetitem8)
        self.tabla_ventasDirectas.setObjectName(u"tabla_ventasDirectas")
        self.tabla_ventasDirectas.setProperty("paginaActual", 0)

        self.horizontalLayout_5.addWidget(self.tabla_ventasDirectas)

        self.tabWidget.addTab(self.tabDirectas, "")
        self.tabPedidos = QWidget()
        self.tabPedidos.setObjectName(u"tabPedidos")
        self.verticalLayout_5 = QVBoxLayout(self.tabPedidos)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.tabla_pedidos = TablaDatos(self.tabPedidos)
        if (self.tabla_pedidos.columnCount() < 11):
            self.tabla_pedidos.setColumnCount(11)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tabla_pedidos.setHorizontalHeaderItem(0, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tabla_pedidos.setHorizontalHeaderItem(1, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tabla_pedidos.setHorizontalHeaderItem(2, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tabla_pedidos.setHorizontalHeaderItem(3, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tabla_pedidos.setHorizontalHeaderItem(4, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.tabla_pedidos.setHorizontalHeaderItem(5, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.tabla_pedidos.setHorizontalHeaderItem(6, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.tabla_pedidos.setHorizontalHeaderItem(7, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.tabla_pedidos.setHorizontalHeaderItem(8, __qtablewidgetitem17)
        __qtablewidgetitem18 = QTableWidgetItem()
        self.tabla_pedidos.setHorizontalHeaderItem(9, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        self.tabla_pedidos.setHorizontalHeaderItem(10, __qtablewidgetitem19)
        self.tabla_pedidos.setObjectName(u"tabla_pedidos")
        self.tabla_pedidos.setProperty("paginaActual", 0)

        self.verticalLayout_5.addWidget(self.tabla_pedidos)

        self.tabWidget.addTab(self.tabPedidos, "")

        self.horizontalLayout_8.addWidget(self.tabWidget)


        self.verticalLayout.addWidget(self.frame_5)

        self.frame_3 = QFrame(AdministrarVentas)
        self.frame_3.setObjectName(u"frame_3")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setStyleSheet(u"QFrame { border:none}")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.frame_3)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(-1, 0, 0, 0)
        self.frame_8 = QFrame(self.frame_3)
        self.frame_8.setObjectName(u"frame_8")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_8.sizePolicy().hasHeightForWidth())
        self.frame_8.setSizePolicy(sizePolicy1)
        self.frame_8.setFrameShape(QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.frame_8)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(-1, 15, 0, 9)
        self.lbContador = QLabel(self.frame_8)
        self.lbContador.setObjectName(u"lbContador")
        self.lbContador.setMinimumSize(QSize(271, 21))
        font4 = QFont()
        font4.setPointSize(11)
        font4.setBold(True)
        self.lbContador.setFont(font4)

        self.gridLayout.addWidget(self.lbContador, 0, 0, 1, 1)

        self.label_3 = QLabel(self.frame_8)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(601, 21))
        font5 = QFont()
        font5.setPointSize(11)
        font5.setBold(False)
        self.label_3.setFont(font5)

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)


        self.gridLayout_2.addWidget(self.frame_8, 1, 0, 1, 1, Qt.AlignBottom)

        self.frame_10 = QFrame(self.frame_3)
        self.frame_10.setObjectName(u"frame_10")
        self.frame_10.setStyleSheet(u"QFrame { border: none }")
        self.frame_10.setFrameShape(QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_10)
        self.horizontalLayout_6.setSpacing(7)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(-1, 0, 0, -1)
        self.btPrimero = QPushButton(self.frame_10)
        self.btPrimero.setObjectName(u"btPrimero")
        self.btPrimero.setMaximumSize(QSize(23, 23))
        font6 = QFont()
        font6.setPointSize(10)
        self.btPrimero.setFont(font6)
        self.btPrimero.setText(u"")
        icon4 = QIcon()
        icon4.addFile(u":/img/resources/images/backward.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btPrimero.setIcon(icon4)

        self.horizontalLayout_6.addWidget(self.btPrimero)

        self.btAtras = QPushButton(self.frame_10)
        self.btAtras.setObjectName(u"btAtras")
        self.btAtras.setMaximumSize(QSize(23, 23))
        self.btAtras.setFont(font6)
        self.btAtras.setText(u"")
        icon5 = QIcon()
        icon5.addFile(u":/img/resources/images/back.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btAtras.setIcon(icon5)

        self.horizontalLayout_6.addWidget(self.btAtras)

        self.lbPagina = QLabel(self.frame_10)
        self.lbPagina.setObjectName(u"lbPagina")
        self.lbPagina.setFont(font6)
        self.lbPagina.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_6.addWidget(self.lbPagina)

        self.btAdelante = QPushButton(self.frame_10)
        self.btAdelante.setObjectName(u"btAdelante")
        self.btAdelante.setMaximumSize(QSize(23, 23))
        self.btAdelante.setFont(font6)
        self.btAdelante.setText(u"")
        icon6 = QIcon()
        icon6.addFile(u":/img/resources/images/next.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btAdelante.setIcon(icon6)

        self.horizontalLayout_6.addWidget(self.btAdelante)

        self.btUltimo = QPushButton(self.frame_10)
        self.btUltimo.setObjectName(u"btUltimo")
        self.btUltimo.setMaximumSize(QSize(23, 23))
        self.btUltimo.setFont(font6)
        self.btUltimo.setText(u"")
        icon7 = QIcon()
        icon7.addFile(u":/img/resources/images/last.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btUltimo.setIcon(icon7)

        self.horizontalLayout_6.addWidget(self.btUltimo)


        self.gridLayout_2.addWidget(self.frame_10, 0, 0, 1, 1, Qt.AlignLeft)

        self.frame_9 = QFrame(self.frame_3)
        self.frame_9.setObjectName(u"frame_9")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame_9.sizePolicy().hasHeightForWidth())
        self.frame_9.setSizePolicy(sizePolicy2)
        self.frame_9.setFrameShape(QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.frame_9)
        self.verticalLayout_6.setSpacing(15)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(50, 0, 18, -1)
        self.btRecibo = QPushButton(self.frame_9)
        self.btRecibo.setObjectName(u"btRecibo")
        sizePolicy2.setHeightForWidth(self.btRecibo.sizePolicy().hasHeightForWidth())
        self.btRecibo.setSizePolicy(sizePolicy2)
        self.btRecibo.setMinimumSize(QSize(371, 38))
        self.btRecibo.setMaximumSize(QSize(504, 38))
        self.btRecibo.setFont(font1)
        self.btRecibo.setStyleSheet(u"")
        self.btRecibo.setText(u"Imprimir recibo")
        icon8 = QIcon()
        icon8.addFile(u":/img/resources/images/bill.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btRecibo.setIcon(icon8)
        self.btRecibo.setIconSize(QSize(30, 30))

        self.verticalLayout_6.addWidget(self.btRecibo)

        self.btOrden = QPushButton(self.frame_9)
        self.btOrden.setObjectName(u"btOrden")
        sizePolicy2.setHeightForWidth(self.btOrden.sizePolicy().hasHeightForWidth())
        self.btOrden.setSizePolicy(sizePolicy2)
        self.btOrden.setMinimumSize(QSize(371, 38))
        self.btOrden.setMaximumSize(QSize(504, 38))
        self.btOrden.setFont(font1)
        self.btOrden.setText(u"Imprimir orden de compra")
        icon9 = QIcon()
        icon9.addFile(u":/img/resources/images/order.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btOrden.setIcon(icon9)
        self.btOrden.setIconSize(QSize(30, 30))

        self.verticalLayout_6.addWidget(self.btOrden)


        self.gridLayout_2.addWidget(self.frame_9, 0, 1, 2, 1, Qt.AlignRight)


        self.verticalLayout.addWidget(self.frame_3)


        self.retranslateUi(AdministrarVentas)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(AdministrarVentas)
    # setupUi

    def retranslateUi(self, AdministrarVentas):
        AdministrarVentas.setWindowTitle(QCoreApplication.translate("AdministrarVentas", u"Form", None))
#if QT_CONFIG(tooltip)
        self.btRegresar.setToolTip(QCoreApplication.translate("AdministrarVentas", u"Regresar a men\u00fa de inicio", None))
#endif // QT_CONFIG(tooltip)
        self.lbTitulo.setText(QCoreApplication.translate("AdministrarVentas", u"Administrar ventas y pedidos", None))
#if QT_CONFIG(tooltip)
        self.btFiltrar.setToolTip(QCoreApplication.translate("AdministrarVentas", u"Filtrar b\u00fasqueda por...", None))
#endif // QT_CONFIG(tooltip)
        self.label_2.setText("")
        self.searchBar.setPlaceholderText(QCoreApplication.translate("AdministrarVentas", u"Busque venta por folio...", None))
#if QT_CONFIG(tooltip)
        self.btTerminar.setToolTip(QCoreApplication.translate("AdministrarVentas", u"Terminar orden seleccionada", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btCancelar.setToolTip(QCoreApplication.translate("AdministrarVentas", u"Marcar venta como cancelada", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("AdministrarVentas", u"Ver desde:", None))
        self.dateDesde.setDisplayFormat(QCoreApplication.translate("AdministrarVentas", u"d 'de' MMMM 'de' yyyy", None))
        self.label_4.setText(QCoreApplication.translate("AdministrarVentas", u"      Hasta:", None))
        self.dateHasta.setDisplayFormat(QCoreApplication.translate("AdministrarVentas", u"d 'de' MMMM 'de' yyyy", None))
        ___qtablewidgetitem = self.tabla_ventasDirectas.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("AdministrarVentas", u"Folio", None));
        ___qtablewidgetitem1 = self.tabla_ventasDirectas.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("AdministrarVentas", u"Vendedor", None));
        ___qtablewidgetitem2 = self.tabla_ventasDirectas.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("AdministrarVentas", u"Cliente", None));
        ___qtablewidgetitem3 = self.tabla_ventasDirectas.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("AdministrarVentas", u"Fecha", None));
        ___qtablewidgetitem4 = self.tabla_ventasDirectas.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("AdministrarVentas", u"Importe", None));
        ___qtablewidgetitem5 = self.tabla_ventasDirectas.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("AdministrarVentas", u"Estado", None));
        ___qtablewidgetitem6 = self.tabla_ventasDirectas.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("AdministrarVentas", u"Pago", None));
        ___qtablewidgetitem7 = self.tabla_ventasDirectas.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("AdministrarVentas", u"M\u00e9todo de pago", None));
        ___qtablewidgetitem8 = self.tabla_ventasDirectas.horizontalHeaderItem(8)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("AdministrarVentas", u"Comentarios", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabDirectas), QCoreApplication.translate("AdministrarVentas", u"Ventas directas", None))
        ___qtablewidgetitem9 = self.tabla_pedidos.horizontalHeaderItem(0)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("AdministrarVentas", u"Folio", None));
        ___qtablewidgetitem10 = self.tabla_pedidos.horizontalHeaderItem(1)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("AdministrarVentas", u"Vendedor", None));
        ___qtablewidgetitem11 = self.tabla_pedidos.horizontalHeaderItem(2)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("AdministrarVentas", u"Cliente", None));
        ___qtablewidgetitem12 = self.tabla_pedidos.horizontalHeaderItem(3)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("AdministrarVentas", u"Fecha", None));
        ___qtablewidgetitem13 = self.tabla_pedidos.horizontalHeaderItem(4)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("AdministrarVentas", u"Fecha de entrega", None));
        ___qtablewidgetitem14 = self.tabla_pedidos.horizontalHeaderItem(5)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("AdministrarVentas", u"Importe", None));
        ___qtablewidgetitem15 = self.tabla_pedidos.horizontalHeaderItem(6)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("AdministrarVentas", u"Estado", None));
        ___qtablewidgetitem16 = self.tabla_pedidos.horizontalHeaderItem(7)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("AdministrarVentas", u"Pago", None));
        ___qtablewidgetitem17 = self.tabla_pedidos.horizontalHeaderItem(8)
        ___qtablewidgetitem17.setText(QCoreApplication.translate("AdministrarVentas", u"M\u00e9todo de pago", None));
        ___qtablewidgetitem18 = self.tabla_pedidos.horizontalHeaderItem(9)
        ___qtablewidgetitem18.setText(QCoreApplication.translate("AdministrarVentas", u"Comentarios", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPedidos), QCoreApplication.translate("AdministrarVentas", u"Ventas sobre pedido", None))
        self.lbContador.setText(QCoreApplication.translate("AdministrarVentas", u"0 ventas en la base de datos.", None))
        self.label_3.setText(QCoreApplication.translate("AdministrarVentas", u"Haga doble click en alguna de las ventas para consultar detalles.", None))
        self.lbPagina.setText(QCoreApplication.translate("AdministrarVentas", u"1 de 1", None))
    # retranslateUi

