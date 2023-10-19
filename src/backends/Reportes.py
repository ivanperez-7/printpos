from functools import partial

from PySide6 import QtWidgets
from PySide6.QtGui import QFont
from PySide6.QtCharts import *
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPainter, QPen

from utils.myinterfaces import InterfazFechasReportes
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
        
        for tbl in [self.ui.tableWidget,
                    self.ui.tableWidget_2,
                    self.ui.tableWidget_3,
                    self.ui.tableWidget_4]:
            tbl.configurarCabecera(lambda col: col not in [0, 3, 4, 5], 
                                   Qt.AlignCenter | Qt.TextWordWrap)
            tbl.tamanoCabecera(11)
            tbl.quitarBordeCabecera()
        
        # fechas por defecto
        manejador = ManejadorVentas(self.conn)
        fechaMin = manejador.obtenerFechaPrimeraVenta()
        
        InterfazFechasReportes(
            self.ui.btQuincena, self.ui.btMes, self.ui.btAnio,
            self.ui.dateDesde, self.ui.dateHasta, fechaMin)
        
        self.ui.btRegresar.clicked.connect(self.goHome)
        self.ui.stackedWidget.currentChanged.connect(self.actualizar_widget_activo)
        self.ui.dateHasta.dateChanged.connect(self.actualizar_widget_activo)
        self.ui.dateDesde.dateChanged.connect(self.actualizar_widget_activo)
        
        self.ui.btTablero.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.btVentas.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.btVendedores.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.btClientes.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(3))
        self.ui.btProductos.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(4))
    
    def showEvent(self, event):
        self.actualizar_widget_activo()
    
    # ==================
    #  FUNCIONES ÚTILES
    # ==================
    @property
    def fechaDesde(self):
        return self.ui.dateDesde.date()
    
    @property
    def fechaHasta(self):
        return self.ui.dateHasta.date()
    
    def actualizar_widget_activo(self):
        funcs = [
            self.actualizar_tablero,
            self.actualizar_tablero,
            self._actualizar_datos2,
            self._actualizar_datos,
            self.actualizar_tablero
        ]
        idx = self.ui.stackedWidget.currentIndex()
        funcs[idx]()
    
    # ************************************************ #
    def actualizar_tablero(self):
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
        self.ui.bar_ventas.alimentar_datos(self.conn)
        self.ui.pie_prods.alimentar_productos(self.conn)
        self.ui.pie_metodos.alimentar_metodos(self.conn)
    
    def _actualizar_datos(self):
        man = ManejadorReportes(self.conn)
        tabla = self.ui.tableWidget_3
        tabla.llenar(man.obtenerReporteClientes(self.fechaDesde, self.fechaHasta))
        tabla.resizeRowsToContents()
    
    def _actualizar_datos2(self):
        man = ManejadorReportes(self.conn)
        tabla = self.ui.tableWidget_2
        tabla.llenar(man.obtenerReporteVendedores(self.fechaDesde, self.fechaHasta))
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
    
    def alimentar_datos(self, conn):
        chart = QChart()
        series = QBarSeries()
        set0 = QBarSet("Ventas brutas")
        
        # Replace this with your sales data for each month
        man = ManejadorReportes(conn)
        current_year = QDate.currentDate().year()
        data = man.obtenerGraficaVentas(current_year)
        
        month_labels = []
        
        for anio_mes, total, num_ventas in data:
            set0.append(total)
            month_labels.append(anio_mes)

        series.append(set0)
        chart.addSeries(series)

        chart.setTitle(f"Ventas por mes del año {current_year}")
        chart.setFont(self.font())
        chart.setTitleFont(self.font())
        chart.setAnimationOptions(QChart.AllAnimations)

        categories_axis = QBarCategoryAxis()
        categories_axis.append(month_labels)
        #categories_axis.setLabelsFont(self.font())
        #categories_axis.setTitleFont(self.font())
        chart.createDefaultAxes()
        chart.setAxisX(categories_axis, series)

        self.setChart(chart)


class ChartView2(QChartView):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        font = QFont()
        font.setPointSize(11)
        self.setFont(font)
    
    def alimentar_productos(self, conn):
        man = ManejadorReportes(conn)
        series = QPieSeries()
        
        for abrev, codigo, num in man.obtenerTopProducto(6)[1:]:
            s = series.append(codigo + ' ({})'.format(stringify_float(num)), num)
            s.hovered.connect(partial(self.handle_slice_hover, s))

        _slice = max(series.slices(), key=lambda s: s.value())
        _slice.setLabelVisible(True)
        _slice.setPen(QPen(Qt.darkRed, 2))
        _slice.setBrush(Qt.red)
        _slice.hovered.disconnect()
        _slice.hovered.connect(partial(self.handle_max_hover, _slice))
        
        chart = QChart()
        chart.setFont(self.font())
        chart.setTitleFont(self.font())
        chart.addSeries(series)
        chart.setTitle('Los otros productos más vendidos')
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().hide()
        
        self.setChart(chart)
        self.setRenderHint(QPainter.Antialiasing)
    
    def alimentar_metodos(self, conn):
        man = ManejadorReportes(conn)
        series = QPieSeries()
        
        for metodo, num in man.obtenerGraficaMetodos():
            s = series.append(metodo + ' ({})'.format(num), num)
            s.hovered.connect(partial(self.handle_slice_hover, s))

        _slice = max(series.slices(), key=lambda s: s.value())
        _slice.setLabelVisible(True)
        _slice.setPen(QPen(Qt.darkBlue, 2))
        _slice.setBrush(Qt.blue)
        _slice.hovered.disconnect()
        _slice.hovered.connect(partial(self.handle_max_hover, _slice))
        
        chart = QChart()
        chart.setFont(self.font())
        chart.setTitleFont(self.font())
        chart.addSeries(series)
        chart.setTitle('Métodos de pago más usados')
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().hide()
        
        self.setChart(chart)
        self.setRenderHint(QPainter.Antialiasing)
    
    def handle_slice_hover(self, _slice, state):
        _slice.setExploded(state)
        _slice.setLabelVisible(state)
    
    def handle_max_hover(self, _slice, state):
        _slice.setExploded(state)


"""
POSIBLES IDEAS.

Product Sales Report: You can display a report that shows which products are selling the most in your store. This can help you 
identify which products are popular among your customers and make informed decisions about inventory and promotions.

Sales Trends Report: You can display a report that shows the sales trends in your store over a period of time, such as monthly or 
quarterly. This can help you identify the seasonal trends in your business and make informed decisions about inventory and promotions.
"""
