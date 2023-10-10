from PySide6 import QtWidgets
from PySide6.QtGui import QFont
from PySide6.QtCharts import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter

from utils.mywidgets import VentanaPrincipal
from utils.sql import ManejadorReportes


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
        
        self.ui.btRegresar.clicked.connect(self.goHome)
        
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
        
        # widgets de gráficos
        test = self.test()
        self.ui.stackedWidget.addWidget(test)
        
        self.ui.btTablero.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.btVentas.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        
    def test(self):
        manejador = ManejadorReportes(self.conn)
        
        data = manejador.fetchall('''
            SELECT 	FIRST 10
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
        
        font = QFont()
        font.setPointSize(11)
        
        chart = QChart()
        chart.setScale(1)
        chart.addSeries(series)
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
        
        chartView = QChartView(chart)
        chartView.setFont(font)
        chartView.setRenderHint(QPainter.Antialiasing)
        return chartView
    
    def test2(self):
        manejador = ManejadorReportes(self.conn)
        
        data = manejador.fetchall('''
            SELECT	FIRST 10
                    P.codigo,
                    SUM(
                        cantidad * IIF(cantidad > 0, 1, NULL)
                    ) AS numVentas,
                    SUM(importe) AS ingresos
            FROM	Ventas_Detallado AS VD
                    LEFT JOIN Productos AS P
                        ON VD.id_productos = P.id_productos
            GROUP	BY 1
            ORDER	BY 2 DESC;
        ''')
        
        categories = []
        set0 = QBarSet('Ventas con este producto')
        set1 = QBarSet('Ingresos de este producto')
        
        for codigo, cantidad, ingresos in data:
            categories.append(codigo)
            set0 << cantidad
            set1 << ingresos
        
        series = QBarSeries()
        series.append(set0)
        series.append(set1)
        
        font = QFont()
        font.setPointSize(11)
        
        chart = QChart()
        chart.setScale(1)
        chart.addSeries(series)
        chart.setTitle('Productos más vendidos')
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
        
        chartView = QChartView(chart)
        chartView.setFont(font)
        chartView.setRenderHint(QPainter.Antialiasing)
        
        self.ui.horizontalLayout_6.addWidget(chartView)
    
    def goHome(self):
        parent: VentanaPrincipal = self.parentWidget()
        parent.goHome()


#########################################
# WIDGETS PERSONALIZADOS PARA EL MÓDULO #
#########################################


"""
POSIBLES IDEAS.

Customer Sales Ranking: You can display a list of the top customers who have spent the most money in your store. This can help you 
identify your loyal customers and reward them with special offers or discounts.

Product Sales Report: You can display a report that shows which products are selling the most in your store. This can help you 
identify which products are popular among your customers and make informed decisions about inventory and promotions.

Customer Loyalty Report: You can display a report that shows how frequently your customers return to your store and make purchases. 
This can help you identify customers who are loyal to your store and reward them with special offers or discounts.

Sales Trends Report: You can display a report that shows the sales trends in your store over a period of time, such as monthly or 
quarterly. This can help you identify the seasonal trends in your business and make informed decisions about inventory and promotions.
"""
