from datetime import datetime

from PySide6 import QtWidgets
from PySide6.QtGui import QFont
from PySide6.QtCharts import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen

from utils.myinterfaces import InterfazFechas
from utils.mywidgets import VentanaPrincipal
from utils.sql import ManejadorReportes, ManejadorVentas


stringify_float = lambda f: f'{int(f):,}' if f.is_integer() else f'{f:,.2f}'

class App_Reportes(QtWidgets.QWidget):
    """ Backend para la ventana de reportes varios. """
    
    def __init__(self, parent: VentanaPrincipal):
        from ui.Ui_Reportes import Ui_Reportes
        
        super().__init__()
        
        self.ui = Ui_Reportes()
        self.ui.setupUi(self)
        
        self.conn = parent.conn
        self.user = parent.user
        
        for tbl in [self.ui.tableWidget, self.ui.tableWidget_2, self.ui.tableWidget_3, self.ui.tableWidget_4]:
            #tbl.configurarCabecera(lambda col: col <= 2 or col == 7, Qt.AlignCenter | Qt.TextWordWrap)
            tbl.tamanoCabecera(11)
            tbl.quitarBordeCabecera()
        
        # fechas por defecto
        manejador = ManejadorVentas(self.conn)
        fechaMin = manejador.obtenerFechaPrimeraVenta()
        
        InterfazFechas(self.ui.btHoy, self.ui.btEstaSemana, self.ui.btEsteMes,
                       self.ui.dateDesde, self.ui.dateHasta, fechaMin)
        
        self.ui.btRegresar.clicked.connect(self.goHome)
        self.ui.dateHasta.dateChanged.connect(self.actualizar_datos)
        self.ui.dateDesde.dateChanged.connect(self.actualizar_datos)
        
        self.ui.btTablero.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.btVentas.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.btVendedores.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.btClientes.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(3))
        self.ui.btProductos.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(4))
    
    def showEvent(self, event):
        self.actualizar_datos()
    
    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    def actualizar_datos(self):
        fechaDesde = self.ui.dateDesde.date()
        fechaHasta = self.ui.dateHasta.date()
        
        # alimentar QLabels
        man = ManejadorReportes(self.conn)
        brutos, num_ventas = man.obtenerIngresosBrutos()
        self.ui.lbIngresosBrutos.setText('${:,.2f}'.format(brutos))
        self.ui.lbCountVentas.setText('a través de {:,d} ventas'.format(num_ventas))
        
        vendedor, cantidad = man.obtenerTopVendedor()
        self.ui.lbVendedorBrutos.setText(vendedor)
        self.ui.lbVendedorTotal.setText('${:,.2f}'.format(cantidad))
        
        abreviado, codigo, count = man.obtenerTopProducto()
        self.ui.lbProdVendidos.setText(codigo)
        self.ui.lbProdCount.setText(stringify_float(count) + ' unidades')
        
        # gráficas 
        self.ui.placeholder_1.alimentarDatos(self.conn)
        
        # llenar tablas
        tabla = self.ui.tableWidget_3
        tabla.llenar(man.obtenerReporteClientes())
        tabla.resizeColumnsToContents()
        tabla.resizeRowsToContents()
        
        tabla = self.ui.tableWidget_2
        tabla.llenar(man.obtenerReporteVendedores())
        tabla.resizeColumnsToContents()
        tabla.resizeRowsToContents()
    
    def goHome(self):
        parent: VentanaPrincipal = self.parentWidget()
        parent.goHome()


#########################################
# WIDGETS PERSONALIZADOS PARA EL MÓDULO #
#########################################
class ChartView(QChartView):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        font = QFont()
        font.setPointSize(11)
        
        self.setFont(font)
        self.setRenderHint(QPainter.Antialiasing)
    
    def alimentarDatos(self, conn):
        manejador = ManejadorReportes(conn)
        
        data = manejador.fetchall('''
            SELECT 	FIRST 5
                    Clientes.nombre,
                    COUNT (
                        IIF(fecha_hora_creacion = fecha_hora_entrega, 1, NULL)
                    ) AS numDirectas,
                    COUNT (
                        IIF(fecha_hora_creacion != fecha_hora_entrega, 1, NULL)
                    ) AS numPedidos
            FROM 	Ventas
                    LEFT JOIN Clientes
                        ON Ventas.id_clientes = Clientes.id_clientes
            WHERE	nombre != 'Público general'
            GROUP	BY Clientes.nombre
            ORDER	BY COUNT(id_ventas) DESC;
        ''')
        
        categories = []
        set0 = QBarSet('Ventas al contado')
        set1 = QBarSet('Ventas sobre pedido')
        
        for nombre, numVentas, numPedidos in data:
            categories.append(nombre)
            set0 << numVentas
            set1 << numPedidos
        
        series = QBarSeries()
        series.append(set0)
        series.append(set1)
        
        font = self.font()
        chart = QChart()
        chart.addSeries(series)
        chart.setScale(1)
        chart.setTitle('Clientes con más ventas del negocio')
        chart.setTitleFont(font)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        axis = QBarCategoryAxis()
        axis.append(categories)
        chart.createDefaultAxes()
        chart.setAxisX(axis, series)
        chart.axisX().setLabelsFont(font)
        chart.axisX().setTitleFont(font)
        chart.axisY().setLabelsFont(font)
        chart.axisY().setTitleFont(font)
        
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.legend().setFont(font)
        self.setChart(chart)


class ChartView2(QChartView):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        font = QFont()
        font.setPointSize(11)
        self.series = QPieSeries()
        
        self.series.append('Jane', 1)
        self.series.append('Joe', 2)
        self.series.append('Andy', 3)
        self.series.append('Barbara', 4)
        self.series.append('Axel', 5)

        self.slice = self.series.slices()[1]
        self.slice.setExploded(True)
        self.slice.setLabelVisible(True)
        self.slice.setPen(QPen(Qt.darkGreen, 2))
        self.slice.setBrush(Qt.green)
        self.slice.setLabelFont(font)
        chart = QChart()
        chart.setFont(font)
        chart.setTitleFont(font)
        chart.addSeries(self.series)
        chart.setTitle('Simple piechart example')
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().hide()
        
        self.setChart(chart)
        self.setRenderHint(QPainter.Antialiasing)


"""
POSIBLES IDEAS.

Product Sales Report: You can display a report that shows which products are selling the most in your store. This can help you 
identify which products are popular among your customers and make informed decisions about inventory and promotions.

Sales Trends Report: You can display a report that shows the sales trends in your store over a period of time, such as monthly or 
quarterly. This can help you identify the seasonal trends in your business and make informed decisions about inventory and promotions.
"""
